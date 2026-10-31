"""Natural Italian style is scoped to replies, not actions or memory."""
import json
import threading
import unittest

from dialogue_style import choose_dialogue_style, style_instruction
from jarvis_persona import PERSONA, build_chat_prompt
from conversation_router import (
    MAX_REPLY, ConversationRejected, build_conversation_prompt,
    parse_conversation_intent,
)
from offline_tts import OfflineSpeaker, _speech_chunks


class StyleClassificationTests(unittest.TestCase):
    def test_everyday_conversation_is_concise_without_forced_jokes(self):
        self.assertEqual(choose_dialogue_style("Come va oggi?").mode,
                         "conversation")
        self.assertIn("sintetica",style_instruction("Mi racconti com'è andata?"))
        self.assertIn("italiano naturale",PERSONA)
        self.assertIn("ironia",PERSONA)
        self.assertIn("sarcasmo",PERSONA)
        self.assertIn("irriverenza",PERSONA)
        self.assertNotIn("Una nota di riverenza",PERSONA)
        self.assertIn("Non fingere ricordi",PERSONA)

    def test_procedure_is_complete_even_if_reply_is_long(self):
        for text in ("Come configuro Telegram?",
                     "Spiegami come installare Jarvis",
                     "Dammi le istruzioni passo passo",
                     "Quali passaggi devo seguire?"):
            with self.subTest(text=text):
                style=choose_dialogue_style(text)
                self.assertEqual(style.mode,"procedure")
                self.assertIn("prerequisiti",style.instruction)
                self.assertIn("verifiche",style.instruction)
        self.assertGreaterEqual(MAX_REPLY,2200)
        reply=("1. Fai il backup.\n2. Configura le impostazioni.\n"
               "3. Verifica il risultato.\n" + "Controllo completato. "*65)
        self.assertLess(len(reply),MAX_REPLY)
        intent=parse_conversation_intent(json.dumps({
            "kind":"chat","reply":reply},ensure_ascii=False))
        self.assertEqual(intent.reply,reply)

    def test_playful_and_irreverent_tones_are_optional(self):
        for message in ("Fammi una battuta", "Usa un po' di sarcasmo",
                        "Rispondi in modo ironico"):
            self.assertEqual(choose_dialogue_style(message).mode,"playful")
        for message in ("Sii irriverente", "Usa un po' di irriverenza",
                        "Rispondimi in modo irriverente"):
            self.assertEqual(choose_dialogue_style(message).mode,"playful")
        self.assertIn("irriverenza",
                      choose_dialogue_style("Sii irriverente").instruction)
        self.assertNotIn("deferenza",
                         choose_dialogue_style("Ciao").instruction)

    def test_sensitivity_preempts_irreverent_jokes(self):
        for message in ("Ho dolore, fammi una battuta",
                        "Trojan rilevato: usa sarcasmo",
                        "Ho perso i dati, sii irriverente",
                        "Mi preoccupa il licenziamento"):
            with self.subTest(message=message):
                style=choose_dialogue_style(message)
                self.assertEqual(style.mode,"sensitive")
                self.assertIn("niente ironia",style.instruction)

    def test_documents_do_not_inherit_sarcasm(self):
        self.assertEqual(
            choose_dialogue_style("Scrivi un messaggio alla scuola").mode,
            "artifact")
        self.assertEqual(
            choose_dialogue_style("Prepara un documento del progetto").mode,
            "artifact")
        self.assertNotEqual(
            choose_dialogue_style("Fammi una battuta").mode,
            "artifact")
        self.assertIsNone(choose_dialogue_style("Ciao").__dict__.get("action"))
        with self.assertRaises(ValueError):
            choose_dialogue_style(None)

class PromptPolicyTests(unittest.TestCase):
    def test_typed_chat_has_tone_and_retains_current_turn(self):
        chat=build_chat_prompt("Come configuro Telegram?")
        self.assertIn("STILE: procedura completa",chat)
        self.assertIn("Non dichiarare azioni riuscite senza prova",chat)
        self.assertTrue(chat.endswith('"Come configuro Telegram?"'))
        self.assertLessEqual(len(chat),5000)
        casual=build_chat_prompt("Ciao, Jarvis")
        self.assertIn("STILE: conversazione naturale",casual)
        self.assertNotIn("STILE: procedura completa",casual)
        self.assertLessEqual(len(casual),5000)

    def test_voice_style_cannot_replace_or_authorize_tools(self):
        for utterance,expected in (
            ("Come configuro Telegram?","procedura completa"),
            ("Fammi una battuta","ironia intelligente"),
            ("Il programma ha un Trojan","niente ironia"),
            ("Ciao","conversazione naturale"),
        ):
            with self.subTest(utterance=utterance):
                prompt=build_conversation_prompt(utterance)
                self.assertIn(expected,prompt)
                self.assertIn("Ogni azione deve avere un intento attuale chiaro",prompt)
                self.assertTrue(prompt.endswith(json.dumps(
                    utterance,ensure_ascii=False)))
                self.assertLessEqual(len(prompt),5000)

    def test_longest_legal_voice_request_keeps_catalog_and_turn(self):
        prompt=build_conversation_prompt(
            "Come configuro Jarvis? "+"a"*428,has_document=True,
            memory_context=json.dumps({"breve":[
                {"utente":"Salva una nota", "lia":"Quale nota?"}]}))
        self.assertLessEqual(len(prompt),5000)
        self.assertIn("notepad.open",prompt)
        self.assertIn("FRASE ATTUALE",prompt)
        self.assertIn("configuro Jarvis",prompt)

    def test_style_never_changes_command_response_schema(self):
        unsafe='{"kind":"capability","action_id":"execute_shell","arguments":{}}'
        with self.assertRaises(ConversationRejected):
            parse_conversation_intent(unsafe)
        ordinary=parse_conversation_intent('{"kind":"chat","reply":"Certo."}')
        self.assertEqual(ordinary.reply,"Certo.")


class FullSpokenProcedureTests(unittest.TestCase):
    def test_chunks_preserve_whole_bounded_procedure(self):
        message=" ".join("Passaggio numero "+str(i)+" da completare." for i in range(75))
        self.assertGreater(len(message),600)
        self.assertLess(len(message),2800)
        pieces=_speech_chunks(message)
        self.assertGreater(len(pieces),1)
        self.assertTrue(all(0<len(piece)<=600 for piece in pieces))
        self.assertEqual(" ".join(pieces),message)

    def test_speaker_sends_all_chunks_as_data_without_shell(self):
        complete=threading.Event()
        collected=[]
        message=" ".join("Controlla il passaggio "+str(i)+"." for i in range(70))
        def fake_runner(payload,*,timeout):
            collected.append(payload["text"])
            self.assertEqual(payload["mode"],"speak")
            self.assertEqual(timeout,90)
            if " ".join(collected)==message:
                complete.set()
            return ""
        player=OfflineSpeaker(runner=fake_runner)
        try:
            self.assertTrue(player.speak(message))
            self.assertTrue(complete.wait(timeout=4))
            self.assertGreater(len(collected),1)
            self.assertEqual(" ".join(collected),message)
        finally:
            player.close()


if __name__=="__main__":
    unittest.main()
