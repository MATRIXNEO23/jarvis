"""Observe the real Telegram pipeline without network, model or real audio."""
import asyncio
from types import SimpleNamespace
import unittest
import test_telegram_listener_lifecycle as listener


class ServiceDiagnosticsTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = listener.ListenerTests()
        await self.f.asyncSetUp()
        self.addCleanup(self.f.doCleanups)

    def snapshot(self):
        reader = getattr(self.f.bridge, 'diagnostic_snapshot', None)
        return reader() if reader else {'counts': {}, 'events': (), 'phase': 'not_observed'}

    async def launch(self):
        client = listener.Client(self.f.bridge)
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
        self.assertNotIn('peer_id', report)

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


class ServiceReportTests(unittest.TestCase):
    def test_bounded_journal_rejects_unrecognized_data_and_snapshots_do_not_mutate_it(self):
        from runtime_diagnostics import ServiceEventLog
        log=ServiceEventLog()
        log.record('PRIVATE api_hash text')
        log.record(['not a code'])
        for _ in range(10050):log.record('update')
        snapshot=log.snapshot()
        self.assertEqual(len(snapshot['events']),64)
        self.assertEqual(snapshot['counts']['update'],9999)
        snapshot['counts']['update']=0
        self.assertEqual(log.snapshot()['counts']['update'],9999)
        self.assertNotIn('PRIVATE',str(log.snapshot()))

    def test_report_does_not_claim_reception_or_leak_unknown_fields(self):
        from runtime_diagnostics import ServiceEventLog,format_service_report
        from test_runtime_diagnostics import capture
        log=ServiceEventLog();log.record('listening')
        snapshot=log.snapshot();snapshot['private_text']='PRIVATE TEXT'
        report=format_service_report(capture(),telegram=snapshot,automatic=True,contacts=1)
        self.assertIn('Nessuna ricezione autorizzata',report)
        self.assertIn('Messaggi autorizzati ricevuti: 0',report)
        self.assertNotIn('PRIVATE TEXT',report)
        self.assertIn('Microfono',report)
        self.assertIn('GPT',report)

    def test_terminal_error_preserves_failure_phase_after_cleanup(self):
        from runtime_diagnostics import ServiceEventLog
        log=ServiceEventLog();log.record('credentials');log.failed();log.record('stopped')
        snapshot=log.snapshot()
        self.assertEqual(snapshot['phase'],'stopped')
        self.assertEqual(snapshot['last_error'],'credentials_failed')
        self.assertEqual(snapshot['error_phase'],'credentials')
