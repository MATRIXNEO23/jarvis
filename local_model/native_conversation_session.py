"""Reusable, opt-in native chat session with bounded local history.

No online fallback, no desktop actions and no model load on import.
"""
from collections import deque
from dataclasses import replace
import json
import re

def clean_native_answer(text):
    """Remove known internal-note sections before storing or speaking."""
    if not isinstance(text, str):
        raise RuntimeError("Risposta Gemma non valida.")
    value = re.sub(r"(?is)<think>.*?</think>", "", text)
    value = re.sub(r"(?is)<think>.*", "", value)
    headers = ("what's going right", "conversation flow", "internal reasoning",
               "analysis:", "thinking:", "reasoning:")
    lines = value.splitlines()
    for index, line in enumerate(lines):
        plain = line.strip().lower().strip('*- "“”')
        if any(plain.startswith(header) for header in headers):
            lines = lines[:index]
            break
    return "\n".join(lines).strip() or "Puoi ripetere la domanda?"

from threading import Lock, RLock

from .memory_preferences import MemoryPreferences, default_memory_preferences_path
from .native_config import NativeModelConfig
from .native_settings import default_native_settings_path


class NativeChatTurn:
    """An answered turn that the owner UI has not yet accepted into history.

    This object is internal data, never a model command or a persistent record.
    Its default repr deliberately does not expose conversational text.
    """
    def __init__(self, session, context_id, question, text):
        self._session = session
        self.context_id = context_id
        self.question = question
        self.text = text
        self._committed = False

    def commit(self):
        return self._session._commit_turn(self)


class NativeConversationSession:
    def __init__(self, adapter, *, config_loader=None, memory_loader=None):
        self.adapter = adapter
        self.config_loader = config_loader or (
            lambda: NativeModelConfig.load(default_native_settings_path()))
        self.memory_loader = memory_loader or (
            lambda: MemoryPreferences.load(default_memory_preferences_path()))
        # Same global budget as before: 32 messages = 16 complete exchanges,
        # shared across contexts, rather than an unbounded cache per project.
        self._turns = deque(maxlen=16)
        self._history_lock = Lock()
        self.prepared = False
        self._prepared_config = None
        self.lock = RLock()

    @property
    def history(self):
        """Snapshot of general-chat messages, for legacy read-only callers."""
        return deque(self._messages(None), maxlen=32)

    def _messages(self, context_id):
        with self._history_lock:
            turns = tuple(self._turns)
        return [message for owner, question, answer in turns if owner == context_id
                for message in (("user", question), ("assistant", answer))]

    def _commit_turn(self, turn):
        # Only a brief metadata lock: accepting an answer must never wait
        # behind a Telegram/model generation holding the inference lock.
        with self._history_lock:
            if turn._committed:
                return False
            self._turns.append((turn.context_id, turn.question, turn.text[:2000]))
            turn._committed = True
            return True

    def _prepare(self, config):
        # Personality is already read into each chat prompt and needs no
        # native change. Keep all inference values from the same snapshot.
        snapshot = replace(config, personality="")
        if self.prepared and snapshot == self._prepared_config:
            return
        self.prepared = False
        self.adapter.prepare(config=config)
        self._prepared_config = snapshot
        self.prepared = True

    def ask(self, question, *, timeout=180, context_id=None):
        """Synchronous standalone API; the GUI uses prepare_turn instead."""
        with self.lock:
            turn = self.prepare_turn(question, timeout=timeout, context_id=context_id)
            turn.commit()
            return turn.text

    def prepare_turn(self, question, *, timeout=180, context_id=None):
        """Generate locally; the UI must validate its epoch before commit()."""
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Domanda locale vuota.")
        if context_id is not None and (not isinstance(context_id, str)
                                      or not re.fullmatch(r"[a-f0-9]{32}", context_id)):
            raise ValueError("Contesto progetto locale non valido.")
        with self.lock:
            config = self.config_loader().validate()
            memory = self.memory_loader().validate()
            budget = memory.available_prompt_tokens(
                config.context_size, config.max_output)
            # Conservative character budget: never claim this is a tokenizer.
            latest = question.strip()
            turns = self._messages(context_id)[-memory.recent_messages:]
            instructions = "Rispondi in italiano in modo diretto, senza analisi o note interne.\n"
            suffix = "Utente: " + latest + "\nJarvis:"
            style = "Stile di risposta: " + " ".join(config.personality.split()) + "\n"
            if config.personality.strip() and len(instructions) + len(style) + len(suffix) <= budget:
                instructions += style
            if len(instructions) + len(suffix) > budget:
                instructions = ""
            history = ""
            # Keep the newest complete messages first. Budget for the actual
            # prompt, not only the question; do not silently lose its role tag.
            if len(suffix) > budget:
                raise ValueError("Domanda troppo lunga per il contesto configurato.")
            for role, text in reversed(turns):
                candidate = ("Utente: " if role == "user" else "Jarvis: ") + text + "\n"
                if len(instructions) + len(history) + len(candidate) + len(suffix) > budget:
                    break
                history = candidate + history
            prompt = instructions + history + suffix
            self._prepare(config)
            result = self.adapter.call("ask", prompt=prompt, timeout=timeout)
            answer = clean_native_answer(result.get("text"))
            return NativeChatTurn(self, context_id, latest, answer)

    def ask_isolated(self, build_prompt, *, timeout=180):
        """Share the loaded model without reading or changing chat history."""
        with self.lock:
            config = self.config_loader().validate()
            memory = self.memory_loader().validate()
            prompt = build_prompt(memory.available_prompt_tokens(
                config.context_size, config.max_output))
            self._prepare(config)
            result = self.adapter.call("ask", prompt=prompt, timeout=timeout)
            return clean_native_answer(result.get("text"))

    def test_generation(self, *, config=None, timeout=180):
        """Explicit isolated trial, serialized with chat/Telegram and reload.

        Keep this session's ownership and history. The saved configuration
        snapshot is passed into prepare so another UI save cannot change the
        model between validation and the native load.
        """
        with self.lock:
            current = self.config_loader().validate()
            if config is not None and config != current:
                raise ValueError("Impostazioni Gemma cambiate: ripeti la prova.")
            memory = self.memory_loader().validate()
            budget = memory.available_prompt_tokens(current.context_size, current.max_output)
            prompt = "Presentati con una breve frase in italiano."
            style = "Stile di risposta: " + " ".join(current.personality.split()) + "\n"
            if current.personality.strip() and len(style) + len(prompt) <= budget:
                prompt = style + prompt
            if len(prompt) > budget:
                raise ValueError("Budget di contesto insufficiente per la prova Gemma.")
            # The old trial loaded a fresh model every time. Preserve that
            # explicit reload, but only after all earlier generations finish.
            self.stop()
            self.adapter.prepare(config=current)
            self._prepared_config = replace(current, personality="")
            self.prepared = True
            result = self.adapter.call("ask", prompt=prompt, timeout=timeout)
            return clean_native_answer(result.get("text"))

    def pick_program(self, question, names, *, timeout=180):
        """Return the index of a suggested app, or None, without chat history."""
        prompt = ("Scegli un programma per la richiesta. Rispondi solo con il numero "
                  "nell'elenco. Rispondi 0 se manca una scelta chiara.\n"
                  + json.dumps(dict(programmi=dict(enumerate(names, 1)),
                                    richiesta=question), ensure_ascii=False))
        with self.lock:
            config = self.config_loader().validate()
            memory = self.memory_loader().validate()
            if len(prompt) > memory.available_prompt_tokens(config.context_size, config.max_output):
                raise ValueError("Richiesta o elenco troppo lungo per il contesto Gemma.")
            self._prepare(config)
            answer = clean_native_answer(
                self.adapter.call("ask", prompt=prompt, timeout=timeout).get("text"))
            if re.fullmatch(r"[0-9]{1,2}", answer):
                index = int(answer) - 1
                if 0 <= index < len(names):
                    return index
            return None

    def stop(self):
        with self.lock:
            # Failed reconfiguration can retain an old provider while this
            # session is unprepared. Revoke state before any abort can fail.
            self.prepared = False
            self._prepared_config = None
            self.adapter.stop()
