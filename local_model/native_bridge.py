"""Direct in-process Gemma bridge using the pinned KoboldCpp Python ABI.

No HTTP service, executable launch or autonomous online fallback. The upstream
module is an explicit dependency supplied by the installer, not downloaded here.
"""
from dataclasses import replace
from pathlib import Path
import threading
import time

from .native_config import NativeModelConfig


class NativeGemmaBridge:
    def __init__(self, config, upstream, *, initialize=None):
        if not isinstance(config, NativeModelConfig):
            raise TypeError("Configurazione nativa richiesta.")
        self.config = config.validate()
        self.upstream = upstream
        self.initialize = initialize
        self._lock = threading.Lock()
        self._loaded = False
        self._stop_requested = threading.Event()

    def load(self):
        """Load once. Caller must supply a verified, pinned upstream adapter."""
        with self._lock:
            if self._loaded:
                return
            if not self.config.model or not Path(self.config.model).is_file():
                raise RuntimeError("Modello GGUF non disponibile.")
            if not self.config.dll or not Path(self.config.dll).is_file():
                raise RuntimeError("Libreria nativa non disponibile.")
            if not callable(self.initialize):
                raise RuntimeError("Inizializzazione ABI nativa non configurata.")
            self.initialize(self.upstream, self.config)
            if not hasattr(self.upstream, "load_model"):
                raise RuntimeError("Adattatore nativo non compatibile.")
            if not self.upstream.load_model(str(Path(self.config.model).resolve())):
                raise RuntimeError("Caricamento modello nativo fallito.")
            self._loaded = True

    def abort(self):
        """Request cooperative abort without waiting for the generation lock."""
        self._stop_requested.set()
        handle = getattr(self.upstream, "handle", None)
        abort = getattr(handle, "abort_generate", None)
        if callable(abort):
            abort()

    def update_generation_settings(self, config):
        """Apply samplers without changing the loaded model or bundled DLL."""
        if not isinstance(config, NativeModelConfig):
            raise TypeError("Configurazione nativa richiesta.")
        config.validate()
        with self._lock:
            self.config = replace(
                self.config, max_output=config.max_output,
                temperature=config.temperature, top_k=config.top_k,
                top_p=config.top_p, seed=config.seed).validate()

    def generate(self, prompt, *, timeout=120):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt vuoto.")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValueError("Timeout non valido.")
        # A native blocking generate() call cannot be forcibly stopped safely
        # from Python; no misleading timeout or cancellation is advertised.
        with self._lock:
            if self._stop_requested.is_set():
                raise RuntimeError("Generazione annullata.")
            if not self._loaded:
                raise RuntimeError("Modello non caricato.")
            c = self.config
            started = time.monotonic()
            result = self.upstream.generate({
                "prompt": prompt, "max_context_length": c.context_size,
                "max_length": c.max_output, "temperature": c.temperature,
                "top_k": c.top_k, "top_p": c.top_p,
                "sampler_seed": c.seed,
                "stop_sequence": ["<end_of_turn>"],
            })
            if self._stop_requested.is_set():
                raise RuntimeError("Generazione annullata.")
            if time.monotonic() - started > timeout:
                raise TimeoutError("Generazione locale oltre il tempo richiesto.")
            if not isinstance(result, dict):
                raise RuntimeError("Generazione nativa: risposta ABI non valida.")
            if result.get("status") != 1:
                status = result.get("status")
                reason = result.get("stopreason")
                raise RuntimeError(
                    "Generazione nativa fallita (status=" + str(status)[:20]
                    + ", stopreason=" + str(reason)[:40] + ").")
            value = result.get("text")
            if not isinstance(value, str) or not value.strip():
                raise RuntimeError("Generazione nativa vuota.")
            return value
