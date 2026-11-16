import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import console_interna
import local_help
import lumi_comandi
import orchestratore
import risposte


class ConsoleInternaTest(unittest.TestCase):
    def test_righe_su_file_e_in_coda(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "console.log"
            console_interna._STATE["path"] = path
            tee = console_interna._Tee(io.StringIO())
            tee.write("prima riga\nseconda")
            tee.write(" riga\n")
            self.assertEqual(console_interna.preleva(), ["prima riga", "seconda riga"])
            self.assertEqual(console_interna.preleva(), [])
            self.assertIn("seconda riga", path.read_text(encoding="utf-8"))
            self.assertEqual(tee.original.getvalue(), "prima riga\nseconda riga\n")
            console_interna._STATE["path"] = None

    def test_avvio_senza_console_nera(self):
        bat = (Path(__file__).resolve().parents[1] / "avvia_lumi.bat").read_text(encoding="utf-8")
        self.assertIn('start "" pyw -3 jarvis.py', bat)
        source = (Path(__file__).resolve().parents[1] / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn('__import__("console_interna").installa()', source)
        self.assertIn("errore_fatale()", source)


class PythonTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.safe = Path(self.folder.name)
        self.asked, self.notes, self.answer = [], [], True
        self.tools = orchestratore.Strumenti(
            ask=lambda q: self.asked.append(q) or self.answer, run_command=lambda t: None,
            folders=[str(self.safe)], notify=self.notes.append, timeout=20)

    def tearDown(self):
        self.folder.cleanup()

    def test_esegue_nella_cartella_sicura_dopo_il_si(self):
        result = self.tools.esegui("esegui_python", {"codice": "print(2 + 3)\nopen('x.txt','w').write('ok')"})
        self.assertIn("Uscita 0", result)
        self.assertIn("5", result)
        self.assertEqual((self.safe / "x.txt").read_text(), "ok")
        self.assertIn("print(2 + 3)", self.notes[0])               # lo script si vede prima
        self.assertEqual(len(self.asked), 1)

    def test_script_lungo_mostrato_tutto_e_file_dell_utente_intatto(self):
        mine = self.safe / "lumi_script.py"
        mine.write_text("# mio", encoding="utf-8")
        code = "x = 1\n" + "\n".join("# riga %d" % n for n in range(600)) + "\nprint('fine')"
        self.assertGreater(len(code), 3000)
        result = self.tools.esegui("esegui_python", {"codice": code})
        self.assertIn("fine", result)
        self.assertIn("print('fine')", self.notes[0])              # anche la coda si vede
        self.assertIn("impronta", self.notes[0])
        self.assertEqual(mine.read_text(encoding="utf-8"), "# mio")
        self.assertEqual(list(self.safe.glob("lumi_script_*.py")), [])   # file temporaneo tolto

    def test_no_e_codice_bloccato(self):
        self.answer = False
        self.assertEqual(self.tools.esegui("esegui_python", {"codice": "print(1)"}), "Permesso negato.")
        for code in ("import shutil\nshutil.rmtree('a')", "import os\nos.remove('a')",
                     "import subprocess\nsubprocess.run('dir')", "import os; os.system('del x')",
                     "Path('a').unlink()", "__import__('os')"):
            self.assertTrue(self.tools.esegui("esegui_python", {"codice": code}).startswith(
                "Codice rifiutato"), code)

    def test_tempo_massimo(self):
        self.tools.timeout = 5
        result = self.tools.esegui("esegui_python", {"codice": "import time\ntime.sleep(30)"})
        self.assertIn("tempo massimo", result)

    def test_senza_cartella_sicura(self):
        tools = orchestratore.Strumenti(ask=lambda q: True, run_command=lambda t: None, folders=[])
        self.assertIn("Nessuna cartella sicura", tools.esegui("esegui_python", {"codice": "print(1)"}))

    def test_tempo_configurabile(self):
        path = self.safe / "o.json"
        orchestratore.salva_cartelle([str(self.safe)], path)
        orchestratore.salva_tempo_python(90, path)
        self.assertEqual(orchestratore.tempo_python(path), 90)
        self.assertEqual(orchestratore.cartelle_sicure(path), [str(self.safe.resolve())])
        with self.assertRaises(ValueError):
            orchestratore.salva_tempo_python(2, path)


class AiutoChiaviTest(unittest.TestCase):
    def test_sezione_con_link_per_ogni_servizio_e_github(self):
        text = local_help._chiavi_servizi()
        for url in ("https://aistudio.google.com/apikey", "https://console.groq.com/keys",
                    "https://github.com/settings/personal-access-tokens/new"):
            self.assertIn(url, text)
        self.assertIn("1. ", text)


class SiNoSenzaNomeTest(unittest.TestCase):
    def tearDown(self):
        lumi_comandi._STATE.update(actions=None, pending=None)
        risposte.done()

    def test_finestra_di_risposta_di_20_secondi(self):
        lumi_comandi.register({"x": lambda: None}, lambda: False)
        with patch("risposte.expect_answer") as expect:
            lumi_comandi.chiedi("x", "Va bene?", lambda t: None, lambda t: None)
        self.assertEqual(expect.call_args.kwargs["seconds"], 20)


class MotoreSempreSeparatoTest(unittest.TestCase):
    def test_niente_casella_nelle_impostazioni(self):
        source = (Path(__file__).resolve().parents[1] / "jarvis.py").read_text(encoding="utf-8")
        self.assertNotIn("engine_separate_var", source)


if __name__ == "__main__":
    unittest.main()
