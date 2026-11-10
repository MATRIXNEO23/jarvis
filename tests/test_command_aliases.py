import tempfile
import unittest
from pathlib import Path

import command_aliases as ca


class CommandAliasTests(unittest.TestCase):
    ITEMS = [{"section": "Musica", "phrase": "sparami {testo}", "command": "metti {testo}"},
             {"section": "Musica", "phrase": "Buonanotte!", "command": "ferma la musica"},
             {"section": "Timer e sveglia", "phrase": "cuoci la pasta",
              "command": "imposta timer nove minuti"}]

    def test_rewrite_with_slot_wake_word_and_exact_phrase(self):
        self.assertEqual(ca.rewrite("sparami i Queen", self.ITEMS), "metti i queen")
        self.assertEqual(ca.rewrite("Lumi, sparami AC/DC", self.ITEMS), "Lumi, metti ac dc")
        self.assertEqual(ca.rewrite("buonanotte", self.ITEMS), "ferma la musica")
        self.assertEqual(ca.rewrite("Cuoci la pasta.", self.ITEMS), "imposta timer nove minuti")
        # Frasi diverse restano invariate (anche se contengono le parole).
        self.assertEqual(ca.rewrite("dimmi buonanotte domani", self.ITEMS),
                         "dimmi buonanotte domani")
        self.assertEqual(ca.rewrite("metti Imagine", self.ITEMS), "metti Imagine")

    def test_invalid_entries_dropped_and_saved_in_profile_file(self):
        bad = [{"phrase": "", "command": "x"}, {"phrase": "ciao", "command": "metti {testo}"},
               {"phrase": "uno", "command": "a"}, {"phrase": "UNO", "command": "b"}]
        self.assertEqual([i["command"] for i in ca.clean(bad)], ["a"])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "command-aliases.json"
            ca.save(self.ITEMS, path)
            self.assertEqual(len(ca.load(path)), 3)
            self.assertEqual(ca.rewrite("buonanotte", path=path), "ferma la musica")
            self.assertEqual(ca.rewrite("buonanotte", path=Path(folder) / "assente.json"),
                             "buonanotte")


if __name__ == "__main__":
    unittest.main()
