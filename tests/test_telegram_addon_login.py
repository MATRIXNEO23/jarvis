"""Accesso Telegram dentro Lumi: codice e password dal pop-up, salvataggio DPAPI
(simulato), nessuna sessione salvata se l'utente annulla."""
import asyncio
import sys
import types
import unittest
from unittest import mock


def fake_telethon(password_needed=False):
    errors = types.ModuleType("telethon.errors")

    class SessionPasswordNeededError(Exception):
        pass
    errors.SessionPasswordNeededError = SessionPasswordNeededError
    sessions = types.ModuleType("telethon.sessions")

    class StringSession:
        def save(self):
            return "SESSIONE"
    sessions.StringSession = StringSession

    class Client:
        def __init__(self, session, api_id, api_hash):
            self.session, self.authorized, self.calls = session, False, []

        async def connect(self):
            pass

        async def disconnect(self):
            pass

        async def is_user_authorized(self):
            return self.authorized

        async def send_code_request(self, phone):
            self.calls.append(("code", phone))

        async def sign_in(self, phone=None, code=None, password=None):
            if password_needed and password is None:
                raise SessionPasswordNeededError()
            self.authorized = True
    root = types.ModuleType("telethon")
    root.TelegramClient = Client
    return {"telethon": root, "telethon.errors": errors, "telethon.sessions": sessions}


class LoginTests(unittest.TestCase):
    def run_login(self, answers, password_needed=False):
        from telegram_addon import login
        saved = []
        security = types.ModuleType("telegram_security")
        security.save_credentials = lambda *a: saved.append(a)
        security.load_credentials = lambda: None
        modules = fake_telethon(password_needed)
        modules["telegram_security"] = security
        replies = iter(answers)
        with mock.patch.dict(sys.modules, modules):
            message = asyncio.run(login._login(12345, "a" * 32, "+393331234567",
                                               lambda *a, **k: next(replies), lambda t: None))
        return message, saved

    def test_code_from_popup_saves_credentials(self):
        message, saved = self.run_login(["12345"])
        self.assertTrue(message.startswith("Accesso salvato"))
        self.assertEqual(saved, [(12345, "a" * 32, "SESSIONE")])

    def test_two_step_password_and_cancel(self):
        message, saved = self.run_login(["12345", "segreta"], password_needed=True)
        self.assertTrue(message.startswith("Accesso salvato"))
        message, saved = self.run_login([None])
        self.assertIn("annullato", message)
        self.assertEqual(saved, [])


if __name__ == "__main__":
    unittest.main()
