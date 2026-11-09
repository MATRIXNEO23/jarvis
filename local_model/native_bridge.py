"""Direct in-process Gemma bridge using the pinned KoboldCpp Python ABI.

No HTTP service, executable launch or autonomous online fallback. The upstream
module is an explicit dependency supplied by the installer, not downloaded here.
"""
from dataclasses import replace
import math
from pathlib import Path
import threading
import time

from .chat_templates import model_family, stop_sequence
from .native_config import NativeModelConfig


class NativeRestartRequired(RuntimeError):
    """A second native model load in one process is refused (F5N.7).

    KoboldCpp exposes no safe unload: native state of a previous load_model
    is not guaranteed to be released or reset. Model, context or thread
    changes therefore apply when Lumi is restarted.
    """


RESTART_MESSAGE = ("Motore locale già caricato in questa sessione: riavvia Lumi "
                   "per usare il nuovo modello o le nuove impostazioni del motore.")
# Resolved DLL paths whose native load_model already ran in this process.
_PROCESS_NATIVE_LOADS = set()


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
        self.last_generation_finish = "unknown"
        self.last_generation_tokens = None
        self.family = "gemma2"

    def load(self):
        """Load once. Caller must supply a verified, pinned upstream adapter."""
        with self._lock:
            self._check_cancelled()
            if self._loaded:
                return
            if not self.config.model or not Path(self.config.model).is_file():
                raise RuntimeError("Modello GGUF non disponibile.")
            if not self.config.dll or not Path(self.config.dll).is_file():
                raise RuntimeError("Libreria nativa non disponibile.")
            # Template/stop follow the GGUF architecture (F5N.7).
            self.family = model_family(self.config.model)
            if not callable(self.initialize):
                raise RuntimeError("Inizializzazione ABI nativa non configurata.")
            dll_key = str(Path(self.config.dll).resolve())
            if dll_key in _PROCESS_NATIVE_LOADS:
                raise NativeRestartRequired(RESTART_MESSAGE)
            self.initialize(self.upstream, self.config)
            self._check_cancelled()
            if not hasattr(self.upstream, "load_model"):
                raise RuntimeError("Adattatore nativo non compatibile.")
            # Reserve before the native call: a failed load also leaves state.
            _PROCESS_NATIVE_LOADS.add(dll_key)
            if not self.upstream.load_model(str(Path(self.config.model).resolve())):
                raise RuntimeError("Caricamento modello nativo fallito.")
            self._check_cancelled()
            self._loaded = True

    @property
    def loaded(self):
        return self._loaded

    def _check_cancelled(self):
        if self._stop_requested.is_set():
            raise RuntimeError("Generazione annullata.")

    def _abort_native(self):
        handle = getattr(self.upstream, "handle", None)
        abort = getattr(handle, "abort_generate", None)
        if callable(abort):
            abort()

    def abort(self):
        """Request cooperative abort without waiting for the generation lock."""
        self._stop_requested.set()
        # No ABI abort against a partially initialized/loading model. load()
        # checks the event before continuing into generation.
        if self._loaded:
            self._abort_native()

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

    def count_tokens(self, prompt):
        """Same special-token mode as generate; never run another inference."""
        with self._lock:
            self._check_cancelled()
            if not self._loaded:
                raise RuntimeError("Modello non caricato.")
            tokenizer = getattr(self.upstream, "tokenize_ids", None)
            if not callable(tokenizer):
                raise RuntimeError("Tokenizer nativo non disponibile.")
            ids = tokenizer(prompt, True)
            self._check_cancelled()
            if not isinstance(ids, (list, tuple)) or not ids:
                raise RuntimeError("Conteggio token nativo non valido.")
            return len(ids)

    def generate(self, prompt, *, timeout=120):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt vuoto.")
        if (type(timeout) not in (int, float) or not math.isfinite(timeout)
                or timeout <= 0 or timeout > threading.TIMEOUT_MAX):
            raise ValueError("Timeout non valido.")
        # Cooperative deadline only: an unresponsive C call must retain the
        # lock until it actually returns. Never reload a second model over it.
        with self._lock:
            self._check_cancelled()
            if not self._loaded:
                raise RuntimeError("Modello non caricato.")
            c = self.config
            self.last_generation_finish = "unknown"
            self.last_generation_tokens = None
            started = time.monotonic()
            expired = threading.Event()
            deadline_lock = threading.Lock()
            finished = False
            abort_error = []

            def expire():
                with deadline_lock:
                    if finished:
                        return
                    expired.set()
                    try:
                        self._abort_native()
                    except Exception as exc:
                        abort_error.append(exc)

            watchdog = threading.Timer(timeout, expire)
            watchdog.daemon = True
            watchdog.start()
            failure = None
            try:
                # Timer.start() may schedule a stop/deadline before native
                # entry. Retire the watchdog through finally in that case too.
                self._check_cancelled()
                if expired.is_set() or time.monotonic() - started >= timeout:
                    raise TimeoutError("Generazione locale oltre il tempo richiesto.")
                result = self.upstream.generate({
                    "prompt": prompt, "max_context_length": c.context_size,
                    "max_length": c.max_output, "temperature": c.temperature,
                    "top_k": c.top_k, "top_p": c.top_p,
                    "sampler_seed": c.seed,
                    "stop_sequence": stop_sequence(self.family),
                })
            except Exception as exc:
                failure = exc
            finally:
                with deadline_lock:
                    finished = True
                    watchdog.cancel()
                # Fence callback completion before releasing the native lock;
                # cancellation alone does not stop an already running Timer.
                watchdog.join()
            self._check_cancelled()
            if expired.is_set() or time.monotonic() - started > timeout:
                raise TimeoutError("Generazione locale oltre il tempo richiesto; "
                                   "annullamento richiesto.") from (failure or (
                                       abort_error[0] if abort_error else None))
            if failure is not None:
                raise failure
            if not isinstance(result, dict):
                raise RuntimeError("Generazione nativa: risposta ABI non valida.")
            if result.get("status") != 1:
                status = result.get("status")
                reason = result.get("stopreason")
                raise RuntimeError(
                    "Generazione nativa fallita (status=" + str(status)[:20]
                    + ", stopreason=" + str(reason)[:40] + ").")
            # KoboldCpp stopreason: 1=stop, other successful values=length.
            # The metadata is non-authoritative; never allow it to grant an
            # action or modify a malformed model response.
            stop = result.get("stopreason")
            self.last_generation_finish = (
                "stop" if type(stop) is int and stop == 1 else
                "length" if type(stop) is int and stop >= 0 else "unknown")
            tokens = result.get("completion_tokens")
            self.last_generation_tokens = tokens if type(tokens) is int and tokens >= 0 else None
            value = result.get("text")
            if not isinstance(value, str) or not value.strip():
                raise RuntimeError("Generazione nativa vuota.")
            return value
