"""Resident CPU runtime contract, pending Windows verification."""
from dataclasses import dataclass, asdict
from pathlib import Path
import json

@dataclass(frozen=True)
class LocalConfig:
    executable: str = ''
    model: str = ''
    threads: int = 2
    batch_threads: int = 2
    context: int = 2048
    output: int = 128
    port: int = 5002
    def validate(self):
        return self
    def command(self):
        return []
    def save(self, path):
        pass
    @classmethod
    def load(cls, path):
        return cls()
