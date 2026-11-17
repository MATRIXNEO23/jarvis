"""056b: il «ciao» dopo una risposta lunga non riceve la risposta vecchia né ricordi."""
import unittest

from local_model.memory_preferences import MemoryPreferences
from local_model.native_config import NativeModelConfig
from local_model.native_conversation_session import NativeConversationSession
from local_model import prompt_breve as pb
from test_native_conversation_session import FakeAdapter


class Adapter(FakeAdapter):
    def context_token_counter(self):
        return lambda prompt: (len(prompt) + 3) // 4 + 1


class CiaoTests(unittest.TestCase):
    def prompt_dopo(self, domanda, memory=None):
        adapter = Adapter()
        session = NativeConversationSession(
            adapter, config_loader=lambda: NativeModelConfig(context_size=2048, max_output=128),
            memory_loader=MemoryPreferences)
        turn = session.prepare_turn("Parlami di Roma")
        turn.text = "Roma è una città antica. " * 40 + "FINE-RISPOSTA-LUNGA"
        turn.commit()
        session.ask(domanda, memory_context=memory)
        return adapter.calls[-1]

    def test_ciao_taglia_la_risposta_vecchia_e_segna_l_ultimo_messaggio(self):
        prompt = self.prompt_dopo("ciao")
        self.assertNotIn("FINE-RISPOSTA-LUNGA", prompt)
        self.assertIn(pb.SEPARATORE, prompt)
        self.assertLess(prompt.index(pb.SEPARATORE), prompt.index("Parlami di Roma"))
        self.assertIn("ciao", prompt.split("<start_of_turn>user")[-1])

    def test_nessun_ricordo_per_il_saluto(self):
        chiamate = []
        def memoria(room):
            chiamate.append(room)
            return "Fatto: ama la pizza"
        memoria.attachment = ()
        prompt = self.prompt_dopo("ciao", memoria)
        self.assertEqual(chiamate, [])
        self.assertNotIn("ama la pizza", prompt)

    def test_domanda_lunga_conserva_la_risposta(self):
        prompt = self.prompt_dopo("Approfondisci quello che hai detto su Roma")
        self.assertIn("FINE-RISPOSTA-LUNGA", prompt)

    def test_classificazione(self):
        self.assertTrue(pb.saluto("Ciao Lumi!"))
        self.assertFalse(pb.saluto("ciao, che tempo fa"))
        self.assertTrue(pb.breve("che ore sono"))
        self.assertFalse(pb.breve("spiegami"))


if __name__ == "__main__":
    unittest.main()
