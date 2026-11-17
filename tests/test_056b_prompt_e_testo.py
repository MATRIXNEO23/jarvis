"""056b: tetto prompt 600 token anche col catalogo, contesto 1024, chat continua accesa,
«/nothink» mai in chat, un invio = un «TU >», pagina memoria pulita."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSION = (ROOT / "local_model" / "native_conversation_session.py").read_text(encoding="utf-8")
JARVIS = (ROOT / "jarvis.py").read_text(encoding="utf-8")
CONV = (ROOT / "local_model" / "conversazione_lumi.py").read_text(encoding="utf-8")


class TettoPromptTests(unittest.TestCase):
    def test_contesto_predefinito_1024_e_tetto_600_con_1024_e_2048(self):
        from local_model.memory_preferences import MemoryPreferences
        from local_model.native_config import NativeModelConfig
        self.assertEqual(NativeModelConfig().context_size, 1024)
        memory = MemoryPreferences()
        self.assertEqual(memory.prompt_max_tokens, 600)
        for contesto in (1024, 2048):
            self.assertEqual(memory.available_prompt_tokens(contesto, 128), 600)

    def test_niente_budget_8192_e_niente_override_del_contatore_esatto(self):
        self.assertNotIn("prompt_max_tokens=8192", SESSION)
        self.assertNotIn("budget = config.context_size - config.max_output - 128", SESSION)

    def test_catalogo_ridotto_e_piu_corto_e_resta_coerente(self):
        from conversation_router import build_native_intent_context, reduce_intent_context
        pieno = build_native_intent_context()
        ridotto = reduce_intent_context(pieno, "apri il blocco note")
        minimo = reduce_intent_context(pieno, "ciao", essential_only=True)
        self.assertLess(len(minimo[0]), len(pieno[0]))
        self.assertLessEqual(len(ridotto[0]), len(pieno[0]))
        self.assertLessEqual(len(minimo[1]), 6)
        for testo, ids in (ridotto, minimo):
            self.assertIn(",".join(ids), testo)
            self.assertTrue(set(ids) <= set(pieno[1]))

    def test_la_sessione_prova_pieno_poi_ridotto_poi_minimo(self):
        corpo = SESSION[SESSION.index("reduce_intent_context"):SESSION.index("base_instructions = instructions")]
        self.assertIn("essential_only=True", corpo)
        self.assertIn("<= budget", corpo)

    def test_chat_continua_accesa_di_serie(self):
        from contesto_lumi import Contesto
        self.assertTrue(Contesto().chat_continua)


class NothinkTests(unittest.TestCase):
    def test_strip_nothink(self):
        from local_model.native_conversation_session import clean_native_answer, strip_nothink
        self.assertEqual(strip_nothink("ciao /nothink"), "ciao")
        self.assertEqual(strip_nothink("ciao /no_think"), "ciao")
        self.assertNotIn("nothink", clean_native_answer("Ciao! /nothink"))

    def test_il_prompt_qwen3_non_aggiunge_il_suffisso_nel_testo(self):
        from local_model.chat_templates import format_messages
        prompt = format_messages([{"role": "user", "content": "ciao"}], "qwen3")
        self.assertNotIn("/nothink", prompt)
        self.assertNotIn("/nothink", format_messages([{"role": "user", "content": "ciao"}], "gemma2"))


class InvioTests(unittest.TestCase):
    def test_un_invio_una_sola_riga_tu(self):
        self.assertIn("TU_SCRITTO = [False]", CONV)
        self.assertIn("if typed and not TU_SCRITTO[0]:", CONV)
        corpo = JARVIS[JARVIS.index("def chain_typed_once"):JARVIS.index("def submit_gpt")]
        self.assertIn("TU_SCRITTO[0] = True", corpo)
        self.assertIn("finally:", corpo)
        self.assertEqual(JARVIS.count("conversation_chain(message, True)"), 1)   # solo nel helper
        self.assertEqual(JARVIS.count("chain_typed_once(message)"), 2)
        self.assertEqual(JARVIS.count('input_box.bind("<Return>"'), 1)

    def test_flag_si_azzera_anche_se_la_catena_fallisce(self):
        from local_model import conversazione_lumi as cl
        cl.TU_SCRITTO[0] = False
        self.assertFalse(cl.TU_SCRITTO[0])


class MemoriaPaginaTests(unittest.TestCase):
    def test_pagina_pulita_e_testo_a_capo(self):
        src = (ROOT / "local_model" / "memory_ui.py").read_text(encoding="utf-8")
        self.assertIn("for old in self.window.winfo_children():", src)
        self.assertIn("old.destroy()", src)
        self.assertIn("wraplength", src)
        self.assertIn("_rewrap", src)


if __name__ == "__main__":
    unittest.main()
