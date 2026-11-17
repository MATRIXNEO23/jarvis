"""056b: ogni impostazione compare in un solo posto (nessun doppione tra le pagine)."""
import ast
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JARVIS = (ROOT / "jarvis.py").read_text(encoding="utf-8")


def _calls(source):
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            yield node


def _kw(call, name):
    for k in call.keywords:
        if k.arg == name:
            return k.value
    return None


class NessunDuplicatoTests(unittest.TestCase):
    def test_ogni_finestra_di_impostazioni_ha_un_solo_pulsante(self):
        comandi = Counter()
        for call in _calls(JARVIS):
            if getattr(call.func, "attr", "") == "Button":
                cmd = _kw(call, "command")
                if isinstance(cmd, ast.Name) and cmd.id.startswith("open_"):
                    comandi[cmd.id] += 1
        for nome in ("open_memory_preferences", "open_online_permissions", "open_native_model_settings"):
            self.assertEqual(comandi[nome], 1, nome)

    def test_riquadri_con_titolo_unico(self):
        titoli = Counter()
        for call in _calls(JARVIS):
            if getattr(call.func, "attr", "") == "LabelFrame":
                text = _kw(call, "text")
                if isinstance(text, ast.Constant):
                    titoli[text.value] += 1
        self.assertEqual([t for t, n in titoli.items() if n > 1], [])

    def test_registro_menu_senza_doppioni(self):
        import impostazioni_menu as im
        prefissi = [p for p, _ in im.MAPPA]
        posti = [place for _, place in im.MAPPA]
        self.assertEqual(len(prefissi), len(set(prefissi)))
        self.assertEqual(len(posti), len(set(posti)))

    def test_modelli_offline_una_sola_pagina(self):
        self.assertNotIn("Anteprima multimodello", JARVIS)
        self.assertNotIn("Gemma (sperimentale)", JARVIS)
        self.assertNotIn("open_multimodel_f5_preview", JARVIS)
        self.assertIn('text="Modelli offline"', JARVIS)

    def test_pagina_addon_modello_solo_pulsante(self):
        corpo = next(n for n in ast.walk(ast.parse(JARVIS))
                     if isinstance(n, ast.FunctionDef) and n.name == "build_model_addon_section")
        bottoni = [c for c in ast.walk(corpo) if getattr(c.func, "attr", "") == "Button"
                   for c in [c] if isinstance(c, ast.Call)]
        self.assertEqual(len(bottoni), 1)
        self.assertEqual(_kw(bottoni[0], "text").value, "Apri impostazioni modelli")


if __name__ == "__main__":
    unittest.main()
