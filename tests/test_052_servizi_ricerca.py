"""052 punti 8 e 9: servizi di ricerca (impostazioni, chiavi, «cerca online», fallback).

Rete simulata (post finto): nessuna chiamata reale ai servizi, nessuna chiave vera.
"""
import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

import lumi_comandi
import servizi_online
import servizi_ricerca as sr
from servizi_ricerca.base import Ricerca, Risultato


def protect(value, encrypt):          # al posto di DPAPI (solo Windows): il file non è in chiaro
    return value[::-1]


def http_error(code):
    return urllib.error.HTTPError("https://x", code, "x", {}, io.BytesIO(b""))


class ParseTests(unittest.TestCase):
    def test_only_the_two_online_commands(self):
        self.assertEqual(sr.parse("cerca online il meteo a Roma"), ("cerca", "il meteo a Roma"))
        self.assertEqual(sr.parse("Lumi, approfondisci online la fusione nucleare"),
                         ("approfondisci", "la fusione nucleare"))
        self.assertEqual(sr.parse("cerca online su Marte")[1], "Marte")
        for text in ("approfondisci la fusione nucleare", "cerca file preventivo", "cerca online",
                     "cerca il meteo", "ricerca online meteo"):
            self.assertIsNone(sr.parse(text), text)

    def test_four_services_with_the_official_key_links_in_order(self):
        self.assertEqual([s.id for s in sr.SERVIZI], ["tavily", "exa", "firecrawl", "linkup"])
        self.assertEqual([s.chiavi for s in sr.SERVIZI], [
            "https://app.tavily.com", "https://dashboard.exa.ai",
            "https://www.firecrawl.dev/app/api-keys", "https://app.linkup.so"])
        self.assertIsNotNone(sr.PER_ID["tavily"].adattatore)
        self.assertTrue(all(sr.PER_ID[i].adattatore is None for i in ("exa", "firecrawl", "linkup")))

    def test_local_hook_takes_cerca_online_but_not_file_search_or_plain_approfondisci(self):
        saved = dict(lumi_comandi._STATE)
        self.addCleanup(lumi_comandi._STATE.update, saved)
        got = []
        lumi_comandi.register({"ricerca": lambda spoken: got.append(spoken) or True}, lambda: False)
        handle = lambda text: lumi_comandi.handle_text(text, lambda *_: None, lambda *_: None)
        self.assertTrue(handle("cerca online il meteo a Roma"))
        self.assertTrue(handle("Lumi, approfondisci online la fusione"))
        self.assertFalse(handle("approfondisci la fusione"))
        self.assertFalse(handle("cerca file preventivo"))
        self.assertEqual(len(got), 2)


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.keys = servizi_online.Chiavi(path=self.folder / "k.keys", protect=protect, ids=sr.PER_ID)

    def fake_services(self, adapters):
        services = {name: Ricerca(id=name, nome=name.title(), chiavi="https://x/" + name,
                                  ordine=n, adattatore=fn)
                    for n, (name, fn) in enumerate(adapters.items(), 1)}
        patch = mock.patch.object(sr, "PER_ID", services)
        patch.start()
        self.addCleanup(patch.stop)
        self.keys.ids = services
        return {"ordine": list(services), "attivi": list(services)}

    def test_second_service_answers_when_the_first_has_no_credits(self):
        calls = []

        def finished(key, query, deep, timeout, post):
            calls.append("a")
            raise http_error(429)

        def works(key, query, deep, timeout, post):
            calls.append(("b", key, deep))
            return Risultato("Risposta breve.", (("Titolo", "https://esempio.it/1"),))
        settings = self.fake_services({"a": finished, "b": works})
        self.keys.salva("a", "SEGRETO-A")
        self.keys.salva("b", "SEGRETO-B")
        name, result = sr.cerca("meteo", True, settings=settings, keys=self.keys)
        self.assertEqual(name, "B")
        self.assertEqual(calls, ["a", ("b", "SEGRETO-B", True)])
        self.assertEqual(result.link[0][1], "https://esempio.it/1")

    def test_all_failing_returns_reasons_without_any_key(self):
        def broken(code):
            def run(*args):
                raise http_error(code)
            return run
        settings = self.fake_services({"a": broken(402), "b": broken(401), "c": broken(500)})
        for name in "abc":
            self.keys.salva(name, "SEGRETO-" + name)
        name, reasons = sr.cerca("meteo", settings=settings, keys=self.keys)
        self.assertIsNone(name)
        text = " ".join(reasons)
        self.assertIn("crediti", text)
        self.assertIn("chiave rifiutata", text)
        self.assertNotIn("SEGRETO", text)

    def test_services_without_key_adapter_or_checkbox_are_skipped(self):
        called = []
        settings = self.fake_services({"a": lambda *a: called.append("a"),
                                       "b": None, "c": lambda *a: called.append("c")})
        self.keys.salva("b", "k")
        self.keys.salva("c", "k")
        settings["attivi"] = ["b", "c"]
        sr.cerca("x", settings=settings, keys=self.keys)
        self.assertEqual(called, ["c"])                 # a: spuntato no; b: senza adattatore
        self.assertEqual(sr.pronti(settings, self.keys)[0].id, "c")

    def test_keys_are_encrypted_on_disk_and_separate_from_online_services(self):
        self.keys.salva("tavily", "tvly-SEGRETISSIMA")
        raw = (self.folder / "k.keys").read_text(encoding="utf-8")
        self.assertNotIn("tvly-SEGRETISSIMA", raw)
        self.assertEqual(self.keys.leggi("tavily"), "tvly-SEGRETISSIMA")
        with self.assertRaises(ValueError):
            self.keys.salva("groq", "x")                # un servizio online non è di ricerca
        with self.assertRaises(ValueError):
            servizi_online.Chiavi(path=self.folder / "o.keys", protect=protect).salva("tavily", "x")

    def test_tavily_adapter_maps_answer_and_links_and_falls_back_to_snippets(self):
        from servizi_ricerca.servizi import tavily
        seen = {}

        def post(url, key, body, timeout):
            seen.update(url=url, key=key, body=body)
            return {"answer": "Fa bel tempo.", "results": [
                {"title": "Meteo", "url": "https://m.it", "content": "sole"}, {"url": ""}]}
        result = tavily.cerca("tvly-k", "meteo Roma", True, 10, post)
        self.assertEqual(seen["url"], "https://api.tavily.com/search")
        self.assertEqual(seen["body"]["search_depth"], "advanced")
        self.assertEqual(result, Risultato("Fa bel tempo.", (("Meteo", "https://m.it"),), ("sole",)))
        basic = tavily.cerca("k", "meteo", False, 10, lambda *a: {
            "answer": None, "results": [{"title": "T", "url": "https://u", "content": "contenuto"}]})
        self.assertEqual(basic.riassunto, "contenuto")
        self.assertEqual(seen["body"]["max_results"], 8)

    def test_text_for_chat_window_and_voice_have_summary_and_links_only(self):
        result = Risultato("Prima frase. " * 40, (("A", "https://a"), ("B", "https://b")))
        chat = sr.testo_chat("Tavily", result)
        self.assertIn("1. [A](https://a)", chat)
        listing = sr.elenco_finestra("Tavily", result)
        self.assertEqual(listing["items"], [("Link", "A", "https://a"), ("Link", "B", "https://b")])
        self.assertLessEqual(len(sr.frase_breve(result)), 290)

    def test_settings_roundtrip_and_unknown_ids_dropped(self):
        path = self.folder / "s.json"
        sr.salva_impostazioni({"ordine": ["linkup", "tavily", "inventato"], "attivi": ["tavily", "zzz"]}, path)
        data = sr.carica_impostazioni(path)
        self.assertEqual(data["ordine"], ["linkup", "tavily", "exa", "firecrawl"])
        self.assertEqual(data["attivi"], ["tavily"])
        self.assertEqual(sr.carica_impostazioni(self.folder / "manca.json")["attivi"], [])


class SettingsSectionTests(unittest.TestCase):
    def test_section_has_four_rows_with_key_buttons_and_links_and_saves_choices(self):
        import tkinter as tk
        from tkinter import ttk
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("nessuno schermo disponibile")
        root.withdraw()
        self.addCleanup(root.destroy)
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        folder = Path(temp.name)
        opened, notes, asked = [], [], []
        keys = servizi_online.Chiavi(path=folder / "k.keys", protect=protect, ids=sr.PER_ID)
        with mock.patch.object(sr, "_cartella", lambda: folder):
            box = sr.costruisci_sezione(root, notes.append, keys=keys, open_url=opened.append,
                                        ask_key=lambda name: asked.append(name) or "tvly-CHIAVE")
        self.assertEqual(box.cget("text"), "Servizi di ricerca")

        def buttons(text):
            found = []

            def walk(widget):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and str(child.cget("text")).startswith(text):
                        found.append(child)
                    walk(child)
            walk(box)
            return found
        for button in buttons("Prendi la chiave"):
            button.invoke()
        self.assertEqual(opened, [s.chiavi for s in sr.SERVIZI])
        with mock.patch.object(sr, "_cartella", lambda: folder):
            buttons("Chiave…")[0].invoke()
        self.assertEqual(asked, ["Tavily"])
        self.assertTrue(keys.presente("tavily"))
        self.assertTrue(any("salvata" in n and "tvly-CHIAVE" not in n for n in notes))
        self.assertNotIn("tvly-CHIAVE", (folder / "k.keys").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
