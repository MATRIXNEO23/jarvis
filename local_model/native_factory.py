"""Opt-in factory for native Gemma. Never changes existing Jarvis defaults."""
import importlib.util
from pathlib import Path

from .native_bridge import NativeGemmaBridge
from .native_config import NativeModelConfig
from .native_initializer import initialize_kobold_cpu
from .native_provider import NativeLocalProvider


def create_native_provider(config, *, upstream_source):
    """Create but do not load a native provider; explicit caller opt-in required."""
    if not isinstance(config, NativeModelConfig):
        raise TypeError("Configurazione nativa non valida.")
    config.validate()
    source = Path(upstream_source).resolve(strict=True)
    if source.name.lower() != "koboldcpp.py":
        raise ValueError("Sorgente ABI non riconosciuto.")
    if not Path(config.dll).is_file() or not Path(config.model).is_file():
        raise FileNotFoundError("DLL o modello GGUF non disponibile.")
    spec = importlib.util.spec_from_file_location("jarvis_native_kobold_pinned", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("Caricamento sorgente nativo non disponibile.")
    upstream = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(upstream)
    bridge = NativeGemmaBridge(
        config, upstream,
        initialize=lambda module, settings: initialize_kobold_cpu(
            module, settings, source))
    return NativeLocalProvider(bridge)
