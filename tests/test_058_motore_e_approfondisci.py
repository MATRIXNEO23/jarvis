"""058 (1-3): «approfondisci» solo con l'ultima risposta offline, priorità alta del motore,
contesto del profilo al caricamento."""
import ast
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "jarvis.py").read_text(encoding="utf-8")
NOMI = ("fast_mode", "ask_online", "deepen_prompt", "submit_deepen", "deepen_last")


def _env(modalita, scambio):
    main = next(n for n in ast.parse(SRC).body if isinstance(n, ast.FunctionDef) and n.name == "main")
    body = [n for n in main.body if isinstance(n, ast.FunctionDef) and n.name in NOMI]
    visti = []
    env = dict(settings={"modalita": modalita}, chat_bubbles=SimpleNamespace(ultimo_scambio=scambio),
               write_line=mock.Mock(), speak_result=mock.Mock())
    env["submit_gemma_voice"] = mock.Mock(side_effect=lambda *a, **k: visti.append(
        __import__("local_model.conversazione_lumi", fromlist=["x"]).TU_SCRITTO[0]))
    env["visti"] = visti
    exec(compile(ast.Module(body=body, type_ignores=[]), "deepen058", "exec"), env)
    return env


class ApprofondisciTests(unittest.TestCase):
    def test_online_va_solo_la_risposta_senza_la_domanda(self):
        env = _env("veloce", ("domanda segreta", "risposta offline"))
        env["deepen_last"](False)
        prompt = env["submit_gemma_voice"].call_args.args[0]
        self.assertIn("risposta offline", prompt)
        self.assertNotIn("domanda segreta", prompt)
        self.assertIn("più a fondo", prompt)

    def test_il_testo_online_non_compare_come_messaggio_tu(self):
        env = _env("veloce", ("d", "r"))
        env["deepen_last"](False)
        self.assertEqual(env["visti"], [True])              # flag alzato durante l'invio
        from local_model import conversazione_lumi as cl
        self.assertFalse(cl.TU_SCRITTO[0])                  # e riabbassato dopo
        env["write_line"].assert_not_called()               # da comando il «TU > approfondisci» c'è già

    def test_il_pulsante_scrive_solo_approfondisci(self):
        env = _env("veloce", None)
        env["deepen_last"](True, "d", "r")
        env["write_line"].assert_called_once_with("TU > approfondisci")

    def test_senza_risposta_offline_chiede_cosa(self):
        env = _env("veloce", None)
        env["deepen_last"](False)
        self.assertIn("Cosa vuoi approfondire?", env["write_line"].call_args.args[0])
        env["submit_gemma_voice"].assert_not_called()

    def test_conferma_in_basso_consumo_usa_lo_stesso_invio_senza_tu(self):
        self.assertIn("submit_deepen(pending[0])", SRC)


class PrioritaTests(unittest.TestCase):
    def test_alta_poi_normale(self):
        from local_model import motore_processo as mp
        chiamate = []
        proc = SimpleNamespace(_handle=77)
        self.assertTrue(mp.imposta_priorita(proc, True, api=lambda h, c: chiamate.append((h, c)) or 1))
        mp.imposta_priorita(proc, False, api=lambda h, c: chiamate.append((h, c)) or 1)
        self.assertEqual(chiamate, [(77, mp.HIGH_PRIORITY_CLASS), (77, mp.NORMAL_PRIORITY_CLASS)])

    def test_senza_processo_o_con_errore_non_fa_nulla(self):
        from local_model import motore_processo as mp
        self.assertFalse(mp.imposta_priorita(None, True, api=lambda h, c: 1))
        self.assertFalse(mp.imposta_priorita(SimpleNamespace(), True, api=lambda h, c: 1))
        def rompe(h, c):
            raise OSError("no")
        self.assertFalse(mp.imposta_priorita(SimpleNamespace(_handle=1), True, api=rompe))

    def test_call_alza_e_riabbassa_anche_in_errore(self):
        from local_model import motore_processo as mp
        adapter = mp.ProcessChatAdapter("src")
        adapter._proc = SimpleNamespace(_handle=5)
        stati = []
        with mock.patch.object(mp, "imposta_priorita", side_effect=lambda p, alta, **k: stati.append(alta)), \
                mock.patch.object(adapter, "_send", side_effect=RuntimeError("x")):
            with self.assertRaises(RuntimeError):
                adapter.call("ask", prompt="x")
        self.assertEqual(stati, [True, False])


class ContestoTests(unittest.TestCase):
    def test_il_caricamento_usa_il_contesto_del_profilo(self):
        from local_model.native_bridge import NativeGemmaBridge
        from local_model.native_config import NativeModelConfig
        config = NativeModelConfig(context_size=800, max_output=200)
        upstream = SimpleNamespace(args=SimpleNamespace(contextsize=1024), maxctx=1024)
        bridge = NativeGemmaBridge(config, upstream)
        bridge._apply_context()
        self.assertEqual((upstream.maxctx, upstream.args.contextsize), (800, 800))
        self.assertIn("self._apply_context()", (ROOT / "local_model" / "native_bridge.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
