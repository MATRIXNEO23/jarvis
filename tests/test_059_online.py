"""059: attese online (30 s in chat), risposte non tagliate, prova di un servizio con DNS/TLS/risposta,
pacchetto con la sola cartella nell'artifact."""
import unittest
from pathlib import Path

import orchestratore as orch
import servizi_online as so

ROOT = Path(__file__).resolve().parents[1]


class AtteseTest(unittest.TestCase):
    def test_la_chat_aspetta_30_secondi_il_lavoro_90(self):
        viste = []
        orig = so.chiama
        passi = [{"role": "assistant", "content": "", "tool_calls": [
            {"id": "1", "function": {"name": "elenca", "arguments": "{}"}}], "_avviso": ""},
            {"role": "assistant", "content": "fatto", "_avviso": ""}]

        def finta(messages, tools=None, only=None, timeout=None, **_k):
            viste.append(timeout)
            return "gemini", "Google Gemini", passi.pop(0)
        so.chiama = finta
        try:
            class Strumenti:
                folders = []
                def esegui(self, nome, args): return "ok"
                def ask(self, q): return True
            orch.rispondi("domanda", tools=Strumenti())
        finally:
            so.chiama = orig
        self.assertEqual(viste, [so.TIMEOUT, so.TIMEOUT_LAVORO])
        self.assertEqual((so.TIMEOUT, so.TIMEOUT_LAVORO), (30, 90))

    def test_risposte_non_tagliate(self):
        self.assertGreaterEqual(so.MAX_RISPOSTA, 8000)


class ProvaReteTest(unittest.TestCase):
    service = so.PER_ID["gemini"]

    def test_tutto_ok(self):
        bene, testo = so.prova_rete(self.service, dns=lambda h: True, connetti=lambda h: True)
        self.assertTrue(bene)
        self.assertIn("DNS ok", testo)

    def test_si_ferma_al_dns(self):
        def dns(host):
            raise OSError("nome sconosciuto")
        bene, testo = so.prova_rete(self.service, dns=dns, connetti=lambda h: True)
        self.assertFalse(bene)
        self.assertIn("si ferma al DNS", testo)

    def test_si_ferma_alla_connessione_o_tls(self):
        def connetti(host):
            raise TimeoutError("timed out")
        import urllib.request
        orig = urllib.request.getproxies
        urllib.request.getproxies = lambda: {}
        try:
            bene, testo = so.prova_rete(self.service, dns=lambda h: True, connetti=connetti)
        finally:
            urllib.request.getproxies = orig
        self.assertFalse(bene)
        self.assertIn("connessione o al TLS", testo)

    def test_la_prova_dell_impostazione_usa_le_tre_fasi(self):
        src = (ROOT / "servizi_online" / "__init__.py").read_text(encoding="utf-8")
        corpo = src[src.index("    def test(service):"):src.index("    def move(")]
        self.assertIn("prova_rete(service)", corpo)
        self.assertIn("risposta ok in", corpo)


class PacchettoTest(unittest.TestCase):
    def test_l_artifact_carica_la_cartella(self):
        wf = (ROOT / ".github" / "workflows" / "f5n-koboldcpp-native-dll-windows.yml").read_text(encoding="utf-8")
        self.assertIn("--number 060", wf)
        self.assertIn("name: lumi-060-prova-candidate", wf)
        self.assertIn("path: dist/artifact", wf)
        builder = (ROOT / "tools" / "build_jarvis_f5_candidate.py").read_text(encoding="utf-8")
        self.assertIn('"artifact" / f"Lumi-{label}-PROVA"', builder)


if __name__ == "__main__":
    unittest.main()
