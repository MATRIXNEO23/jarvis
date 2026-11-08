"""Regression: an oversized immediate answer must not erase its antecedent."""
import unittest
from local_model.memory_preferences import MemoryPreferences
from local_model.native_config import NativeModelConfig
from local_model.native_conversation_session import NativeConversationSession
from test_native_conversation_session import FakeAdapter


class CountingAdapter(FakeAdapter):
    def context_token_counter(self):
        # Boundary fixture: four ASCII characters per token, with one BOS.
        return lambda prompt: (len(prompt) + 3) // 4 + 1


class ContextWindowTests(unittest.TestCase):
    def session(self):
        adapter = CountingAdapter()
        session = NativeConversationSession(
            adapter, config_loader=lambda: NativeModelConfig(context_size=1024, max_output=128),
            memory_loader=MemoryPreferences)
        return session, adapter

    def test_real_token_budget_keeps_recent_exchange_larger_than_legacy_char_cap(self):
        session, adapter = self.session()
        turn = session.prepare_turn('Spiegami Mussolini')
        turn.text = 'Una spiegazione storica. ' * 32
        self.assertTrue(turn.commit())
        session.ask('Continua quella spiegazione')
        self.assertIn('Spiegami Mussolini', adapter.calls[-1])
        self.assertIn('Una spiegazione storica.', adapter.calls[-1])
        self.assertLessEqual(adapter.context_token_counter()(adapter.calls[-1]), 768)

    def test_oversized_recent_answer_preserves_referenced_sentence_with_roles(self):
        session, adapter = self.session()
        turn = session.prepare_turn('Parliamo di Mussolini')
        turn.text = ('Primo argomento. ' * 75 + 'La parola clown era una metafora. '
                     + 'Altri dettagli. ' * 60)
        turn.commit()
        session.ask('Perché hai detto clown?')
        prompt = adapter.calls[-1]
        self.assertIn('Parliamo di Mussolini', prompt)
        self.assertIn('clown era una metafora', prompt)
        self.assertIn('<start_of_turn>model\n', prompt)
        self.assertLessEqual(adapter.context_token_counter()(prompt), 768)

    def test_current_question_is_not_rejected_by_old_600_character_limit(self):
        session, adapter = self.session()
        question = 'Domanda articolata. ' * 50
        session.ask(question)
        self.assertIn(question.strip(), adapter.calls[-1])

    def test_active_counter_failure_does_not_generate_with_estimate(self):
        session, adapter = self.session()
        def failed():
            def count(prompt):
                raise RuntimeError('tokenizer unavailable')
            return count
        adapter.context_token_counter = failed
        with self.assertRaisesRegex(RuntimeError, 'tokenizer unavailable'):
            session.ask('ciao')
        self.assertEqual(adapter.calls, [])
