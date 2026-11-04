"""Direct in-process Gemma bridge using the pinned KoboldCpp Python ABI.

No HTTP service, executable launch or autonomous online fallback. The upstream
module is an explicit dependency supplied by the installer, not downloaded here.
"""
import importlib.util
from pathlib import Path
import threading

from .native_config import NativeModelConfig


class NativeGemmaBridge:
    def __init__(self, config, upstream):
        if not isinstance(config, NativeModelConfig):
            raise TypeError("Configurazione nativa richiesta.")
        self.config = config.validate()
        self.upstream = upstream
        self._lock = threading.Lock()
        self._loaded = False

    def load(self):
        """Load once. Caller must supply a verified, pinned upstream adapter."""
        with self._lock:
            if self._loaded:
                return
            if not self.config.model or not Path(self.config.model).is_file():
                raise RuntimeError("Modello GGUF non disponibile.")
            if not self.config.dll or not Path(self.config.dll).is_file():
                raise RuntimeError("Libreria nativa non disponibile.")
            # Upstream ABI initialization is intentionally not guessed here.
            # The verified inference proof initializes these globals explicitly.
            if not hasattr(self.upstream, "load_model"):
                raise RuntimeError("Adattatore nativo non compatibile.")
            if not self.upstream.load_model(str(Path(self.config.model).resolve())):
                raise RuntimeError("Caricamento modello nativo fallito.")
            self._loaded = True

    def generate(self, prompt, *, timeout=120):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt vuoto.")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValueError("Timeout non valido.")
        # A native blocking generate() call cannot be forcibly stopped safely
        # from Python; no misleading timeout or cancellation is advertised.
        with self._lock:
            if not self._loaded:
                raise RuntimeError("Modello non caricato.")
            c = self.config
            result = self.upstream.generate({
                "prompt": prompt, "max_context_length": c.context_size,
                "max_length": c.max_output, "temperature": c.temperature,
                "top_k": c.top_k, "top_p": c.top_p,
                "sampler_seed": c.seed,
                "stop_sequence": ["<end_of_turn>"],
            })
            if not isinstance(result, dict) or result.get("status") != 1:
                raise RuntimeError("Generazione nativa fallita.")
            value = result.get("text")
            if not isinstance(value, str) or not value.strip():
                raise RuntimeError("Generazione nativa vuota.")
            return value
