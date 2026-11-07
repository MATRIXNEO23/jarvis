"""ModelService-compatible local inference adapter, no online or HTTP access.

This is an opt-in component; existing Jarvis routing is unchanged.
"""
import threading


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
            if prompt is None:
                if not isinstance(messages, list) or not messages:
                    raise RuntimeError("Messaggi mancanti.")
                parts = []
                for message in messages:
                    if not isinstance(message, dict) or message.get("role") not in ("user", "assistant"):
                        raise RuntimeError("Formato messaggi non supportato.")
                    content = message.get("content")
                    if not isinstance(content, str) or not content.strip():
                        raise RuntimeError("Contenuto messaggio non valido.")
                    role = "model" if message["role"] == "assistant" else "user"
                    parts.append("<start_of_turn>" + role + "\n" + content + "<end_of_turn>\n")
                prompt = "".join(parts) + "<start_of_turn>model\n"
            elif isinstance(prompt, str) and prompt.strip():
                prompt = "<start_of_turn>user\n" + prompt + "<end_of_turn>\n<start_of_turn>model\n"
            else:
                raise RuntimeError("Prompt locale non valido.")
            self.bridge.load()
            return self.bridge.generate(prompt, timeout=timeout)

    def stop(self):
        # Request cooperative abort without acquiring the ask/load lock.
        self._stopped = True
        abort = getattr(self.bridge, "abort", None)
        if callable(abort):
            abort()
