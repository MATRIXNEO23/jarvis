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
    def __init__(self, bridge, *, disconnect_early=False, disconnect_error=False):
        self.bridge = bridge
        self._disconnected = asyncio.get_running_loop().create_future()
        self.disconnect_early = disconnect_early
        self.disconnect_error = disconnect_error
        self.closed = False
        self.sent = []

    @property
    def disconnected(self):
        # A property may return a fresh shield Future on each read.
        return asyncio.shield(self._disconnected)

    async def connect(self):
        pass

    async def is_user_authorized(self):
        return True

    def on(self, event_filter):
        def register(callback):
            if event_filter == 'raw':
                self.raw_callback = callback
                return callback
            self.callback = callback
            if self.disconnect_early:
                loop = asyncio.get_running_loop()
                if self.disconnect_error:
                    loop.call_soon(self._disconnected.set_exception, ConnectionError('Controlled transport failure'))
                else:
                    loop.call_soon(self._disconnected.set_result, None)
            return callback
        return register

    async def send_file(self, peer, path, voice_note=False):
        self.sent.append((peer, voice_note))
        return SimpleNamespace(id=401)

    async def disconnect(self):
        self.closed = True
        if not self._disconnected.done():
            self._disconnected.set_result(None)


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
        module.events = SimpleNamespace(NewMessage=lambda **kwargs:kwargs, Raw="raw")
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
            ignored=[e[1] for e in self.events if e[0]=='telegram_status' and 'ignorato' in e[1]]
            self.assertEqual(len(ignored),1)          # una volta sola per mittente
            self.assertIn('[ID 99]',ignored[0])
        finally:
            self.bridge.stop()
            await asyncio.wait_for(task,2)
        self.assertTrue(client.closed)

    async def test_raw_update_is_processed_when_newmessage_handler_never_fires(self):
        """026: sul PC i nuovi messaggi arrivavano come aggiornamenti grezzi ma
        il gestore NewMessage non veniva chiamato: ora si recuperano per ID."""
        client = Client(self.bridge)
        fetched = []
        async def get_messages(user_id, ids):
            fetched.append((user_id, ids))
            return SimpleNamespace(id=ids, out=False, voice=False, message='Ciao da raw')
        client.get_messages = get_messages
        self.boundary(client)
        task = asyncio.create_task(self.bridge._run())
        try:
            for _ in range(20):
                if hasattr(client,'raw_callback'):
                    break
                await asyncio.sleep(0)
            UpdateShortMessage = type('UpdateShortMessage', (), {})
            update = UpdateShortMessage()
            update.out, update.user_id, update.id = False, 44, 77
            other = UpdateShortMessage()
            other.out, other.user_id, other.id = False, 99, 78     # non autorizzato
            real_sleep = asyncio.sleep
            async def quick(_seconds):
                await real_sleep(0)
            with patch('telegram_bridge.asyncio.sleep', new=quick):
                await client.raw_callback(update)
                await client.raw_callback(other)
                for _ in range(50):
                    if client.sent:
                        break
                    await real_sleep(0.01)
            self.assertEqual(fetched, [(44, 77)])
            self.assertEqual(len(client.sent), 1)
            self.assertEqual(sum(e[0]=='telegram_received' for e in self.events),1)
        finally:
            self.bridge.stop()
            await asyncio.wait_for(task,2)

    async def test_terminal_disconnect_clears_enabled_flag_and_reports_stop(self):
        client = Client(self.bridge)
        self.boundary(client)
        module = sys.modules['telethon']
        module.TelegramClient = lambda *args, **kwargs: Client(self.bridge, disconnect_early=True)
        task = asyncio.create_task(asyncio.to_thread(self.bridge._thread_main))
        try:
            done,_ = await asyncio.wait({task},timeout=2)
            self.assertIn(task,done)
        finally:
            self.bridge.stop()
            await asyncio.wait_for(task,2)
        self.assertFalse(self.bridge.is_enabled())
        self.assertTrue(any(e[0]=='telegram_status' and 'terminata' in e[1] for e in self.events))
        self.assertTrue(any(e[0]=='telegram_stopped' for e in self.events))

    async def test_terminal_exception_is_consumed_without_unhandled_future_warning(self):
        client = Client(self.bridge, disconnect_early=True, disconnect_error=True)
        self.boundary(client)
        loop = asyncio.get_running_loop()
        previous = loop.get_exception_handler()
        warnings = []
        loop.set_exception_handler(lambda loop, context: warnings.append(context))
        try:
            with self.assertRaises(TelegramBridgeError) as caught:
                await asyncio.wait_for(self.bridge._run(),2)
            self.assertNotIn('Controlled transport failure', str(caught.exception))
            await asyncio.sleep(0)
            self.assertEqual(warnings, [])
        finally:
            loop.set_exception_handler(previous)
        self.assertFalse(client._disconnected.cancelled())
