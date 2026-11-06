"""Reusable, opt-in native chat session with bounded local history.

No online fallback, no desktop actions and no model load on import.
"""
from collections import deque
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

from threading import RLock

from .memory_preferences import MemoryPreferences, default_memory_preferences_path
from .native_config import NativeModelConfig
from .native_settings import default_native_settings_path


class NativeConversationSession:
    def __init__(self, adapter, *, config_loader=None, memory_loader=None):
        self.adapter = adapter
        self.config_loader = config_loader or (
            lambda: NativeModelConfig.load(default_native_settings_path()))
        self.memory_loader = memory_loader or (
            lambda: MemoryPreferences.load(default_memory_preferences_path()))
        self.history = deque(maxlen=32)
        self.prepared = False
        self.lock = RLock()

    def ask(self, question, *, timeout=180):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Domanda locale vuota.")
        with self.lock:
            config = self.config_loader().validate()
            memory = self.memory_loader().validate()
            budget = memory.available_prompt_tokens(
                config.context_size, config.max_output)
            # Conservative character budget: never claim this is a tokenizer.
            latest = question.strip()
            turns = list(self.history)[-memory.recent_messages:]
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
            if not self.prepared:
                self.adapter.prepare()
                self.prepared = True
            result = self.adapter.call("ask", prompt=prompt, timeout=timeout)
            answer = clean_native_answer(result.get("text"))
            self.history.append(("user", latest))
            self.history.append(("assistant", answer[:2000]))
            return answer

    def ask_isolated(self, build_prompt, *, timeout=180):
        """Share the loaded model without reading or changing chat history."""
        with self.lock:
            config = self.config_loader().validate()
            memory = self.memory_loader().validate()
            prompt = build_prompt(memory.available_prompt_tokens(
                config.context_size, config.max_output))
            if not self.prepared:
                self.adapter.prepare()
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
            if not self.prepared:
                self.adapter.prepare()
                self.prepared = True
            answer = clean_native_answer(
                self.adapter.call("ask", prompt=prompt, timeout=timeout).get("text"))
            if re.fullmatch(r"[0-9]{1,2}", answer):
                index = int(answer) - 1
                if 0 <= index < len(names):
                    return index
            return None

    def stop(self):
        with self.lock:
            if self.prepared:
                self.adapter.stop()
                self.prepared = False
