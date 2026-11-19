"""F5N.7: chat template and stop token per local model family.

The family is read from the GGUF header key ``general.architecture`` (a few
bytes, no model load). Gemma stays the default when no model file is set, so
existing Gemma behaviour is unchanged. Unknown architectures are refused
instead of being sent a wrong template.
"""
import os
from pathlib import Path
import struct

from .native_provider import format_gemma_messages
from .qwen25_template_f5 import format_qwen25_instruct
from .qwen3_template_f5 import format_qwen3_nothink

_ARCH_FAMILY = {"gemma": "gemma2", "gemma2": "gemma2", "gemma3": "gemma2",
                "qwen2": "qwen25", "qwen3": "qwen3"}
_STOP = {"gemma2": "<end_of_turn>", "qwen25": "<|im_end|>", "qwen3": "<|im_end|>"}
FAMILY_LABELS = {"gemma2": "Gemma", "qwen25": "Qwen2.5", "qwen3": "Qwen3"}
_SCALAR = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 8, 11: 8, 12: 8}
_cache = {}


class ModelFamilyError(ValueError):
    pass


def _read(stream, size):
    data = stream.read(size)
    if len(data) != size:
        raise ModelFamilyError("Intestazione GGUF incompleta.")
    return data


def _string(stream):
    (length,) = struct.unpack("<Q", _read(stream, 8))
    if length > 1 << 20:
        raise ModelFamilyError("Intestazione GGUF non valida.")
    return _read(stream, length).decode("utf-8", "replace")


def _skip(stream, value_type):
    if value_type in _SCALAR:
        stream.seek(_SCALAR[value_type], os.SEEK_CUR)
    elif value_type == 8:
        _string(stream)
    elif value_type == 9:
        item_type, count = struct.unpack("<IQ", _read(stream, 12))
        if item_type in _SCALAR:
            stream.seek(_SCALAR[item_type] * count, os.SEEK_CUR)
        else:
            for _ in range(count):
                _skip(stream, item_type)
    else:
        raise ModelFamilyError("Tipo GGUF sconosciuto.")


def gguf_architecture(path, *, max_keys=64):
    """Return ``general.architecture`` reading only the GGUF metadata header."""
    with open(path, "rb") as stream:
        if _read(stream, 4) != b"GGUF":
            raise ModelFamilyError("Il file non è un modello GGUF.")
        (version,) = struct.unpack("<I", _read(stream, 4))
        if version < 2:
            raise ModelFamilyError("Versione GGUF non supportata.")
        _tensors, keys = struct.unpack("<QQ", _read(stream, 16))
        for _ in range(min(keys, max_keys)):
            key = _string(stream)
            (value_type,) = struct.unpack("<I", _read(stream, 4))
            if key == "general.architecture" and value_type == 8:
                return _string(stream)
            _skip(stream, value_type)
    raise ModelFamilyError("Architettura del modello non trovata nel GGUF.")


def model_family(model_path):
    """Family for a configured model; Gemma when no model file is set yet."""
    if not model_path or not Path(model_path).is_file():
        return "gemma2"
    path = Path(model_path)
    stat = path.stat()
    key = (str(path.resolve()), stat.st_size, stat.st_mtime_ns)
    if key not in _cache:
        try:
            arch = gguf_architecture(path)
        except (ModelFamilyError, OSError, struct.error):
            # Not a readable GGUF: keep the historical Gemma default; the
            # native load reports the real error for such a file.
            return "gemma2"
        family = _ARCH_FAMILY.get(arch)
        if family is None:
            raise ModelFamilyError("Famiglia di modello non supportata: " + arch[:40])
        _cache.clear()
        _cache[key] = family
    return _cache[key]


def format_messages(messages, family):
    if family == "gemma2":
        return format_gemma_messages(messages)
    if family == "qwen25":
        return format_qwen25_instruct(messages)
    if family == "qwen3":
        return format_qwen3_nothink(messages)
    raise ModelFamilyError("Famiglia di modello non supportata.")


def stop_sequence(family):
    if family not in _STOP:
        raise ModelFamilyError("Famiglia di modello non supportata.")
    return [_STOP[family]]
