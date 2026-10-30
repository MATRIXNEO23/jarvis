"""Second Brain tests: persistent recall across restarts without fake actions."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sqlite3
from contextlib import closing
import unittest

from conversation_memory import ConversationMemory
from second_brain import SecondBrain, BrainError


class ShortTermTests(unittest.TestCase):
    def test_follow_up_has_previous_clarification(self):
        memory = ConversationMemory()
        memory.remember("Apri quel documento", "Quale documento intendi?", "clarify")
        self.assertIn("Quale documento", memory.context())
        memory.remember("Quello degli appunti", "Ora ho capito.", "chat")
        self.assertIn("Quello degli appunti", memory.context())
        self.assertIn("Apri quel documento", memory.context())

    def test_limited_history_and_clear(self):
        memory = ConversationMemory()
        for i in range(20):
            memory.remember("frase " + str(i), "risposta " + str(i))
        self.assertLessEqual(len(memory), 8)
        self.assertNotIn("frase 0", memory.context())
        self.assertLessEqual(len(memory.context()), 1050)
        memory.clear()
        self.assertEqual(memory.context(), "[]")


class DurableMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "Jarvis" / "second_brain.sqlite3"
        self.brain = SecondBrain(self.path)

    def test_dialogue_survives_restart(self):
        self.assertTrue(self.brain.remember_turn(
            "Vorrei creare un testo su Venezia",
            "Ti preparo un testo su Venezia.", "chat"))
        self.assertTrue(self.brain.remember_turn(
            "Intendo nel documento", "Quale documento intendi?", "clarify"))
        restarted = SecondBrain(self.path)
        last = restarted.recent_turns()
        self.assertEqual(len(last), 2)
        self.assertIn("Venezia", last[0]["user"])
        self.assertIn("Quale", last[1]["lia"])
        self.assertIn("Venezia", restarted.prompt_context("Venezia"))

    def test_sent_email_requires_real_external_receipt(self):
        with self.assertRaises(BrainError):
            self.brain.record_email_sent(recipient="test@example.com",
                                         subject="Appuntamento",
                                         provider_message_id="mail-123",
                                         verified=False)
        self.assertEqual(self.brain.stats(), (0, 0))
        self.assertTrue(self.brain.record_email_sent(
            recipient="test@example.com", subject="Appuntamento",
            provider_message_id="mail-123", verified=True))
        # A network retry with the same real receipt never creates a second send.
        self.assertFalse(self.brain.record_email_sent(
            recipient="test@example.com", subject="Appuntamento",
            provider_message_id="mail-123", verified=True))
        restarted = SecondBrain(self.path)
        hits = restarted.search("Ti ricordi la mail per l'appuntamento?", limit=4)
        self.assertTrue(hits)
        self.assertEqual(hits[0].source, "verified_action")
        self.assertIn("Appuntamento", hits[0].summary)
        self.assertIn("test@example.com", hits[0].summary)
        self.assertEqual(hits[0].reference, "mail-123")
        with closing(sqlite3.connect(self.path)) as db:
            payload = db.execute("SELECT metadata_json FROM action_receipts").fetchone()[0]
        self.assertNotIn("body", payload)

    def test_conversation_claim_is_not_proof_of_email_sent(self):
        self.brain.remember_turn("Ho inviato una mail", "Hai detto che l'hai inviata.")
        hits = self.brain.search("mail")
        self.assertTrue(hits)
        self.assertTrue(all(hit.source != "verified_action" for hit in hits))
        self.assertEqual(self.brain.stats(), (1, 0))

    def test_only_successful_tasks_can_be_marked_done(self):
        with self.assertRaises(BrainError):
            self.brain.record_completed_action(
                "explorer.drive_c", "Explorer", "Disco locale C aperto.",
                receipt_id="task-123", verified=False)
        self.assertEqual(self.brain.stats(), (0, 0))
        self.brain.record_completed_action(
            "explorer.drive_c", "Explorer", "Disco locale C aperto.",
            receipt_id="task-123", verified=True)
        self.assertEqual(self.brain.stats(), (0, 1))

    def test_unsafe_metadata_and_secrets_not_saved(self):
        with self.assertRaises(BrainError):
            self.brain.record_completed_action(
                "mail.send", "email", "Email inviata",
                receipt_id="x", verified=True,
                metadata={"body": "Testo riservato"})
        self.assertFalse(self.brain.remember_turn(
            "La mia password è segreta", "Non registrarla."))
        self.assertEqual(self.brain.stats(), (0, 0))

    def test_prompt_memory_is_bounded(self):
        for i in range(18):
            self.brain.remember_turn(
                "Domanda precedente " + str(i),
                "Risposta precedente lunga " + "L" * 130, "chat")
        for i in range(10):
            self.brain.record_completed_action(
                "downloads.list", "Download", "Elenco scaricamenti " + str(i),
                receipt_id="task-" + str(i), verified=True)
        prompt = self.brain.prompt_context("scaricamenti")
        self.assertLessEqual(len(prompt), 1100)
        self.assertIn("verified_action", prompt)
        self.assertIsInstance(json.loads(prompt), dict)

    def test_explicit_clear_and_no_replay_after_restart(self):
        self.brain.remember_turn("Mi ricordi la mail?", "Non ho ricevute di invio.")
        self.brain.record_completed_action(
            "calculator.open", "Calcolatrice", "Calcolatrice aperta",
            receipt_id="task-200", verified=True)
        self.assertEqual(self.brain.stats(), (1, 1))
        self.brain.clear_all()
        restarted = SecondBrain(self.path)
        self.assertEqual(restarted.stats(), (0, 0))
        self.assertEqual(restarted.search("calcolatrice"), ())
        self.assertNotIn("Calcolatrice aperta", restarted.prompt_context("calcolatrice"))


if __name__ == "__main__":
    unittest.main()
