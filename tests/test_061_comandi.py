"""061 punti 2 e 7 e aggiunta delle 08:19: comandi nuovi o tolti, «aiuto» apre l'aiuto F1,
ogni comando dell'elenco F1 esiste davvero, i comandi tolti non compaiono da nessuna parte."""
import re
import unittest
from pathlib import Path

import command_aliases
import lumi_comandi

ROOT = Path(__file__).resolve().parents[1]
TOLTI = ("passa a GPT", "passa a Gemma", "torna a Gemma", "usa GPT", "model_switch_target", "try_model_switch",
         "brain_online_on", "brain_online_off")
# I comandi dell'elenco F1 (local_help.py) sui modelli: ognuno deve essere davvero riconosciuto.
ELENCO_F1 = {"passa online": "mode_fast", "passa offline": "mode_low",
             "modalità veloce": "mode_fast", "modalità basso consumo": "mode_low",
             "cervello online acceso": "mode_fast", "cervello online spento": "mode_low",
             "cambia modello": "model_choose", "aiuto": "help_open", "comandi": "help_open"}


def sorgenti():
    for path in ROOT.rglob("*"):
        parti = set(path.relative_to(ROOT).parts)
        if parti & {"tests", ".git", "__pycache__", "dist", "audit", "node_modules", "evidence", "prove", "superpowers"}:
            continue
        if path.name in ("HANDOFF-LUMI-CORRENTE.md", "DECISIONI-E-LEZIONI.md", "DECISIONI-RIORDINO-058.md",
                         "PROPOSTA-RIORDINO-058.md", "ARCH-01-F5-CHECKPOINT.md", "CHANGELOG.md"):
            continue
        if path.parts[-2:-1] == ("docs",) and path.suffix == ".md":
            continue                                    # documenti storici delle build passate
        if path.suffix in (".py", ".json", ".md", ".mjs", ".txt", ".html"):
            yield path


class ComandiTest(unittest.TestCase):
    def test_ogni_comando_dell_elenco_f1_e_riconosciuto(self):
        for frase, chiave in ELENCO_F1.items():
            with self.subTest(frase=frase):
                self.assertEqual(lumi_comandi.parse(frase), chiave)
                self.assertEqual(lumi_comandi.parse("Lumi, " + frase), chiave)

    def test_l_elenco_f1_li_nomina_tutti(self):
        guida = (ROOT / "local_help.py").read_text(encoding="utf-8")
        for frase in ("passa online", "passa offline", "modalità veloce", "modalità basso consumo", "cambia modello"):
            self.assertIn(frase, guida)

    def test_il_catalogo_della_personalizzazione_ha_i_comandi_nuovi(self):
        voci = set(command_aliases._FIXED["Modelli e modalità"])
        for frase in ("passa online", "passa offline", "modalità veloce", "modalità basso consumo", "cambia modello"):
            self.assertIn(frase, voci)
            self.assertIn(frase, command_aliases.DESCRIPTIONS)
        self.assertIn("Modelli e modalità", command_aliases.BASE_SECTIONS)
        self.assertNotIn("passa a GPT", voci)

    def test_i_comandi_tolti_non_sono_piu_riconosciuti(self):
        for frase in ("passa a GPT", "passa a Gemma", "torna a Gemma", "usa GPT", "Lumi passa a GPT"):
            self.assertIsNone(lumi_comandi.parse(frase), frase)

    def test_i_comandi_tolti_non_compaiono_da_nessuna_parte(self):
        trovati = []
        for path in sorgenti():
            testo = path.read_text(encoding="utf-8", errors="ignore")
            for parola in TOLTI:
                if parola.casefold() in testo.casefold():
                    trovati.append((str(path.relative_to(ROOT)), parola))
        self.assertEqual(trovati, [])

    def test_la_scheda_e_la_guida_parlano_dei_comandi_nuovi(self):
        import scheda_lumi
        testo = scheda_lumi.scheda(scheda_lumi.fatti(addons=(), local_model="", local_on=True, online=False, mic=""))
        self.assertIn("passa online", testo)
        self.assertIn("aiuto", testo)


class AiutoF1Test(unittest.TestCase):
    def test_aiuto_apre_la_finestra_f1_non_l_elenco_in_chat(self):
        self.assertEqual(lumi_comandi.parse("aiuto"), "help_open")
        self.assertEqual(lumi_comandi.parse("Lumi, apri l'aiuto"), "help_open")
        src = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn('"help_open": lambda: show_help()', src)
        invio = src[src.index("    def send_console_input("):]
        self.assertIn("show_help()", invio[:2500])


if __name__ == "__main__":
    unittest.main()
