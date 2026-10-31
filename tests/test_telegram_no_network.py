"""Integration without Telegram network, Windows audio or OpenAI login."""
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from workspace_memory import WorkspaceMemory
from telegram_bridge import TelegramBridge


class FakeClient:
    def __init__(self):
        self.sent=[]
    async def send_file(self,peer,path,voice_note=False):
        self.sent.append((peer,Path(path).name,voice_note))
        return SimpleNamespace(id=401)


def fake_voice(text,folder,voice=""):
    out=Path(folder)/"note.ogg"
    out.write_bytes(b"simulated audio")
    return out


class TelegramNoNetworkTest(unittest.IsolatedAsyncioTestCase):
    async def test_explicit_owner_note_verbatim_and_exactly_once(self):
        with tempfile.TemporaryDirectory() as temporary:
            db=WorkspaceMemory(Path(temporary)/"work.sqlite3")
            peer_id=44
            db.note_for_contact(peer_id,"Domani sono disponibile.")
            events=[]
            def forbidden_gpt(_prompt):
                self.fail("Owner relay must not depend on GPT's paraphrase.")
            bridge=TelegramBridge(db,peer_id,"Contatto",
                                  forbidden_gpt,events.append)
            bridge._enabled.set()
            client=FakeClient()
            event=SimpleNamespace(message=SimpleNamespace(
                id=10,voice=False,message="Ciao"))
            with patch("telegram_bridge.make_telegram_voice",fake_voice):
                await bridge._handle(client,object(),event)
            self.assertEqual(len(client.sent),1)
            self.assertTrue(client.sent[0][2])
            activity=db.telegram_activity(peer_id)
            replies=[e for e in activity if e["direction"]=="outgoing"]
            self.assertEqual(len(replies),1)
            self.assertIn("Domani sono disponibile.",replies[0]["text"])
            self.assertEqual(db.pending_for_contact(peer_id),())
            with patch("telegram_bridge.make_telegram_voice",fake_voice):
                await bridge._handle(client,object(),event)
            self.assertEqual(len(client.sent),1)

    async def test_manual_switch_off_prevents_any_send(self):
        with tempfile.TemporaryDirectory() as temporary:
            db=WorkspaceMemory(Path(temporary)/"work.sqlite3")
            bridge=TelegramBridge(db,45,"Contatto",lambda _: "Ciao",
                                  lambda _:None)
            client=FakeClient()
            event=SimpleNamespace(message=SimpleNamespace(
                id=11,voice=False,message="Ciao"))
            await bridge._handle(client,object(),event)
            self.assertEqual(client.sent,[])
            self.assertEqual(db.telegram_counts(45)["received"],0)


if __name__=="__main__":
    unittest.main()
