import json
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

import menu_tendine as menu_modelli
import orchestratore
import servizi_online as so
from servizi_online import quote


def fake_protect(value, encrypt):
    return bytes(b ^ 0x21 for b in value)


class ServiziInFileSeparatiTest(unittest.TestCase):
    def test_un_file_per_servizio(self):
        folder = Path(so.__file__).with_name("servizi")
        files = {p.stem for p in folder.glob("*.py") if p.stem != "__init__"}
        self.assertEqual(files, {s.id for s in so.SERVIZI})
        self.assertEqual(so.SERVIZI[0].id, "gemini")
        for service in so.SERVIZI:
            if service.tipo != "account":        # 058: il GPT dal browser non ha pagina delle chiavi
                self.assertTrue(service.chiavi.startswith("https://"), service.id)
            self.assertTrue(service.limite, service.id)
            self.assertGreaterEqual(len(service.passi), 3, service.id)


class QuoteTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / "uso.json"

    def tearDown(self):
        self.folder.cleanup()

    def test_conteggio_colori_e_avviso_una_volta(self):
        warnings = [quote.registra("openrouter", 100, path=self.path, soglia=0.8) for _ in range(45)]
        info = quote.stato("openrouter", path=self.path)                 # limite noto: 50/giorno
        self.assertEqual(info["richieste"], 45)
        self.assertAlmostEqual(info["usato"], 0.9)
        self.assertEqual(info["colore"], quote.ROSSO)
        self.assertEqual(sum(1 for w in warnings if w), 1)               # avviso solo una volta
        self.assertIn("80%", [w for w in warnings if w][0])
        self.assertEqual(quote.stato("openrouter", limite_utente=1000, path=self.path)["colore"],
                         quote.AZZURRO)

    def test_rimaste_dal_servizio(self):
        quote.registra("groq", 10, {"X-RateLimit-Remaining-Requests": "400",
                                    "x-ratelimit-limit-requests": "1000"}, path=self.path)
        info = quote.stato("groq", path=self.path)
        self.assertAlmostEqual(info["usato"], 0.6)
        self.assertEqual(info["colore"], quote.ARANCIONE)

    def test_limite_sconosciuto(self):
        quote.registra("gemini", 5, path=self.path)
        info = quote.stato("gemini", path=self.path)
        self.assertIsNone(info["usato"])
        self.assertEqual(info["testo"], "1 richieste oggi")

    def test_stima_token(self):
        self.assertEqual(quote.stima_token([{"content": "x" * 400}, {"content": None}]), 100)


class ConfermaTokenTest(unittest.TestCase):
    def test_troppo_testo_chiede_prima(self):
        asked = []
        tools = orchestratore.Strumenti(ask=lambda q: asked.append(q) or False,
                                        run_command=lambda t: None, folders=[])
        calls = []
        history = [("domanda " * 400, "risposta " * 400)] * 8        # ~12.000 token
        result = orchestratore.rispondi("riassumi", tools=tools, history=history,
                                        call=lambda *a, **k: calls.append(1))
        self.assertEqual(result, (None, ["annullato: troppo testo per la quota"]))
        self.assertEqual(calls, [])
        self.assertIn("token", asked[0])


class MenuModelliTest(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        self.root.withdraw()
        self.folder = tempfile.TemporaryDirectory()
        self.dir = Path(self.folder.name)
        self.patch = patch.object(so, "_cartella", lambda: self.dir)
        self.patch.start()
        self.keys = so.Chiavi(self.dir / "k.keys", protect=fake_protect)
        self.keys.salva("groq", "gsk_x")
        self.button = tk.Button(self.root, text="Online ▾")
        self.button.pack()
        self.opened = []
        self.menu = menu_modelli.MenuModelli(self.root, self.button,
                                             open_settings=lambda: self.opened.append(1),
                                             open_url=lambda u: None, keys=self.keys)

    def tearDown(self):
        self.menu.close()
        self.patch.stop()
        self.root.destroy()
        self.folder.cleanup()

    def test_spunte_in_uso_e_chiusura(self):
        self.assertEqual(self.button.cget("text"), "Online ▾")
        self.menu.toggle()
        self.assertIsNotNone(self.menu.popup)
        self.assertNotIn("xai", self.menu.vars)                          # a pagamento: non qui
        self.menu.vars["groq"].set(True)
        self.menu._toggle("groq")
        saved = json.loads((self.dir / "servizi_online.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["attivi"], ["groq"])
        self.assertEqual(self.button.cget("text"), "Online ▾")
        self.assertEqual(menu_modelli.servizio_in_uso(so.carica_impostazioni(), self.keys), "groq")

        class Event:
            widget = self.root
        self.menu._click_anywhere(Event())                               # clic altrove: si chiude
        self.assertIsNone(self.menu.popup)


if __name__ == "__main__":
    unittest.main()
