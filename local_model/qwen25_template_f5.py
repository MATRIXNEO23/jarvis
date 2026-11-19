"""F5.3b.3: experimental text-only Qwen2.5-Instruct ChatML serializer.

Reference: official Qwen/Qwen2.5-0.5B-Instruct tokenizer_config.json.
Do not use for Qwen3, Qwen-VL, tools, system policies or model inference.
An explicit model-template match is required before any production routing.
"""
from .model_profiles_f5 import ProfileError


_SPECIAL = (
    "<|im_start|>", "<|im_end|>", "<|ghissue|>", "<|fim_prefix|>",
    "<|fim_middle|>", "<|tool_call|>", "<tool_call>", "</tool_call>",
)


def format_qwen25_instruct(messages):
    """Format an alternating user/assistant dialogue ending in a user turn.

    The official tokenizer template inserts a default system instruction when
    none is present. This isolated serializer uses exactly that text for its
    supported no-tools, no-system-role subset.
    """
    if (type(messages) is not list or not messages or len(messages) % 2 != 1):
        raise ProfileError("Invalid Qwen2.5 dialogue")
    out = ["<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. "
           "You are a helpful assistant.<|im_end|>\n"]
    for i, message in enumerate(messages):
        role = "user" if i % 2 == 0 else "assistant"
        if type(message) is not dict or set(message) != {"role", "content"}:
            raise ProfileError("Invalid Qwen2.5 text message")
        if message["role"] != role:
            raise ProfileError("Invalid Qwen2.5 role sequence")
        content = message["content"]
        if type(content) is not str or not content.strip() or len(content) > 65536:
            raise ProfileError("Invalid Qwen2.5 message content")
        # Model-generated or user data may contain chat template delimiters;
        # render them as inert Unicode lookalikes, not structural tokens.
        for marker in _SPECIAL:
            content = content.replace(marker, marker.replace("<", "‹").replace(">", "›"))
        out.append("<|im_start|>" + role + "\n" + content + "<|im_end|>\n")
    out.append("<|im_start|>assistant\n")
    return "".join(out)
