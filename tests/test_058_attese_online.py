"""058 (04:16): attesa 30 s in chat e 90 s per i lavori dell'orchestratore; modello di Gemini invariato.
La scelta «Ragionamento» è sospesa (l'utente la sta ridefinendo): qui si prova che NON c'è."""
import inspect
import unittest

import servizi_online as so


class AtteseTests(unittest.TestCase):
    def test_chat_30_secondi_lavori_90(self):
        self.assertEqual(so.TIMEOUT, 30)
        self.assertEqual(so.TIMEOUT_LAVORO, 90)
        self.assertEqual(inspect.signature(so.chiedi).parameters["timeout"].default, 30)
        self.assertEqual(inspect.signature(so.chiama).parameters["timeout"].default, 90)

    def test_gemini_resta_flash_latest(self):
        self.assertEqual(so.PER_ID["gemini"].modello, "gemini-flash-latest")

    def test_nessun_parametro_di_ragionamento_e_mandato(self):
        corpi = []

        def post(url, key, body, timeout):
            corpi.append(body)
            return {"choices": [{"message": {"content": "ok"}}]}
        import tempfile
        from pathlib import Path
        keys = so.Chiavi(Path(tempfile.mkdtemp()) / "k.keys", protect=lambda v, e: v[::-1])
        keys.salva("gemini", "k")
        settings = {"ordine": ["gemini"], "attivi": ["gemini"], "modelli": {}, "limiti": {},
                    "usa_sempre": False, "proponi_lunghe": True}
        so.chiedi(so.messaggi("ciao"), settings=settings, keys=keys, post=post)
        self.assertNotIn("reasoning_effort", corpi[0])
        self.assertNotIn("reasoning", corpi[0])


if __name__ == "__main__":
    unittest.main()
