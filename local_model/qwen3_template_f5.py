"""F5N.6: experimental text-only Qwen3 ChatML serializer, thinking disabled.

Reference: official Qwen3 chat template with ``enable_thinking=False``: same
``<|im_start|>``/``<|im_end|>`` turns as Qwen2.5, no default system message,
and an empty ``<think>`` block opened in the assistant prefix so the model
answers directly (important on a slow CPU). Not imported by Jarvis runtime;
an explicit model-template match is required before production routing.
"""
from .model_profiles_f5 import ProfileError

QWEN3_STOP = "<|im_end|>"

_SPECIAL = (
    "<|im_start|>", "<|im_end|>", "<|endoftext|>", "<think>", "</think>",
    "<tool_call>", "</tool_call>", "<tool_response>", "</tool_response>",
)


def _inert(content):
    for marker in _SPECIAL:
        content = content.replace(marker, marker.replace("<", "‹").replace(">", "›"))
    return content


def format_qwen3_nothink(messages, *, system=None):
    """Format alternating user/assistant turns ending in a user turn.

    ``system`` is optional and only added when given (Qwen3 has no default
    system text). Assistant history is plain text: reasoning is never stored.
    """
    if type(messages) is not list or not messages or len(messages) % 2 != 1:
        raise ProfileError("Invalid Qwen3 dialogue")
    out = []
    if system is not None:
        if type(system) is not str or not system.strip() or len(system) > 8192:
            raise ProfileError("Invalid Qwen3 system text")
        out.append("<|im_start|>system\n" + _inert(system.strip()) + "<|im_end|>\n")
    for i, message in enumerate(messages):
        role = "user" if i % 2 == 0 else "assistant"
        if type(message) is not dict or set(message) != {"role", "content"}:
            raise ProfileError("Invalid Qwen3 text message")
        if message["role"] != role:
            raise ProfileError("Invalid Qwen3 role sequence")
        content = message["content"]
        if type(content) is not str or not content.strip() or len(content) > 65536:
            raise ProfileError("Invalid Qwen3 message content")
        out.append("<|im_start|>" + role + "\n" + _inert(content.strip()) + "<|im_end|>\n")
    out.append("<|im_start|>assistant\n<think>\n\n</think>\n\n")
    return "".join(out)
