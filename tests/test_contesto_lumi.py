import json
import tempfile
import unittest
from pathlib import Path

import chat_elenco
import contesto_lumi
from contesto_lumi import Contesto, filtra_ricordi, finestra_continua
from local_model.chat_sessions import ChatSessionStore
from local_model.memory_preferences import MemoryPreferences
from local_model.native_config import NativeModelConfig
from local_model.native_conversation_session import NativeConversationSession
from test_native_context_window import CountingAdapter


def pair(n):
    return (("user", "domanda %d" % n), ("assistant", "risposta %d" % n))


class RicordiTest(unittest.TestCase):
    BRAIN = json.dumps({"related": [{"fact": "gatto Fufi"}], "recent": [{"user": "ciao"}]})
    EMPTY = json.dumps({"related": [], "recent": [{"user": "ciao"}]})
    PROJECT = json.dumps({"recent": [{"utente": "x"}], "evidence": [], "project": "Casa"})

    def test_mai_sempre_pertinenti(self):
        self.assertEqual(filtra_ricordi(self.BRAIN, "mai"), "")
        self.assertEqual(filtra_ricordi(self.BRAIN, "sempre"), self.BRAIN)
        self.assertEqual(json.loads(filtra_ricordi(self.BRAIN, "pertinenti")),
                         {"related": [{"fact": "gatto Fufi"}]})

    def test_pertinenti_senza_ricordi_trovati_non_manda_niente(self):
        self.assertEqual(filtra_ricordi(self.EMPTY, "pertinenti"), "")

    def test_pertinenti_tiene_lo_stato_del_progetto(self):
        self.assertEqual(json.loads(filtra_ricordi(self.PROJECT, "pertinenti")), {"project": "Casa"})

    def test_testo_non_json_non_passa(self):
        self.assertEqual(filtra_ricordi("{rotto", "pertinenti"), "")


class FinestraContinuaTest(unittest.TestCase):
    def window(self, total, room):
        return finestra_continua(lambda: total,
                                 lambda count: [pair(n) for n in range(total - count, total)],
                                 lambda history: len(history) <= room)

    def test_tutto_se_ci_sta(self):
        history, metrics = self.window(5, 10)
        self.assertEqual(history[0], pair(0))
        self.assertEqual(metrics["omitted"], 0)

    def test_inizio_fisso_finche_il_contesto_non_e_pieno(self):
        starts = [self.window(total, 12)[0][0] for total in range(13, 21)]
        self.assertTrue(all(start == pair(8) for start in starts))   # salta a blocchi di 8
        self.assertEqual(self.window(21, 12)[0][0], pair(16))

    def test_niente_scambi(self):
        self.assertIsNone(self.window(0, 10))
        self.assertIsNone(self.window(3, 0))


class ImpostazioniTest(unittest.TestCase):
    def test_salva_carica_e_file_rovinato(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "contesto.json"
            self.assertEqual(contesto_lumi.carica(path), Contesto())
            contesto_lumi.salva(Contesto(chat_continua=True, ricordi_locale="mai"), path)
            self.assertEqual(contesto_lumi.carica(path), Contesto(True, "mai"))
            path.write_text("{rotto", encoding="utf-8")
            self.assertEqual(contesto_lumi.carica(path), Contesto())
            with self.assertRaises(ValueError):
                contesto_lumi.salva(Contesto(ricordi_locale="forse"), path)


class LettoreChatTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.store = ChatSessionStore(Path(self.folder.name) / "chat.sqlite3")
        self.elenco = chat_elenco.ElencoChat(self.store, lambda: None, lambda *a: None)
        contesto_lumi._ULTIMA_CHAT[0] = "inizio"

    def tearDown(self):
        chat_elenco._CURRENT["elenco"] = None
        self.folder.cleanup()

    def test_cronologia_della_chat_scelta_e_reset_al_cambio(self):
        forgets = []
        self.elenco.save("prima domanda", "prima risposta")
        read = contesto_lumi.lettore_chat(None, forget=lambda: forgets.append(1),
                                          settings=Contesto(chat_continua=True))
        self.assertEqual(forgets, [1])
        self.assertEqual(read.total_pairs(), 1)
        self.assertEqual(read.recent_pairs(4)[0][0], ("user", "prima domanda"))
        self.assertTrue(read.continuous)
        self.assertEqual(read(500), "")
        contesto_lumi.lettore_chat(None, forget=lambda: forgets.append(1))
        self.assertEqual(forgets, [1])                  # stessa chat: niente reset
        self.elenco.new_chat()
        contesto_lumi.lettore_chat(None, forget=lambda: forgets.append(1))
        self.assertEqual(forgets, [1, 1])

    def test_ricordi_filtrati(self):
        read = contesto_lumi.lettore_chat(lambda budget: RicordiTest.EMPTY,
                                          settings=Contesto(ricordi_locale="pertinenti"))
        self.assertEqual(read(500), "")


class PromptContinuoTest(unittest.TestCase):
    def test_chat_continua_usa_la_chat_intera_e_tiene_l_inizio(self):
        adapter = CountingAdapter()
        session = NativeConversationSession(
            adapter, config_loader=lambda: NativeModelConfig(context_size=2048, max_output=128),
            memory_loader=lambda: MemoryPreferences(cronologia_ridotta=False))   # 056c
        chat = [pair(n) for n in range(12)]

        def reader(budget):
            return ""
        reader.continuous = True
        reader.total_pairs = lambda: len(chat)
        reader.recent_pairs = lambda count: chat[-count:]
        session.ask("domanda nuova", memory_context=reader)
        first = adapter.calls[-1]
        # Molto più dei 4 scambi della chat normale: tutta la chat entra.
        self.assertIn("domanda 0", first)
        self.assertIn("risposta 11", first)
        chat.append(pair(12))
        session.ask("un'altra", memory_context=reader)
        second = adapter.calls[-1]
        common = first.split("domanda nuova")[0]
        self.assertTrue(second.startswith(common))      # inizio identico: fast forwarding


if __name__ == "__main__":
    unittest.main()
