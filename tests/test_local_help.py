import os
import unittest
from unittest.mock import Mock
from test_typed_timer_routing import TypedTimerTests

@unittest.skipUnless(os.name=='nt','Windows only')
class LocalHelpTests(unittest.TestCase):
    def test_help_is_local_even_with_gemma_and_pending_document(self):
        harness=TypedTimerTests();self.addCleanup(harness.doCleanups)
        for word in ('aiuto','help','comandi','cosa puoi fare'):
            e=harness.environment(word)
            e['doc_dialog'].phase='awaiting_close'
            e['handle_document_confirmation']=Mock()
            e['show_help']=Mock()
            e['send_console_input']()
            e['show_help'].assert_called_once_with()
            e['submit_gemma_trial'].assert_not_called()
            e['handle_document_confirmation'].assert_not_called()
            self.assertEqual(e['request'].value,'')
