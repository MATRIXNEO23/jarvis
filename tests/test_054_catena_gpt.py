"""054: catena online gratuiti, poi «Uso GPT?» (sì/no senza finestre), poi gli altri modelli;
«cerca online» senza chiave Tavily; «approfondisci» senza «online» resta a Gemma."""
import ast
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import servizi_online
import servizi_ricerca as sr

ROOT = Path(__file__).resolve().parents[1]
CATENA = ("start_conversation_gpt", "conversation_chain", "local_after_gpt", "offer_gpt", "resume_gpt", "send_to_gpt")


def _funzioni(*names):
    tree = ast.parse((ROOT / "jarvis.py").read_text(encoding="utf-8"))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    return [n for n in main.body if isinstance(n, ast.FunctionDef) and n.name in names]


def _env(**extra):
    env = dict(closing=False, voice_mode=SimpleNamespace(get=lambda: "conversation"),
               GPT_CONVERSATION="conversation", CONTINUOUS="continuous",
               PUSH_TO_TALK="premi_per_parlare", gpt_enabled=SimpleNamespace(get=lambda: True),
               active_gpt=False, busy_gpt=False, try_self_diagnostic=mock.Mock(return_value=False),
               submit_gemma_voice=mock.Mock(return_value=True), run_gpt=mock.Mock(return_value=True),
               documents=SimpleNamespace(current=None), conversation_epoch=1,
               current_capability_snapshot=lambda _: {"telegram_voice_send": False},
               build_conversation_prompt=lambda *a, **k: "prompt",
               recent_memory_for_gpt=lambda _: "", capability_status_prompt=lambda _: "",
               active_addon_actions=lambda: (), ConversationRejected=ValueError,
               write_line=mock.Mock(), speak_result=mock.Mock())
    env.update(extra)
    module = ast.Module(body=_funzioni(*CATENA), type_ignores=[])
    exec(compile(module, "catena", "exec"), env)
    return env


def _avvia(env, testo, online):
    with mock.patch("servizi_online.disponibili", return_value=online), \
            mock.patch("intent_normalizer.before_model", return_value=False), \
            mock.patch("richiamo.risposta_di_lumi", return_value=None), \
            mock.patch("model_gate.enabled", return_value=True):
        env["start_conversation_gpt"](testo)


class GptNonCollegatoTests(unittest.TestCase):
    def test_with_online_available_the_request_reaches_online_not_gpt(self):
        env = _env(active_gpt=False)
        _avvia(env, "scrivimi uno script Python che somma due numeri", True)
        env["submit_gemma_voice"].assert_called_once_with(
            "scrivimi uno script Python che somma due numeri", typed=False, route="online")
        env["run_gpt"].assert_not_called()

    def test_without_online_and_without_gpt_the_question_goes_to_the_local_model_with_a_notice(self):
        env = _env(active_gpt=False)
        _avvia(env, "che cos'è la fotosintesi", False)
        env["submit_gemma_voice"].assert_called_once_with(
            "che cos'è la fotosintesi", typed=False, route="locale")
        self.assertIn("non collegato", env["write_line"].call_args_list[0].args[0])
        env["run_gpt"].assert_not_called()

    def test_a_script_with_nothing_available_gets_a_clear_message_never_silence(self):
        env = _env(active_gpt=False)
        _avvia(env, "scrivimi uno script Python", False)
        env["submit_gemma_voice"].assert_not_called()
        env["speak_result"].assert_called_once()
        self.assertTrue(any("script" in c.args[0] for c in env["write_line"].call_args_list))

    def test_local_model_busy_gives_a_message(self):
        env = _env(active_gpt=False, submit_gemma_voice=mock.Mock(return_value=False))
        _avvia(env, "dimmi una storia", False)
        env["speak_result"].assert_called_once()


class GptCollegatoTests(unittest.TestCase):
    def test_connected_gpt_still_tries_free_online_first(self):
        env = _env(active_gpt=True)
        _avvia(env, "spiegami la relatività", True)
        env["submit_gemma_voice"].assert_called_once_with("spiegami la relatività", typed=False, route="online")
        env["run_gpt"].assert_not_called()

    def test_without_online_gpt_is_asked_with_the_pending_yes_no_and_no_dialog(self):
        env = _env(active_gpt=True)
        with mock.patch("lumi_comandi.chiedi") as chiedi:
            _avvia(env, "spiegami la relatività", False)
        chiedi.assert_called_once()
        self.assertEqual(chiedi.call_args.args[0], "gpt_yes")
        self.assertIn("Uso GPT", chiedi.call_args.args[1])
        self.assertEqual(chiedi.call_args.kwargs["no_action"], "gpt_no")
        env["run_gpt"].assert_not_called()

    def test_yes_sends_to_gpt_and_no_goes_to_the_local_model(self):
        env = _env(active_gpt=True)
        with mock.patch("lumi_comandi.chiedi"):
            _avvia(env, "spiegami la relatività", False)
        env["resume_gpt"](True)
        env["run_gpt"].assert_called_once()
        self.assertTrue(env["run_gpt"].call_args.kwargs["consent_granted"])
        env["submit_gemma_voice"].assert_not_called()
        env = _env(active_gpt=True)
        with mock.patch("lumi_comandi.chiedi"):
            _avvia(env, "spiegami la relatività", False)
        env["resume_gpt"](False)
        env["run_gpt"].assert_not_called()
        env["submit_gemma_voice"].assert_called_once_with(
            "spiegami la relatività", typed=False, route="locale")

    def test_no_dialog_window_in_the_chain(self):
        for function in _funzioni(*CATENA):
            names = {n.id for n in ast.walk(function) if isinstance(n, ast.Name)}
            names |= {n.attr for n in ast.walk(function) if isinstance(n, ast.Attribute)}
            for forbidden in ("messagebox", "askyesno", "Toplevel", "simpledialog",
                              "confirm_gpt_inference"):
                self.assertNotIn(forbidden, names, function.name)

    def test_online_failure_moves_on_to_the_gpt_question_then_the_other_models(self):
        source = (ROOT / "local_model" / "conversazione_lumi.py").read_text(encoding="utf-8")
        self.assertIn('("online_gpt", (spoken, typed, note), voice_epoch)', source)
        self.assertIn('run_action("gpt_offer")', source)
        self.assertIn('"gpt_yes": lambda: resume_gpt(True)',
                      (ROOT / "jarvis.py").read_text(encoding="utf-8"))

    def test_gpt_failure_after_sending_falls_to_the_local_model(self):
        source = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn('local_after_gpt(original_phrase, channel == "typed_conversation")', source)


class RicercaSenzaChiaveTests(unittest.TestCase):
    def _lumi_ricerca(self, ricerca_mod):
        class Sync:
            def __init__(self, target=None, **kw):
                self.target = target

            def start(self):
                self.target()
        env = dict(write_line=mock.Mock(), speak_result=mock.Mock(),
                   root=SimpleNamespace(after=lambda ms, fn: fn(), clipboard_clear=mock.Mock(),
                                        clipboard_append=mock.Mock()),
                   threading=SimpleNamespace(Thread=Sync), tk=SimpleNamespace(TclError=OSError))
        module = ast.Module(body=_funzioni("lumi_ricerca"), type_ignores=[])
        exec(compile(module, "ricerca", "exec"), env)
        return env

    def test_without_tavily_key_lumi_answers_at_once_with_the_link(self):
        env = self._lumi_ricerca(sr)
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(sr, "chiavi", lambda path=None: sr.Chiavi(
                    path=Path(tmp) / "k", protect=lambda v, e: v, ids=sr.PER_ID)), \
                mock.patch.object(sr, "carica_impostazioni",
                                  return_value={"ordine": ["tavily"], "attivi": ["tavily"]}):
            self.assertTrue(env["lumi_ricerca"]("cerca online meteo Roma domani"))
        text = env["write_line"].call_args.args[0]
        self.assertIn("https://app.tavily.com", text)
        self.assertIn("chiave", text)
        env["speak_result"].assert_called_once()

    def test_empty_decrypted_key_counts_as_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            keys = sr.Chiavi(path=Path(tmp) / "k", protect=lambda v, e: v, ids=sr.PER_ID)
            (Path(tmp) / "k").write_text('{"tavily": ""}', encoding="utf-8")
            self.assertEqual(sr.pronti({"ordine": ["tavily"], "attivi": ["tavily"]}, keys), [])

    def test_with_key_summary_and_clickable_sources_go_straight_to_the_chat(self):
        env = self._lumi_ricerca(sr)
        risultato = sr.Risultato("Domani sole a Roma.", (("Meteo", "https://m.example/roma"),),
                                 ("Previsioni per domani",))
        with mock.patch.object(sr, "pronti", return_value=[object()]), \
                mock.patch.object(sr, "carica_impostazioni",
                                  return_value={"ordine": ["tavily"], "attivi": ["tavily"]}), \
                mock.patch.object(sr, "cerca", return_value=("Tavily", risultato)), \
                mock.patch("file_access.ui.show_results") as window:
            self.assertTrue(env["lumi_ricerca"]("cerca online meteo Roma domani"))
        window.assert_not_called()                      # niente finestra risultati separata
        chat = env["write_line"].call_args.args[0]
        self.assertIn("Domani sole a Roma.", chat.split("Fonti:")[0])
        self.assertIn("1. [Meteo](https://m.example/roma)", chat)
        self.assertIn("    Previsioni per domani", chat)
        env["speak_result"].assert_called_once()

    def test_unexpected_error_is_reported_in_chat_never_silence(self):
        env = self._lumi_ricerca(sr)
        with mock.patch.object(sr, "pronti", return_value=[object()]), \
                mock.patch.object(sr, "cerca", side_effect=RuntimeError("x")):
            env["lumi_ricerca"]("cerca online meteo Roma domani")
        self.assertTrue(any("Nessun servizio" in c.args[0] for c in env["write_line"].call_args_list))
        env["speak_result"].assert_called_once()

    def test_the_gpt_chain_is_not_reached_by_cerca_online(self):
        calls = []
        import lumi_comandi
        lumi_comandi.register({"ricerca": lambda spoken: calls.append(spoken) or True}, lambda: False)
        self.assertTrue(lumi_comandi.handle_text("cerca online meteo Roma domani",
                                                 lambda t: None, lambda t: None))
        self.assertEqual(calls, ["cerca online meteo Roma domani"])


class ApprofondisciTests(unittest.TestCase):
    def test_only_with_online_it_goes_to_the_search_services(self):
        self.assertTrue(sr.approfondisci_locale("approfondisci la fotosintesi"))
        self.assertTrue(sr.approfondisci_locale("Lumi, approfondisci la fotosintesi"))
        self.assertFalse(sr.approfondisci_locale("approfondisci online la fotosintesi"))
        self.assertEqual(sr.parse("approfondisci la fotosintesi"), None)
        self.assertEqual(sr.parse("approfondisci online la fotosintesi"),
                         ("approfondisci", "la fotosintesi"))

    def test_approfondisci_without_online_answers_gemma_even_with_online_ready(self):
        env = _env(active_gpt=True)
        _avvia(env, "approfondisci la fotosintesi", True)
        env["submit_gemma_voice"].assert_called_once_with("approfondisci la fotosintesi",
                                                         typed=False, route="locale")
        env["run_gpt"].assert_not_called()

    def test_submit_gemma_voice_keeps_approfondisci_local(self):
        source = (ROOT / "local_model" / "conversazione_lumi.py").read_text(encoding="utf-8")
        self.assertIn('approfondisci_locale(spoken)', source)


if __name__ == "__main__":
    unittest.main()
