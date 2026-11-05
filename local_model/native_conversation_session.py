"""Reusable, opt-in native chat session with bounded local history.

No online fallback, no desktop actions and no model load on import.
"""
from collections import deque
import re

# Never forward recognizable model-side planning sections to the console or TTS.
_PLANNING_HEADER = re.compile(r'(?im)^\s*(?:[-*] ?)?(?:["“”]?)(?:what.s going right|conversation flow|internal reasoning|analysis|thinking|reasoning|plan of action)(?:["“”]?)\s*:?\s*from threading import RLock

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
            if len(latest) > budget:
                raise ValueError("Domanda troppo lunga per il contesto configurato.")
            turns = list(self.history)[-memory.recent_messages:]
            instruction = ("Rispondi come Jarvis in italiano, in modo naturale e diretto. "
                           "Non scrivere analisi, piani, istruzioni interne o note di valutazione. "
                           "Non fingere di aver eseguito azioni sul computer.\\n")
            prefix = instruction
            suffix = "Utente: " + latest + "\\nJarvis:"
            # Keep the newest complete messages first. Budget for the actual
            # prompt, not only the question; do not silently lose its role tag.
            if len(suffix) > budget:
                raise ValueError("Domanda troppo lunga per il contesto configurato.")
            for role, text in reversed(turns):
                candidate = ("Utente: " if role == "user" else "Jarvis: ") + text + "\n"
                if len(prefix) + len(candidate) + len(suffix) > budget:
                    break
                prefix = candidate + prefix
            prompt = prefix + suffix
            if not self.prepared:
                self.adapter.prepare()
                self.prepared = True
            result = self.adapter.call("ask", prompt=prompt, timeout=timeout)
            answer = clean_native_answer(result.get("text"))
            self.history.append(("user", latest))
            self.history.append(("assistant", answer[:2000]))
            return answer

    def stop(self):
        with self.lock:
            if self.prepared:
                self.adapter.stop()
                self.prepared = False
)
_INLINE_PLANNING = re.compile(r'(?im)^\s*[-*]?\s*["“”]?(?:what.s going right|conversation flow|internal reasoning|analysis|thinking|reasoning)["“”]?\s*[:—-]')


def clean_native_answer(text):
    """Conservative visible/spoken answer filter; do not expose planning notes."""
    if not isinstance(text, str):
        raise RuntimeError('Risposta Gemma non valida.')
    value = re.sub(r'(?is)<think>.*?</think>', '', text)
    value = re.sub(r'(?is)<think>.*from threading import RLock

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
            if len(latest) > budget:
                raise ValueError("Domanda troppo lunga per il contesto configurato.")
            turns = list(self.history)[-memory.recent_messages:]
            prefix = ""
            suffix = "Utente: " + latest
            # Keep the newest complete messages first. Budget for the actual
            # prompt, not only the question; do not silently lose its role tag.
            if len(suffix) > budget:
                raise ValueError("Domanda troppo lunga per il contesto configurato.")
            for role, text in reversed(turns):
                candidate = ("Utente: " if role == "user" else "Jarvis: ") + text + "\n"
                if len(prefix) + len(candidate) + len(suffix) > budget:
                    break
                prefix = candidate + prefix
            prompt = prefix + suffix
            if not self.prepared:
                self.adapter.prepare()
                self.prepared = True
            result = self.adapter.call("ask", prompt=prompt, timeout=timeout)
            answer = result.get("text")
            if not isinstance(answer, str):
                raise RuntimeError("Risposta Gemma non valida.")
            self.history.append(("user", latest))
            self.history.append(("assistant", answer[:2000]))
            return answer

    def stop(self):
        with self.lock:
            if self.prepared:
                self.adapter.stop()
                self.prepared = False
, '', value)
    value = re.sub(r'(?is)```(?:thinking|analysis|reasoning)\b.*?```', '', value)
    lines = value.splitlines()
    cut = next((i for i, line in enumerate(lines) if _PLANNING_HEADER.match(line) or _INLINE_PLANNING.match(line)), None)
    if cut is not None:
        lines = lines[:cut]
    value = '\n'.join(lines).strip()
    return value or 'Non riesco a formulare una risposta affidabile. Puoi ripetere la domanda?'

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
            if len(latest) > budget:
                raise ValueError("Domanda troppo lunga per il contesto configurato.")
            turns = list(self.history)[-memory.recent_messages:]
            prefix = ""
            suffix = "Utente: " + latest
            # Keep the newest complete messages first. Budget for the actual
            # prompt, not only the question; do not silently lose its role tag.
            if len(suffix) > budget:
                raise ValueError("Domanda troppo lunga per il contesto configurato.")
            for role, text in reversed(turns):
                candidate = ("Utente: " if role == "user" else "Jarvis: ") + text + "\n"
                if len(prefix) + len(candidate) + len(suffix) > budget:
                    break
                prefix = candidate + prefix
            prompt = prefix + suffix
            if not self.prepared:
                self.adapter.prepare()
                self.prepared = True
            result = self.adapter.call("ask", prompt=prompt, timeout=timeout)
            answer = result.get("text")
            if not isinstance(answer, str):
                raise RuntimeError("Risposta Gemma non valida.")
            self.history.append(("user", latest))
            self.history.append(("assistant", answer[:2000]))
            return answer

    def stop(self):
        with self.lock:
            if self.prepared:
                self.adapter.stop()
                self.prepared = False
