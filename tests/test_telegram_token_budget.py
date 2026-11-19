"""9/11 Pavilion: Telegram local reply failed with 'Contesto Gemma insufficiente'.

The token budget was used as a character count for the Telegram prompt; the
fixed rules alone (290 chars) exceeded small budgets before any generation.
"""
import unittest

from local_model.memory_preferences import MemoryPreferences
from local_model.native_config import NativeModelConfig
from local_model.native_conversation_session import NativeConversationSession
import json

from telegram_bridge import telegram_local_messages, telegram_local_prompt
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



def context_of(*events):
    return json.dumps({"ultimi_messaggi": [{"da": who, "testo": text} for who, text in events]})


class TelegramTurnsTests(unittest.TestCase):
    """9/11: last 3 exchanges as real turns, short replies."""

    def test_last_three_exchanges_become_alternating_turns(self):
        ctx = context_of(("contatto", "Ciao"), ("jarvis", "Ciao!"),
                         ("contatto", "Vieni stasera?"), ("jarvis", "Chiedo ad Alberto."),
                         ("contatto", "Ok, alle 9?"), ("jarvis", "Gli riferisco le 9."))
        messages = telegram_local_messages("E se piove?", ctx, "Amico", 3)
        self.assertEqual([m["role"] for m in messages],
                         ["user", "assistant"] * 3 + ["user"])
        self.assertIn("massimo 2-3 frasi", messages[0]["content"])
        self.assertIn("Amico", messages[0]["content"])
        self.assertTrue(messages[0]["content"].endswith("Ciao"))
        self.assertEqual(messages[-1]["content"], "E se piove?")
        self.assertNotIn("ultimi_messaggi", str(messages))

    def test_fewer_pairs_drop_oldest_and_unanswered_message_joins_current(self):
        ctx = context_of(("jarvis", "orfano"), ("contatto", "A"), ("jarvis", "B"),
                         ("contatto", "senza risposta"))
        messages = telegram_local_messages("domanda", ctx, "", 3)
        self.assertEqual([m["role"] for m in messages], ["user", "assistant", "user"])
        self.assertEqual(messages[-1]["content"], "senza risposta\ndomanda")
        none = telegram_local_messages("domanda", ctx, "", 0)
        self.assertEqual(len(none), 1)
        self.assertIn("Sei Lumi", none[0]["content"])

    def test_session_drops_pairs_until_the_prompt_fits(self):
        adapter = TokenCountingAdapter()
        session = NativeConversationSession(
            adapter,
            config_loader=lambda: NativeModelConfig(context_size=1024, max_output=640),
            memory_loader=lambda: MemoryPreferences())
        long_ctx = context_of(*[(("contatto" if i % 2 == 0 else "jarvis"), "parola " * 60)
                                for i in range(6)])
        answer = session.ask_isolated_messages(
            lambda pairs: telegram_local_messages("Ultima domanda", long_ctx, "", pairs))
        self.assertTrue(answer)
        self.assertIn("Ultima domanda", adapter.calls[-1])
        self.assertLessEqual((len(adapter.calls[-1]) + 3) // 4, 1024 - 640 - 128)
        self.assertEqual(list(session.history), [])


if __name__ == "__main__":
    unittest.main()
