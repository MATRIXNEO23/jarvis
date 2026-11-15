import io
import json
import os
import tempfile
import tkinter as tk
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

import lumi_comandi
import servizi_online as so


def fake_protect(value, encrypt):
    return bytes(b ^ 0x5A for b in value)


def http_error(code):
    return urllib.error.HTTPError("https://x", code, "err", {}, io.BytesIO(b"{}"))


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.dir = Path(self.folder.name)
        self.keys = so.Chiavi(self.dir / "k.keys", protect=fake_protect)
        self.patch = patch.object(so, "_cartella", lambda: self.dir)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.folder.cleanup()


class FrasiTest(unittest.TestCase):
    def test_ragiona_online(self):
        self.assertEqual(so.forza_online("ragiona online, spiegami i buchi neri"),
                         (True, "spiegami i buchi neri"))
        self.assertEqual(so.forza_online("Lumi chiedi online chi ha vinto"), (True, "chi ha vinto"))
        self.assertEqual(so.forza_online("ragiona online")[0], False)
        self.assertEqual(so.forza_online("spiegami"), (False, "spiegami"))
        self.assertTrue(so.domanda_lunga("parola " * 30))


class ChiaviTest(BaseTest):
    def test_cifrate_e_togliibili(self):
        self.keys.salva("groq", "gsk_segreta")
        raw = (self.dir / "k.keys").read_text(encoding="utf-8")
        self.assertNotIn("gsk_segreta", raw)
        self.assertEqual(self.keys.leggi("groq"), "gsk_segreta")
        self.keys.salva("groq", "")
        self.assertFalse(self.keys.presente("groq"))
        with self.assertRaises(ValueError):
            self.keys.salva("inventato", "x")

    def test_dpapi_vera_su_windows(self):
        if os.name != "nt":
            self.skipTest("DPAPI solo su Windows")
        keys = so.Chiavi(self.dir / "vera.keys")
        keys.salva("gemini", "AIza-prova")
        self.assertEqual(keys.leggi("gemini"), "AIza-prova")


class ChiamataTest(BaseTest):
    def settings(self, attivi):
        data = so.carica_impostazioni(self.dir / "manca.json")
        data["attivi"] = attivi
        return data

    def test_ordine_quota_finita_passa_al_successivo(self):
        self.keys.salva("gemini", "a")
        self.keys.salva("groq", "b")
        calls = []

        def post(url, key, body, timeout):
            calls.append((url, key, body["model"]))
            if "googleapis" in url:
                raise http_error(429)
            return {"choices": [{"message": {"content": " Ciao! "}}]}

        name, text = so.chiedi(so.messaggi("ciao"), settings=self.settings(["gemini", "groq", "mistral"]),
                               keys=self.keys, post=post)
        self.assertEqual((name, text), ("Groq", "Ciao!"))
        self.assertEqual([c[1] for c in calls], ["a", "b"])
        self.assertEqual(calls[1][2], "llama-3.3-70b-versatile")

    def test_tutti_falliti_con_motivi(self):
        self.keys.salva("groq", "b")

        def post(url, key, body, timeout):
            raise http_error(401)

        name, reasons = so.chiedi(so.messaggi("x"), settings=self.settings(["groq", "mistral"]),
                                  keys=self.keys, post=post)
        self.assertIsNone(name)
        self.assertEqual(reasons, ["Groq: chiave non valida", "Mistral: manca la chiave"])

    def test_messaggi_con_cronologia_e_dati(self):
        messages = so.messaggi("e poi?", [("chi era Verdi", "Un compositore.")], ["[a.txt] testo"])
        self.assertEqual([m["role"] for m in messages], ["system", "user", "assistant", "user"])
        self.assertIn("Dati di riferimento", messages[-1]["content"])
        self.assertTrue(messages[-1]["content"].endswith("Domanda: e poi?"))

    def test_rispondi_usa_chat_e_allegati(self):
        seen = {}
        self.keys.salva("groq", "b")

        def post(url, key, body, timeout):
            seen["messages"] = body["messages"]
            return {"choices": [{"message": {"content": "ok"}}]}

        with patch("chat_elenco.contesto_recente", lambda count: [("prima", "risposta")]), \
                patch("allegati.per_online", lambda q: ["[f.txt] pezzo"]):
            name, _ = so.rispondi("domanda", card="[Scheda di Lumi]", settings=self.settings(["groq"]),
                                  keys=self.keys, post=post)
        self.assertEqual(name, "Groq")
        last = seen["messages"][-1]["content"]
        self.assertIn("[Scheda di Lumi]", last)
        self.assertIn("[f.txt] pezzo", last)
        self.assertEqual(seen["messages"][1]["content"], "prima")


class PercorsoTest(BaseTest):
    def test_scelte(self):
        data = so.carica_impostazioni()
        self.assertEqual(so.percorso("ragiona online ciao", settings=data, keys=self.keys), ("locale", "ciao"))
        self.keys.salva("groq", "b")
        data["attivi"] = ["groq"]
        self.assertEqual(so.percorso("ragiona online ciao", settings=data, keys=self.keys), ("online", "ciao"))
        self.assertEqual(so.percorso("ciao", settings=data, keys=self.keys)[0], "locale")
        self.assertEqual(so.percorso("parola " * 30, settings=data, keys=self.keys)[0], "proponi")
        data["usa_sempre"] = True
        self.assertEqual(so.percorso("ciao", settings=data, keys=self.keys)[0], "online")
        self.assertEqual(so.percorso("ciao", "locale", settings=data, keys=self.keys)[0], "locale")

    def test_impostazioni_ripulite(self):
        (self.dir / "servizi_online.json").write_text(json.dumps(
            {"ordine": ["groq", "falso"], "attivi": ["falso", "groq"], "modelli": {"groq": "x", "z": "y"}}),
            encoding="utf-8")
        data = so.carica_impostazioni()
        self.assertEqual(data["ordine"][0], "groq")
        self.assertEqual(len(data["ordine"]), len(so.SERVIZI))
        self.assertEqual(data["attivi"], ["groq"])
        self.assertEqual(data["modelli"], {"groq": "x"})


class SiNoTest(unittest.TestCase):
    def tearDown(self):
        lumi_comandi._STATE.update(actions=None, pending=None)

    def test_no_esegue_l_azione_del_no(self):
        calls = []
        lumi_comandi.register({"online_yes": lambda: calls.append("si"),
                               "online_no": lambda: calls.append("no")}, lambda: False)
        lumi_comandi.chiedi("online_yes", "La passo all'online?", lambda t: None, lambda t: None,
                            no_action="online_no")
        self.assertTrue(lumi_comandi.handle_text("no", lambda t: None, lambda t: None))
        lumi_comandi.chiedi("online_yes", "La passo all'online?", lambda t: None, lambda t: None,
                            no_action="online_no")
        self.assertTrue(lumi_comandi.handle_text("sì", lambda t: None, lambda t: None))
        self.assertEqual(calls, ["no", "si"])


class SezioneTest(BaseTest):
    def test_caselle_chiave_ordine(self):
        try:
            root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        root.withdraw()
        notes = []
        try:
            box = so.costruisci_sezione(root, notes.append, ask_key=lambda name: "chiave",
                                        keys=self.keys, open_url=lambda u: None,
                                        run_async=lambda fn: fn(),
                                        post=lambda *a: {"choices": [{"message": {"content": "ok"}}]})
            lines = box.winfo_children()[1].winfo_children()
            self.assertEqual(len(lines), len(so.SERVIZI))
            first = lines[0].winfo_children()
            first[0].invoke()                       # casella del primo servizio
            first[3].invoke()                       # «Chiave…»
            self.assertTrue(self.keys.presente(so.SERVIZI[0].id))
            saved = json.loads((self.dir / "servizi_online.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["attivi"], [so.SERVIZI[0].id])
            lines = box.winfo_children()[1].winfo_children()
            lines[0].winfo_children()[4].invoke()   # «Prova»
            self.assertIn("funziona", notes[-1])
            lines[0].winfo_children()[6].invoke()   # «↓»
            saved = json.loads((self.dir / "servizi_online.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["ordine"][1], so.SERVIZI[0].id)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
