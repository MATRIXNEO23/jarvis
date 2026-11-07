"""JRV-AUD-018: temporary Windows profiles, actual settings/owner callbacks.

No live settings, credentials, microphone or account is touched. Manual recovery
below is fixture setup, not an automatic reset feature of Jarvis.
"""
import ast
import copy
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import test_activity_status as callbacks
from settings import DEFAULTS, load_settings, save_settings


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class SettingsRecoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.path = self.root / "settings.json"

    def assert_prudent(self, data):
        for flag in ("gpt_enabled", "auto_listen", "tts_enabled", "memory_enabled",
                     "telegram_enabled", "keep_awake_fullscreen"):
            self.assertIs(data[flag], False, flag)

    def load_with_warnings(self):
        warnings = []
        try:
            value = load_settings(self.path, warnings=warnings)
        except TypeError:
            self.fail("load_settings lacks optional warning collector")
        return value, warnings

    def test_truncated_settings_keep_mic_and_gpt_off_without_changing_original(self):
        original = b'{"gpt_enabled":false,"auto_listen":false'
        self.path.write_bytes(original)
        self.assert_prudent(load_settings(self.path))
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(set(self.root.iterdir()), {self.path})

    def test_invalid_utf8_settings_start_prudently_and_stay_untouched(self):
        original = b'\xff\xfe{"gpt_enabled":false}'
        self.path.write_bytes(original)
        self.assert_prudent(load_settings(self.path))
        self.assertEqual(self.path.read_bytes(), original)

    def test_read_permission_error_is_prudent_without_silent_overwrite(self):
        original = b'{"gpt_enabled":false,"auto_listen":false}'
        self.path.write_bytes(original)
        with patch.object(Path, "read_text", side_effect=PermissionError("Controlled unreadable profile")):
            value = load_settings(self.path)
        self.assert_prudent(value)
        self.assertEqual(self.path.read_bytes(), original)

    def test_nonobject_json_is_not_a_valid_first_installation_profile(self):
        for payload in ([], None, 1, "profile"):
            with self.subTest(payload=payload):
                self.path.write_text(json.dumps(payload), encoding="utf-8")
                self.assert_prudent(load_settings(self.path))

    def test_invalid_present_mic_or_gpt_flags_fail_prudently(self):
        for flag in ("gpt_enabled", "auto_listen"):
            for value in ("false", 0, 1, None, []):
                with self.subTest(flag=flag, invalid_value=value):
                    self.path.write_text(json.dumps({flag:value}), encoding="utf-8")
                    self.assert_prudent(load_settings(self.path))

    def test_warning_identifies_recovery_without_including_private_file_content(self):
        original = b'{"private":"DO_NOT_ECHO_THIS_VALUE",'
        self.path.write_bytes(original)
        value, warnings = self.load_with_warnings()
        self.assert_prudent(value)
        self.assertEqual(len(warnings), 1)
        self.assertIn(str(self.path), warnings[0])
        self.assertIn("ripristin", warnings[0].lower())
        self.assertNotIn("DO_NOT_ECHO_THIS_VALUE", warnings[0])
        self.assertEqual(self.path.read_bytes(), original)

    def test_missing_profile_retains_existing_installation_defaults_without_warnings(self):
        value, warnings = self.load_with_warnings()
        self.assertEqual(value, DEFAULTS)
        self.assertEqual(warnings, [])
        self.assertFalse(self.path.exists())

    def test_valid_and_legacy_profiles_retain_preferences_without_warnings_or_writes(self):
        for payload in ({"gpt_enabled":False}, {"gpt_enabled":True,"auto_listen":True},
                        {"gpt_enabled":False,"auto_listen":False,"tts_enabled":True,
                         "tts_voice":"Fixture voice","timer_volume":35}):
            with self.subTest(payload=payload):
                raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.path.write_bytes(raw)
                value, warnings = self.load_with_warnings()
                for key, wanted in payload.items():
                    self.assertEqual(value[key], wanted)
                self.assertEqual(warnings, [])
                self.assertEqual(self.path.read_bytes(), raw)

    def test_save_after_unreadable_load_or_dict_copy_cannot_replace_original(self):
        for copied in (False, True):
            with self.subTest(copied=copied):
                raw = b'{"gpt_enabled":false,'
                self.path.write_bytes(raw)
                value = load_settings(self.path)
                if copied:
                    value = dict(value)
                value["timer_volume"] = 25
                with self.assertRaisesRegex(OSError, "ripristin|recuper"):
                    save_settings(value, self.path)
                self.assertEqual(self.path.read_bytes(), raw)
                self.assertFalse(self.path.with_suffix(".tmp").exists())

    def test_corruption_after_valid_load_is_checked_again_before_save(self):
        save_settings(dict(DEFAULTS, gpt_enabled=False, auto_listen=False), self.path)
        value = load_settings(self.path)
        raw = b'{"gpt_enabled":false,"auto_listen":'
        self.path.write_bytes(raw)
        with self.assertRaises(OSError):
            save_settings(value, self.path)
        self.assertEqual(self.path.read_bytes(), raw)

    def test_save_rejects_existing_wrong_shape_flag_or_encoding(self):
        for raw in (b'[]', b'{"gpt_enabled":"false"}', b'{"auto_listen":null}', b'\xff'):
            with self.subTest(raw=raw):
                self.path.write_bytes(raw)
                with self.assertRaises(OSError):
                    save_settings(dict(DEFAULTS), self.path)
                self.assertEqual(self.path.read_bytes(), raw)

    def test_save_read_failure_does_not_create_temp_or_replace_unreadable_target(self):
        raw = b'{"gpt_enabled":false}'
        self.path.write_bytes(raw)
        with patch.object(Path, "read_text", side_effect=PermissionError("Controlled read denial")):
            with self.assertRaises(OSError):
                save_settings(dict(DEFAULTS), self.path)
        self.assertEqual(self.path.read_bytes(), raw)
        self.assertFalse(self.path.with_suffix(".tmp").exists())

    def test_guard_preserves_a_preexisting_temp_file_and_unrelated_history(self):
        raw = b'{'
        self.path.write_bytes(raw)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_bytes(b"preexisting recoverable temporary data")
        history = self.root / "history.sqlite3"
        history.write_bytes(b"unrelated history marker")
        with self.assertRaises(OSError):
            save_settings(dict(DEFAULTS), self.path)
        self.assertEqual(self.path.read_bytes(), raw)
        self.assertEqual(temporary.read_bytes(), b"preexisting recoverable temporary data")
        self.assertEqual(history.read_bytes(), b"unrelated history marker")

    def test_explicit_manual_restore_then_normal_save_keeps_backup(self):
        raw = b'{"gpt_enabled":false,'
        self.path.write_bytes(raw)
        backup = self.root / "settings-original.private-backup"
        backup.write_bytes(self.path.read_bytes())  # Explicit fixture/user action.
        self.path.write_text('{"gpt_enabled":false,"auto_listen":false}', encoding="utf-8")
        value, warnings = self.load_with_warnings()
        self.assertEqual(warnings, [])
        value["timer_volume"] = 25
        save_settings(value, self.path)
        restored = load_settings(self.path)
        self.assertFalse(restored["gpt_enabled"])
        self.assertFalse(restored["auto_listen"])
        self.assertEqual(restored["timer_volume"],25)
        self.assertEqual(backup.read_bytes(),raw)


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class SettingsRecoveryOwnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        callbacks.ActivityStatusTests.setUpClass()

    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "settings.json"
        self.enterContext(patch("settings.default_path",return_value=self.path))
        self.harness = callbacks.ActivityStatusTests()

    def startup(self):
        env = {"load_settings":load_settings}
        prefix = []
        for node in callbacks.ActivityStatusTests.main.body:
            if (isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="root"
                                                    for t in node.targets)):
                break
            prefix.append(copy.deepcopy(node))
        exec(compile(ast.fix_missing_locations(ast.Module(body=prefix,type_ignores=[])),
                     "real-settings-main-prefix","exec"),env)
        env.update(tk=SimpleNamespace(BooleanVar=callbacks.Value), closing=False,
                   change_voice_mode=Mock(), voice_mode=callbacks.Value("standby"),
                   GPT_CONVERSATION="conversazione_gpt", startup_greeting=lambda:"Pronto",
                   write_line=Mock(), speaker=Mock(), selected_voice=Mock(),
                   root=SimpleNamespace(after=Mock()), run_gpt=Mock())
        variables = []
        for node in callbacks.ActivityStatusTests.main.body:
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in
                    ("gpt_enabled","auto_listen_enabled","spoken_enabled") for t in node.targets):
                variables.append(copy.deepcopy(node))
        self.assertEqual(len(variables),3)
        exec(compile(ast.fix_missing_locations(ast.Module(body=variables,type_ignores=[])),
                     "real-settings-UI-values","exec"),env)
        self.harness.callback("speak_result",env)
        self.harness.callback("initial_launch",env)
        schedule = next(node for node in callbacks.ActivityStatusTests.main.body
                        if isinstance(node,ast.If) and isinstance(node.test,ast.Call)
                        and isinstance(node.test.func,ast.Attribute)
                        and isinstance(node.test.func.value,ast.Name)
                        and node.test.func.value.id=="gpt_enabled")
        exec(compile(ast.fix_missing_locations(ast.Module(body=[copy.deepcopy(schedule)],type_ignores=[])),
                     "real-GPT-startup-schedule","exec"),env)
        return env

    def test_corrupted_profile_never_autostarts_mic_gpt_or_tts_and_warns_once(self):
        raw = b'{"gpt_enabled":false,"auto_listen":'
        self.path.write_bytes(raw)
        env = self.startup()
        self.assertFalse(env["gpt_enabled"].get())
        self.assertFalse(env["auto_listen_enabled"].get())
        env["root"].after.assert_not_called()
        env["initial_launch"]()
        env["initial_launch"]()  # No repeating recovery warning if invoked again.
        env["change_voice_mode"].assert_not_called()
        env["speaker"].speak.assert_not_called()
        warnings = [call.args[0] for call in env["write_line"].call_args_list
                    if call.args[0].startswith("IMPOSTAZIONI >")]
        self.assertEqual(len(warnings),1)
        self.assertIn(str(self.path),warnings[0])
        self.assertEqual(self.path.read_bytes(),raw)

    def test_valid_opt_in_startup_keeps_existing_microphone_and_gpt_behavior(self):
        save_settings(dict(DEFAULTS), self.path)
        env = self.startup()
        self.assertTrue(env["gpt_enabled"].get())
        self.assertTrue(env["auto_listen_enabled"].get())
        env["root"].after.assert_called_once()
        env["initial_launch"]()
        env["change_voice_mode"].assert_called_once_with()
        self.assertEqual(env["voice_mode"].get(),env["GPT_CONVERSATION"])
        self.assertFalse(any(call.args[0].startswith("IMPOSTAZIONI >")
                             for call in env["write_line"].call_args_list))

    def test_telegram_reconfigure_surfaces_guard_failure_without_overwriting_profile(self):
        raw = b'{'
        self.path.write_bytes(raw)
        env = dict(telegram_bridge=Mock(),load_settings=load_settings,save_settings=save_settings,
                   settings=dict(DEFAULTS),telegram_auto=callbacks.Value(True),
                   telegram_voice_dialog=Mock(),telegram_status=callbacks.Value(""),
                   selected_telegram_contacts=lambda:[],write_line=Mock())
        self.harness.callback("telegram_reconfigure",env)()
        self.assertFalse(env["telegram_auto"].get())
        self.assertIn("Impossibile salvare",env["telegram_status"].get())
        self.assertEqual(self.path.read_bytes(),raw)


if __name__=="__main__":
    unittest.main()
