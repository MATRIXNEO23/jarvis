"""Reusable, opt-in native chat session with bounded local history.

No online fallback, no desktop actions and no model load on import.
"""
from collections import deque
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
