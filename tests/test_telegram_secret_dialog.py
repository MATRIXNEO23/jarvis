"""Regression for Windows Telegram setup: masked clipboard paste and 2FA."""
from __future__ import annotations

import sys
import tkinter as tk
from unittest.mock import patch
import unittest

from configura_telegram import valid_api_hash
from telegram_secret_dialog import prompt_masked_secret, secret_length_ok


class TelegramSecretDialogTests(unittest.TestCase):
    def test_api_hash_validation_does_not_store_or_echo_input(self):
        self.assertTrue(valid_api_hash("a" * 32))
        self.assertTrue(valid_api_hash("abcdef0123456789ABCDEF0123456789"))
        self.assertFalse(valid_api_hash("a" * 31))
        self.assertFalse(valid_api_hash("a" * 33))
        self.assertFalse(valid_api_hash("x" * 32))
        self.assertFalse(valid_api_hash(""))
        self.assertFalse(valid_api_hash(None))

    def test_field_length_guards(self):
        self.assertTrue(secret_length_ok("a" * 32, 32, 80))
        self.assertFalse(secret_length_ok("a" * 31, 32, 80))
        self.assertFalse(secret_length_ok("a" * 81, 32, 80))
        self.assertFalse(secret_length_ok(None, 1, 256))
        self.assertFalse(secret_length_ok("abc", 0, 256))
        self.assertFalse(secret_length_ok("abc", 1, 900))

    @unittest.skipUnless(sys.platform == "win32", "Requires Windows Tk desktop")
    def test_real_windows_tk_paste_button_masks_input(self):
        # Dummy value only, no account or Telegram network access.
        dummy = "a" * 32
        real_tk = tk.Tk
        finished = []

        def tk_factory():
            root = real_tk()

            def interact():
                children = root.winfo_children()
                field = next(w for w in children if isinstance(w, tk.Entry))
                row = next(w for w in children if isinstance(w, tk.Frame))
                buttons = {w.cget("text"): w for w in row.winfo_children()
                           if isinstance(w, tk.Button)}
                self.assertEqual(field.cget("show"), "*")
                root.clipboard_clear()
                root.clipboard_append(dummy)
                buttons["Incolla"].invoke()
                self.assertEqual(field.get(), dummy)
                buttons["Conferma"].invoke()
                finished.append(True)

            root.after(120, interact)
            # Avoid a stuck CI in the event of widget regression.
            root.after(2500, lambda: root.destroy() if root.winfo_exists() else None)
            return root

        with patch("telegram_secret_dialog.tk.Tk", side_effect=tk_factory):
            result = prompt_masked_secret(
                "Telegram test", "Incolla API hash", min_length=32, max_length=80)
        self.assertEqual(result, dummy)
        self.assertEqual(finished, [True])

    @unittest.skipUnless(sys.platform == "win32", "Requires Windows Tk desktop")
    def test_real_windows_tk_cancel_returns_none(self):
        real_tk = tk.Tk

        def factory():
            root = real_tk()
            root.after(120, lambda: root.event_generate("<Escape>"))
            root.after(2500, lambda: root.destroy() if root.winfo_exists() else None)
            return root

        with patch("telegram_secret_dialog.tk.Tk", side_effect=factory):
            result = prompt_masked_secret(
                "Telegram test", "Annulla setup", min_length=32, max_length=80)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
