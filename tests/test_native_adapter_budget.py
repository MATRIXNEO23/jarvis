import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from local_model.native_chat_adapter import NativeChatAdapter
from local_model.native_config import NativeModelConfig


class FakeProvider:
    def ask(self, **kwargs):
        return "risposta"


class AdapterBudgetTests(unittest.TestCase):
    def test_configured_window_enforced_without_model(self):
        adapter = NativeChatAdapter("unused")
        adapter.provider = FakeProvider()
        adapter.config = NativeModelConfig(context_size=512, max_output=128)
        with tempfile.TemporaryDirectory() as folder:
            prefs_path = Path(folder) / "memory.json"
            with patch("local_model.memory_preferences.default_memory_preferences_path",
                       return_value=prefs_path):
                self.assertEqual(adapter.call("ask", prompt="ciao")["text"], "risposta")
                with self.assertRaises(ValueError):
                    adapter.call("ask", prompt="x" * 257)


if __name__ == "__main__":
    unittest.main()
