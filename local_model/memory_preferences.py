"""Validated, persistent idle-memory preferences. No background work on import."""
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import tempfile


_OLD_DEFAULT_HISTORY = 250
# Chiavi del file accanto (memory.native.json): le vecchie versioni rifiutano chiavi in più in memory.json.
NATIVE_KEYS = ("history_max_tokens", "cronologia_ridotta", "chat_continua", "ricordi_locale")
_RICORDI = ("mai", "pertinenti", "sempre")


@dataclass(frozen=True)
class MemoryPreferences:
    idle_seconds: int = 60
    recent_messages: int = 8
    summarize_every: int = 8
    summary_max_tokens: int = 150
    prompt_max_tokens: int = 500        # 056c: valore di partenza dei modelli nuovi
    max_background_jobs: int = 1
    conversation_priority: bool = True
    pause_on_heavy_load: bool = True
    background_summaries: bool = True
    # 021: 250 -> 200 to shorten the prompt a little on the Pavilion; the
    # newest exchange is always protected, so the dialogue stays coherent.
    history_max_tokens: int = 200
    # 056c: «Cronologia ridotta per domande brevi» (accesa) e il vecchio blocco «Contesto»
    # (chat continua, ricordi): ora nello stesso posto della memoria del prompt, cioè nel profilo.
    cronologia_ridotta: bool = True
    chat_continua: bool = True
    ricordi_locale: str = "pertinenti"

    def validate(self):
        for key, minimum, maximum in (
            ("idle_seconds", 10, 3600),
            ("recent_messages", 2, 32),
            ("summarize_every", 2, 64),
            ("summary_max_tokens", 32, 1024),
            ("prompt_max_tokens", 128, 8192),
            ("max_background_jobs", 1, 1),
            ("history_max_tokens", 128, 600),
        ):
            value = getattr(self, key)
            if type(value) is not int or not minimum <= value <= maximum:
                raise ValueError("Valore non valido: " + key)
        if self.ricordi_locale not in _RICORDI:
            raise ValueError("Valore non valido: ricordi_locale")
        for key in ("conversation_priority", "pause_on_heavy_load",
                    "background_summaries", "cronologia_ridotta", "chat_continua"):
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
            legacy_keys = set(cls.__dataclass_fields__) - set(NATIVE_KEYS)
            if not isinstance(obj, dict) or set(obj) != legacy_keys:
                raise ValueError("Schema memoria non valido.")
            # Older releases reject additional keys in memory.json. Keep the
            # token policy in a small sidecar; loading never migrates/writes.
            native_path = path.with_suffix(".native.json")
            native = {}
            if native_path.exists():
                native = json.loads(native_path.read_text(encoding="utf-8"))
                if (not isinstance(native, dict) or "history_max_tokens" not in native
                        or not set(native) <= set(NATIVE_KEYS)):
                    raise ValueError("Schema budget cronologia non valido.")
                if native["history_max_tokens"] == _OLD_DEFAULT_HISTORY:
                    # Untouched old default follows the new, lighter default.
                    native = dict(native, history_max_tokens=cls.history_max_tokens)
            return cls(**obj, **native).validate()
        except (OSError, UnicodeError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("Impostazioni memoria danneggiate.") from exc

    def available_prompt_tokens(self, context_size, max_output, reserve=128):
        """Return the legacy character budget consumed by native prompt builders.

        Keep the API/JSON names for existing profiles. context_size/max_output
        are model tokens; their numeric remainder caps the character budget.
        This policy is not a tokenizer or a guarantee for every Unicode text.
        """
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
        legacy = asdict(self)
        native = {key: legacy.pop(key) for key in NATIVE_KEYS}
        _save_json(path, legacy)
        _save_json(path.with_suffix(".native.json"), native)


def _save_json(path, data):
    """Atomic per file; I/O errors propagate to the existing settings UI."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=path.name + ".", suffix=".tmp", delete=False
        ) as stream:
            temp = Path(stream.name)
            json.dump(data, stream, indent=2)
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
