"""Actual local Tk view: refresh/copy are explicit, never test a service."""
import ast
import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


@unittest.skipUnless(os.name == 'nt', 'Windows Tk only')
class ServiceDiagnosticsUITests(unittest.TestCase):
    def test_real_read_only_view_refreshes_and_copies_only_on_request(self):
        self.assertIsNotNone(importlib.util.find_spec('runtime_diagnostics_ui'),
                             'Settings cannot show a service report')
        from runtime_diagnostics_ui import ServiceDiagnosticsWindow
        import tkinter as tk
        root = tk.Tk();root.withdraw()
        self.addCleanup(root.destroy)
        getter = Mock(side_effect=['Rapporto iniziale', 'Rapporto aggiornato'])
        view = ServiceDiagnosticsWindow(root, get_report=getter)
        self.addCleanup(lambda: view.window.destroy() if view.window.winfo_exists() else None)
        root.update_idletasks()
        self.assertEqual(view.text.cget('state'), 'disabled')
        self.assertIn('Rapporto iniziale', view.text.get('1.0', 'end'))
        self.assertEqual(getter.call_count, 1)
        root.update_idletasks()
        self.assertEqual(getter.call_count, 1)  # no polling or background checks
        view.refresh()
        self.assertIn('Rapporto aggiornato', view.text.get('1.0', 'end'))
        view.copy_report()
        self.assertIn('Rapporto aggiornato', root.clipboard_get())
        self.assertEqual(getter.call_count, 2)  # copying uses what was shown

    def test_refresh_failure_shows_safe_error_without_exception_text(self):
        self.assertIsNotNone(importlib.util.find_spec('runtime_diagnostics_ui'))
        from runtime_diagnostics_ui import ServiceDiagnosticsWindow
        import tkinter as tk
        root = tk.Tk();root.withdraw();self.addCleanup(root.destroy)
        view = ServiceDiagnosticsWindow(root, get_report=Mock(side_effect=RuntimeError('SECRET_TOKEN')))
        self.addCleanup(view.window.destroy)
        report = view.text.get('1.0','end')
        self.assertIn('non disponibile', report)
        self.assertNotIn('SECRET_TOKEN', report)

    def test_settings_callback_samples_services_without_native_model_or_network(self):
        import test_activity_status as fixture
        fixture.ActivityStatusTests.setUpClass()
        main = fixture.ActivityStatusTests.main
        callback = next((n for n in main.body if isinstance(n,ast.FunctionDef)
                         and n.name=='snapshot_services_report'), None)
        self.assertIsNotNone(callback, 'Settings report not connected to real runtime')
        from runtime_diagnostics import RuntimeEventCounters,collect_runtime_evidence,format_runtime_evidence
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            env=dict(snapshot_runtime_evidence=lambda:collect_runtime_evidence(
                gpt_enabled=False,gpt_connected=False,sdk_installed=False,node_available=False,
                bridge_file_present=False,bridge_running=False,voice_present=False,
                voice_mode='standby',voice_listening=False,voice_model_present=False,
                local_engine_present=False,local_store_present=False,workspace_present=False,
                workspace_store_present=False,counters=RuntimeEventCounters()),
                format_runtime_evidence=format_runtime_evidence,Path=Path,
                gemma_session=[None],memory_enabled=SimpleNamespace(get=lambda:False),
                gpt_enabled=SimpleNamespace(get=lambda:False),telegram_auto=SimpleNamespace(get=lambda:True),
                telegram_bridge=None,selected_telegram_contacts=lambda:[],credentials_present=lambda:False,
                get_gemma_session=Mock(side_effect=AssertionError('must not start model')))
            exec(compile(ast.Module(body=[callback],type_ignores=[]),'settings-report','exec'),env)
            report=env['snapshot_services_report']()
            self.assertIn('Telegram', report)
            self.assertIn('Gemma', report)
            self.assertIn('Microfono', report)
            self.assertIn('non avviato', report)
            self.assertNotIn('SECRET', report)
            env['get_gemma_session'].assert_not_called()

    def test_shared_diagnostic_command_opens_services_instead_of_running_static_audit(self):
        import test_activity_status as fixture
        from self_diagnostics import diagnostic_request
        fixture.ActivityStatusTests.setUpClass()
        harness=fixture.ActivityStatusTests()
        env=dict(is_external_review_request=lambda _:False,diagnostic_request=diagnostic_request,
                 open_service_diagnostics=Mock(),inspect_jarvis=Mock(),write_line=Mock(),
                 diagnostic_busy=False,pending_external_review=False,last_diagnostic_audit=None,
                 last_runtime_evidence=None)
        callback=harness.callback('try_self_diagnostic',env)
        self.assertTrue(callback('Jarvis, apri diagnostica servizi'))
        env['open_service_diagnostics'].assert_called_once()
        env['inspect_jarvis'].assert_not_called()
        for phrase in ('non aprire diagnostica servizi','cosa è la diagnostica servizi?'):
            self.assertIsNone(diagnostic_request(phrase))

    def test_actual_open_callback_reuses_view_and_reopens_after_close(self):
        import test_activity_status as fixture
        import tkinter as tk
        fixture.ActivityStatusTests.setUpClass()
        root=tk.Tk();root.withdraw();self.addCleanup(root.destroy)
        settings=tk.Toplevel(root);settings.withdraw();self.addCleanup(settings.destroy)
        getter=Mock(return_value='Rapporto')
        env=dict(root=root,settings_window=settings,snapshot_services_report=getter)
        callback=fixture.ActivityStatusTests().callback('open_service_diagnostics',env)
        callback();first=root._jarvis_services_diagnostic
        root.update()
        callback();self.assertIs(root._jarvis_services_diagnostic,first)
        first.window.event_generate('<Escape>');root.update()
        self.assertFalse(first.window.winfo_exists())
        callback();second=root._jarvis_services_diagnostic
        self.addCleanup(second.window.destroy)
        root.update()
        self.assertIsNot(first,second)
        self.assertIn('Rapporto',second.text.get('1.0','end'))
        self.assertFalse(bool(settings.winfo_viewable()))
