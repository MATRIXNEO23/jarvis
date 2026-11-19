import random
from unittest.mock import patch
import tempfile
import unittest
from pathlib import Path

import aiuto_comandi
import scheda_lumi
from aiuto_comandi import Aiuto
from controllo_pc.service import ControlService
from test_controllo_pc import make


class AiutoTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / "aiuto.json"
        self.shown, self.spoken, self.asked = [], [], []

    def tearDown(self):
        self.folder.cleanup()

    def run_command(self, aiuto, mode, action=None):
        aiuto.dopo_comando(mode, action=action, show=self.shown.append, speak=self.spoken.append,
                           ask=lambda q, yes, no: self.asked.append((q, yes, no)))

    def test_offre_il_tutorial_una_volta_per_modalita_e_riquadro(self):
        aiuto = Aiuto(self.path, base_help=ControlService._HELP)
        self.run_command(aiuto, "video")
        self.run_command(aiuto, "video")
        self.run_command(aiuto, "explorer")
        self.assertEqual([a[1:] for a in self.asked], [("tutorial_yes", "tutorial_no")] * 2)
        self.assertIn("Ti guido passo passo", self.asked[0][0])
        self.assertIn("«pausa»", self.shown[0])
        self.assertIn("nascondi i comandi", self.shown[0])
        self.assertIn("vai su Download", self.shown[-1])      # dalla lista del Controllo PC
        again = Aiuto(self.path)                               # stato salvato
        self.assertEqual(sorted(again.state["tutorial"]), ["explorer", "video"])

    def test_tutorial_guidato_aspetta_il_comando_giusto(self):
        aiuto = Aiuto(self.path)
        self.run_command(aiuto, "video")                       # offerta
        first = aiuto.avvia_guida()
        self.assertIn("5 passi", first)
        self.assertIn("«pausa»", first)
        self.run_command(aiuto, "video", "play")               # comando sbagliato: resta al passo 1
        self.assertEqual(self.spoken, [])
        self.run_command(aiuto, "video", "media_pause")
        self.assertIn("Passo 2", self.spoken[-1])
        self.assertIn("Passo 3", aiuto.salta())
        for action in ("show_numbers", "pick"):
            self.run_command(aiuto, "video", action)
        self.run_command(aiuto, "video", "home")
        self.assertIn("tutorial finito", self.spoken[-1])
        self.assertIsNone(aiuto.guida)
        aiuto.avvia_guida("griglia")
        self.assertEqual(aiuto.esci(), "Tutorial chiuso.")
        self.assertEqual(aiuto.esci(), "Non c'è nessun tutorial in corso.")

    def test_chiede_una_volta_dopo_molti_usi(self):
        aiuto = Aiuto(self.path)
        for _ in range(aiuto_comandi.USI_PRIMA_DI_CHIEDERE + 5):
            self.run_command(aiuto, "griglia")
        questions = [a for a in self.asked if a[1] == "help_off"]
        self.assertEqual(len(questions), 1)
        self.assertIn("sì o no", questions[0][0])

    def test_riquadro_spento_e_tutorial_da_rivedere(self):
        aiuto = Aiuto(self.path)
        aiuto.imposta_riquadro(False)
        self.run_command(aiuto, "notepad")
        self.assertEqual(self.shown, [])
        self.assertFalse(Aiuto(self.path).riquadro)
        aiuto.rivedi_tutorial()
        self.run_command(aiuto, "notepad")
        self.assertEqual(len(self.asked), 2)

    def test_comandi_vocali_del_tutorial(self):
        import lumi_comandi
        self.assertEqual(lumi_comandi.parse("salta passo"), "tutorial_skip")
        self.assertEqual(lumi_comandi.parse("Lumi, esci dal tutorial"), "tutorial_stop")
        self.assertEqual(lumi_comandi.parse("fammi il tutorial"), "tutorial_start")


class CambiaParolaTest(unittest.TestCase):
    def test_parola_tua_per_un_comando(self):
        import la_mia_voce
        from types import SimpleNamespace
        import tkinter as tk
        status = []
        fake = SimpleNamespace(last_phrase=lambda: "scorri giù",
                               status=SimpleNamespace(set=status.append))
        with tempfile.TemporaryDirectory() as folder, \
                patch("command_aliases.default_file", lambda: Path(folder) / "alias.json"):
            result = la_mia_voce.VoiceWindow.change_word(fake, ask=lambda: "vai giù")
            self.assertIn("Aggiunta", result)
            import command_aliases
            self.assertEqual(command_aliases.rewrite("vai giù", path=Path(folder) / "alias.json"),
                             "scorri giù")
            self.assertIsNone(la_mia_voce.VoiceWindow.change_word(fake, ask=lambda: "sette"))
            self.assertIn("non confondere", status[-1])


class ServizioTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.service, self.backend = make(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_modalita_e_aggancio_dopo_i_comandi(self):
        handled, toggles = [], []
        self.service.on_handled = handled.append
        self.service.on_help_toggle = toggles.append
        self.service.show_strip = lambda text: None
        self.backend.front = 11
        self.assertEqual(self.service.current_mode(), "notepad")
        self.backend.front = 22
        self.assertEqual(self.service.current_mode(), "video")
        self.service.handle("show_commands", {})
        self.service.handle("hide_commands", {})
        self.assertEqual(toggles, [True, False])
        self.assertEqual(handled, [])             # mostra/nascondi non ridisegnano il riquadro

    def test_un_errore_dell_aiuto_non_ferma_il_comando(self):
        def boom(action):
            raise RuntimeError("aiuto rotto")
        self.service.on_handled = boom
        self.service.show_strip = lambda text: None
        self.assertIsNotNone(self.service.handle("show_commands", {}))
        self.backend.front = 11
        self.assertIsNotNone(self.service.handle("list_windows", {}))


class SchedaTest(unittest.TestCase):
    INFO = scheda_lumi.fatti(addons=("Controllo PC", "Musica"), local_model="C:/m/gemma-3-4b.gguf",
                             local_on=True, online=False, mic="ascolto continuo")

    def test_domande_su_lumi(self):
        for text in ("chi sei?", "Lumi come funzioni", "che modello usi", "presentati",
                     "quali add-on sono attivi"):
            self.assertTrue(scheda_lumi.domanda_su_lumi(text), text)
        for text in ("cosa sai fare", "apri chrome", "chi è il presidente"):
            self.assertFalse(scheda_lumi.domanda_su_lumi(text), text)

    def test_scheda_con_dati_veri(self):
        card = scheda_lumi.scheda(self.INFO)
        for part in ("Controllo PC, Musica", "gemma-3-4b.gguf", "Servizi online: nessuno pronto", "ascolto continuo"):
            self.assertIn(part, card)

    def test_frasi_pronte_variano_e_dicono_modello_spento(self):
        info = dict(self.INFO, locale=False)
        answers = {scheda_lumi.risposta_pronta(info, random.Random(seed)) for seed in range(12)}
        self.assertGreater(len(answers), 1)
        self.assertTrue(all("spento" in a for a in answers))

    def test_fatti_da_contesto_parziale(self):
        class D:
            active_gpt = True
        info = scheda_lumi.fatti_da(D())
        self.assertTrue(info["online"])
        self.assertEqual(info["addons"], [])


if __name__ == "__main__":
    unittest.main()
