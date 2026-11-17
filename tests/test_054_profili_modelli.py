"""054: profili per famiglia (3 slot), «I miei modelli», quota stimata e interruttore ricerca."""
import ast
import struct
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import servizi_ricerca as sr
from local_model import miei_modelli, profili_famiglia as pf, scelta_modello
from local_model.native_config import NativeModelConfig

ROOT = Path(__file__).resolve().parents[1]


def gguf(path: Path, arch: str = "", size: int = 100) -> Path:
    body = b"GGUF" + b"\0" * 12
    if arch:
        body += b"general.architecture" + struct.pack("<IQ", 8, len(arch)) + arch.encode()
    path.write_bytes(body + b"x" * size)
    return path


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name) / "addon-data" / "modello_locale"
        self.dir.mkdir(parents=True)
        self.cfg = self.dir / "native.json"
        (self.dir / "modelli").mkdir()
        self.gemma = gguf(self.dir / "modelli" / "gemma-2-2b.gguf")
        self.qwen = gguf(self.dir / "modelli" / "Qwen3-1.7B.gguf")

    def save(self, model, **values):
        NativeModelConfig(model=str(model), **values).save(self.cfg)


class FamilyRecognitionTests(Base):
    def test_family_from_file_name_and_from_metadata(self):
        self.assertEqual(pf.riconosci_famiglia("gemma-2-2b-it.gguf"), ("gemma", True))
        self.assertEqual(pf.riconosci_famiglia("Qwen3-1.7B-Q4_K_M.gguf"), ("qwen", True))
        self.assertEqual(pf.riconosci_famiglia("modello-xyz.gguf"), ("generico", False))
        # i metadati vincono sul nome
        self.assertEqual(pf.riconosci_famiglia("strano.gguf", "qwen3"), ("qwen", True))
        file = gguf(Path(self.tmp.name) / "x.gguf", "gemma3")
        self.assertEqual(pf.leggi_architettura(file), "gemma3")
        self.assertEqual(pf.riconosci_famiglia(file), ("gemma", True))

    def test_unknown_family_is_flagged_in_the_message(self):
        self.assertIn("sconosciuta", pf.messaggio_famiglia("generico", False, 1))
        self.assertNotIn("sconosciuta", pf.messaggio_famiglia("gemma", True, 2))


class MigrationAndSlotsTests(Base):
    def test_current_values_migrate_into_slot_1_and_others_are_defaults(self):
        self.save(self.gemma, temperature=0.3, max_output=200)
        info = pf.assicura(self.cfg)
        self.assertEqual((info["famiglia"], info["slot"]), ("gemma", 1))
        data = pf.carica(self.cfg)["famiglie"]["gemma"]["slot"]
        self.assertEqual(data["1"]["temperature"], 0.3)
        self.assertEqual(data["1"]["max_output"], 200)
        self.assertEqual(data["2"], pf.default_valori())
        self.assertEqual(data["3"], pf.default_valori())
        self.assertEqual(NativeModelConfig.load(self.cfg).temperature, 0.3)   # nulla perso

    def test_last_slot_is_remembered_per_family(self):
        self.save(self.gemma, temperature=0.3)
        pf.assicura(self.cfg)
        pf.scegli_slot("gemma", 2, self.cfg)
        pf.salva_in_slot("gemma", 2, self.cfg)
        # passo a Qwen: ha il suo slot 1 (i valori attuali), poi scelgo il 3
        pf.applica_modello(self.qwen, self.cfg)
        self.assertEqual(pf.slot_ricordato("qwen", self.cfg), 1)
        pf.scegli_slot("qwen", 3, self.cfg)
        # torno a Gemma: carica lo slot 2 ricordato, non il default né l'1
        revised, family, known, _ = pf.applica_modello(self.gemma, self.cfg)
        self.assertEqual((family, known), ("gemma", True))
        self.assertEqual(pf.slot_ricordato("gemma", self.cfg), 2)
        self.assertEqual(revised.temperature, pf.carica(self.cfg)["famiglie"]["gemma"]["slot"]["2"]["temperature"])
        pf.applica_modello(self.qwen, self.cfg)
        self.assertEqual(pf.slot_ricordato("qwen", self.cfg), 3)

    def test_save_in_slot_and_restore_default(self):
        self.save(self.gemma)
        pf.assicura(self.cfg)
        NativeModelConfig.load(self.cfg)
        config = replace(NativeModelConfig.load(self.cfg), temperature=1.1, top_k=40)
        config.save(self.cfg)
        pf.salva_in_slot("gemma", 3, self.cfg)
        self.assertEqual(pf.carica(self.cfg)["famiglie"]["gemma"]["slot"]["3"]["temperature"], 1.1)
        result = pf.ripristina_default("gemma", 3, self.cfg)
        self.assertEqual(result["config"].temperature, NativeModelConfig().temperature)
        self.assertEqual(pf.carica(self.cfg)["famiglie"]["gemma"]["slot"]["3"], pf.default_valori())

    def test_slot_switch_says_when_the_engine_must_restart(self):
        self.save(self.gemma)
        pf.assicura(self.cfg)
        data = pf.carica(self.cfg)
        data["famiglie"]["gemma"]["slot"]["2"]["context_size"] = 4096
        pf._salva(data, self.cfg)
        result = pf.scegli_slot("gemma", 2, self.cfg)
        self.assertTrue(result["serve_riavvio"])
        self.assertIn("context_size", result["campi_riavvio"])
        result = pf.scegli_slot("gemma", 1, self.cfg)
        self.assertTrue(result["serve_riavvio"])
        with self.assertRaises(ValueError):
            pf.scegli_slot("gemma", 4, self.cfg)

    def test_choosing_a_model_uses_the_same_function_for_voice_and_button(self):
        self.save(self.gemma, temperature=0.4)
        revised = scelta_modello.salva_scelta(self.qwen, self.cfg)
        self.assertEqual(revised.model, str(self.qwen))
        self.assertIn("qwen", pf.carica(self.cfg)["famiglie"])
        source = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn("lumi_model_use(models[number - 1])", source)      # voce
        self.assertIn("on_use=lambda target: lumi_model_use(target)", source)   # pulsante


class MieiModelliTests(Base):
    def test_list_marks_the_model_in_use(self):
        self.save(self.gemma)
        rows = dict((p.name, active) for p, active in miei_modelli.righe(self.cfg))
        self.assertTrue(rows["gemma-2-2b.gguf"])
        self.assertFalse(rows["Qwen3-1.7B.gguf"])

    def test_add_copies_in_chunks_with_progress_and_rejects_bad_files(self):
        self.save(self.gemma)
        source = gguf(Path(self.tmp.name) / "nuovo.gguf", size=1000)
        steps = []
        target = miei_modelli.aggiungi_modello(source, self.cfg, progress=lambda d, t: steps.append((d, t)),
                                               chunk=300)
        self.assertEqual(target.read_bytes(), source.read_bytes())
        self.assertGreater(len(steps), 1)
        self.assertEqual(steps[-1][0], steps[-1][1])
        self.assertFalse(list(target.parent.glob("*.copia")))
        with self.assertRaises(ValueError):
            miei_modelli.aggiungi_modello(source, self.cfg)            # già presente
        other = Path(self.tmp.name) / "a.txt"
        other.write_text("x")
        with self.assertRaises(ValueError):
            miei_modelli.aggiungi_modello(other, self.cfg)

    def test_cancelled_copy_leaves_no_partial_file(self):
        source = gguf(Path(self.tmp.name) / "grande.gguf", size=1000)
        with self.assertRaises(ValueError):
            miei_modelli.aggiungi_modello(source, self.cfg, chunk=100, cancel=lambda: True)
        self.assertFalse((self.dir / "modelli" / "grande.gguf").exists())
        self.assertFalse(list((self.dir / "modelli").glob("grande*.copia")))

    def test_remove_goes_to_trash_and_never_removes_the_model_in_use(self):
        self.save(self.gemma)
        trash = mock.Mock(return_value=True)
        with self.assertRaises(ValueError):
            miei_modelli.rimuovi_modello(self.gemma, self.cfg, trash)
        trash.assert_not_called()
        miei_modelli.rimuovi_modello(self.qwen, self.cfg, trash)
        trash.assert_called_once_with([self.qwen])
        with self.assertRaises(OSError):
            miei_modelli.rimuovi_modello(self.qwen, self.cfg, mock.Mock(return_value=False))


class MieiModelliButtonsTests(Base):
    """Un test per pulsante, con Tk reale (CI Windows) e callback finte."""

    def setUp(self):
        super().setUp()
        import tkinter as tk
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk non disponibile")
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.save(self.gemma)
        self.notes, self.used = [], []

    def section(self, **extra):
        return miei_modelli.costruisci_sezione(
            self.root, self.notes.append, on_use=self.used.append, config_path=self.cfg, **extra)

    def test_button_use_calls_the_shared_function_with_the_selected_model(self):
        box = self.section()
        box.listbox.selection_set(1)
        box.use()
        self.assertEqual(self.used, [self.qwen])

    def test_button_add_copies_without_blocking_and_refreshes(self):
        source = gguf(Path(self.tmp.name) / "extra.gguf", size=500)
        box = self.section(ask_file=lambda: str(source), run_async=lambda fn: fn())
        box.add()
        self.root.update()
        self.assertTrue((self.dir / "modelli" / "extra.gguf").exists())
        self.assertEqual(box.listbox.size(), 3)

    def test_button_remove_asks_confirmation_and_skips_the_model_in_use(self):
        trash = mock.Mock(return_value=True)
        confirm = mock.Mock(return_value=True)
        box = self.section(confirm=confirm, al_cestino=trash)
        box.listbox.selection_set(0)          # gemma: in uso
        box.remove()
        trash.assert_not_called()
        box.listbox.selection_clear(0, "end")
        box.listbox.selection_set(1)
        box.remove()
        confirm.assert_called()
        trash.assert_called_once()
        confirm.return_value = False
        trash.reset_mock()
        box.remove()
        trash.assert_not_called()

    def test_profile_buttons_save_and_restore(self):
        box = self.section()
        box.save_slot()
        box.reset_slot()
        self.assertEqual(pf.carica(self.cfg)["famiglie"]["gemma"]["slot"]["1"], pf.default_valori())


class QuotaAndSwitchTests(unittest.TestCase):
    def test_estimated_quota_from_local_counters(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "uso.json"
            for _ in range(3):
                sr.quota.registra("tavily", oggi="2026-11-17", path=path)
            sr.quota.registra("tavily", oggi="2026-11-18", path=path)
            info = sr.quota.stato("tavily", 1000, oggi="2026-11-18", path=path)
            self.assertEqual((info["oggi"], info["mese"]), (1, 4))
            self.assertAlmostEqual(info["usato"], 0.004)
            self.assertIn("stima", info["testo"])
            self.assertTrue(info["stima"])
            # nuovo mese: i contatori ripartono
            self.assertEqual(sr.quota.stato("tavily", 1000, oggi="2026-12-01", path=path)["mese"], 0)
            # limite ignoto: niente percentuale, solo conteggi
            self.assertIsNone(sr.quota.stato("tavily", 0, oggi="2026-11-18", path=path)["usato"])
            # soglie dei colori come nei servizi online
            for _ in range(900):
                sr.quota.registra("tavily", oggi="2026-11-18", path=path)
            self.assertEqual(sr.quota.stato("tavily", 1000, oggi="2026-11-18", path=path)["colore"],
                             sr.quota.ROSSO)

    def test_search_switch_is_saved_and_blocks_cerca_online(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "servizi_ricerca.json"
            self.assertTrue(sr.ricerca_accesa(path))
            self.assertFalse(sr.imposta_accesa(False, path))
            self.assertFalse(sr.ricerca_accesa(path))
            self.assertTrue(sr.imposta_accesa(True, path))
        source = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn("RICERCA OFF > ", source)
        self.assertIn('hud.add_quick_button("ricerca", "RICERCA ON", toggle_ricerca_online, after="model")',
                      source)


if __name__ == "__main__":
    unittest.main()
