"""Validated, persistent idle-memory preferences. No background work on import."""
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import tempfile


@dataclass(frozen=True)
class MemoryPreferences:
    idle_seconds: int = 60
    recent_messages: int = 8
    summarize_every: int = 8
    summary_max_tokens: int = 150
    prompt_max_tokens: int = 600
    max_background_jobs: int = 1
    conversation_priority: bool = True
    pause_on_heavy_load: bool = True
    background_summaries: bool = True

    def validate(self):
        for key, minimum, maximum in (
            ("idle_seconds", 10, 3600),
            ("recent_messages", 2, 32),
            ("summarize_every", 2, 64),
            ("summary_max_tokens", 32, 1024),
            ("prompt_max_tokens", 128, 8192),
            ("max_background_jobs", 1, 1),
        ):
            value = getattr(self, key)
            if type(value) is not int or not minimum <= value <= maximum:
                raise ValueError("Valore non valido: " + key)
        for key in ("conversation_priority", "pause_on_heavy_load",
                    "background_summaries"):
            if type(getattr(self, key)) is not bool:
                raise ValueError("Valore non valido: " + key)
        if self.summary_max_tokens >= self.prompt_max_tokens:
            raise ValueError("Il riassunto deve essere minore del budget prompt.")
        return self

    @classmethod
    def load(cls, path):
        path = Path(path)
        if not path.exists():
            return cls()
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(obj, dict) or set(obj) != set(cls.__dataclass_fields__):
                raise ValueError("Schema memoria non valido.")
            return cls(**obj).validate()
        except (OSError, UnicodeError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("Impostazioni memoria danneggiate.") from exc

    def available_prompt_tokens(self, context_size, max_output, reserve=128):
        """Limit memory prompt to the model window after output reservation."""
        self.validate()
        if any(type(x) is not int for x in (context_size, max_output, reserve)):
            raise ValueError("Dimensioni contesto non valide.")
        if context_size < 256 or max_output < 1 or reserve < 0:
            raise ValueError("Dimensioni contesto non valide.")
        available = context_size - max_output - reserve
        if available < 1:
            raise ValueError("Contesto insufficiente per risposta e margine.")
        return min(self.prompt_max_tokens, available)

    def save(self, path):
        self.validate()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent,
                prefix=path.name + ".", suffix=".tmp", delete=False
            ) as stream:
                temp = Path(stream.name)
                json.dump(asdict(self), stream, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            if temp is not None and temp.exists():
                temp.unlink()


def default_memory_preferences_path():
    trial = os.environ.get("JARVIS_TRIAL_HOME")
    if trial:
        return Path(trial) / "addon-data" / "modello_locale" / "memory.json"
    local = os.environ.get("LOCALAPPDATA")
    if not local:
        raise RuntimeError("LOCALAPPDATA non disponibile.")
    return Path(local) / "Jarvis" / "addon-data" / "modello_locale" / "memory.json"
