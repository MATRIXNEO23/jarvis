import tempfile
import tkinter as tk
import unittest
from types import SimpleNamespace
from pathlib import Path
from tkinter import ttk

import impostazioni_menu as im


class NavigazioneTest(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.nb = ttk.Notebook(self.win)
        self.nb.pack(fill="both", expand=True)
        self.pages = {}
        self.boxes = {}

        def page(title, sections, loose=()):
            frame = ttk.Frame(self.nb)
            self.nb.add(frame, text=title)
            self.pages[title] = frame
            for text in loose:
                ttk.Label(frame, text=text).pack(anchor="w")
            for text in sections:
                box = ttk.LabelFrame(frame, text=text)
                box.pack(fill="x", pady=3)
                self.boxes[text] = box

        page("Voce", ["Risposte vocali offline — voci di Windows"], ["Voce e ascolto"])
        page("GPT e memoria", ["Modello locale Gemma (sperimentale)", "Connessione ChatGPT",
                               "Memoria generale", "Servizi online (API ufficiali)",
                               "Riquadro sconosciuto"])
        page("Progetti e servizi", ["La mia voce", "Add-on — installazione locale e permessi",
                                    "GitHub (sola lettura, add-on spento di serie)"])
        page("Timer e allarmi", ["Sveglia"], ["Timer e allarmi"])
        page("Interfaccia", [], ["Tieni sveglio lo schermo"])
        self.nav = im.Navigazione(self.win, self.nb, self.pages, main_root=self.root)

    def tearDown(self):
        self.root.destroy()

    def test_categorie_e_voci(self):
        voci = self.nav.voci()
        self.assertEqual(list(voci), ["Interfaccia", "Voce", "Memoria", "Modelli", "Add-on"])
        self.assertEqual(voci["Voce"], ["Microfono e ascolto", "Voci", "La mia voce"])
        self.assertEqual(voci["Modelli"], ["Modello locale", "GPT dal browser", "Servizi online", "Altro"])
        self.assertIn("⏰ Timer e sveglia", voci["Add-on"])
        self.assertIn("🐙 GitHub", voci["Add-on"])
        self.assertEqual(voci["Memoria"], ["Second Brain"])

    def test_mostra_solo_la_voce_scelta_e_niente_si_perde(self):
        self.nav.apri_categoria("Modelli")
        self.nav.mostra("Modelli", "Servizi online")
        self.assertTrue(self.boxes["Servizi online (API ufficiali)"].winfo_manager())
        self.assertFalse(self.boxes["Connessione ChatGPT"].winfo_manager())
        self.assertEqual(self.nb.select(), str(self.pages["GPT e memoria"]))
        self.nav.mostra("Voce", "La mia voce")
        self.assertTrue(self.boxes["La mia voce"].winfo_manager())
        self.assertFalse(self.boxes["Servizi online (API ufficiali)"].winfo_manager())
        self.assertEqual(self.nb.select(), str(self.pages["Progetti e servizi"]))
        every = [w for items in self.nav.tree.values() for entries in items.values() for _p, w in entries]
        self.assertEqual(len(every), sum(len(p.winfo_children()) for p in self.pages.values()))

    def test_clic_nella_finestra_principale_chiude(self):
        self.win.deiconify()
        self.win.update()

        self.nav._click_main(SimpleNamespace(widget=self.root))
        self.win.update()
        self.assertFalse(self.win.winfo_viewable())


class PagineTest(unittest.TestCase):
    def test_versione_e_licenze_dai_file(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            self.assertEqual(im.versione(base)["nome"], "Lumi (versione di sviluppo)")
            (base / "VERSIONE.json").write_text('{"build_label": "049", "source_commit": "abcdef123"}',
                                                encoding="utf-8")
            self.assertEqual(im.versione(base), {"nome": "Lumi 049", "commit": "abcdef1", "motore": ""})
            (base / "native_engine").mkdir()
            (base / "terze_parti").mkdir()
            (base / "terze_parti" / "LEGGIMI.md").write_text(
                "| Cartella | Progetto | Versione | Licenza | Fonte | Uso |\n|---|---|---|---|---|---|\n"
                "| `pypdf/` | pypdf | 7.1.0 | BSD-3-Clause | x | PDF |\n", encoding="utf-8")
            names = [n for n, _l in im.licenze(base)]
            self.assertEqual(names, ["KoboldCpp (motore del modello locale)", "pypdf 7.1.0"])

    def test_licenze_del_repository(self):
        self.assertIn("pypdf 7.1.0", [n for n, _l in im.licenze()])


if __name__ == "__main__":
    unittest.main()
