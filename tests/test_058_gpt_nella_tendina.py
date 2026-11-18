"""058 (richiesta utente 17/11 05:04): nella tendina «Online» la voce GPT è il GPT dal browser:
collegato / non collegato con «Collega», nessuna chiave, nessun testo sulla quota di Codex."""
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest import mock

import menu_modelli
import servizi_online as so

ROOT = Path(__file__).resolve().parents[1]
GPT = "chatgpt_account"


def _testi(widget):
    out = []
    for child in widget.winfo_children():
        try:
            out.append(str(child.cget("text")))
        except tk.TclError:
            pass
        out += _testi(child)
    return out


class DescrizioneTests(unittest.TestCase):
    def test_il_servizio_non_e_a_chiave(self):
        service = so.PER_ID[GPT]
        self.assertEqual(service.tipo, "account")
        self.assertEqual(service.chiavi, "")
        blocco = (service.limite + " " + " ".join(service.passi) + " " + service.uso).lower()
        self.assertIn("browser", blocco)
        self.assertIn("collega", blocco)
        self.assertNotIn("codex", blocco)
        self.assertNotIn("quota", blocco)

    def test_l_aiuto_chiavi_non_manda_a_cercare_una_chiave_per_gpt(self):
        testo = so.aiuto_chiavi()
        blocco = testo.split("CHATGPT (TUO ACCOUNT)")[1].split("\n\n")[0]
        self.assertNotIn("Pagina della chiave", blocco)

    def test_in_uso_conta_anche_il_gpt_collegato(self):
        class SenzaChiavi:
            def presente(self, _):
                return False
        settings = {"ordine": [GPT, "groq"], "attivi": [GPT]}
        self.assertIsNone(menu_modelli.servizio_in_uso(settings, SenzaChiavi()))
        self.assertEqual(menu_modelli.servizio_in_uso(settings, SenzaChiavi(), lambda i: i == GPT), GPT)

    def test_collega_e_cablato_in_jarvis(self):
        src = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn("on_connect=lambda: collega_gpt()", src)
        self.assertIn("collega=lambda: collega_gpt()", src)
        self.assertIn("def collega_gpt()", src)


class NienteDoppioniTests(unittest.TestCase):
    """Decisione utente 04:06: tutti i servizi online stanno in UN posto solo."""

    def test_la_pagina_gpt_dal_browser_non_esiste_piu_nel_menu_impostazioni(self):
        import impostazioni_menu as im
        voci = [voce for _titolo, (_cat, voce) in im.MAPPA]
        self.assertNotIn("GPT dal browser", voci)
        self.assertEqual(len(voci), len(set(voci)))                  # nessuna voce ripetuta
        self.assertEqual(len([t for t, _ in im.MAPPA]), len({t for t, _ in im.MAPPA}))
        self.assertEqual(sum(1 for _t, (c, _v) in im.MAPPA if c == "Modelli" and "ervizi" in _v), 2)

    def test_il_collegamento_gpt_sta_dentro_servizi_online(self):
        src = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn("gpt_panel = ttk.LabelFrame(servizi_online_box,", src)
        self.assertNotIn('text="Connessione ChatGPT"', src)
        self.assertIn("Autorizzazioni GPT per funzione", src)
        self.assertEqual(src.count('text="Connetti ChatGPT"'), 1)
        self.assertEqual(src.count('text="Scollega account"'), 1)

    def test_i_servizi_hanno_nomi_e_id_unici(self):
        self.assertEqual(len({s.id for s in so.SERVIZI}), len(so.SERVIZI))
        self.assertEqual(len({s.nome for s in so.SERVIZI}), len(so.SERVIZI))
        self.assertEqual([s.id for s in so.SERVIZI].count(GPT), 1)


class TendinaTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        self.root.withdraw()
        self.folder = tempfile.TemporaryDirectory()
        self.dir = Path(self.folder.name)
        self.patch = mock.patch.object(so, "_cartella", lambda: self.dir)
        self.patch.start()
        self.saved = dict(so.ACCOUNT)
        self.keys = so.Chiavi(self.dir / "k.keys", protect=lambda v, e: v[::-1])
        self.button = tk.Button(self.root, text="Online ▾")
        self.button.pack()
        self.collegato = []
        self.menu = menu_modelli.MenuModelli(self.root, self.button, open_settings=lambda: None,
                                             open_url=lambda u: None, keys=self.keys,
                                             on_connect=lambda: self.collegato.append(1))

    def tearDown(self):
        self.menu.close()
        so.ACCOUNT.update(self.saved)
        self.patch.stop()
        self.root.destroy()
        self.folder.cleanup()

    def _riga_gpt(self):
        self.menu.toggle()
        testi = _testi(self.menu.popup)
        self.assertIn("ChatGPT (tuo account)", " ".join(testi))
        return testi

    def test_non_collegato_mostra_collega_e_non_la_chiave(self):
        so.ACCOUNT.update(pronto=lambda: False)
        testi = self._riga_gpt()
        self.assertIn("non collegato", testi)
        self.assertIn("Collega", testi)
        blocco = " ".join(t for t in testi if "ChatGPT" in t or t in ("non collegato", "Collega"))
        self.assertNotIn("manca la chiave", blocco)
        self.assertFalse([t for t in testi if "Codex" in t])

    def test_la_voce_gpt_compare_una_volta_sola(self):
        so.ACCOUNT.update(pronto=lambda: True)
        testi = self._riga_gpt()
        self.assertEqual(sum(1 for t in testi if t.startswith("ChatGPT (tuo account)")), 1)
        self.assertEqual(len([t for t in testi if t.startswith("ChatGPT")]), 1)

    def test_collegato_non_mostra_il_pulsante(self):
        so.ACCOUNT.update(pronto=lambda: True)
        testi = self._riga_gpt()
        self.assertIn("collegato", testi)
        self.assertNotIn("Collega", testi)
        self.assertNotIn("non collegato", testi)


if __name__ == "__main__":
    unittest.main()
