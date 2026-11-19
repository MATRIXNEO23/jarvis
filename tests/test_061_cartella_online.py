"""061 punto 6, riordino passo 2: la cartella online/ ha gpt_client, gpt_bridge.mjs, installa_gpt,
servizi_online e servizi_ricerca; nessun richiamo ai vecchi percorsi."""
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPOSTATI = ("gpt_client.py", "gpt_bridge.mjs", "installa_gpt.ps1", "installa_gpt.bat",
            "servizi_online", "servizi_ricerca")
VECCHI = (re.compile(r"^\s*(?:from|import)\s+(?:servizi_online|servizi_ricerca|gpt_client)\b", re.M),
          re.compile(r"__import__\(\s*[\"'](?:servizi_online|servizi_ricerca|gpt_client)[\"']\s*\)"),
          re.compile(r"patch(?:\.object)?\(\s*[\"'](?:servizi_online|servizi_ricerca)\."))


class CartellaOnlineTest(unittest.TestCase):
    def test_i_file_stanno_in_online_e_non_nella_radice(self):
        for nome in SPOSTATI:
            self.assertTrue((ROOT / "online" / nome).exists(), nome)
            self.assertFalse((ROOT / nome).exists(), nome)

    def test_i_pacchetti_si_importano_dal_nuovo_posto(self):
        from online import gpt_client, servizi_online, servizi_ricerca
        import online
        self.assertIs(__import__("online").servizi_online, servizi_online)
        self.assertTrue(hasattr(gpt_client, "GPTClient"))
        self.assertEqual(servizi_ricerca.PER_ID["tavily"].id, "tavily")
        self.assertIn("chatgpt_account", servizi_online.PER_ID)
        self.assertEqual(Path(gpt_client.__file__).parent, ROOT / "online")

    def test_il_ponte_trova_gpt_bridge_nella_sua_cartella(self):
        from online.gpt_client import GPTClient
        self.assertTrue((GPTClient().app_dir / "gpt_bridge.mjs").is_file())

    def test_nessun_richiamo_ai_vecchi_percorsi(self):
        trovati = []
        for nome in subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines():
            if not nome.endswith((".py", ".yml", ".mjs", ".bat", ".ps1")) or nome.startswith(("docs/", "audit/")):
                continue
            if nome == "tests/test_061_cartella_online.py":
                continue
            testo = (ROOT / nome).read_text(encoding="utf-8", errors="ignore")
            for modello in VECCHI:
                if modello.search(testo):
                    trovati.append((nome, modello.pattern[:30]))
            for vecchio in ("node --check gpt_bridge.mjs", ".\\installa_gpt.ps1", "'installa_gpt.ps1'"):
                if vecchio in testo:
                    trovati.append((nome, vecchio))
        self.assertEqual(trovati, [])

    def test_i_richiami_fuori_dai_moduli_sono_stati_aggiornati(self):
        self.assertIn('"online" / "gpt_bridge.mjs"', (ROOT / "jarvis.py").read_text(encoding="utf-8"))
        self.assertIn("online/installa_gpt.ps1", (ROOT / "componenti" / "catalog.py").read_text(encoding="utf-8"))
        self.assertIn("online/gpt_client.py", (ROOT / "self_diagnostics.py").read_text(encoding="utf-8"))
        tests = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
        self.assertIn("node --check online/gpt_bridge.mjs", tests)
        self.assertIn("online/installa_gpt.ps1", tests)
        smoke = (ROOT / ".github" / "workflows" / "gpt-smoke.yml").read_text(encoding="utf-8")
        self.assertIn("online/gpt_bridge.mjs", smoke)

    def test_il_pacchetto_prende_online_perche_usa_i_file_di_git(self):
        from tools import build_jarvis_f5_candidate as build
        for nome in ("online/gpt_client.py", "online/gpt_bridge.mjs", "online/installa_gpt.bat",
                     "online/servizi_online/__init__.py", "online/servizi_ricerca/__init__.py"):
            self.assertTrue(build.include(Path(nome)), nome)


if __name__ == "__main__":
    unittest.main()
