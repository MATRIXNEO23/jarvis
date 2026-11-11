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


    def test_catalog_includes_enabled_programs_and_section_save(self):
        class Apps:
            def available(self):
                return True

            def entries(self):
                return ({"name": "Spotify", "enabled": True, "available": True},
                        {"name": "Paint", "enabled": False, "available": True})

        class Engine:
            program_apps = Apps()
            file_access = None
        cat = ca.catalog(Engine(), music=False, pc=False)
        self.assertEqual(cat["Programmi e app"], ["apri Spotify"])
        self.assertIn("metti {testo}", cat["Musica"])
        old = [{"section": "Musica", "phrase": "vecchia", "command": "ferma la musica"},
               {"section": "Timer e sveglia", "phrase": "pasta", "command": "imposta timer nove minuti"}]
        items = ca.replace_section("Musica", {"metti {testo}": "sparami; voglio sentire",
                                              "ferma la musica": "",
                                              "apri Spotify": "musica on"}, old)
        phrases = {i["phrase"]: i["command"] for i in items}
        self.assertEqual(phrases, {"pasta": "imposta timer nove minuti",
                                   "sparami {testo}": "metti {testo}",
                                   "voglio sentire {testo}": "metti {testo}",
                                   "musica on": "apri Spotify"})
        self.assertEqual(ca.section_rows("Musica", ["metti {testo}"], items),
                         [("metti {testo}", "sparami {testo}; voglio sentire {testo}")])
        self.assertEqual(ca.rewrite("voglio sentire i Queen", items), "metti i queen")


if __name__ == "__main__":
    unittest.main()
