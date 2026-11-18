"""059: «Modello ▾» e «Potenza ▾» con testo intero e casella larga nella colonna reale della chat
(360 px, come in animated_hud.py), a 1366x768."""
import tkinter as tk
import unittest
from tkinter import ttk

import selettore_chat


class ColonnaChatTest(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        self.root.geometry("1366x768+0+0")
        self.colonna = tk.Frame(self.root, width=360, bg="#06192a")
        self.colonna.pack(side="left", fill="y")
        self.colonna.pack_propagate(False)
        host = tk.Frame(self.colonna, bg="#06192a")
        host.pack(side="bottom", fill="x", padx=10, pady=(8, 9))
        self.input_row = tk.Frame(host)
        self.input_row.pack(fill="x")
        self.selettori = tk.Frame(host)
        self.selettori.pack(fill="x", pady=(0, 4), before=self.input_row)
        tk.Button(self.input_row, text="●", width=2, font=("Segoe UI", 13, "bold")).pack(side="left", ipady=3)
        tk.Button(self.input_row, text="📎", width=2).pack(side="left")
        self.casella = ttk.Entry(self.input_row, font=("Segoe UI", 10))
        self.casella.pack(side="left", fill="x", expand=True, ipady=6)
        for testo in ("➤", "⋯", "?"):
            tk.Button(self.input_row, text=testo, width=2, font=("Segoe UI Symbol", 15)).pack(side="left")
        self.tasti = selettore_chat.crea_tasti(self.selettori, espandi=True)
        self.root.update()

    def tearDown(self):
        self.root.destroy()

    def test_testo_intero_e_dentro_la_colonna(self):
        bordo = self.selettori.winfo_rootx() + self.selettori.winfo_width()
        for tasto in self.tasti:
            self.assertGreaterEqual(tasto.winfo_width(), tasto.winfo_reqwidth())      # «Potenza ▾» non tagliato
            self.assertLessEqual(tasto.winfo_rootx() + tasto.winfo_width(), bordo)
        primo, secondo = self.tasti
        self.assertLessEqual(primo.winfo_x() + primo.winfo_width(), secondo.winfo_x())

    def test_la_casella_non_e_stretta(self):
        self.assertGreater(self.casella.winfo_width(), 150)

    def test_i_selettori_stanno_sopra_la_casella(self):
        self.assertLess(self.selettori.winfo_rooty(), self.input_row.winfo_rooty())


class CablaggioTest(unittest.TestCase):
    def test_jarvis_usa_una_riga_propria(self):
        from pathlib import Path
        src = (Path(__file__).resolve().parents[1] / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn("selettore_riga.pack(fill=\"x\", pady=(0, 4), before=input_row)", src)


if __name__ == "__main__":
    unittest.main()
