"""9/11 Pavilion: Telegram local reply failed with 'Contesto Gemma insufficiente'.

The token budget was used as a character count for the Telegram prompt; the
fixed rules alone (290 chars) exceeded small budgets before any generation.
"""
import unittest

from local_model.memory_preferences import MemoryPreferences
from local_model.native_config import NativeModelConfig
from local_model.native_conversation_session import NativeConversationSession
from telegram_bridge import telegram_local_prompt
from test_native_conversation_session import FakeAdapter


class TokenCountingAdapter(FakeAdapter):
    def context_token_counter(self):
        return lambda text: (len(text) + 3) // 4


class TelegramTokenBudgetTests(unittest.TestCase):
    def session(self, adapter):
        return NativeConversationSession(
            adapter,
            config_loader=lambda: NativeModelConfig(context_size=1024, max_output=640),
            memory_loader=lambda: MemoryPreferences())

    def test_small_token_budget_still_answers_with_real_tokenizer(self):
        adapter = TokenCountingAdapter()
        answer = self.session(adapter).ask_isolated(
            lambda budget: telegram_local_prompt("Ciao, ci vediamo stasera?",
                                                 "Mio Tim: ciao", budget, "Amico stretto"))
        self.assertTrue(answer)
        self.assertIn("ci vediamo stasera", adapter.calls[-1])
        self.assertLessEqual((len(adapter.calls[-1]) + 3) // 4, 1024 - 640 - 128)

    def test_without_tokenizer_the_legacy_character_rule_is_unchanged(self):
        with self.assertRaisesRegex(ValueError, "insufficiente"):
            self.session(FakeAdapter()).ask_isolated(
                lambda budget: telegram_local_prompt("Ciao", "", budget, ""))


if __name__ == "__main__":
    unittest.main()
