"""Offline checks of the dedicated Windows Telegram-50 trial profile."""
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from prepara_test_telegram50 import prepare_trial
from settings import default_path, load_settings, save_settings


class TelegramTrialTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        home=Path(self.temp.name)/"Local"
        self.original=home/"Jarvis"
        self.trial=home/"Jarvis-Telegram50-Trial"
        self.original.mkdir(parents=True)
        current=load_settings(self.original/"settings.json")
        current["telegram_enabled"]=True
        current["auto_listen"]=True
        current["telegram_contacts"]=[{"id":123,"name":"Amico","enabled":True}]
        save_settings(current,self.original/"settings.json")
        self.original_auth=self.original/"telegram-auth.dpapi"
        self.original_auth.write_bytes(b"JARVIS-TG1\nEncrypted-test-data")
        self.original_db=self.original/"jarvis_workspaces.sqlite3"
        with closing(sqlite3.connect(self.original_db)) as db:
            db.execute("CREATE TABLE sample(value TEXT)")
            db.execute("INSERT INTO sample(value) VALUES('original')")
            db.commit()

    def test_profile_isolated_and_original_files_unchanged(self):
        original_settings=self.original.joinpath("settings.json").read_bytes()
        original_auth=self.original_auth.read_bytes()
        original_db=self.original_db.read_bytes()
        result=prepare_trial(self.original,self.trial)
        self.assertTrue(result)
        self.assertEqual(self.original.joinpath("settings.json").read_bytes(),original_settings)
        self.assertEqual(self.original_auth.read_bytes(),original_auth)
        self.assertEqual(self.original_db.read_bytes(),original_db)
        self.assertTrue((self.trial/"jarvis_workspaces.sqlite3").is_file())
        self.assertEqual((self.trial/"telegram-auth.dpapi").read_bytes(),original_auth)
        copied=load_settings(self.trial/"settings.json")
        self.assertFalse(copied["telegram_enabled"])
        self.assertTrue(copied["auto_listen"])
        self.assertEqual(copied["telegram_contacts"][0]["id"],123)
        with closing(sqlite3.connect(self.trial/"jarvis_workspaces.sqlite3")) as db:
            self.assertEqual(db.execute("SELECT value FROM sample").fetchone()[0],
                             "original")
            db.execute("UPDATE sample SET value='test-only'")
            db.commit()
        with closing(sqlite3.connect(self.original_db)) as db:
            self.assertEqual(db.execute("SELECT value FROM sample").fetchone()[0],
                             "original")

    def test_repeat_launch_does_not_overwrite_trial_history_or_settings(self):
        prepare_trial(self.original,self.trial)
        with closing(sqlite3.connect(self.trial/"jarvis_workspaces.sqlite3")) as db:
            db.execute("UPDATE sample SET value='keep-trial'")
            db.commit()
        settings=load_settings(self.trial/"settings.json")
        settings["telegram_enabled"]=True
        save_settings(settings,self.trial/"settings.json")
        prepare_trial(self.original,self.trial)
        with closing(sqlite3.connect(self.trial/"jarvis_workspaces.sqlite3")) as db:
            self.assertEqual(db.execute("SELECT value FROM sample").fetchone()[0],
                             "keep-trial")
        self.assertTrue(load_settings(self.trial/"settings.json")["telegram_enabled"])

    def test_existing_trial_enables_microphone_once_and_then_respects_off(self):
        prepare_trial(self.original,self.trial)
        settings_path=self.trial/"settings.json"
        current=load_settings(settings_path)
        current["auto_listen"]=False
        save_settings(current,settings_path)
        (self.trial/".microphone-on-startup-v2").unlink()
        prepare_trial(self.original,self.trial)
        self.assertTrue(load_settings(settings_path)["auto_listen"])
        current=load_settings(settings_path)
        current["auto_listen"]=False
        save_settings(current,settings_path)
        prepare_trial(self.original,self.trial)
        self.assertFalse(load_settings(settings_path)["auto_listen"])

    def test_other_memory_databases_and_addons_are_trial_only(self):
        with closing(sqlite3.connect(self.original/"second_brain.sqlite3")) as db:
            db.execute("CREATE TABLE facts(value TEXT)")
            db.execute("INSERT INTO facts VALUES('owner')")
            db.commit()
        addon_dir=self.original/"addons"
        addon_dir.mkdir()
        (addon_dir/"diagnostica.json").write_text('{"example":1}',encoding="utf-8")
        (self.original/"addons-approvals.json").write_text(
            '{"diagnostica":"approved"}',encoding="utf-8")
        prepare_trial(self.original,self.trial)
        self.assertTrue((self.trial/"addons"/"diagnostica.json").exists())
        self.assertTrue((self.trial/"addons-approvals.json").exists())
        with closing(sqlite3.connect(self.trial/"second_brain.sqlite3")) as db:
            self.assertEqual(db.execute("SELECT value FROM facts").fetchone()[0],
                             "owner")
            db.execute("UPDATE facts SET value='trial'")
            db.commit()
        with closing(sqlite3.connect(self.original/"second_brain.sqlite3")) as db:
            self.assertEqual(db.execute("SELECT value FROM facts").fetchone()[0],
                             "owner")

    def test_single_launcher_always_prepares_isolated_trial(self):
        launcher=(Path(__file__).resolve().parent.parent/"avvia_jarvis.bat").read_text(
            encoding="utf-8")
        self.assertIn("JARVIS_TRIAL_HOME",launcher)
        self.assertIn("prepara_test_telegram50.py",launcher)
        self.assertIn("py -3 jarvis.py",launcher)
        self.assertFalse(
            (Path(__file__).resolve().parent.parent/"AVVIA_TEST_TELEGRAM50.bat").exists())

    def test_default_path_redirects_only_when_explicitly_enabled(self):
        with patch.dict(os.environ,{"JARVIS_TRIAL_HOME":str(self.trial)}):
            self.assertEqual(default_path(),self.trial/"settings.json")
        with patch.dict(os.environ,{"JARVIS_TRIAL_HOME":""}):
            self.assertNotEqual(default_path(),self.trial/"settings.json")

    def test_refuses_same_or_nested_source_folder(self):
        with self.assertRaises(RuntimeError):
            prepare_trial(self.original,self.original)
        with self.assertRaises(RuntimeError):
            prepare_trial(self.original,self.original/"child")


if __name__=="__main__":
    unittest.main()
