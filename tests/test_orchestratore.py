import json
import tempfile
import threading
import unittest
from pathlib import Path

import lumi_comandi
import orchestratore as orch
import risposte


def tool_call(name, args, ident="c1"):
    return {"id": ident, "type": "function",
            "function": {"name": name, "arguments": json.dumps(args)}}


class StrumentiTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.safe = Path(self.folder.name) / "sicura"
        self.other = Path(self.folder.name) / "altra"
        self.safe.mkdir()
        self.other.mkdir()
        (self.safe / "preventivo.txt").write_text("Totale: 120 euro", encoding="utf-8")
        (self.other / "segreto.txt").write_text("privato", encoding="utf-8")
        self.questions, self.commands, self.answer = [], [], False
        self.tools = orch.Strumenti(ask=self.ask, run_command=self.commands.append,
                                    folders=[str(self.safe)])

    def tearDown(self):
        self.folder.cleanup()

    def ask(self, question):
        self.questions.append(question)
        return self.answer

    def test_nelle_cartelle_sicure_lavora_da_solo(self):
        self.assertIn("preventivo.txt", self.tools.esegui("cerca_file", {"nome": "preventivo"}))
        self.assertEqual(self.tools.esegui("leggi_file", {"percorso": str(self.safe / "preventivo.txt")}),
                         "Totale: 120 euro")
        result = self.tools.esegui("scrivi_file", {"percorso": str(self.safe / "riassunto.txt"),
                                                   "testo": "120 euro"})
        self.assertIn("Scritto", result)
        self.assertEqual(self.questions, [])

    def test_fuori_e_comandi_chiedono_il_permesso(self):
        self.assertEqual(self.tools.esegui("leggi_file", {"percorso": str(self.other / "segreto.txt")}),
                         "Permesso negato.")
        self.assertEqual(self.tools.esegui("scrivi_file", {"percorso": str(self.other / "x.txt"),
                                                           "testo": "a"}), "Permesso negato.")
        self.assertFalse((self.other / "x.txt").exists())
        self.assertEqual(self.tools.esegui("comando_lumi", {"comando": "apri blocco note"}),
                         "Permesso negato.")
        self.assertEqual(self.commands, [])
        self.answer = True
        self.assertEqual(self.tools.esegui("leggi_file", {"percorso": str(self.other / "segreto.txt")}),
                         "privato")
        self.tools.esegui("comando_lumi", {"comando": "apri blocco note"})
        self.assertEqual(self.commands, ["apri blocco note"])
        self.assertEqual(len(self.questions), 5)

    def test_niente_strumento_per_cancellare(self):
        names = {t["function"]["name"] for t in orch.STRUMENTI}
        self.assertFalse(any("cancell" in n or "elimin" in n for n in names))
        self.assertEqual(self.tools.esegui("elimina_file", {}), "Strumento sconosciuto.")

    def test_cartelle_salvate(self):
        path = Path(self.folder.name) / "o.json"
        orch.salva_cartelle([str(self.safe), str(self.safe)], path)
        self.assertEqual(orch.cartelle_sicure(path), [str(self.safe.resolve())])
        self.assertTrue(orch.dentro(self.safe / "a" / "b.txt", orch.cartelle_sicure(path)))
        self.assertFalse(orch.dentro(self.other / "b.txt", orch.cartelle_sicure(path)))


class CicloTest(unittest.TestCase):
    def test_piu_passi_poi_risposta(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "preventivo.txt").write_text("Totale: 120 euro", encoding="utf-8")
            tools = orch.Strumenti(ask=lambda q: False, run_command=lambda t: None, folders=[folder])
            replies = [
                {"content": "", "tool_calls": [tool_call("cerca_file", {"nome": "preventivo"})]},
                {"content": "", "tool_calls": [tool_call("leggi_file", {"percorso": str(Path(folder) / "preventivo.txt")}, "c2")]},
                {"content": "Il totale è 120 euro."}]
            seen, notes = [], []

            def call(messages, tools=None, only=None):
                seen.append((list(messages), only))
                return "groq", "Groq", replies[len(seen) - 1]

            name, text = orch.rispondi("trova il preventivo e dimmi il totale", tools=tools,
                                       call=call, notify=notes.append)
        self.assertEqual((name, text), ("Groq", "Il totale è 120 euro."))
        self.assertEqual([s[1] for s in seen], [None, "groq", "groq"])    # stesso servizio
        last = seen[-1][0]
        self.assertEqual(last[-1]["role"], "tool")
        self.assertIn("120 euro", last[-1]["content"])
        self.assertIn(folder, last[0]["content"])
        self.assertEqual(len(notes), 2)

    def test_troppi_passi_si_ferma(self):
        tools = orch.Strumenti(ask=lambda q: False, run_command=lambda t: None, folders=[])
        call = lambda m, tools=None, only=None: ("g", "G", {"tool_calls": [tool_call("cerca_file", {"nome": "x"})]})
        self.assertIn("troppi passi", orch.rispondi("x", tools=tools, call=call)[1])

    def test_servizi_non_disponibili(self):
        tools = orch.Strumenti(ask=lambda q: False, run_command=lambda t: None, folders=[])
        call = lambda m, tools=None, only=None: (None, None, ["Groq: quota finita"])
        self.assertEqual(orch.rispondi("x", tools=tools, call=call), (None, ["Groq: quota finita"]))


class ConsensoTest(unittest.TestCase):
    def tearDown(self):
        orch.SESSIONE["sempre"] = False
        lumi_comandi._STATE.update(actions=None, pending=None)

    def test_sempre_vale_finche_l_online_resta_acceso(self):
        self.assertTrue(orch.consenso_necessario(True))
        orch.SESSIONE["sempre"] = True
        self.assertFalse(orch.consenso_necessario(True))
        self.assertFalse(orch.consenso_necessario(False))          # online spento: decade
        self.assertTrue(orch.consenso_necessario(True))

    def test_risposte_si_no_sempre(self):
        calls = []
        lumi_comandi.register({"orch_once": lambda: calls.append("una"),
                               "orch_local": lambda: calls.append("no"),
                               "orch_always": lambda: calls.append("sempre")}, lambda: False)
        for answer in ("sempre", "sì", "no"):
            lumi_comandi.chiedi("orch_once", "Uso l'online?", lambda t: None, lambda t: None,
                                no_action="orch_local", always_action="orch_always")
            self.assertTrue(lumi_comandi.handle_text(answer, lambda t: None, lambda t: None))
        self.assertEqual(calls, ["sempre", "una", "no"])
        self.assertTrue(risposte.is_answer("sempre"))
        self.assertIn("sempre", risposte.GRAMMAR)

    def test_permesso_dal_thread_di_lavoro(self):
        asked = []

        def ask_ui(question, reply):
            asked.append(question)
            orch.RISPOSTA["reply"] = reply

        ask = orch.permesso_da_thread(lambda fn: fn(), ask_ui, timeout=5)
        result = {}
        worker = threading.Thread(target=lambda: result.update(ok=ask("Posso leggere?")))
        worker.start()
        for _ in range(100):
            if orch.RISPOSTA["reply"] is not None:
                break
            threading.Event().wait(0.02)
        orch.rispondi_permesso(True)
        worker.join(5)
        self.assertTrue(result["ok"])
        self.assertEqual(asked, ["Posso leggere?"])
        quick = orch.permesso_da_thread(lambda fn: fn(), lambda q, r: None, timeout=0.1)
        self.assertFalse(quick("Nessuno risponde?"))               # senza risposta: no


if __name__ == "__main__":
    unittest.main()
