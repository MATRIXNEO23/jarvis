import tempfile
import tkinter as tk
import unittest
from pathlib import Path

import ricordi
import servizi_online
from preference_voice import parse_preference_intent
from second_brain import SecondBrain


class Base(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.brain = SecondBrain(Path(self.folder.name) / "brain.sqlite3")
        ricordi.ULTIMO.update(id=None, breve="", quando=0.0)

    def tearDown(self):
        ricordi.CERVELLO["get"] = lambda: None
        self.folder.cleanup()


class ArchivioTest(Base):
    def test_salva_cerca_cancella(self):
        a = self.brain.salva_ricordo("Alberto ha un Pavilion con 10 GB di RAM",
                                     "Il PC di Alberto: HP Pavilion, i3-2100, 10 GB RAM, Windows 10",
                                     categoria="su_di_te", fonte="online")
        self.brain.salva_ricordo("Progetto Lumi: menu impostazioni a cascata", categoria="progetti")
        self.assertIsNone(self.brain.salva_ricordo("alberto ha un pavilion con 10 gb di ram"))
        self.assertIsNone(self.brain.salva_ricordo("la mia password è 1234"))
        found = self.brain.ricordi("pavilion")
        self.assertEqual([r["id"] for r in found], [a])
        self.assertEqual(self.brain.ricordi("progett")[0]["categoria"], "progetti")   # prefisso
        self.assertEqual(len(self.brain.ricordi()), 2)
        self.assertEqual(len(self.brain.ricordi(categoria="progetti")), 1)
        self.assertTrue(self.brain.cancella_ricordo(a))
        self.assertEqual(self.brain.ricordi("pavilion"), [])
        self.assertFalse(self.brain.cancella_ricordo(a))

    def test_gemma_riceve_solo_le_frasi_brevi(self):
        self.brain.salva_ricordo("Alberto usa il Pavilion", "x" * 900, categoria="su_di_te")
        raw = self.brain.prompt_context("che pc usa alberto con il pavilion", budget=530)
        self.assertIn("Alberto usa il Pavilion", raw)
        self.assertNotIn("xxxx", raw)
        self.assertLessEqual(len(raw), 530)


class RicordiTest(Base):
    def test_estrai_le_righe_dell_online(self):
        text = ("Ecco fatto.\n[[RICORDO|persone|Marco è il fratello di Alberto|Marco, fratello]]\n"
                "[[RICORDO|boh|Frase|]]")
        clean, found = ricordi.estrai(text)
        self.assertEqual(clean, "Ecco fatto.")
        self.assertEqual(found[0], ("persone", "Marco è il fratello di Alberto", "Marco, fratello"))
        self.assertEqual(found[1][0], "altro")

    def test_salva_mostra_e_cancellalo(self):
        clock = [100.0]
        saved = ricordi.salva(self.brain, [("persone", "Marco è il fratello", "Marco")],
                              fonte="online", clock=lambda: clock[0])
        self.assertIn("cancellalo", ricordi.avviso(saved))
        self.assertEqual(ricordi.cancella_se_chiesto(self.brain, "apri chrome", lambda: clock[0]), "")
        clock[0] += 30
        self.assertIn("cancellato", ricordi.cancella_se_chiesto(self.brain, "Lumi cancellalo",
                                                                lambda: clock[0]))
        self.assertEqual(self.brain.ricordi(), [])
        ricordi.salva(self.brain, [("altro", "Una cosa", "Una cosa")], fonte="online",
                      clock=lambda: clock[0])
        clock[0] += ricordi.FINESTRA_CANCELLA + 1
        self.assertEqual(ricordi.cancella_se_chiesto(self.brain, "cancellalo", lambda: clock[0]), "")

    def test_ricordati_che_frase_libera(self):
        intent = parse_preference_intent("Lumi ricordati che giovedì ho il dentista")
        self.assertEqual((intent.kind, intent.value), ("ricordo", "giovedì ho il dentista"))
        self.assertEqual(parse_preference_intent("salva preferenza boh").kind, "unsupported")
        self.assertEqual(parse_preference_intent("ricordati che preferisco risposte brevi").kind, "set")
        message = ricordi.da_utente(self.brain, intent.value)
        self.assertIn("Giovedì ho il dentista", message)
        self.assertEqual(self.brain.ricordi()[0]["categoria"], "su_di_te")
        self.assertEqual(ricordi.da_utente(self.brain, intent.value), "Questo lo ricordavo già.")
        self.assertIn("non disponibile", ricordi.da_utente(None, "x"))

    def test_l_online_riceve_le_versioni_complete(self):
        self.brain.salva_ricordo("Lumi: menu a cascata", "Lumi: menu a cascata, decisi il 15/11, "
                                 "manca la memoria", categoria="progetti")
        text = ricordi.per_online(self.brain, "come va il menu di lumi")
        self.assertIn("manca la memoria", text)
        self.assertIn("[Progetti]", text)
        self.assertEqual(ricordi.per_online(None, "x"), "")

    def test_messaggi_online_istruzione_e_cronologia_della_chat(self):
        history = [(("user", "chi era Verdi"), ("assistant", "Un compositore."))]
        messages = servizi_online.messaggi("e poi?", history)
        self.assertIn("[[RICORDO|", messages[0]["content"])
        self.assertEqual(messages[1]["content"], "chi era Verdi")
        self.assertEqual(messages[2]["content"], "Un compositore.")


class PaginaTest(Base):
    def test_ricerca_e_cartelle(self):
        try:
            root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        root.withdraw()
        try:
            import ricordi_ui
            self.brain.salva_ricordo("Marco è il fratello", categoria="persone")
            self.brain.salva_ricordo("Lumi usa Gemma", categoria="su_lumi")
            page = ricordi_ui.PaginaRicordi(root, lambda: self.brain, confirm=lambda *a: True,
                                            after=lambda ms, fn: fn())
            folders = [page.tree.item(i, "text") for i in page.tree.get_children()]
            self.assertIn("📁 Persone (1)", folders)
            self.assertEqual(len(folders), len(ricordi.CATEGORIE))
            page.query.set("marco")
            self.assertEqual([i["breve"] for i in page.rows.values()], ["Marco è il fratello"])
            page.tree.focus(next(iter(page.rows)))
            page.cancella()
            self.assertEqual(len(self.brain.ricordi()), 1)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
