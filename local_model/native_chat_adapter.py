"""Opt-in native inference adapter; no network fallback."""
from .native_config import NativeModelConfig
from .native_factory import create_native_provider
from .native_settings import RELOAD_FIELDS, default_native_settings_path


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
        provider, previous = self.provider, self.config
        if provider is not None and previous is not None and all(
                getattr(previous, field) == getattr(config, field)
                for field in RELOAD_FIELDS | {"dll"}):
            provider.bridge.update_generation_settings(config)
            self.config = config
            return
        # Validate/create first; do not stop a working provider for a missing
        # file. The session lock serializes replacement with every inference.
        provider = create_native_provider(config, upstream_source=self.source)
        self.stop()
        self.provider = provider
        self.config = config

    def call(self, action, *, timeout=120, **arguments):
        if action != "ask":
            raise ValueError("Native adapter supports ask only")
        # stop() can detach the owner while this call is in progress. Keep the
        # selected provider stable; its stop flag/bridge handle cancellation.
        provider = self.provider
        if provider is None:
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
        result = provider.ask(timeout=timeout, **arguments)
        return {"text": result}

    def stop(self):
        # An abort failure must not leave a stopped provider reusable as ready.
        provider, self.provider = self.provider, None
        if provider is not None:
            provider.stop()
