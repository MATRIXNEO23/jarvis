"""026: carattere in cima al prompt, regola di lunghezza in fondo, fast forwarding."""
import json
import tempfile
import unittest
from pathlib import Path

from local_model.native_config import NativeModelConfig
from local_model.persona import length_rule, persona_block, wants_explanation


class PersonaTests(unittest.TestCase):
    def test_default_adds_nothing(self):
        config = NativeModelConfig()
        self.assertEqual(persona_block(config), "")
        self.assertEqual(length_rule(config, "Ciao"), "")

    def test_two_traits_notes_and_free_text_are_one_short_block(self):
        config = NativeModelConfig(character_main="dolce", character_extra="monella",
                                   personality="parla  semplice", user_notes="Mi chiamo Alberto.")
        block = persona_block(config)
        self.assertEqual(block, "Carattere: sei dolce e un po' monella.\n"
                                "Stile: parla semplice\nSull'utente: Mi chiamo Alberto.\n")
        self.assertLess(len(block.split()), 50)

    def test_spy_words_switch_to_a_single_explain_rule(self):
        config = NativeModelConfig(reply_length="2", explain_sentences=8)
        self.assertEqual(length_rule(config, "Che ore sono?"), "Rispondi in massimo 2 frasi.")
        for question in ("Spiegami la fotosintesi", "come funziona il motore?",
                         "approfondisci", "dimmelo in dettaglio", "Descrivimi Roma",
                         "consigliami dei film"):
            self.assertEqual(length_rule(config, question), "Spiega in massimo 8 frasi.", question)
        for question in ("perché non va?", "dimmi tutto", "raccontami una storia"):
            self.assertFalse(wants_explanation(question), question)
        self.assertEqual(length_rule(NativeModelConfig(reply_length="brief"), "Ciao"),
                         "Rispondi brevemente.")
        self.assertEqual(length_rule(NativeModelConfig(reply_length="1"), "Ciao"),
                         "Rispondi in una frase.")

    def test_invalid_choices_are_rejected(self):
        with self.assertRaises(ValueError):
            NativeModelConfig(character_main="cattiva").validate()
        with self.assertRaises(ValueError):
            NativeModelConfig(reply_length="9").validate()
        with self.assertRaises(ValueError):
            NativeModelConfig(explain_sentences=40).validate()

    def test_settings_of_older_builds_still_load(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "native.json"
            old = {k: v for k, v in NativeModelConfig().__dict__.items()
                   if k not in ("fast_forward", "character_main", "character_extra",
                                "reply_length", "explain_sentences", "user_notes")}
            path.write_text(json.dumps(old), encoding="utf-8")
            loaded = NativeModelConfig.load(path)
            self.assertTrue(loaded.fast_forward)
            self.assertEqual(loaded.character_main, "")


class PromptOrderTests(unittest.TestCase):
    def test_persona_at_top_rule_next_to_question(self):
        from local_model.memory_preferences import MemoryPreferences
        from local_model.native_conversation_session import NativeConversationSession
        from tests.test_native_conversation_session import FakeAdapter
        adapter = FakeAdapter()
        config = NativeModelConfig(context_size=1024, max_output=128, character_main="ironica",
                                   reply_length="2")
        session = NativeConversationSession(adapter, config_loader=lambda: config,
                                            memory_loader=MemoryPreferences)
        session.ask("Ciao, come stai?")
        session.ask("Spiegami la luna")
        first, second = adapter.calls[-2], adapter.calls[-1]
        self.assertIn("Carattere: sei ironica.", first)
        self.assertLess(first.index("Carattere"), first.index("Ti chiami Lumi"))
        self.assertTrue(first.rstrip().split("Ciao, come stai?")[1].startswith("\n(Rispondi in massimo 2 frasi.)"))
        self.assertIn("Spiegami la luna\n(Spiega in massimo 8 frasi.)", second)
        # the start of the prompt is identical: fast forwarding can reuse it
        common = len(first.split("Ciao, come stai?")[0])
        self.assertEqual(first[:common], second[:common])


class FastForwardFlagTests(unittest.TestCase):
    def test_off_passes_nofastforward_and_needs_reload(self):
        from local_model.native_settings import update_native_settings
        revised, reload_needed = update_native_settings(NativeModelConfig(), {"fast_forward": False})
        self.assertFalse(revised.fast_forward)
        self.assertTrue(reload_needed)
        _, reload_needed = update_native_settings(NativeModelConfig(), {"character_main": "dolce"})
        self.assertFalse(reload_needed)


if __name__ == "__main__":
    unittest.main()
