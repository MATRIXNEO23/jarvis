"""Real bridge lifecycle and inbound flow; only Telegram/audio boundaries faked."""
import asyncio
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
from telegram_bridge import TelegramBridge, TelegramBridgeError
from workspace_memory import WorkspaceMemory
from test_telegram_no_network import fake_voice


class Client:
    def __init__(self, bridge, *, disconnect_early=False):
        self.bridge = bridge
        self.disconnected = asyncio.get_running_loop().create_future()
        self.disconnect_early = disconnect_early
        self.closed = False
        self.sent = []

    async def connect(self):
        pass

    async def is_user_authorized(self):
        return True

    def on(self, event_filter):
        def register(callback):
            self.callback = callback
            if self.disconnect_early:
                asyncio.get_running_loop().call_soon(self.disconnected.set_result, None)
            return callback
        return register

    async def send_file(self, peer, path, voice_note=False):
        self.sent.append((peer, voice_note))
        return SimpleNamespace(id=401)

    async def disconnect(self):
        self.closed = True
        if not self.disconnected.done():
            self.disconnected.set_result(None)


class ListenerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.events = []
        self.workspace = WorkspaceMemory(Path(folder.name)/'workspace.sqlite3')
        self.bridge = TelegramBridge(self.workspace,44,'Selected',None,self.events.append,
            credential_loader=lambda:dict(session='fixture',api_id=1,api_hash='fixture'),
            reply_with_context=lambda text,context,peer:'Risposta controllata')
        self.bridge._enabled.set()

    def boundary(self, client):
        module = ModuleType('telethon')
        module.TelegramClient = lambda *args, **kwargs: client
        module.events = SimpleNamespace(NewMessage=lambda **kwargs:kwargs)
        sessions = ModuleType('telethon.sessions')
        sessions.StringSession = lambda value:value
        async def contacts(_client):
            return {44:('Selected',object())}
        self.enterContext(patch.dict(sys.modules,{'telethon':module,'telethon.sessions':sessions}))
        self.enterContext(patch('telegram_bridge.verified_contact_entities',contacts))
        self.enterContext(patch('telegram_bridge.make_telegram_voice',fake_voice))

    async def test_terminal_disconnect_does_not_leave_listener_waiting_as_if_active(self):
        client = Client(self.bridge, disconnect_early=True)
        self.boundary(client)
        async def run():
            try:
                await self.bridge._run()
            except TelegramBridgeError:
                pass
        task = asyncio.create_task(run())
        try:
            done,_ = await asyncio.wait({task},timeout=.25)
            self.assertIn(task,done,'Terminal disconnect left the listener waiting for manual Stop')
        finally:
            self.bridge.stop()
            await asyncio.wait_for(task,2)
        self.assertTrue(client.closed)

    async def test_registered_incoming_handler_replies_once_only_for_allowed_contact(self):
        client = Client(self.bridge)
        self.boundary(client)
        task = asyncio.create_task(self.bridge._run())
        try:
            for _ in range(20):
                if hasattr(client,'callback'):
                    break
                await asyncio.sleep(0)
            for peer,out in [(99,False),(44,True),(44,False),(44,False)]:
                event = SimpleNamespace(sender_id=peer,is_private=True,out=out,
                    message=SimpleNamespace(id=10,voice=False,message='Ciao'))
                await client.callback(event)
            self.assertEqual(len(client.sent),1)
            self.assertTrue(client.sent[0][1])
            self.assertEqual(sum(e[0]=='telegram_received' for e in self.events),1)
        finally:
            self.bridge.stop()
            await asyncio.wait_for(task,2)
        self.assertTrue(client.closed)
