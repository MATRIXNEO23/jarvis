"""Validated native CPU model settings. No executable or server launch."""
from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path
import tempfile


PERSONALITY_LIMIT = 240


@dataclass(frozen=True)
class NativeModelConfig:
    dll: str = ""
    model: str = ""
    threads: int = 2
    batch_threads: int = 2
    context_size: int = 2048
    max_output: int = 128
    temperature: float = 0.7
    top_k: int = 100
    top_p: float = 0.9
    seed: int = -1
    personality: str = ""
    # 026: fast forwarding (riuso dell'inizio del prompt), carattere e lunghezza.
    fast_forward: bool = True
    character_main: str = ""
    character_extra: str = ""
    reply_length: str = ""
    explain_sentences: int = 8
    user_notes: str = ""

    def validate(self):
        for key, low, high in (
            ("threads", 1, 32), ("batch_threads", 1, 32),
            ("context_size", 256, 32768), ("max_output", 1, 8192),
            ("top_k", 1, 1000), ("seed", -1, 2147483647),
        ):
            value = getattr(self, key)
            if type(value) is not int or not math.isfinite(value) or not low <= value <= high:
                raise ValueError(f"Parametro non valido: {key}")
        for key, low, high in (("temperature", 0, 2), ("top_p", 0, 1)):
            value = getattr(self, key)
            if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
                raise ValueError(f"Parametro non valido: {key}")
        if self.max_output > self.context_size:
            raise ValueError("Max output supera la finestra di contesto.")
        for key in ("dll", "model"):
            value = getattr(self, key)
            if not isinstance(value, str) or "\x00" in value:
                raise ValueError(f"Percorso non valido: {key}")
        if (not isinstance(self.personality, str) or "\x00" in self.personality
                or len(self.personality) > PERSONALITY_LIMIT):
            raise ValueError(f"Istruzioni di carattere non valide (massimo {PERSONALITY_LIMIT} caratteri).")
        from .persona import CHARACTERS, EXPLAIN_MAX, EXPLAIN_MIN, LENGTHS, NOTES_LIMIT
        if type(self.fast_forward) is not bool:
            raise ValueError("Parametro non valido: fast_forward")
        for key in ("character_main", "character_extra"):
            if getattr(self, key) not in ("", *CHARACTERS):
                raise ValueError(f"Carattere non valido: {key}")
        if self.reply_length not in LENGTHS:
            raise ValueError("Lunghezza risposte non valida.")
        if type(self.explain_sentences) is not int or not EXPLAIN_MIN <= self.explain_sentences <= EXPLAIN_MAX:
            raise ValueError("Parametro non valido: explain_sentences")
        if (not isinstance(self.user_notes, str) or "\x00" in self.user_notes
                or len(self.user_notes) > NOTES_LIMIT):
            raise ValueError(f"Note sull'utente non valide (massimo {NOTES_LIMIT} caratteri).")
        return self

    def save(self, path):
        self.validate()
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=target.parent,
                prefix=target.name + ".", suffix=".tmp", delete=False
            ) as stream:
                temp_path = Path(stream.name)
                json.dump(asdict(self), stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_path, target)
        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink()

    @classmethod
    def load(cls, path):
        target = Path(path)
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            fields = set(cls.__dataclass_fields__)
            # Campi aggiunti dopo: un file di una build precedente resta valido.
            optional = {"personality", "fast_forward", "character_main", "character_extra",
                        "reply_length", "explain_sentences", "user_notes"}
            if (not isinstance(data, dict) or not set(data) <= fields
                    or not fields - optional <= set(data)):
                raise ValueError("Schema configurazione non valido.")
            return cls(**data).validate()
        except (UnicodeError, json.JSONDecodeError, TypeError) as exc:
            raise ValueError("Configurazione locale danneggiata.") from exc
