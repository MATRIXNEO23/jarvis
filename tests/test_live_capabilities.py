"""Live GPT capability registry: no network, SDK login or Telegram sends."""
from __future__ import annotations

from dataclasses import replace
import json
import unittest
from unittest.mock import patch

from capability_registry import (
    CapabilityRejected, capability_prompt, resolve_capability,
)
from conversation_router import build_conversation_prompt, parse_conversation_intent
from jarvis_persona import build_chat_prompt
from live_capabilities import (
    AddonBinding, LiveCapabilityRegistry, capability_status_prompt,
    snapshot_capabilities,
)


def state(contacts=None, *, credentials=True, voice=True,
          telethon=True, auto=False, has_document=False, registry=None):
    data={"telegram_contacts": contacts if contacts is not None else [
        {"id":12,"name":"Nico","enabled":True},
    ],"telegram_enabled":auto}
    return snapshot_capabilities(
        settings=data, has_document=has_document,
        telegram_credentials=credentials,
        telegram_voice_dependencies=voice,
        voice_stream_open=False, registry=registry,
        telethon_installed=telethon)


class LiveCapabilityRegistryTests(unittest.TestCase):
    def test_telegram_rechecks_settings_before_every_turn(self):
        ok=state()
        no_peer=state(contacts=[])
        disabled=state(contacts=[
            {"id":12,"name":"Nico","enabled":False}])
        self.assertTrue(ok["telegram_voice_send"])
        self.assertFalse(no_peer["telegram_voice_send"])
        self.assertFalse(disabled["telegram_voice_send"])
        self.assertNotEqual(ok["revision"],disabled["revision"])
        self.assertNotIn("Nico",capability_status_prompt(ok))
        self.assertNotIn("12",capability_status_prompt(ok))

    def test_dependency_and_auto_switch_states(self):
        for args in ({"credentials":False},{"voice":False},{"telethon":False}):
            with self.subTest(args=args):
                self.assertFalse(state(**args)["telegram_voice_send"])
        self.assertFalse(state(auto=False)["telegram_auto_reply"])
        self.assertTrue(state(auto=True)["telegram_auto_reply"])
        self.assertNotEqual(state(auto=False)["revision"],state(auto=True)["revision"])

    def test_dialog_and_file_catalog_are_not_authority(self):
        self.assertNotIn("telegram.voice.start",capability_prompt())
        self.assertIn("telegram.voice.start",
                      capability_prompt(telegram_send_ready=True))
        with self.assertRaises(CapabilityRejected):
            resolve_capability("telegram.voice.start",{"recipient":"Nico"})
        resolved=resolve_capability(
            "telegram.voice.start",{"recipient":"Nico"},
            telegram_send_ready=True)
        self.assertEqual(resolved.handler,"telegram_voice_dialog")
        self.assertEqual(resolved.recipient,"Nico")
        for bad in ({},{"recipient":"Nico","message":"Ciao"},
                    {"recipient":"Nico\nistruzione"},
                    {"recipient":"Nico","peer_id":12}):
            with self.subTest(args=bad):
                with self.assertRaises(CapabilityRejected):
                    resolve_capability("telegram.voice.start",bad,
                                       telegram_send_ready=True)

    def test_external_gpt_can_propose_only_first_dialog_step(self):
        payload=json.dumps({"kind":"capability",
                            "action_id":"telegram.voice.start",
                            "arguments":{"recipient":"Nico"}})
        with self.assertRaises(Exception):
            parse_conversation_intent(payload,telegram_send_ready=False)
        result=parse_conversation_intent(payload,telegram_send_ready=True)
        self.assertEqual(result.capability.handler,"telegram_voice_dialog")
        self.assertEqual(result.capability.recipient,"Nico")

    def test_prompts_get_new_version_while_preserving_latest_user_request(self):
        on=state(auto=True)
        off=state(contacts=[])
        say_on=capability_status_prompt(on)
        say_off=capability_status_prompt(off)
        self.assertNotEqual(say_on,say_off)
        one=build_conversation_prompt(
            "Mandami un vocale a Nico",
            runtime_info=say_on,telegram_send_ready=True)
        two=build_conversation_prompt(
            "Mandami un vocale a Nico",
            runtime_info=say_off,telegram_send_ready=False)
        self.assertIn("telegram.voice.start",one)
        self.assertNotIn('"id":"telegram.voice.start"',two)
        self.assertIn("non_disponibile",two)
        self.assertTrue(one.endswith('"Mandami un vocale a Nico"'))
        self.assertLessEqual(len(one),5000)
        typed=build_chat_prompt(
            "Che cosa sai fare?",runtime_info=say_on)
        self.assertIn("telegram_vocale",typed)
        self.assertTrue(typed.endswith('"Che cosa sai fare?"'))
        self.assertLessEqual(len(typed),5000)
        long=build_conversation_prompt(
            "x"*450,has_document=True,
            runtime_info=say_on,telegram_send_ready=True)
        self.assertLessEqual(len(long),5000)

    def test_registration_unregistration_and_toggle_update_live(self):
        hub=LiveCapabilityRegistry()
        active={"value":True}
        adapter=AddonBinding(
            "addon.sample.read_status", "Lettura stato componente di prova",
            availability=lambda:active["value"],handler=lambda:None)
        first=state(registry=hub)
        hub.register(adapter)
        second=state(registry=hub)
        self.assertNotEqual(first["revision"],second["revision"])
        self.assertEqual(second["addons"][0]["status"],"installed")
        active["value"]=False
        third=state(registry=hub)
        self.assertEqual(third["addons"][0]["status"],"disabled")
        self.assertNotEqual(third["revision"],second["revision"])
        self.assertIn("non_abilitata",capability_status_prompt(third))
        hub.unregister("addon.sample.read_status")
        self.assertEqual(state(registry=hub)["addons"],())
        # Registration is descriptive; no GPT permissions were granted.
        with self.assertRaises(CapabilityRejected):
            resolve_capability("addon.sample.read_status",{})

    def test_reject_unverified_addon_descriptions_without_handler(self):
        hub=LiveCapabilityRegistry()
        for name in ("shell.run","addon.bad.run;rm","addon.ABC.run"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    hub.register(AddonBinding(
                        name,"Task",lambda:True,lambda:True))
        with self.assertRaises(ValueError):
            hub.register(AddonBinding("addon.safe.run","Task",
                                      lambda:True,None))

    def test_runtime_catalog_changes_change_revision(self):
        import live_capabilities
        from capability_registry import load_catalog
        before=load_catalog()
        changed=tuple({**entry,"description":entry["description"]+"."}
                      if i==0 else entry for i,entry in enumerate(before))
        with patch.object(live_capabilities,"load_catalog",return_value=before):
            initial=state()
        with patch.object(live_capabilities,"load_catalog",return_value=changed):
            updated=state()
        self.assertNotEqual(initial["revision"],updated["revision"])

    def test_no_private_data_leaves_status_summary(self):
        snap=state(contacts=[
            {"id":91234566,"name":"Segreto Personale","enabled":True}])
        output=capability_status_prompt(snap)
        self.assertNotIn("Segreto",output)
        self.assertNotIn("91234566",output)
        self.assertIn("contatti_autorizzati",output)


if __name__=="__main__":
    unittest.main()
