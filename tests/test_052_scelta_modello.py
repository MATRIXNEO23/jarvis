"""052 punto 7: «cambia modello» (elenco dei .gguf, scelta salvata). DB/file solo temporanei."""
import json
import tempfile
import unittest
from pathlib import Path

import lumi_comandi
from local_model import scelta_modello as sm
from local_model.native_config import NativeModelConfig


class ModelChoiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.models = self.root / "modelli-utente"
        self.models.mkdir()
        for name in ("Qwen_Qwen3-1.7B-Q4_K_M.gguf", "gemma-2-2b-it-Q4.gguf", "mmproj-vision.gguf"):
            (self.models / name).write_bytes(b"GGUF")
        (self.models / "note.txt").write_text("non è un modello", encoding="utf-8")
        self.config = self.root / "addon-data" / "modello_locale" / "native.json"
        NativeModelConfig(model=str(self.models / "gemma-2-2b-it-Q4.gguf"),
                          threads=3).save(self.config)

    def test_lists_only_text_gguf_in_the_folder_of_the_current_model(self):
        names = [m.name for m in sm.elenca_modelli(self.config)]
        self.assertEqual(names, ["gemma-2-2b-it-Q4.gguf", "Qwen_Qwen3-1.7B-Q4_K_M.gguf"])

    def test_list_is_limited_to_nine_and_has_no_duplicates(self):
        for n in range(12):
            (self.models / ("extra%02d.gguf" % n)).write_bytes(b"GGUF")
        models = sm.elenca_modelli(folders=[self.models, self.models])
        self.assertEqual(len(models), 9)
        self.assertEqual(len({m.name for m in models}), 9)

    def test_numbered_text_for_window_and_voice(self):
        models = sm.elenca_modelli(self.config)
        window_text, spoken = sm.testo_elenco(models)
        self.assertIn("1. gemma 2 2b it Q4", window_text)
        self.assertIn("2. Qwen Qwen3 1.7B Q4 K M", window_text)
        self.assertIn("Quale scegli", spoken)
        self.assertIn("2 modelli", spoken)
        self.assertIn("Non trovo", sm.testo_elenco([])[0])

    def test_choice_is_saved_and_other_settings_are_kept(self):
        chosen = self.models / "Qwen_Qwen3-1.7B-Q4_K_M.gguf"
        sm.salva_scelta(chosen, self.config)
        saved = json.loads(self.config.read_text(encoding="utf-8"))
        self.assertEqual(saved["model"], str(chosen))
        self.assertEqual(saved["threads"], 3)
        self.assertEqual(sm.modello_in_uso(self.config), str(chosen))

    def test_missing_or_wrong_file_is_refused_and_config_untouched(self):
        before = self.config.read_text(encoding="utf-8")
        with self.assertRaises(ValueError):
            sm.salva_scelta(self.models / "sparito.gguf", self.config)
        with self.assertRaises(ValueError):
            sm.salva_scelta(self.models / "note.txt", self.config)
        self.assertEqual(self.config.read_text(encoding="utf-8"), before)

    def test_phrases_reach_the_registered_action(self):
        saved = dict(lumi_comandi._STATE)
        self.addCleanup(lumi_comandi._STATE.update, saved)
        calls = []
        lumi_comandi.register({"model_choose": lambda: calls.append(1),
                               "model_restart": lambda: calls.append("riavvio")}, lambda: False)
        for text in ("Lumi, cambia modello", "cambia il modello", "scegli il modello locale",
                     "elenca i modelli", "quali modelli ho"):
            calls.clear()
            self.assertTrue(lumi_comandi.handle_text(text, lambda *_: None, lambda *_: None), text)
            self.assertEqual(calls, [1], text)
        calls.clear()
        self.assertTrue(lumi_comandi.handle_text("riavvia il modello", lambda *_: None, lambda *_: None))
        self.assertEqual(calls, ["riavvio"])


if __name__ == "__main__":
    unittest.main()
