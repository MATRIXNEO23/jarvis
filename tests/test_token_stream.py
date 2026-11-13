"""Streaming of partial local-model text (build 021)."""
import threading
import time
import unittest

from local_model.native_bridge import NativeGemmaBridge
from local_model.native_config import NativeModelConfig
from local_model.token_stream import current, streaming, visible_text


class VisibleTextTests(unittest.TestCase):
    def test_cuts_stop_and_holds_back_partial_stop(self):
        self.assertEqual(visible_text("Ciao!<end_of_turn>x", "<end_of_turn>"), "Ciao!")
        self.assertEqual(visible_text("Ciao <end_of", "<end_of_turn>"), "Ciao ")
        self.assertEqual(visible_text("Ciao", None), "Ciao")

    def test_callback_is_per_thread_and_restored(self):
        def callback(_text):
            pass
        with streaming(callback):
            self.assertIs(current(), callback)
            other = []
            t = threading.Thread(target=lambda: other.append(current()))
            t.start(); t.join()
            self.assertEqual(other, [None])
        self.assertIsNone(current())


class GrowingUpstream:
    """Fake engine: text grows while generate() runs; old answer before start."""

    def __init__(self):
        self.handle = self
        self.text = "risposta precedente"

    def get_pending_output(self):
        return self.text.encode("utf-8")

    def generate(self, args):
        self.text = ""
        for word in ("Ciao", " Alberto.", " Come", " stai?", "<end_of_turn>"):
            time.sleep(0.2)
            self.text += word
        return {"status": 1, "stopreason": 1, "text": "Ciao Alberto. Come stai?"}


class BridgeStreamTests(unittest.TestCase):
    def make_bridge(self, upstream):
        bridge = NativeGemmaBridge(NativeModelConfig(), upstream, initialize=lambda *_: None)
        bridge._loaded = True
        bridge.family = "gemma2"
        return bridge

    def test_partial_text_grows_without_stale_or_stop_markers(self):
        bridge = self.make_bridge(GrowingUpstream())
        chunks = []
        with streaming(chunks.append):
            final = bridge.generate("prompt", timeout=10)
        self.assertEqual(final, "Ciao Alberto. Come stai?")
        self.assertGreaterEqual(len(chunks), 2)
        self.assertNotIn("risposta precedente", "".join(chunks))
        self.assertTrue(all(b.startswith(a) for a, b in zip(chunks, chunks[1:])))
        self.assertFalse(any("<end" in c for c in chunks))

    def test_no_callback_no_stream_thread(self):
        bridge = self.make_bridge(GrowingUpstream())
        self.assertEqual(bridge.generate("prompt", timeout=10), "Ciao Alberto. Come stai?")


class ReplyStreamTests(unittest.TestCase):
    def test_action_schema_streams_only_chat_reply(self):
        from local_model.token_stream import visible_reply
        self.assertEqual(visible_reply('{"kind":"chat","reply":"Ecco tre film: \\"Up'), 'Ecco tre film: "Up')
        self.assertEqual(visible_reply('{"kind":"capability","action_id":"x"'), "")
        self.assertEqual(visible_reply('{"kind":"chat","rep'), "")
        self.assertEqual(visible_reply("Testo normale"), "Testo normale")


class SpeechTextTests(unittest.TestCase):
    def test_emoji_and_markdown_are_not_read_aloud(self):
        from offline_tts import speech_text
        self.assertEqual(speech_text("**Ecco** tre film 🎬😊:\n- *Inception* 🍿\n- # Matrix ✨ !"),
                         "Ecco tre film: Inception. Matrix!")


class ChatStreamTests(unittest.TestCase):
    def test_very_long_sentence_starts_at_a_comma(self):
        from chat_stream import ChatStream
        spoken = []
        stream = ChatStream()
        stream.speak = lambda text: spoken.append(text) or True
        stream.voice_enabled = lambda: True
        long_text = "Ti consiglio Inception di Nolan, " * 5 + "e poi"
        stream._speak_sentences(long_text)
        self.assertTrue(spoken and spoken[0].endswith(","))

    def test_speaks_completed_sentences_then_only_the_rest(self):
        from chat_stream import ChatStream
        spoken, final = [], []
        stream = ChatStream()
        stream.speak = lambda text: spoken.append(text) or True
        stream.voice_enabled = lambda: True
        stream._speak_sentences("Ciao Alberto. Come")
        stream._speak_sentences("Ciao Alberto. Come stai")
        self.assertEqual(spoken, ["Ciao Alberto."])
        stream.speak_final("Ciao Alberto. Come stai?", final.append)
        self.assertEqual(final, ["Come stai?"])

    def test_unconfigured_stream_is_a_no_op_and_final_speaks_everything(self):
        from chat_stream import ChatStream
        stream, final = ChatStream(), []
        self.assertIsNone(stream.sink(1))
        stream.drain(1, True)
        stream.speak_final("Tutto.", final.append)
        self.assertEqual(final, ["Tutto."])


if __name__ == "__main__":
    unittest.main()


class TelegramHeaderTests(unittest.TestCase):
    def test_old_and_renamed_credential_headers_are_both_readable(self):
        import base64, json, tempfile
        from pathlib import Path
        from telegram_security import load_credentials, save_credentials
        plain = json.dumps({"api_id": 1, "api_hash": "a" * 32, "session": "s" * 40}).encode()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "auth.dpapi"
            for header in (b"JARVIS-TG1\n", b"LUMI-TG1\n"):
                path.write_bytes(header + base64.b64encode(plain))
                self.assertEqual(load_credentials(path, protect=lambda v, _e: v)["api_id"], 1)
            save_credentials(1, "a" * 32, "s" * 40, path=path, protect=lambda v, _e: v)
            self.assertTrue(path.read_bytes().startswith(b"JARVIS-TG1\n"))
