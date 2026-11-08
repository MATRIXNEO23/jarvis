"""Actual Windows voice callback; controlled transcripts, no live GPT or mic."""
import os
import unittest
from unittest.mock import Mock

import test_voice_corrections_review as voice_fixture
from voice_control import CONTINUOUS, GPT_CONVERSATION


@unittest.skipUnless(os.name == 'nt', 'Windows-only user requirement')
class GPTVoiceAddressingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        voice_fixture.VoiceCorrectionReviewTests.setUpClass()

    def setUp(self):
        self.fixture = voice_fixture.VoiceCorrectionReviewTests()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.setUp()
        self.fixture.voice_environment()
        self.env = self.fixture.env
        self.env.update(pending_conversation=[], conversation_epoch=7,
                        mic_status=voice_fixture.Value(''))

    def receive(self, text):
        self.fixture.receive_voice(text)

    def test_ambient_conversation_never_dispatches_or_queues(self):
        for busy in (False, True):
            self.env['busy_gpt'] = busy
            for _ in range(50):
                self.receive('mi racconti cosa avete fatto ieri sera')
        self.env['start_conversation_gpt'].assert_not_called()
        self.env['try_file_command'].assert_not_called()
        self.env['submit_local'].assert_not_called()
        self.env['write_line'].assert_not_called()
        self.assertEqual(self.env['pending_conversation'], [])
        self.assertEqual(self.env['last_voice_sample'].get(), 'apri blocco moto')
        self.assertEqual(self.env['voice_mode'].get(), GPT_CONVERSATION)

    def test_each_request_requires_name_at_start(self):
        self.receive('Jarvis, raccontami qualcosa')
        self.receive('continua il racconto')
        self.receive('stavamo parlando di Jarvis ieri')
        self.receive('jarvisiano raccontami qualcosa')
        self.env['start_conversation_gpt'].assert_called_once_with('raccontami qualcosa')

    def test_name_alone_does_not_authorize_later_room_speech(self):
        self.receive('Ehi Jarvis')
        self.receive('mi racconti qualcosa')
        self.env['start_conversation_gpt'].assert_not_called()
        self.env['try_file_command'].assert_not_called()
        self.receive('Jarvis mi racconti qualcosa')
        self.env['start_conversation_gpt'].assert_called_once_with('mi racconti qualcosa')

    def test_learned_correction_cannot_invent_addressing(self):
        self.env['speech_lexicon'] = Mock()
        self.env['speech_lexicon'].correct.return_value = 'Jarvis apri browser'
        self.receive('garbis apri browser')
        self.env['speech_lexicon'].correct.assert_not_called()
        self.env['submit_local'].assert_not_called()
        self.env['start_conversation_gpt'].assert_not_called()

    def test_busy_gemma_rejects_only_addressed_requests(self):
        self.env['gpt_enabled'].set(False)
        self.env['gemma_trial_busy'][0] = True
        self.receive('mi racconti qualcosa')
        self.receive('Jarvis mi racconti qualcosa')
        self.receive('continua pure')
        self.assertEqual(self.env['pending_conversation'], [])
        self.env['start_conversation_gpt'].assert_not_called()
        self.assertEqual([call.args[0] for call in self.env['write_line'].call_args_list], [
            'TU > mi racconti qualcosa',
            'GEMMA > Sto ancora elaborando. Ripeti la frase al termine.',
        ])

    def test_local_command_stays_local_and_background_cannot_trigger_it(self):
        self.receive('apri browser')
        self.env['submit_local'].assert_not_called()
        self.receive('Jarvis apri browser')
        self.env['submit_local'].assert_called_once_with(
            message_override='apri browser', source_utterance='apri browser')
        self.env['start_conversation_gpt'].assert_not_called()

    def test_tts_audio_cannot_arm_or_dispatch_a_request(self):
        self.env['speaker'].is_audible = lambda: True
        self.receive('Jarvis')
        self.receive('Jarvis raccontami qualcosa')
        self.env['speaker'].is_audible = lambda: False
        self.receive('mi racconti qualcosa')
        self.env['start_conversation_gpt'].assert_not_called()
        self.env['try_file_command'].assert_not_called()

    def test_common_address_forms_and_punctuation(self):
        for text in ('jarvis raccontami qualcosa', 'Jarvis, raccontami qualcosa',
                     'Ehi Jarvis: raccontami qualcosa', 'Hey Jarvis raccontami qualcosa'):
            with self.subTest(text=text):
                self.env['start_conversation_gpt'].reset_mock()
                self.receive(text)
                self.env['start_conversation_gpt'].assert_called_once_with('raccontami qualcosa')

    def test_continuous_mode_logs_and_dispatches_without_wake_word(self):
        self.fixture.voice_environment(CONTINUOUS)
        self.receive('apri browser')
        self.env['write_line'].assert_called_once_with('TU > apri browser')
        self.env['submit_local'].assert_called_once_with(
            message_override='apri browser', source_utterance='apri browser')
        self.env['start_conversation_gpt'].assert_not_called()

    def test_continuous_mode_sends_only_unhandled_speech_to_gemma(self):
        self.fixture.voice_environment(CONTINUOUS)
        self.receive('raccontami qualcosa')
        self.env['write_line'].assert_called_once_with('TU > raccontami qualcosa')
        self.env['try_file_command'].assert_called_once_with('raccontami qualcosa')
        self.env['submit_local'].assert_not_called()
        self.env['start_conversation_gpt'].assert_called_once_with('raccontami qualcosa')

    def test_continuous_mode_accepts_an_optional_name(self):
        self.fixture.voice_environment(CONTINUOUS)
        self.receive('Jarvis')
        self.env['write_line'].assert_not_called()
        self.receive('Jarvis apri browser')
        self.env['submit_local'].assert_called_once_with(
            message_override='apri browser', source_utterance='apri browser')

    def test_manual_dictation_still_inserts_free_text_without_commands(self):
        self.fixture.voice_environment(CONTINUOUS)
        self.env['dictation'].enabled = True
        self.env['dictation'].insert = Mock(return_value='inserito')
        self.env['sync_dictation_ui'] = Mock()
        self.receive('questo testo viene dettato intenzionalmente')
        self.env['dictation'].insert.assert_called_once_with(
            'questo testo viene dettato intenzionalmente')
        self.env['try_file_command'].assert_not_called()
        self.env['submit_local'].assert_not_called()
        self.env['start_conversation_gpt'].assert_not_called()
