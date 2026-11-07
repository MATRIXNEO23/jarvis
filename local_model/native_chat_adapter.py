"""Opt-in native inference adapter; no network fallback."""
from .native_config import NativeModelConfig
from .native_factory import create_native_provider
from .native_settings import default_native_settings_path


class NativeChatAdapter:
    def __init__(self, source):
        self.source = source
        self.provider = None
        self.config = None

    def prepare(self, *, config=None):
        if config is None:
            config = NativeModelConfig.load(default_native_settings_path())
        if not isinstance(config, NativeModelConfig):
            raise TypeError("Configurazione nativa richiesta.")
        config.validate()
        from .memory_preferences import MemoryPreferences, default_memory_preferences_path
        memory = MemoryPreferences.load(default_memory_preferences_path())
        memory.available_prompt_tokens(config.context_size, config.max_output)
        self.config = config
        self.provider = create_native_provider(config, upstream_source=self.source)

    def call(self, action, *, timeout=120, **arguments):
        if action != "ask":
            raise ValueError("Native adapter supports ask only")
        if self.provider is None:
            raise RuntimeError("Native model not prepared")
        from .memory_preferences import MemoryPreferences, default_memory_preferences_path
        memory = MemoryPreferences.load(default_memory_preferences_path())
        budget = memory.available_prompt_tokens(
            self.config.context_size, self.config.max_output)
        prompt = arguments.get("prompt")
        if isinstance(prompt, str) and len(prompt) > budget:
            raise ValueError(
                "Prompt troppo lungo per il budget conservativo: "
                + str(len(prompt)) + " caratteri, limite " + str(budget)
                + ". Ridurre il contesto o aumentare il budget.")
        result = self.provider.ask(timeout=timeout, **arguments)
        return {"text": result}

    def stop(self):
        if self.provider is not None:
            self.provider.stop()
            self.provider = None
