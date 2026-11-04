"""Opt-in native inference adapter; no network fallback."""
from .native_config import NativeModelConfig
from .native_factory import create_native_provider
from .native_settings import default_native_settings_path


class NativeChatAdapter:
    def __init__(self, source):
        self.source = source
        self.provider = None

    def prepare(self):
        config = NativeModelConfig.load(default_native_settings_path())
        self.provider = create_native_provider(config, upstream_source=self.source)

    def call(self, action, *, timeout=120, **arguments):
        if action != "ask":
            raise ValueError("Native adapter supports ask only")
        if self.provider is None:
            raise RuntimeError("Native model not prepared")
        result = self.provider.ask(timeout=timeout, **arguments)
        return {"text": result}

    def stop(self):
        if self.provider is not None:
            self.provider.stop()
            self.provider = None
