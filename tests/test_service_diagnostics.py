"""Observe the real Telegram pipeline without network, model or real audio."""
import asyncio
from types import SimpleNamespace
import unittest
from test_telegram_listener_lifecycle import ListenerTests, Client


class ServiceDiagnosticsTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = ListenerTests()
        await self.f.asyncSetUp()
        self.addCleanup(self.f.doCleanups)

    def snapshot(self):
        reader = getattr(self.f.bridge, 'diagnostic_snapshot', None)
        return reader() if reader else {'counts': {}, 'events': (), 'phase': 'not_observed'}

    async def launch(self):
        client = Client(self.f.bridge)
        self.f.boundary(client)
        task = asyncio.create_task(self.f.bridge._run())
        for _ in range(20):
            if hasattr(client, 'callback'):
                break
            await asyncio.sleep(0)
        async def cleanup():
            self.f.bridge.stop()
            await asyncio.wait_for(task, 2)
        self.addAsyncCleanup(cleanup)
        return client

    async def test_listener_ready_does_not_claim_message_reception(self):
        await self.launch()
        report = self.snapshot()
        self.assertEqual(report['phase'], 'listening')
        self.assertEqual(report['counts'].get('received', 0), 0)

    async def test_filtered_update_and_success_are_visible_without_private_content(self):
        client = await self.launch()
        for peer in (99, 44):
            if hasattr(client, 'raw_callback'):
                await client.raw_callback(SimpleNamespace())
            await client.callback(SimpleNamespace(sender_id=peer, is_private=True, out=False,
                message=SimpleNamespace(id=10,voice=False,message='PRIVATE_SENTINEL_secret')))
        report = self.snapshot()
        self.assertEqual(len(client.sent), 1)
        for code in ('update', 'filtered_contact', 'received', 'model_started', 'sent'):
            self.assertGreater(report['counts'].get(code, 0), 0, code)
        self.assertNotIn('PRIVATE_SENTINEL', str(report))
        self.assertNotIn('Selected', str(report))
        self.assertNotIn('401', str(report))

    async def test_model_failure_is_distinguished_from_no_reception(self):
        client = await self.launch()
        def failed(*args):
            raise RuntimeError('PRIVATE_EXCEPTION_SENTINEL')
        self.f.bridge.reply_with_context = failed
        await client.callback(SimpleNamespace(sender_id=44,is_private=True,out=False,
            message=SimpleNamespace(id=11,voice=False,message='Testo privato')))
        report = self.snapshot()
        self.assertEqual(report['counts'].get('received'), 1)
        self.assertEqual(report['last_error'], 'model_failed')
        self.assertNotIn('PRIVATE_EXCEPTION', str(report))
        self.assertEqual(client.sent, [])
