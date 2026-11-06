"""Offline tests: DPAPI payload never written raw, exact contact gate, orbit."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, call

from hud_orbits import (MARKER_COLORS, MAX_MARKERS, OrbitMarkers,
                        TELEGRAM_PULSE_DIM, orbit_position, sanitize_nodes)
from telegram_bridge import (
    accepted_private_message,telegram_assistant_prompt,clean_generated_reply)
from telegram_security import save_credentials,load_credentials
from settings import load_settings,save_settings


class OrbitsAndTelegramTests(unittest.TestCase):
    def test_project_and_telegram_colors_have_safe_bounded_orbits(self):
        self.assertEqual(sanitize_nodes([{"id":"a","name":"Cantiere","kind":"project"},
                                         {"id":"telegram:1","name":"Messaggi",
                                          "kind":"telegram"}]),
                         (("a","project","Cantiere"),
                          ("telegram:1","telegram","Messaggi")))
        self.assertEqual(sanitize_nodes([{"id":"x","name":"","kind":"project"}]),())
        self.assertEqual(len(sanitize_nodes(
            [{"id":str(i),"name":"P"+str(i),"kind":"project"}
             for i in range(70)])),MAX_MARKERS)
        p0=orbit_position(0,3,0,100,100,60)
        p1=orbit_position(1,3,0,100,100,60)
        self.assertNotEqual(p0,p1)
        self.assertNotEqual(p0,orbit_position(0,3,1,100,100,60))
        with self.assertRaises(ValueError):
            orbit_position(4,3,0,100,100,60)

    def test_telegram_marker_pulses_until_seen_and_remains_clickable(self):
        canvas = Mock()
        canvas.create_oval.side_effect = range(1, 5)
        open_chat = Mock()
        markers = OrbitMarkers(canvas, open_chat)
        node = {"id": "telegram:123", "name": "Contatto", "kind": "telegram_unread"}
        markers.update([node], 100, 100, 60, 0.1)
        self.assertIn(call(2, fill=MARKER_COLORS["telegram_unread"]),
                      canvas.itemconfigure.call_args_list)
        canvas.itemconfigure.reset_mock()
        markers.update([node], 100, 100, 60, 0.8)
        self.assertIn(call(2, fill=TELEGRAM_PULSE_DIM),
                      canvas.itemconfigure.call_args_list)
        markers._click(0)
        open_chat.assert_called_once_with("telegram:123")

        canvas.itemconfigure.reset_mock()
        node["kind"] = "telegram"
        markers.update([node], 100, 100, 60, 0.9)
        markers.update([node], 100, 100, 60, 1.5)
        self.assertEqual(canvas.create_oval.call_args.kwargs["fill"], MARKER_COLORS["telegram"])
        canvas.itemconfigure.assert_not_called()

    def test_only_exact_authorized_private_peer_can_be_replied(self):
        self.assertTrue(accepted_private_message(123,True,False,123))
        for args in ((123,False,False,123),(123,True,True,123),
                     (123,True,False,456),("123",True,False,123),
                     (123,True,False,0),(123,1,False,123)):
            self.assertFalse(accepted_private_message(*args))

    def test_telegram_prompt_uses_only_explicitly_authorized_notes(self):
        p=telegram_assistant_prompt(
            "Ciao, come sta?",
            context='{"recent":[{"utente":"Siamo amici"}]}',
            pending=[{"message":"Alberto ha detto che domani sarà libero"}])
        self.assertIn("non fingere",p)
        self.assertIn("domani sarà libero",p)
        self.assertIn("accesso ai file",p)
        self.assertNotIn("Progetto Segreto",p)
        self.assertEqual(clean_generated_reply("a"*800),"a"*430)
        self.assertEqual(clean_generated_reply("Il token di accesso"),"")
        self.assertEqual(clean_generated_reply("password: prova"),"")

    def test_session_credentials_encrypted_and_not_in_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/"secrets.dpapi"
            # Fake round-trip protector for CI; real Windows path uses DPAPI.
            def dummy(value,encrypt):
                return bytes(b ^ 0x5c for b in value)
            save_credentials(112233,"f"*32,"sessionsecret"*6,file,protect=dummy)
            raw=file.read_bytes()
            self.assertNotIn(b"sessionsecret",raw)
            self.assertNotIn(b'"api_hash"',raw)
            d=load_credentials(file,protect=dummy)
            self.assertEqual(d["api_id"],112233)
            self.assertEqual(d["api_hash"],"f"*32)
            settings=Path(folder)/"settings.json"
            config=load_settings(settings)
            self.assertFalse(config["telegram_enabled"])
            config.update({"telegram_enabled":True,
                           "telegram_peer_id":456,
                           "telegram_contact_name":"Contatto"})
            save_settings(config,settings)
            saved=settings.read_text(encoding="utf-8")
            self.assertNotIn("sessionsecret",saved)
            self.assertIn('"telegram_peer_id": 456',saved)


if __name__=="__main__":
    unittest.main()
