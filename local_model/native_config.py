"""Validated native CPU model settings. No executable or server launch."""
from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path
import tempfile


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
            if not isinstance(data, dict) or set(data) != set(cls.__dataclass_fields__):
                raise ValueError("Schema configurazione non valido.")
            return cls(**data).validate()
        except (UnicodeError, json.JSONDecodeError, TypeError) as exc:
            raise ValueError("Configurazione locale danneggiata.") from exc
