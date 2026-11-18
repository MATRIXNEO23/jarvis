"""060, passo 1 del riordino: ogni nome pubblico spostato resta importabile dal file nuovo."""
import importlib
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]

NOMI = {
    "chat_testo": ["ROLES", "IDENTITY", "classify", "COLORE", "segmenti", "ha_link", "inserisci",
                   "ChatStream", "STREAM"],
    "menu_tendine": ["BG", "PANEL", "TEXT", "MUTED", "CYAN", "servizio_in_uso", "MenuModelli",
                     "servizio_attivo", "MenuRicerca", "voci", "MenuModello"],
    "dialogue": ["normalized_utterance", "is_short_followup", "is_ambiguous_short_reply",
                 "is_unusable_project_name", "mentions_current_project",
                 "needs_project_clarification", "single_question", "focus_hint",
                 "PendingProjectReference", "DialogueStyle", "choose_dialogue_style",
                 "style_instruction"],
    "action_planner": ["ApprovedPlan", "PlanRejected", "parse_plan", "build_planning_prompt",
                       "run_approved_plan"],
    "window_chrome": ["install_window_chrome", "adatta", "area_utile", "MARGINE_X", "MARGINE_Y",
                      "MINIMO", "GWL_STYLE", "_WindowApi"],
}
VECCHI = ["chat_link", "chat_ruoli", "chat_stream", "menu_modello", "menu_ricerca", "menu_modelli",
          "dialogue_style", "dialogue_focus", "plan_runner", "finestra_adatta"]


class RiordinoTests(unittest.TestCase):
    def test_nomi_pubblici_importabili_dal_file_nuovo(self):
        for modulo, nomi in NOMI.items():
            m = importlib.import_module(modulo)
            for nome in nomi:
                self.assertTrue(hasattr(m, nome), f"{modulo}.{nome} manca")

    def test_stato_stream_unico(self):
        import chat_testo
        self.assertIsInstance(chat_testo.STREAM, chat_testo.ChatStream)
        self.assertIs(importlib.import_module("chat_testo").STREAM, chat_testo.STREAM)

    def test_nessun_richiamo_ai_vecchi_nomi(self):
        pattern = re.compile(r"(?:\bfrom\s+|\bimport\s+|__import__\(\s*[\"'])(%s)\b" % "|".join(VECCHI))
        for p in list(ROOT.glob("*.py")) + list(ROOT.glob("*/*.py")):
            if p.name == Path(__file__).name or "floorplan" in p.parts:
                continue
            for n, riga in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                self.assertIsNone(pattern.search(riga), f"{p.relative_to(ROOT)}:{n} {riga.strip()}")
        for v in VECCHI:
            self.assertFalse((ROOT / (v + ".py")).exists(), v)

    def test_finestra_adatta_senza_windows(self):
        sorgente = (ROOT / "window_chrome.py").read_text(encoding="utf-8")
        self.assertNotRegex(sorgente, r"(?m)^from ctypes import wintypes")
        self.assertNotRegex(sorgente, r"(?m)^(?:from|import) .*\bwin32")

    def test_file_spostati_fuori_dal_pacchetto(self):
        self.assertTrue((ROOT / "docs" / "LEGGIMI_PROVA_TELEGRAM_50.txt").is_file())
        self.assertTrue((ROOT / "docs" / "LEGGIMI-ACCESSO-FILE.txt").is_file())
        self.assertFalse((ROOT / "LEGGIMI_PROVA_TELEGRAM_50.txt").exists())
        self.assertFalse((ROOT / "LEGGIMI-ACCESSO-FILE.txt").exists())
        # il preparatore resta in radice: avvia_lumi.bat lo lancia a ogni avvio
        self.assertTrue((ROOT / "prepara_test_telegram50.py").is_file())


if __name__ == "__main__":
    unittest.main()
