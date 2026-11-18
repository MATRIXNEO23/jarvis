"""058 (04:22): «Modello ▾» e «Potenza ▾» accanto alla casella della chat. La catena non cambia:
il selettore decide solo quale servizio online usare e con quale potenza."""
import tempfile
import tkinter as tk
import unittest
import urllib.error
from pathlib import Path
from tkinter import ttk

import servizi_online as so

ROOT = Path(__file__).resolve().parents[1]


def _settings(**extra):
    base = {"ordine": ["gemini", "groq", "openrouter"], "attivi": ["gemini", "groq", "openrouter"],
            "modelli": {}, "limiti": {}, "usa_sempre": False, "proponi_lunghe": True,
            "modello_chat": "auto", "potenza": "auto"}
    base.update(extra)
    return base


def _keys():
    keys = so.Chiavi(Path(tempfile.mkdtemp()) / "k.keys", protect=lambda v, e: v[::-1])
    for i in ("gemini", "groq", "openrouter", "openai", "mistral"):
        keys.salva(i, "k-" + i)
    return keys


class OrdineTests(unittest.TestCase):
    def test_automatico_segue_l_ordine_della_tendina_online(self):
        self.assertEqual(so.ordine_di_prova(_settings()), ["gemini", "groq", "openrouter"])

    def test_il_servizio_scelto_va_per_primo_con_ripiego_sugli_altri(self):
        self.assertEqual(so.ordine_di_prova(_settings(modello_chat="groq")), ["groq", "gemini", "openrouter"])

    def test_un_servizio_non_spuntato_non_conta(self):
        self.assertEqual(so.ordine_di_prova(_settings(modello_chat="groq", attivi=["gemini"])),
                         ["gemini", "groq", "openrouter"])

    def test_chiedi_usa_il_servizio_scelto_e_ripiega_con_la_riga_d_errore(self):
        chiamate, righe = [], []

        def post(url, key, body, timeout):
            chiamate.append(url.split("/")[2])
            if "groq" in url:
                raise urllib.error.HTTPError(url, 429, "x", {}, None)
            return {"choices": [{"message": {"content": "ok"}}]}
        salvato = dict(so.AVVISO)
        so.AVVISO["scrivi"] = righe.append
        try:
            nome, _ = so.chiedi(so.messaggi("ciao"), settings=_settings(modello_chat="groq"),
                                keys=_keys(), post=post)
        finally:
            so.AVVISO.update(salvato)
        self.assertEqual(chiamate[0], "api.groq.com")             # il scelto per primo
        self.assertEqual(nome, "Google Gemini")                    # ripiego sul primo della tendina
        self.assertIn("Groq non ha risposto", righe[0])

    def test_la_catena_offline_e_i_comandi_non_sono_toccati(self):
        src = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn("if submit_gemma_voice(spoken, typed=typed, route=\"locale\") is False:", src)
        self.assertIn('"Vado online? Di\' sì o no."', src)
        self.assertNotIn("Lumi offline", (ROOT / "selettore_chat.py").read_text(encoding="utf-8").split('"""')[2])


class PotenzaTests(unittest.TestCase):
    def corpo(self, service_id, scelta, contesto, modello=None):
        service = so.PER_ID[service_id]
        return so.parametro_potenza(service, modello or service.modello, scelta, contesto)

    def test_auto_e_bassa_in_chat_e_normale_per_i_lavori(self):
        self.assertEqual(self.corpo("gemini", "auto", "chat"), {"reasoning_effort": "low"})
        self.assertEqual(self.corpo("gemini", "auto", "lavoro"), {})

    def test_scelte_esplicite(self):
        self.assertEqual(self.corpo("gemini", "bassa", "lavoro"), {"reasoning_effort": "low"})
        self.assertEqual(self.corpo("gemini", "media", "chat"), {"reasoning_effort": "medium"})
        self.assertEqual(self.corpo("gemini", "alta", "chat"), {"reasoning_effort": "high"})

    def test_openrouter_usa_il_suo_campo(self):
        self.assertEqual(self.corpo("openrouter", "alta", "chat"), {"reasoning": {"effort": "high"}})

    def test_groq_e_openai_solo_con_i_modelli_compatibili(self):
        self.assertEqual(self.corpo("groq", "alta", "chat"), {"reasoning_effort": "high"})       # gpt-oss
        self.assertEqual(self.corpo("groq", "alta", "chat", "llama-3.3-70b-versatile"), {})
        self.assertEqual(self.corpo("openai", "alta", "chat"), {})                               # gpt-4o-mini
        self.assertEqual(self.corpo("openai", "alta", "chat", "gpt-5-mini"), {"reasoning_effort": "high"})

    def test_i_servizi_che_non_lo_supportano_non_ricevono_il_parametro(self):
        for ident in ("mistral", "nvidia", "xai", "anthropic", "chatgpt_account"):
            self.assertEqual(self.corpo(ident, "alta", "chat"), {}, ident)

    def test_il_corpo_inviato_e_la_ripetizione_senza_parametro(self):
        corpi = []

        def post(url, key, body, timeout):
            corpi.append(body)
            if "reasoning_effort" in body:
                raise urllib.error.HTTPError(url, 400, "x", {}, None)     # il servizio lo rifiuta
            return {"choices": [{"message": {"content": "ok"}}]}
        nome, testo = so.chiedi(so.messaggi("ciao"), settings=_settings(attivi=["gemini"]),
                                keys=_keys(), post=post)
        self.assertEqual((nome, testo), ("Google Gemini", "ok"))
        self.assertEqual(len(corpi), 2)
        self.assertEqual(corpi[0]["reasoning_effort"], "low")
        self.assertNotIn("reasoning_effort", corpi[1])

    def test_senza_supporto_non_si_manda_nulla(self):
        corpi = []

        def post(url, key, body, timeout):
            corpi.append(body)
            return {"choices": [{"message": {"content": "ok"}}]}
        so.chiedi(so.messaggi("ciao"), settings=_settings(ordine=["mistral"], attivi=["mistral"],
                                                          potenza="alta"), keys=_keys(), post=post)
        self.assertNotIn("reasoning_effort", corpi[0])
        self.assertNotIn("reasoning", corpi[0])

    def test_i_lavori_dell_orchestratore_con_auto_non_mandano_nulla(self):
        corpi = []

        def post(url, key, body, timeout):
            corpi.append(body)
            return {"choices": [{"message": {"role": "assistant", "content": "ok"}}]}
        so.chiama(so.messaggi("ciao"), settings=_settings(attivi=["gemini"]), keys=_keys(), post=post)
        self.assertNotIn("reasoning_effort", corpi[0])

    def test_le_attese(self):
        self.assertEqual((so.TIMEOUT, so.TIMEOUT_LAVORO), (30, 90))


class SalvataggioTests(unittest.TestCase):
    def test_le_scelte_restano_tra_un_avvio_e_l_altro(self):
        path = Path(tempfile.mkdtemp()) / "s.json"
        data = so.carica_impostazioni(path)
        self.assertEqual((data["modello_chat"], data["potenza"]), ("auto", "auto"))
        data.update(modello_chat="groq", potenza="alta")
        so.salva_impostazioni(data, path)
        again = so.carica_impostazioni(path)
        self.assertEqual((again["modello_chat"], again["potenza"]), ("groq", "alta"))

    def test_valori_non_validi_tornano_ad_auto(self):
        path = Path(tempfile.mkdtemp()) / "s.json"
        path.write_text('{"modello_chat": "inventato", "potenza": "enorme"}', encoding="utf-8")
        data = so.carica_impostazioni(path)
        self.assertEqual((data["modello_chat"], data["potenza"]), ("auto", "auto"))

    def test_il_pannello_non_cancella_le_scelte_dei_selettori(self):
        src = (ROOT / "servizi_online" / "__init__.py").read_text(encoding="utf-8")
        self.assertIn('settings["modello_chat"], settings["potenza"] = fresh["modello_chat"], fresh["potenza"]', src)


class LayoutTests(unittest.TestCase):
    """A 1366x768: tasti alla stessa altezza della casella, senza tagli né sovrapposizioni,
    tendine dentro la finestra."""

    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        self.root.geometry("1366x768+0+0")
        self.cartella = tempfile.TemporaryDirectory()
        self.riga = tk.Frame(self.root, bg="#06192a")
        self.riga.pack(side="bottom", fill="x", padx=10, pady=8)       # la casella è in fondo
        tk.Button(self.riga, text="●", width=2, font=("Segoe UI", 13, "bold")).pack(side="left", padx=(0, 6), ipady=3)
        self.casella = ttk.Entry(self.riga, font=("Segoe UI", 10))
        self.casella.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=6)   # come in jarvis.py
        import selettore_chat
        self.sel = selettore_chat
        self.tasti = selettore_chat.crea_tasti(self.riga)
        tk.Button(self.riga, text="➤", width=2, font=("Segoe UI Symbol", 15)).pack(side="left", padx=(0, 3))
        self.root.update()

    def tearDown(self):
        self.root.destroy()
        self.cartella.cleanup()

    def test_stessa_altezza_nessun_taglio_nessuna_sovrapposizione(self):
        altezza = self.riga.winfo_height()
        for tasto in self.tasti:
            self.assertAlmostEqual(tasto.winfo_height(), altezza, delta=2)
            self.assertTrue(tasto.winfo_ismapped())
            self.assertGreaterEqual(tasto.winfo_reqwidth(), tasto.label.winfo_reqwidth())   # testo intero
            self.assertGreaterEqual(tasto.winfo_width(), tasto.winfo_reqwidth())            # non tagliato
        self.assertLessEqual(self.casella.winfo_height(), altezza)
        elementi = sorted([self.casella, *self.tasti], key=lambda w: w.winfo_x())
        for sinistro, destro in zip(elementi, elementi[1:]):
            self.assertLessEqual(sinistro.winfo_x() + sinistro.winfo_width(), destro.winfo_x())
        ultimo = elementi[-1]
        self.assertLessEqual(ultimo.winfo_x() + ultimo.winfo_width(), self.riga.winfo_width())
        self.assertGreater(self.casella.winfo_width(), 300)                                 # la casella resta larga

    def test_le_tendine_si_aprono_dentro_la_finestra(self):
        path = Path(self.cartella.name) / "s.json"
        tendine = self.sel.collega(self.root, self.tasti, settings_path=path, finestra=self.root)
        sinistra, alto = self.root.winfo_rootx(), self.root.winfo_rooty()
        destra, basso = sinistra + self.root.winfo_width(), alto + self.root.winfo_height()
        for tendina, tasto in zip(tendine, self.tasti):
            tendina.open()
            tendina.popup.update()
            x, y = tendina.popup.winfo_x(), tendina.popup.winfo_y()
            self.assertGreaterEqual(x, sinistra)
            self.assertGreaterEqual(y, alto)
            self.assertLessEqual(x + tendina.popup.winfo_width(), destra)
            self.assertLessEqual(y + tendina.popup.winfo_height(), basso)
            self.assertLessEqual(y + tendina.popup.winfo_height(), tasto.winfo_rooty() + 2)   # sopra il tasto
            tendina.close()

    def test_posiziona_sotto_il_tasto_se_sopra_non_c_e_posto(self):
        tk.Frame(self.root, width=10, height=10).place(x=0, y=0)
        alto = tk.Button(self.root, text="x")
        alto.place(x=1200, y=5)
        popup = tk.Toplevel(self.root)
        tk.Frame(popup, width=300, height=200).pack()
        popup.update_idletasks()
        self.root.update()
        x, y = self.sel.posiziona(popup, alto, self.root)
        self.assertGreaterEqual(y, alto.winfo_rooty() + alto.winfo_height())
        self.assertLessEqual(x + popup.winfo_reqwidth(), self.root.winfo_rootx() + self.root.winfo_width())
        popup.destroy()

    def test_la_scelta_si_salva_e_il_modello_non_spuntato_non_compare(self):
        path = Path(self.cartella.name) / "s.json"
        so.salva_impostazioni(dict(so.carica_impostazioni(path), attivi=["groq"]), path)
        modello, potenza = self.sel.collega(self.root, self.tasti, settings_path=path, finestra=self.root)
        modello.open()
        testi = []

        def raccogli(w):
            for c in w.winfo_children():
                try:
                    testi.append(str(c.cget("text")))
                except tk.TclError:
                    pass
                raccogli(c)
        raccogli(modello.popup)
        etichette = " | ".join(testi)
        self.assertIn("Automatico", etichette)
        self.assertIn("Groq", etichette)
        self.assertNotIn("Google Gemini", etichette)                  # non spuntato
        self.assertNotIn("offline", etichette.lower().split("la catena")[0])   # niente «Lumi offline»
        modello._scegli("modello_chat", "groq")
        potenza._scegli("potenza", "alta")
        saved = so.carica_impostazioni(path)
        self.assertEqual((saved["modello_chat"], saved["potenza"]), ("groq", "alta"))

    def test_cablaggio_in_jarvis(self):
        src = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn('selettore_tasti = __import__("selettore_chat").crea_tasti(selettore_riga, espandi=True)', src)   # 059
        self.assertIn('__import__("selettore_chat").collega(', src)


if __name__ == "__main__":
    unittest.main()
