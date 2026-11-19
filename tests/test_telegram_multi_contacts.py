"""Telegram multi-contact and owner-initiated OGG flow: no network required."""
from __future__ import annotations

import ast
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from telegram_bridge import TelegramBridge, TelegramBridgeError, accepted_private_message
from telegram_directory import _display_name, _safe_user
from telegram_outbound_flow import (
    VoiceSendDialog, parse_telegram_send_intent, resolve_selected_recipient,
)
from settings import load_settings, normalize_telegram_contacts, save_settings


CONTACTS = [
    {"id": 11, "name": "Nico Rossi", "enabled": True},
    {"id": 12, "name": "Anna Bianchi", "enabled": True},
    {"id": 13, "name": "Marco", "enabled": False},
]


class FakeClock:
    def __init__(self):
        self.now = 20.
    def __call__(self):
        return self.now


class TelegramContactTests(unittest.TestCase):
    def test_existing_single_contact_is_migrated_only_if_absent(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"settings.json"
            path.write_text('{"gpt_enabled":true,"telegram_peer_id":99,'
                            '"telegram_contact_name":"Nico"}', encoding="utf8")
            config = load_settings(path)
            self.assertEqual(config["telegram_contacts"],
                             [{"id":99,"name":"Nico","enabled":True}])
            config["telegram_contacts"] = []
            save_settings(config,path)
            self.assertEqual(load_settings(path)["telegram_contacts"], [])

    def test_contact_selection_is_durable_and_filters_bad_ids(self):
        from settings import DEFAULTS
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"settings.json"
            config = {**DEFAULTS, "telegram_contacts": CONTACTS}
            save_settings(config,path)
            self.assertEqual(load_settings(path)["telegram_contacts"], CONTACTS)
            self.assertEqual(normalize_telegram_contacts([
                {"id":11,"name":"Nico","enabled":True},
                {"id":11,"name":"duplicate","enabled":True},
                {"id":False,"name":"bad","enabled":True},
                {"id":13,"name":"Name","enabled":False},
            ]), [{"id":11,"name":"Nico","enabled":True},
                  {"id":13,"name":"Name","enabled":False}])
            self.assertFalse(any(c["enabled"] for c in
                                 normalize_telegram_contacts([
                                     {"id":13,"name":"Off","enabled":False}])))

    def test_default_deny_tg_peer_by_numeric_id(self):
        allowed={11:"Nico Rossi",12:"Anna Bianchi"}
        self.assertTrue(accepted_private_message(11,True,False,allowed))
        self.assertTrue(accepted_private_message(12,True,False,allowed))
        self.assertFalse(accepted_private_message(13,True,False,allowed))
        self.assertFalse(accepted_private_message(11,False,False,allowed))
        self.assertFalse(accepted_private_message(11,True,True,allowed))
        self.assertFalse(accepted_private_message(True,True,False,allowed))

    def test_bridge_stores_only_checked_contacts(self):
        bridge=TelegramBridge(None,0,"",lambda _:"",lambda _:None,
                              allowed_contacts=CONTACTS)
        self.assertEqual(bridge.allowed_contacts,
                         {11:"Nico Rossi",12:"Anna Bianchi"})
        self.assertEqual(bridge._last_sent,{})
        with self.assertRaises(TelegramBridgeError):
            TelegramBridge(None,0,"",lambda _:"",lambda _:None,
                           allowed_contacts=[CONTACTS[-1]])

    def test_directory_never_accepts_bot_self_or_deleted(self):
        self.assertFalse(_safe_user(SimpleNamespace(id=8,bot=True)))
        self.assertFalse(_safe_user(SimpleNamespace(id=9,is_self=True)))
        self.assertFalse(_safe_user(SimpleNamespace(id=10,deleted=True)))
        self.assertTrue(_safe_user(SimpleNamespace(id=11)))
        self.assertEqual(_display_name(SimpleNamespace(
            first_name="Nico",last_name="Rossi")), "Nico Rossi")


class TelegramVoiceDialogTests(unittest.TestCase):
    def test_recognizes_requested_speech_and_text(self):
        for value in ("Lumi, manda un messaggio a Nico",
                      "manda un messaggio vocale a Nico",
                      "invia audio a Nico",
                      "Ok Lumi manda vocale a Nico"):
            self.assertEqual(parse_telegram_send_intent(value),"Nico")
        for value in ("rispondi a Nico", "manda un messaggio",
                      "manda un messaggio a", "fai un'autodiagnosi"):
            self.assertIsNone(parse_telegram_send_intent(value))

    def test_full_name_or_unique_first_name_never_guessed(self):
        self.assertEqual(resolve_selected_recipient("Nico",CONTACTS)[1]["id"],11)
        self.assertEqual(resolve_selected_recipient("Nico Rossi",CONTACTS)[1]["id"],11)
        self.assertEqual(resolve_selected_recipient("Marco",CONTACTS)[0],
                         "not_selected")
        with_duplicates=CONTACTS+[{"id":14,"name":"Nico Bianchi","enabled":True}]
        self.assertEqual(resolve_selected_recipient("Nico",with_duplicates)[0],
                         "ambiguous")
        self.assertEqual(resolve_selected_recipient("Nico Rossi",with_duplicates)[1]["id"],11)

    def test_requires_message_confirmation_then_one_shot_send(self):
        clock=FakeClock()
        flow=VoiceSendDialog(clock=clock)
        self.assertEqual(flow.begin(CONTACTS[0]).kind,"ask_message")
        self.assertEqual(flow.receive("Buongiorno!",CONTACTS).kind,"ask_confirm")
        reply=flow.receive("confermo",CONTACTS)
        self.assertEqual((reply.kind,reply.peer_id,reply.message),
                         ("send",11,"Buongiorno!"))
        self.assertFalse(flow.pending)
        self.assertEqual(flow.receive("confermo",CONTACTS).kind,"not_pending")

    def test_cancel_revocation_and_timeout_must_not_send(self):
        clock=FakeClock()
        flow=VoiceSendDialog(clock=clock,ttl=5)
        flow.begin(CONTACTS[0])
        self.assertEqual(flow.receive("annulla",CONTACTS).kind,"cancelled")
        flow.begin(CONTACTS[0])
        flow.receive("Messaggio",CONTACTS)
        changed=[{**CONTACTS[0],"enabled":False},CONTACTS[1]]
        self.assertEqual(flow.receive("confermo",changed).kind,"revoked")
        flow.begin(CONTACTS[0])
        clock.now+=6
        self.assertEqual(flow.receive("confermo",CONTACTS).kind,"expired")

    def test_gui_requires_confirmation_and_voice_note_true(self):
        source=(Path(__file__).resolve().parent.parent/"telegram_ui.py").read_text(encoding="utf8")
        sender=(Path(__file__).resolve().parent.parent/"telegram_directory.py").read_text(encoding="utf8")
        ui=ast.parse(source)
        send=ast.parse(sender)
        self.assertIn("messagebox.askyesno",source)
        self.assertIn("voice_note=True",sender)
        self.assertIn("make_telegram_voice",sender)
        self.assertIn("on_send(contact",source)
        self.assertTrue(ui and send)

    def test_telegram_speech_routes_before_gpt_request(self):
        source=(Path(__file__).resolve().parent.parent/"jarvis.py").read_text(encoding="utf8")
        start=source.index("    def send_console_input(event=None) -> None:")
        end=source.index("    def toggle_console_tools() -> None:",start)
        body=source[start:end]
        self.assertLess(body.index("try_telegram_voice_send(message)"),
                        body.index("submit_gpt()"))
        # Pulsanti della sezione Telegram: spostata in telegram_addon/lumi_ui.py (divisione
        # di jarvis.py, passo 2a); il collegamento deve restare uguale.
        ui=(Path(__file__).resolve().parent.parent/"telegram_addon"/"lumi_ui.py").read_text(encoding="utf8")
        self.assertIn("telegram_contacts_button.configure(command=d.open_telegram_contact_list)",ui)
        self.assertIn("telegram_send_button.configure(command=open_telegram_manual_send)",ui)
        self.assertIn("telegram_owner_sent",source)
        self.assertIn("telegram_owner_error",source)


class TelegramOutboundNetworkBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def test_revoke_before_send_prevents_network_call(self):
        from unittest.mock import patch
        from telegram_directory import _send_telegram_voice, TelegramDirectoryError
        import telegram_directory

        class FakeClient:
            def __init__(self):
                self.sent = 0
                self.closed = False
            async def send_file(self, peer, path, voice_note=False):
                self.sent += 1
                self.voice_note = voice_note
                return SimpleNamespace(id=123)
            async def disconnect(self):
                self.closed = True

        client = FakeClient()
        async def fake_auth():
            return client
        async def fake_contacts(_client):
            return {11: ("Nico Rossi", object())}
        def fake_voice(_text,folder,_voice=""):
            file = Path(folder)/"test.ogg"
            file.write_bytes(b"not real audio")
            return file

        with patch.object(telegram_directory, "_authenticated_client", fake_auth), \
             patch.object(telegram_directory, "verified_contact_entities", fake_contacts), \
             patch.object(telegram_directory, "make_telegram_voice", fake_voice):
            with self.assertRaises(TelegramDirectoryError):
                await _send_telegram_voice(11,"Ciao Nico","",lambda:False)
            self.assertEqual(client.sent,0)
            self.assertTrue(client.closed)
            client.closed = False
            result = await _send_telegram_voice(11,"Ciao Nico","",lambda:True)
            self.assertEqual(result,123)
            self.assertEqual(client.sent,1)
            self.assertTrue(client.voice_note)
            self.assertTrue(client.closed)


if __name__ == "__main__":
    unittest.main()
