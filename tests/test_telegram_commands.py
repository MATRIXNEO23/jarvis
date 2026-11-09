import unittest
from telegram_commands import explicit_telegram_note

class NoteParsing(unittest.TestCase):
 def test_note_only_to_authorized_contact(self):
  self.assertEqual(explicit_telegram_note('Lumi, riferisci alla mia amica che domani la chiamo', 'Maria'), 'domani la chiamo')
  self.assertIsNone(explicit_telegram_note('Informa qualcun altro', 'Maria'))
  self.assertIsNone(explicit_telegram_note('Riferisci a Laura che vengo', 'Maria'))

if __name__ == '__main__':
 unittest.main()
