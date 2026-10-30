"""Document-close dialogue policy: no actual files, windows or GPT calls."""
import unittest

from document_dialog import DocumentDialog


class DocumentDialogTests(unittest.TestCase):
    def setUp(self):
        self.dialog = DocumentDialog()

    def start(self, *, dirty=True, path="C:/Users/Public/Documents/nota.txt"):
        return self.dialog.begin("notepad-17", "nota.txt", dirty=dirty,
                                 saved_path=path)

    def test_unsaved_close_requires_a_choice(self):
        self.start()
        response = self.dialog.request_close()
        self.assertEqual(response.kind, "ask_choice")
        self.assertIn("salvare e chiudere", response.message)
        self.assertEqual(self.dialog.phase, "awaiting_close_choice")
        self.assertEqual(self.dialog.reply("come stai?").kind, "invalid")
        self.assertEqual(self.dialog.phase, "awaiting_close_choice")

    def test_save_and_close_is_intent_not_immediate_success(self):
        self.start()
        self.dialog.request_close()
        response = self.dialog.reply("Salva ed esci")
        self.assertEqual(response.kind, "save_then_close")
        self.assertEqual(response.document_id, "notepad-17")
        self.assertEqual(self.dialog.phase, "executing")
        # Failure MUST leave the document open, never say 'saved'.
        self.assertEqual(
            self.dialog.operation_completed("notepad-17", succeeded=False).kind,
            "failed")
        self.assertEqual(self.dialog.phase, "editing")
        self.assertTrue(self.dialog.dirty)

    def test_explicit_success_clears_old_confirmation(self):
        self.start()
        self.dialog.request_close()
        self.dialog.reply("salva e chiudi")
        self.assertEqual(
            self.dialog.operation_completed("notepad-17", succeeded=True).kind,
            "closed")
        self.assertEqual(self.dialog.phase, "idle")
        self.assertEqual(self.dialog.reply("salva").kind, "ignored")

    def test_discard_requires_two_distinct_voice_confirmations(self):
        self.start()
        self.dialog.request_close()
        response = self.dialog.reply("chiudi senza salvare")
        self.assertEqual(response.kind, "ask_discard_confirmation")
        self.assertEqual(self.dialog.reply("sì").kind, "invalid")
        self.assertEqual(self.dialog.reply("salva e chiudi").kind, "invalid")
        self.assertEqual(self.dialog.phase, "awaiting_discard_confirmation")
        self.assertEqual(self.dialog.reply(
            "confermo uscita senza salvare").kind, "discard_then_close")
        self.assertEqual(self.dialog.phase, "executing")

    def test_cancel_never_discards_text(self):
        self.start()
        self.dialog.request_close()
        self.dialog.reply("non salvare")
        result = self.dialog.reply("annulla")
        self.assertEqual(result.kind, "cancel")
        self.assertEqual(self.dialog.phase, "editing")
        self.assertTrue(self.dialog.dirty)
        self.assertEqual(self.dialog.document_id, "notepad-17")

    def test_new_document_asks_for_destination_and_does_not_guess(self):
        self.start(path=None)
        self.dialog.request_close()
        response = self.dialog.reply("salva e chiudi")
        self.assertEqual(response.kind, "ask_destination")
        self.assertEqual(self.dialog.phase, "awaiting_save_destination")
        self.assertEqual(self.dialog.reply("salva in C:").kind, "ask_destination")
        self.assertEqual(self.dialog.phase, "awaiting_save_destination")
        self.assertEqual(self.dialog.provide_destination("").kind, "invalid")
        response = self.dialog.provide_destination(
            "C:/Users/Public/Documents/nuova-nota.txt")
        self.assertEqual(response.kind, "save_as_then_close")
        self.assertEqual(self.dialog.phase, "executing")

    def test_clean_document_does_not_require_data_loss_confirmation(self):
        self.start(dirty=False)
        self.assertEqual(self.dialog.request_close().kind, "close_clean")
        self.assertEqual(self.dialog.phase, "executing")

    def test_wrong_doc_cannot_confirm_completion(self):
        self.start()
        self.dialog.request_close()
        self.dialog.reply("salva e chiudi")
        with self.assertRaises(ValueError):
            self.dialog.operation_completed("another-document", succeeded=True)
        self.assertEqual(self.dialog.document_id, "notepad-17")

    def test_revoke_cannot_resurrect_old_decision(self):
        self.start()
        self.dialog.request_close()
        self.dialog.revoke_pending()
        self.assertEqual(self.dialog.reply("salva e chiudi").kind, "ignored")
        self.assertEqual(self.dialog.phase, "editing")
        self.dialog.reset()
        self.assertEqual(self.dialog.phase, "idle")
        self.assertEqual(self.dialog.reply("chiudi senza salvare").kind, "ignored")

    def test_incomplete_document_identity_rejected(self):
        with self.assertRaises(ValueError):
            self.dialog.begin("", "nota.txt", dirty=True)
        self.start()
        with self.assertRaises(ValueError):
            self.dialog.begin("second", "altro.txt", dirty=False)
        self.dialog.reset()
        self.assertIsNone(self.dialog.document_id)

    def test_mark_dirty_only_during_editing(self):
        self.start(dirty=False)
        self.dialog.mark_dirty()
        self.assertTrue(self.dialog.dirty)
        self.dialog.request_close()
        with self.assertRaises(ValueError):
            self.dialog.mark_dirty()


if __name__ == "__main__":
    unittest.main()
