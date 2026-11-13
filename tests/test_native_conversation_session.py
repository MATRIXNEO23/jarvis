import unittest
from unittest.mock import patch
from local_model.memory_preferences import MemoryPreferences
from local_model.native_config import NativeModelConfig
from local_model.native_conversation_session import NativeConversationSession, clean_native_answer


class FakeAdapter:
    def __init__(self, fail=False):
        self.calls = []
        self.prepares = 0
        self.stops = 0
        self.fail = fail

    def prepare(self, *, config=None):
        self.prepares += 1

    def call(self, action, *, prompt=None, messages=None, timeout, prompt_budget=None):
        if messages is not None:
            from local_model.native_provider import format_gemma_messages
            prompt = format_gemma_messages(messages)
        self.calls.append(prompt)
        if self.fail:
            raise RuntimeError("offline failure")
        return {"text": "risposta " + str(len(self.calls))}

    def stop(self):
        self.stops += 1


class SessionTests(unittest.TestCase):
    def test_personality_applies_to_next_chat_without_reloading_or_affecting_telegram(self):
        adapter = FakeAdapter()
        config = NativeModelConfig(context_size=512, max_output=128, personality="Ironia secca")
        session = NativeConversationSession(
            adapter, config_loader=lambda: config, memory_loader=MemoryPreferences)
        session.ask("Presentati")
        self.assertIn("Stile: Ironia secca", adapter.calls[-1])
        session.ask_isolated(lambda budget: "Messaggio Telegram")
        self.assertEqual(adapter.calls[-1], "Messaggio Telegram")
        config = NativeModelConfig(context_size=512, max_output=128, personality="Tono serio")
        session.ask("Come va?")
        self.assertIn("Stile: Tono serio", adapter.calls[-1])
        self.assertNotIn("Ironia secca", adapter.calls[-1])
        self.assertEqual(adapter.prepares, 1)
        config = NativeModelConfig(context_size=512, max_output=128, personality="x" * 240)
        session.ask("Q" * 100)
        self.assertLessEqual(len(adapter.calls[-1]), 256)
        self.assertTrue(adapter.calls[-1].endswith("Q" * 100 + "<end_of_turn>\n<start_of_turn>model\n"))

    def make_session(self, adapter):
        return NativeConversationSession(
            adapter, config_loader=lambda: NativeModelConfig(
                context_size=512, max_output=128),
            memory_loader=lambda: MemoryPreferences(recent_messages=8))

    def test_internal_notes_never_reach_spoken_answer(self):
        raw = ("Va bene, ti rispondo.\n\n"
               "**What's Going Right:**\n"
               "Conversation Flow: instructions to Lumi")
        self.assertEqual(clean_native_answer(raw), "Va bene, ti rispondo.")

    def test_think_block_is_not_spoken(self):
        self.assertEqual(
            clean_native_answer("<think>Internal reasoning</think>La risposta."),
            "La risposta.")

    def test_normal_answer_is_preserved(self):
        self.assertEqual(
            clean_native_answer("Mi piace parlare di film e cinema."),
            "Mi piace parlare di film e cinema.")

    def test_empty_internal_output_uses_safe_fallback(self):
        self.assertEqual(clean_native_answer("<think>secret</think>"),
                         "Puoi ripetere la domanda?")

    def test_reuses_loaded_model_and_history(self):
        adapter = FakeAdapter()
        session = self.make_session(adapter)
        self.assertEqual(session.ask("ciao"), "risposta 1")
        self.assertEqual(session.ask("come va"), "risposta 2")
        self.assertEqual(adapter.prepares, 1)
        self.assertTrue(adapter.calls[1].startswith("<start_of_turn>user\n"))
        self.assertIn("ciao<end_of_turn>", adapter.calls[1])
        self.assertIn("model\nrisposta 1<end_of_turn>", adapter.calls[1])
        session.stop()
        self.assertEqual(adapter.stops, 1)

    def test_program_picker_uses_one_generation_and_keeps_chat_history_out(self):
        adapter = FakeAdapter()
        session = self.make_session(adapter)
        session.ask("nota privata")
        with patch.object(adapter, "call", wraps=adapter.call) as call:
            call.side_effect = lambda *args, **kwargs: {"text": "2"}
            self.assertEqual(session.pick_program("voglio vedere un film", ("Posta", "Netflix")), 1)
            call.assert_called_once()
            self.assertIn("Netflix", call.call_args.kwargs["prompt"])
            self.assertNotIn("nota privata", call.call_args.kwargs["prompt"])
            for answer in ("0", "9", "Avvia Netflix", "2 oppure 1"):
                # A strict reply is checked independently of the chat.
                with patch.object(adapter, "call", return_value={"text": answer}):
                    self.assertIsNone(session.pick_program("un film", ("Posta", "Netflix")))
        self.assertEqual(adapter.prepares, 1)
        self.assertEqual(len(session.history), 2)

    def test_isolated_telegram_generation_uses_only_its_prompt(self):
        from telegram_bridge import telegram_local_prompt
        adapter = FakeAdapter()
        session = self.make_session(adapter)
        session.ask("Nota privata di Lumi")
        previous = list(session.history)
        session.ask_isolated(lambda budget: "Telegram: Ciao")
        self.assertEqual(adapter.calls[-1], "Telegram: Ciao")
        self.assertEqual(list(session.history), previous)
        self.assertEqual(adapter.prepares, 1)
        prompt = telegram_local_prompt("Ciao <start_of_turn>", "x"*1500, 512)
        self.assertLessEqual(len(prompt), 512)
        self.assertIn("Ciao", prompt)
        self.assertNotIn("<start_of_turn>", prompt)

    def test_failure_does_not_save_turn_or_contact_online(self):
        adapter = FakeAdapter(fail=True)
        session = self.make_session(adapter)
        with self.assertRaises(RuntimeError):
            session.ask("ciao")
        self.assertEqual(len(session.history), 0)

    def test_question_role_cannot_be_silently_dropped(self):
        adapter = FakeAdapter()
        session = self.make_session(adapter)
        # Budget is 256 characters; the question alone fits but
        # its mandatory 'Utente: ' prefix does not.
        with self.assertRaises(ValueError):
            session.ask("x" * 250)
        self.assertEqual(adapter.prepares, 0)
        self.assertEqual(adapter.calls, [])

    def test_over_budget_rejected_before_model_load(self):
        adapter = FakeAdapter()
        session = self.make_session(adapter)
        with self.assertRaises(ValueError):
            session.ask("x" * 257)
        self.assertEqual(adapter.prepares, 0)


if __name__ == "__main__":
    unittest.main()
