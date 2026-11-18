"""056 A, C3, E: Basso consumo (offline subito, online solo con il «sì»), Veloce, approfondisci,
«apri il N» e la spunta che non si perde. Esecuzione di funzioni reali di jarvis.py via AST."""
import ast
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import risposte
import servizi_online as so
import settings as settings_module

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "jarvis.py").read_text(encoding="utf-8")
CATENA = ("conversation_chain", "local_after_gpt", "fast_mode", "ask_online", "deepen_prompt", "submit_deepen", "deepen_last")


def _funzioni(*names):
    main = next(n for n in ast.parse(SRC).body if isinstance(n, ast.FunctionDef) and n.name == "main")
    return [n for n in main.body if isinstance(n, ast.FunctionDef) and n.name in names]


def _env(modalita, last="", **extra):
    env = dict(settings={"modalita": modalita}, last_question=[last],
               chat_bubbles=SimpleNamespace(ultimo_scambio=(last, "risposta precedente") if last else None),
               submit_gemma_voice=mock.Mock(return_value=True),
               write_line=mock.Mock(), speak_result=mock.Mock(),
               lumi_ricerca=mock.Mock(return_value=False))
    env.update(extra)
    exec(compile(ast.Module(body=_funzioni(*CATENA), type_ignores=[]), "catena056", "exec"), env)
    return env


class BassoConsumoTests(unittest.TestCase):
    def test_domanda_normale_va_all_offline_anche_con_online_pronto(self):
        env = _env("basso_consumo")
        with mock.patch("servizi_online.disponibili", return_value=True), \
                mock.patch("lumi_comandi.chiedi") as chiedi:
            env["conversation_chain"]("chi ha scritto i Promessi sposi?", False)
        env["submit_gemma_voice"].assert_called_once_with(
            "chi ha scritto i Promessi sposi?", typed=False, route="locale")
        chiedi.assert_not_called()

    def test_script_chiede_prima_di_andare_online(self):
        env = _env("basso_consumo")
        with mock.patch("servizi_online.disponibili", return_value=True), \
                mock.patch("lumi_comandi.chiedi") as chiedi:
            env["conversation_chain"]("scrivimi uno script che rinomina i file", True)
        self.assertEqual(chiedi.call_args.args[0], "online_yes")
        self.assertIn("Vado online?", chiedi.call_args.args[1])
        self.assertEqual(chiedi.call_args.kwargs["no_action"], "online_no")
        env["submit_gemma_voice"].assert_not_called()
        self.assertEqual(so.IN_ATTESA["domanda"][:2], ("scrivimi uno script che rinomina i file", True))

    def test_approfondisci_chiede_conferma_e_usa_l_ultima_domanda(self):
        env = _env("basso_consumo", last="la fotosintesi")
        with mock.patch("servizi_online.disponibili", return_value=True), \
                mock.patch("lumi_comandi.chiedi") as chiedi:
            env["conversation_chain"]("approfondisci", False)
        self.assertEqual(chiedi.call_args.args[0], "online_yes")
        prompt = so.IN_ATTESA["domanda"][0]            # 057: domanda + risposta offline + istruzione
        self.assertNotIn("la fotosintesi", prompt)      # 058: solo la risposta, mai la domanda
        self.assertIn("risposta precedente", prompt)
        self.assertIn("più a fondo", prompt)
        self.assertEqual(so.IN_ATTESA["domanda"][1:], (True, True))
        env["submit_gemma_voice"].assert_not_called()

    def test_approfondisci_senza_domanda_lo_dice(self):
        env = _env("basso_consumo", last="")
        env["conversation_chain"]("approfondisci", False)
        self.assertIn("Cosa vuoi approfondire?", env["write_line"].call_args.args[0])
        env["speak_result"].assert_called_once()
        env["submit_gemma_voice"].assert_not_called()

    def test_senza_servizi_online_lo_dice_e_non_chiede(self):
        env = _env("basso_consumo", last="x")
        with mock.patch("servizi_online.disponibili", return_value=False), \
                mock.patch("lumi_comandi.chiedi") as chiedi:
            env["conversation_chain"]("approfondisci", False)
        chiedi.assert_not_called()
        self.assertIn("nessun servizio online", env["write_line"].call_args.args[0].lower())


class VeloceTests(unittest.TestCase):
    def test_veloce_va_online_senza_conferma_e_il_locale_e_di_riserva(self):
        env = _env("veloce")
        with mock.patch("servizi_online.disponibili", return_value=True), \
                mock.patch("lumi_comandi.chiedi") as chiedi:
            env["conversation_chain"]("spiegami la relatività", False)
        env["submit_gemma_voice"].assert_called_once_with("spiegami la relatività", typed=False, route="online")
        chiedi.assert_not_called()
        env = _env("veloce")
        with mock.patch("servizi_online.disponibili", return_value=False):
            env["conversation_chain"]("spiegami la relatività", False)
        env["submit_gemma_voice"].assert_called_once_with("spiegami la relatività", typed=False, route="locale")

    def test_veloce_approfondisci_va_diretto_online(self):
        env = _env("veloce", last="la luna")
        with mock.patch("lumi_comandi.chiedi") as chiedi:
            env["conversation_chain"]("approfondisci", False)
        chiamata = env["submit_gemma_voice"].call_args
        self.assertEqual(chiamata.kwargs, {"typed": True, "route": "online"})
        self.assertNotIn("la luna", chiamata.args[0])
        self.assertIn("risposta precedente", chiamata.args[0])
        chiedi.assert_not_called()


class RispostaNoTests(unittest.TestCase):
    def test_no_ad_approfondisci_resta_offline_e_no_al_codice_va_al_locale(self):
        fn = _funzioni("resume_online_question")
        env = dict(submit_gemma_voice=mock.Mock(), write_line=mock.Mock())
        exec(compile(ast.Module(body=fn, type_ignores=[]), "resume", "exec"), env)
        so.IN_ATTESA["domanda"] = ("la luna", False, True)
        env["resume_online_question"]("locale")
        env["submit_gemma_voice"].assert_not_called()
        so.IN_ATTESA["domanda"] = ("scrivi uno script", True, False)
        env["resume_online_question"]("locale")
        env["submit_gemma_voice"].assert_called_once_with("scrivi uno script", typed=True, route="locale")

    def test_il_motore_non_forza_piu_l_online_con_route_esplicita(self):
        source = (ROOT / "local_model" / "conversazione_lumi.py").read_text(encoding="utf-8")
        self.assertIn('if orig_route is None and __import__("servizi_online").richiesta_codice(spoken):', source)
        self.assertNotIn("Catena 17/11", source)

    def test_pulsante_approfondisci_sotto_la_risposta(self):
        bolle = (ROOT / "chat_bolle.py").read_text(encoding="utf-8")
        self.assertIn('text="Approfondisci"', bolle)
        self.assertIn("deepen_last(True, question, answer)", SRC)
        self.assertIn("lambda q=question, a=answer: self.deepen(q, a)", bolle)

    def test_pulsante_usa_domanda_e_risposta_della_bolla(self):
        env = _env("veloce", last="")
        env["deepen_last"](True, "perché il cielo è blu?", "Per la diffusione della luce.")
        arg = env["submit_gemma_voice"].call_args.args[0]
        self.assertNotIn("perché il cielo è blu?", arg)
        self.assertIn("Per la diffusione della luce.", arg)


class ApriIlNumeroTests(unittest.TestCase):
    def test_numero_con_apri(self):
        for frase, n in (("apri il 2", 2), ("apri il secondo", 2), ("apri 3", 3), ("il 2", 2)):
            self.assertEqual(risposte.number_of(frase), n, frase)
        self.assertIsNone(risposte.number_of("apri la porta"))

    def test_apre_solo_http_dell_ultima_ricerca_senza_conferma(self):
        env = dict(ricerca_risultati=[["https://a.it", "javascript:x", "http://b.it"]],
                   write_line=mock.Mock(), speak_result=mock.Mock())
        exec(compile(ast.Module(body=_funzioni("open_search_result"), type_ignores=[]), "o", "exec"), env)
        with mock.patch("webbrowser.open") as apri:
            env["open_search_result"](1)
            env["open_search_result"](2)
            env["open_search_result"](9)
        apri.assert_called_once_with("https://a.it")


class SpuntaNonSiPerdeTests(unittest.TestCase):
    def test_il_pannello_applica_solo_le_sue_modifiche(self):
        ordine = ["gemini", "groq", "mistral"]
        # il pannello era stato disegnato con Mistral spuntato; la tendina l'ha spento dopo
        base = {"mistral"}
        voluti = {"gemini": False, "groq": False, "mistral": True}   # spunte vecchie del pannello
        self.assertEqual(so.unisci_attivi([], ordine, voluti, base), [])
        # una spunta cambiata davvero nel pannello viene applicata
        voluti["groq"] = True
        self.assertEqual(so.unisci_attivi([], ordine, voluti, base), ["groq"])
        # e quella messa nella tendina nel frattempo resta
        self.assertEqual(so.unisci_attivi(["gemini"], ordine, voluti, base), ["gemini", "groq"])

    def test_il_salvataggio_del_pannello_rilegge_il_file(self):
        for modulo in ("servizi_online", "servizi_ricerca"):
            testo = (ROOT / modulo / "__init__.py").read_text(encoding="utf-8")
            self.assertIn("fresh = carica_impostazioni()", testo, modulo)

    def test_errore_di_salvataggio_della_tendina_non_e_nascosto(self):
        with tempfile.TemporaryDirectory() as tmp:
            avvisi = []
            import menu_tendine as menu_modelli
            menu = object.__new__(menu_modelli.MenuModelli)
            menu.so = so
            menu.settings_path = Path(tmp)               # una cartella: scrivere fallisce
            menu.notify = avvisi.append
            menu.button = SimpleNamespace(configure=lambda **k: None)
            menu.refresh_button = lambda: None
            menu._save({"ordine": ["gemini"], "attivi": []})
            self.assertTrue(avvisi and "non salvata" in avvisi[0])


class ModalitaImpostazioneTests(unittest.TestCase):
    def test_salvata_e_riletta_e_valore_strano_torna_basso_consumo(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            data = settings_module.load_settings(path)
            self.assertEqual(data["modalita"], "basso_consumo")
            data["modalita"] = "veloce"
            settings_module.save_settings(data, path)
            self.assertEqual(settings_module.load_settings(path)["modalita"], "veloce")
            path.write_text(path.read_text(encoding="utf-8").replace("veloce", "turbo"), encoding="utf-8")
            self.assertEqual(settings_module.load_settings(path)["modalita"], "basso_consumo")


if __name__ == "__main__":
    unittest.main()
