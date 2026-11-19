import unittest

import la_mia_voce


class FakeLexicon:
    def __init__(self):
        self.learned = []

    def learn_phrase(self, heard, intended, *, user_confirmed=False):
        assert user_confirmed is True
        self.learned.append((heard, intended))
        return heard, intended


class MyVoiceTests(unittest.TestCase):
    def tearDown(self):
        la_mia_voce.stop()

    def test_session_learns_only_differences(self):
        lexicon = FakeLexicon()
        session = la_mia_voce.Session(lexicon, phrases=["file successivo", "Deep Impact"])
        la_mia_voce.start(session)
        self.assertTrue(la_mia_voce.receive("file successivo"))
        self.assertTrue(la_mia_voce.receive("dip impact"))
        self.assertEqual(lexicon.learned, [("dip impact", "deep impact")])
        self.assertFalse(la_mia_voce.receive("altro"))           # finita: torna ai comandi

    def test_pause_is_bounded(self):
        old, old_path = la_mia_voce._STATE["pause"], la_mia_voce._path
        try:
            la_mia_voce._STATE["pause"] = None
            self.assertGreaterEqual(la_mia_voce.pause_seconds(), 0.0)
            la_mia_voce._path = lambda: None
            self.assertEqual(la_mia_voce.set_pause(9), la_mia_voce.MAX_PAUSE)
        finally:
            la_mia_voce._STATE["pause"] = old
            la_mia_voce._path = old_path


if __name__ == "__main__":
    unittest.main()
