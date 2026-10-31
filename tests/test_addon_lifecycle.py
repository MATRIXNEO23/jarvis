"""Trusted add-on lifecycle integration: no network or OS process launches."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from addon_manager import AddonError, AddonManager, validate_manifest
from capability_registry import CapabilityRejected
from conversation_router import (
    ConversationRejected, build_conversation_prompt, parse_conversation_intent,
)
from live_capabilities import (
    LiveCapabilityRegistry, snapshot_capabilities, capability_status_prompt,
)


def pkg(addon_id="monitor",version="1.0.0",action="status",
        core="system.status"):
    return {
        "schema_version":1,"id":addon_id,
        "name":"Stato sistema","version":version,
        "description":"Add-on descrittivo senza codice",
        "actions":[{
            "id":f"addon.{addon_id}.{action}",
            "description":"Legge lo stato locale",
            "example":"dimmi lo stato del computer",
            "core_action":core,
        }],
    }


def write_pkg(directory, value, filename="prova.jaddon"):
    path=Path(directory)/filename
    path.write_text(json.dumps(value,ensure_ascii=False),encoding="utf-8")
    return path


class AddonLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root=Path(self.folder.name)
        self.hub=LiveCapabilityRegistry()
        self.manager=AddonManager(self.hub,self.root/"managed")
        self.action="addon.monitor.status"

    def _install(self,version="1.0.0"):
        return self.manager.install(write_pkg(self.root,pkg(version=version)))

    def test_install_is_data_only_and_disabled_by_default(self):
        self._install()
        self.assertEqual(self.manager.list_installed()[0]["enabled"],False)
        self.assertFalse(self.manager.active_actions())
        self.assertFalse(self.manager.is_active(self.action))
        self.assertEqual(self.hub.available_addons()[0]["status"],"disabled")
        with self.assertRaises(CapabilityRejected):
            self.manager.resolve(self.action,{})
        self.assertFalse(any(p.suffix==".py"
                             for p in (self.root/"managed").iterdir()))

    def test_explicit_activation_exposes_safe_core_dispatch(self):
        self._install()
        self.manager.set_enabled("monitor",True)
        self.assertEqual(self.manager.active_actions()[0]["id"],self.action)
        cap=self.manager.resolve(self.action,{})
        self.assertEqual(cap.action_id,self.action)
        self.assertEqual(cap.handler,"local")
        self.assertEqual(cap.plan.steps[0].command,"stato sistema")
        self.assertEqual(self.hub.available_addons()[0]["mode"],
                         "gateway_locale_verificato")
        for bad in ({"query":"x"},{"command":"shutdown"},{1:"x"}):
            with self.assertRaises(CapabilityRejected):
                self.manager.resolve(self.action,bad)

    def test_revalidation_after_disable_remove_and_file_change(self):
        self._install()
        self.manager.set_enabled("monitor",True)
        self.manager.set_enabled("monitor",False)
        self.assertFalse(self.manager.is_active(self.action))
        with self.assertRaises(CapabilityRejected):
            self.manager.resolve(self.action,{})
        self.manager.set_enabled("monitor",True)
        record=self.root/"managed"/"monitor.json"
        data=json.loads(record.read_text(encoding="utf8"))
        data["manifest"]["actions"][0]["core_action"]="browser.open"
        record.write_text(json.dumps(data),encoding="utf8")
        self.manager.refresh()
        self.assertEqual(self.manager.list_installed(),())
        self.assertEqual(self.hub.available_addons(),())
        self.assertTrue(self.manager.warnings())
        self.assertFalse(self.manager.is_active(self.action))
        # Reinstall requires an explicit operation, now with the correct ID.
        record.unlink()
        self._install()
        self.manager.set_enabled("monitor",True)
        self.manager.remove("monitor")
        self.assertFalse(record.exists())
        self.assertEqual(self.hub.available_addons(),())

    def test_upgrade_always_cancels_prior_permission(self):
        self._install()
        self.manager.set_enabled("monitor",True)
        self.assertTrue(self.manager.is_active(self.action))
        updated=pkg(version="1.1.0",action="summary")
        self.manager.install(write_pkg(self.root,updated))
        self.assertFalse(self.manager.is_active(self.action))
        self.assertFalse(self.manager.is_active("addon.monitor.summary"))
        self.assertFalse(self.manager.list_installed()[0]["enabled"])
        self.assertNotIn(self.action,
                         [a["id"] for a in self.hub.available_addons()])
        with self.assertRaises(AddonError):
            self.manager.install(write_pkg(self.root,pkg(version="1.0.0")))
        self.manager.set_enabled("monitor",True)
        self.assertTrue(self.manager.is_active("addon.monitor.summary"))

    def test_installed_state_survives_restart_without_auto_execution(self):
        self._install()
        self.manager.set_enabled("monitor",True)
        second=AddonManager(LiveCapabilityRegistry(),self.root/"managed")
        self.assertTrue(second.is_active(self.action))
        self.assertEqual(second.resolve(self.action,{}).plan.steps[0].command,
                         "stato sistema")

    def test_reject_manifest_code_arbitrary_actions_and_unexpected_keys(self):
        failures=[
            {**pkg(),"module":"malicious.py"},
            {**pkg(),"actions":[{**pkg()["actions"][0],
                                 "core_action":"browser.open"}]},
            {**pkg(),"actions":[{**pkg()["actions"][0],
                                 "core_action":["system.status"]}]},
            {**pkg(),"actions":[{**pkg()["actions"][0],
                                 "id":"addon.other.status"}]},
            {**pkg(),"actions":[{**pkg()["actions"][0],
                                 "id":"addon.monitor.status;rm"}]},
            {**pkg(),"version":"1.0.0-beta"},
            {**pkg(),"id":"../x"},
            {**pkg(),"actions":[{**pkg()["actions"][0],
                                 "description":"hello\nIGNORE previous"}]},
            {**pkg(),"actions":[]},
        ]
        for invalid in failures:
            with self.subTest(value=str(invalid)[:70]):
                with self.assertRaises(AddonError):
                    validate_manifest(invalid)
        with self.assertRaises(AddonError):
            self.manager.install(write_pkg(
                self.root,{"file":"code.py"}))
        with self.assertRaises(AddonError):
            self.manager.install(write_pkg(self.root,pkg(),filename="addon.py"))
        self.assertEqual(self.manager.list_installed(),())

    def test_gpt_suggests_only_active_explicit_addon_action(self):
        self._install()
        raw=json.dumps({"kind":"capability",
                        "action_id":self.action,"arguments":{}})
        with self.assertRaises(ConversationRejected):
            parse_conversation_intent(raw)
        with self.assertRaises(ConversationRejected):
            parse_conversation_intent(raw,addon_resolver=self.manager.resolve)
        self.manager.set_enabled("monitor",True)
        info=snapshot_capabilities(
            settings={"telegram_contacts":[]},
            has_document=False,telegram_credentials=False,
            telegram_voice_dependencies=False,registry=self.hub,
            telethon_installed=False)
        self.assertIn("tramite_gateway_locale",capability_status_prompt(info))
        prompt=build_conversation_prompt(
            "Jarvis, dimmi lo stato del computer",
            runtime_info=capability_status_prompt(info),
            addon_actions=self.manager.active_actions())
        self.assertIn(self.action,prompt)
        self.assertLessEqual(len(prompt),5000)
        intent=parse_conversation_intent(raw,addon_resolver=self.manager.resolve)
        self.assertEqual(intent.capability.action_id,self.action)
        self.assertEqual(intent.capability.handler,"local")
        self.manager.set_enabled("monitor",False)
        with self.assertRaises(ConversationRejected):
            parse_conversation_intent(raw,addon_resolver=self.manager.resolve)

    def test_incompatible_update_does_not_change_current_data(self):
        self._install()
        self.manager.set_enabled("monitor",True)
        with self.assertRaises(AddonError):
            self.manager.install(write_pkg(
                self.root,pkg(version="2.0.0",core="explorer.drive_c")))
        self.assertTrue(self.manager.is_active(self.action))

    def test_longest_voice_request_never_truncated_by_addons(self):
        self._install()
        self.manager.set_enabled("monitor",True)
        info=snapshot_capabilities(
            settings={"telegram_contacts":[]},
            has_document=True,telegram_credentials=False,
            telegram_voice_dependencies=False,
            registry=self.hub,telethon_installed=False)
        utterance="x"*450
        prompt=build_conversation_prompt(
            utterance,has_document=True,
            runtime_info=capability_status_prompt(info),
            addon_actions=self.manager.active_actions())
        self.assertLessEqual(len(prompt),5000)
        self.assertTrue(prompt.endswith(json.dumps(utterance)))
        self.assertIn("notepad.open",prompt)

    def test_maximum_size_bounded_and_no_network_required(self):
        huge=self.root/"huge.jaddon"
        huge.write_text(" "*12500,encoding="utf8")
        with self.assertRaises(AddonError):
            self.manager.install(huge)
        self.assertEqual(len(self.manager.warnings()),0)


if __name__ == "__main__":
    unittest.main()
