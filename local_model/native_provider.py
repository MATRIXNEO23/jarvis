"""ModelService-compatible local inference adapter, no online or HTTP access.

This is an opt-in component; existing Jarvis routing is unchanged.
"""
import threading


def format_gemma_messages(messages):
    """Serialize text-only Gemma 2/3 IT turns exactly once, without a system role."""
    if not isinstance(messages, list) or not messages or len(messages) % 2 != 1:
        raise RuntimeError("Messaggi Gemma non validi.")
    parts = []
    for index, message in enumerate(messages):
        expected = "user" if index % 2 == 0 else "assistant"
        if not isinstance(message, dict) or message.get("role") != expected:
            raise RuntimeError("Sequenza ruoli Gemma non valida.")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Contenuto messaggio non valido.")
        # Conversational data must not introduce new native role boundaries.
        for token in ("<start_of_turn>", "<end_of_turn>", "<bos>", "<eos>"):
            content = content.replace(token, token.replace("<", "‹").replace(">", "›"))
        role = "model" if expected == "assistant" else "user"
        parts.append("<start_of_turn>" + role + "\n" + content + "<end_of_turn>\n")
    return "".join(parts) + "<start_of_turn>model\n"


class NativeLocalProvider:
    def __init__(self, bridge):
        self.bridge = bridge
        self._lock = threading.RLock()
        self._stopped = False

    def ask(self, *, prompt=None, messages=None, timeout=120, **kwargs):
        with self._lock:
            if self._stopped:
                raise RuntimeError("Modello locale arrestato.")
            if kwargs:
                raise RuntimeError("Parametri locali non supportati.")
            if prompt is not None and messages is not None:
                raise RuntimeError("Specificare prompt oppure messaggi.")
            if prompt is None:
                pass
            elif isinstance(prompt, str) and prompt.strip():
                messages = [{"role": "user", "content": prompt}]
            else:
                raise RuntimeError("Prompt locale non valido.")
            self.bridge.load()
            from .chat_templates import format_messages
            prompt = format_messages(messages, getattr(self.bridge, "family", "gemma2"))
            return self.bridge.generate(prompt, timeout=timeout)

    def count_tokens(self, prompt):
        with self._lock:
            if self._stopped:
                raise RuntimeError("Modello locale arrestato.")
            self.bridge.load()
            return self.bridge.count_tokens(prompt)

    def stop(self):
        # Request cooperative abort without acquiring the ask/load lock.
        self._stopped = True
        abort = getattr(self.bridge, "abort", None)
        if callable(abort):
            abort()
