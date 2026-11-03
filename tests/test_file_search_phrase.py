"""Windows regressions for the exact failed Minecraft search phrase."""
import os
import unittest

import test_file_access as access_tests


@unittest.skipUnless(os.name == 'nt', 'Windows-only user requirement')
class FileSearchPhraseTests(unittest.TestCase):
    setUp = access_tests.FileAccessTests.setUp

    def test_user_phrase_searches_the_folder_name_not_the_preposition(self):
        target = self.docs / 'Minecraft'
        target.mkdir()
        command = self.files.parse_command('Cercami la cartella di Minecraft')
        self.assertEqual(command, ('search', {'query': 'Minecraft'}))
        result = self.engine.execute_file(*command)
        self.assertEqual(result.status, 'completed', result.message)
        self.assertEqual(len(self.files._results), 1)
        self.assertTrue(os.path.samefile(self.files._results[0], target))

    def test_without_preposition_and_quoted_literal_names_are_preserved(self):
        for phrase, expected in (
            ('cerca cartella Minecraft', 'Minecraft'),
            ('trovami la cartella di Minecraft', 'Minecraft'),
            ('cercami il file di Minecraft', 'Minecraft'),
            ('cerca cartella "di Minecraft"', '"di Minecraft"'),
            ('cerca file diario.txt', 'diario.txt'),
        ):
            with self.subTest(phrase=phrase):
                self.assertEqual(self.files.parse_command(phrase),
                                 ('search', {'query': expected}))

    def test_scoped_search_keeps_the_authorized_scope_after_the_preposition(self):
        self.assertEqual(self.files.parse_command('cerca la cartella di Minecraft in documenti'),
                         ('search', {'query': 'Minecraft', 'scope': 'documenti'}))


if __name__ == '__main__':
    unittest.main()
