"""Legacy executable configuration compatibility; native Gemma does not use it."""
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import os
import tempfile


@dataclass(frozen=True)
class LocalConfig:
    executable: str = ""
    model: str = ""
    threads: int = 2
    batch_threads: int = 2
    context: int = 2048
    output: int = 128
    port: int = 5002

    def validate(self):
        for key, minimum, maximum in (
            ("threads", 1, 32), ("batch_threads", 1, 32),
            ("context", 256, 32768), ("output", 1, 8192),
            ("port", 1024, 65535),
        ):
            value = getattr(self, key)
            if type(value) is not int or not minimum <= value <= maximum:
                raise ValueError("Invalid legacy setting: " + key)
        if self.output > self.context:
            raise ValueError("Output exceeds context")
        for key in ("executable", "model"):
            value = getattr(self, key)
            if not isinstance(value, str) or "\x00" in value:
                raise ValueError("Invalid legacy path: " + key)
        return self

    def command(self):
        self.validate()
        return [
            self.executable, "--model", self.model, "--usecpu", "--noavx2",
            "--host", "127.0.0.1", "--port", str(self.port),
            "--threads", str(self.threads), "--blasthreads",
            str(self.batch_threads), "--contextsize", str(self.context),
            "--skiplauncher",
        ]

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
                json.dump(asdict(self), stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            if temp is not None and temp.exists():
                temp.unlink()

    @classmethod
    def load(cls, path):
        path = Path(path)
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or set(data) != set(cls.__dataclass_fields__):
                raise ValueError("Invalid legacy configuration schema")
            return cls(**data).validate()
        except (OSError, UnicodeError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("Corrupt legacy configuration") from exc
