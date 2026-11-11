import tempfile
import unittest
from pathlib import Path
from unittest import mock

import frasi_lumi as f


class FrasiTests(unittest.TestCase):
    def test_variants_never_same_twice_and_placeholders(self):
        data = {"added": {}, "removed": {}}
        previous = None
        for _ in range(30):
            text = f.say("passo", data, finestra="Download")
            self.assertIn("Download", text)
            self.assertNotEqual(text, previous)
            previous = text

    def test_user_phrases_add_edit_remove_restore(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "frasi.json"
            f.add("passo", "Via su {finestra}!", path)
            rows = f.phrases("passo", f.load(path))
            self.assertIn(("Via su {finestra}!", True), rows)
            f.edit("passo", "Via su {finestra}!", "Eccomi in {finestra}!", path)
            f.remove("passo", "Ecco {finestra}.", path)                 # una predefinita
            rows = f.phrases("passo", f.load(path))
            self.assertIn(("Eccomi in {finestra}!", True), rows)
            self.assertNotIn(("Ecco {finestra}.", False), rows)
            f.restore_defaults("passo", path)
            rows = f.phrases("passo", f.load(path))
            self.assertIn(("Ecco {finestra}.", False), rows)
            self.assertIn(("Eccomi in {finestra}!", True), rows)        # le tue restano

    def test_greetings_by_hour(self):
        with mock.patch.object(f, "load", return_value={"added": {}, "removed": {}}):
            morning = [p for p, _ in f.phrases("avvio_mattina", {"added": {}, "removed": {}})]
            self.assertIn(f.greeting("avvio", 8), morning)
            evening = [p for p, _ in f.phrases("chiusura_sera", {"added": {}, "removed": {}})]
            self.assertIn(f.greeting("chiusura", 22), evening)


class LumiCommandsTests(unittest.TestCase):
    def test_parse_and_confirmations(self):
        import lumi_comandi as l
        self.assertEqual(l.parse("Lumi, riduci a icona"), "minimize")
        self.assertIsNone(l.parse("minimizza"))                         # resta al Controllo PC
        self.assertEqual(l.parse("chiudi Lumi"), "close")
        self.assertEqual(l.parse("spegni il pc"), "shutdown_pc")
        self.assertIsNone(l.parse("spegni la sveglia"))
        done, lines, hidden = [], [], [False]
        actions = {k: (lambda k=k: done.append(k)) for k in
                   ("minimize", "close", "restart", "shutdown_pc", "cancel_shutdown", "hide", "wake")}
        l.register(actions, lambda: hidden[0])
        self.assertFalse(l.handle_text("sveglia", lines.append, lines.append))   # Lumi visibile: è la sveglia
        hidden[0] = True
        self.assertTrue(l.handle_text("Lumi, sveglia", lines.append, lines.append))
        self.assertEqual(done, ["wake"])
        self.assertTrue(l.handle_text("spegni il computer", lines.append, lines.append))
        self.assertEqual(done, ["wake"])                                 # prima chiede
        self.assertTrue(l.handle_text("no", lines.append, lines.append))
        self.assertTrue(l.handle_text("riavvia Lumi", lines.append, lines.append))
        self.assertTrue(l.handle_text("sì", lines.append, lines.append))
        self.assertEqual(done, ["wake", "restart"])
        l.register(None, lambda: False)


if __name__ == "__main__":
    unittest.main()
