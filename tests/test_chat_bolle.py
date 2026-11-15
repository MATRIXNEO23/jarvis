import tkinter as tk
import unittest

from chat_bolle import Bolle


class ChatBolleTest(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        self.root.withdraw()
        self.text = tk.Text(self.root)
        self.calls = []
        self.bolle = Bolle(self.text, copy=lambda v: self.calls.append(("copia", v)),
                           read=lambda v: self.calls.append(("leggi", v)),
                           regenerate=lambda q: self.calls.append(("rigenera", q)),
                           limit=4)

    def tearDown(self):
        self.root.destroy()

    def scrivi(self, role, body):
        mark = self.bolle.inizio()
        self.text.insert("end", role + "\n" + body + "\n\n", role)
        self.bolle.fine(role, body, mark)

    def bottoni(self):
        return [w for bar in self.bolle.bars.values() for w in bar.winfo_children()]

    def test_risposta_ha_copia_leggi_rigenera_con_la_domanda_giusta(self):
        self.scrivi("utente", "che ore sono")
        self.scrivi("jarvis", "Sono le tre.")
        buttons = {b.cget("text"): b for b in self.bottoni()}
        self.assertEqual(set(buttons), {"copia", "leggi", "rigenera"})
        for name in ("copia", "leggi", "rigenera"):
            buttons[name].invoke()
        self.assertEqual(self.calls, [("copia", "Sono le tre."), ("leggi", "Sono le tre."),
                                      ("rigenera", "che ore sono")])
        self.assertIn("bolla_utente", self.text.tag_names("1.0"))

    def test_comandi_senza_pulsanti_e_senza_domanda_niente_rigenera(self):
        self.scrivi("comando", "Timer avviato")
        self.assertEqual(self.bolle.bars, {})
        self.scrivi("jarvis", "Ciao")
        self.assertEqual([b.cget("text") for b in self.bottoni()], ["copia", "leggi"])

    def test_restano_solo_gli_ultimi_messaggi(self):
        for n in range(6):
            self.scrivi("utente", "domanda %d" % n)
            self.scrivi("jarvis", "risposta %d" % n)
        self.assertEqual(len(self.bolle.marks), 4)
        self.assertEqual(len(self.bolle.bars), 2)
        content = self.text.get("1.0", "end")
        self.assertNotIn("domanda 3", content)
        self.assertIn("domanda 4", content)
        self.assertIn("risposta 5", content)

    def test_azzera_toglie_pulsanti(self):
        self.scrivi("utente", "a")
        self.scrivi("jarvis", "b")
        self.bolle.azzera()
        self.assertEqual((self.bolle.bars, self.bolle.marks, self.bolle.last_user), ({}, [], ""))


if __name__ == "__main__":
    unittest.main()
