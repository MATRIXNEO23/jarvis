"""058 (04:16): attesa 30 s in chat e 90 s per i lavori dell'orchestratore; modello di Gemini invariato.
La potenza è provata in test_058_selettore_chat.py."""
import inspect
import unittest

from online import servizi_online as so
class AtteseTests(unittest.TestCase):
    def test_chat_30_secondi_lavori_90(self):
        self.assertEqual(so.TIMEOUT, 30)
        self.assertEqual(so.TIMEOUT_LAVORO, 90)
        self.assertEqual(inspect.signature(so.chiedi).parameters["timeout"].default, 30)
        self.assertEqual(inspect.signature(so.chiama).parameters["timeout"].default, 90)

    def test_gemini_resta_flash_latest(self):
        self.assertEqual(so.PER_ID["gemini"].modello, "gemini-flash-latest")


if __name__ == "__main__":
    unittest.main()
