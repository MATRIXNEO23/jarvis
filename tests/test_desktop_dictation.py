"""Offline dictation policy tests; never access a real microphone or keyboard."""
import unittest

from desktop_dictation import DesktopDictation, FocusedWindow, dictation_voice_action


class DictationCommandTests(unittest.TestCase):
    def test_exact_start_and_stop(self):
        self.assertEqual(dictation_voice_action("Jarvis, attiva dettatura vocale"), "start")
        self.assertEqual(dictation_voice_action("Jarvis interrompi dettatura"), "stop")
        self.assertEqual(dictation_voice_action("disattiva dettatura"), "stop")

    def test_ordinary_speech_never_toggles(self):
        self.assertIsNone(dictation_voice_action("scrivi buongiorno a tutti"))
        self.assertIsNone(dictation_voice_action("attiva dettatura ed esegui comandi"))


class DictationSafetyTests(unittest.TestCase):
    def prepare(self, initial):
        focus = [initial]
        written = []
        subject = DesktopDictation(
            app_pid=100, windows=True, focus_provider=lambda: focus[0],
            sender=written.append,
        )
        return subject, focus, written

    def test_starts_disabled_and_has_no_automatic_input(self):
        editor = FocusedWindow(21, 22, 200)
        subject, focus, written = self.prepare(editor)
        self.assertFalse(subject.enabled)
        subject.insert("ciao")
        self.assertEqual(written, [])
        subject.enable()
        self.assertEqual(subject.target, editor)
        self.assertEqual(subject.insert("ciao"), "Dettatura inserita nel campo selezionato.")
        self.assertEqual(written, ["ciao "])
        subject.disable()
        subject.insert("altro")
        self.assertEqual(written, ["ciao "])

    def test_click_to_choose_target_only_after_manual_activation(self):
        self_window = FocusedWindow(1, 2, 100)
        editor = FocusedWindow(21, 22, 200)
        subject, focus, written = self.prepare(self_window)
        subject.enable()
        self.assertIsNone(subject.target)
        self.assertIn("non inserito", subject.insert("non ancora"))
        focus[0] = editor
        self.assertIn("inserita", subject.insert("il mio testo"))
        self.assertEqual(written, ["il mio testo "])
        self.assertEqual(subject.target, editor)

    def test_window_change_drops_input_until_user_rearms(self):
        editor = FocusedWindow(21, 22, 200)
        subject, focus, written = self.prepare(editor)
        subject.enable()
        focus[0] = FocusedWindow(45, 46, 300)
        self.assertIn("sospesa", subject.insert("messaggio segreto"))
        self.assertEqual(written, [])
        subject.disable()
        subject.enable()
        self.assertIn("inserita", subject.insert("nuovo testo"))
        self.assertEqual(written, ["nuovo testo "])

    def test_focus_change_within_same_window_drops_input(self):
        editor = FocusedWindow(21, 22, 200)
        subject, focus, written = self.prepare(editor)
        subject.enable()
        focus[0] = FocusedWindow(21, 23, 200)
        self.assertIn("sospesa", subject.insert("prova"))
        self.assertFalse(written)

    def test_native_password_and_self_window_blocked(self):
        editor = FocusedWindow(21, 22, 200)
        subject, focus, written = self.prepare(editor)
        subject.enable()
        focus[0] = FocusedWindow(21, 23, 200, password_field=True)
        self.assertIn("non inserito", subject.insert("1234"))
        focus[0] = FocusedWindow(33, 44, 100)
        self.assertIn("non inserito", subject.insert("1234"))
        self.assertEqual(written, [])

    def test_newline_and_bounded_text(self):
        editor = FocusedWindow(21, 22, 200)
        subject, focus, written = self.prepare(editor)
        subject.enable()
        subject.insert("a capo")
        self.assertEqual(written, ["\n"])
        self.assertIn("troppo lungo", subject.insert("x" * 301))
        self.assertEqual(len(written), 1)

    def test_non_windows_no_input(self):
        subject, focus, written = self.prepare(FocusedWindow(21, 22, 200))
        subject.windows = False
        self.assertIn("Windows", subject.enable())
        self.assertFalse(subject.enabled)
        self.assertFalse(written)


if __name__ == "__main__":
    unittest.main()
