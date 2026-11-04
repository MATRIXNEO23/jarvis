"""Windows contract tests. Only inference/account transports are substituted."""
import os
import unittest
from unittest.mock import Mock
from local_model.service import ModelService

@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class ModelRoutingTests(unittest.TestCase):
    def setUp(self):
        self.local=Mock()
        self.local.ask.return_value={"text":"Ciao, signore.","provider":"local"}
        self.online=Mock()
        self.online.call.return_value={"text":"Risposta online"}
        self.consent=Mock(return_value=False)
    def service(self, local=True, online=False):
        return ModelService(self.online,self.local,local_enabled=local,
                            online_enabled=online,consent=self.consent)
    def test_local_dialogue_works_with_online_switched_off(self):
        result=self.service().call("ask",prompt="Ciao")
        self.assertEqual(result["text"],"Ciao, signore.")
        self.online.call.assert_not_called()
        self.consent.assert_not_called()
    def test_enabled_online_does_not_replace_successful_local(self):
        self.service(online=True).call("ask",prompt="Ciao")
        self.local.ask.assert_called_once()
        self.online.call.assert_not_called()
    def test_explicit_online_needs_one_consent_before_inference(self):
        self.consent.return_value=True
        result=self.service(online=True).call("ask",prompt="Domanda",force_online=True)
        self.assertEqual(result["text"],"Risposta online")
        self.consent.assert_called_once()
        self.online.call.assert_called_once_with("ask",timeout=120,prompt="Domanda")
    def test_online_off_rejects_even_explicit_request_without_inference(self):
        with self.assertRaises(RuntimeError):
            self.service().call("ask",prompt="Domanda",force_online=True)
        self.online.call.assert_not_called()
        self.consent.assert_not_called()
    def test_local_failure_cannot_spend_online_quota_without_approval(self):
        self.local.ask.side_effect=RuntimeError("modello assente")
        with self.assertRaises(RuntimeError):
            self.service(online=True).call("ask",prompt="Ciao")
        self.online.call.assert_not_called()
        self.consent.assert_called_once()
    def test_telegram_request_reports_its_origin_for_owner_consent(self):
        self.local.ask.side_effect=RuntimeError("timeout")
        with self.assertRaises(RuntimeError):
            self.service(online=True).call("ask",prompt="Testo Telegram",origin="Telegram")
        self.assertEqual(self.consent.call_args.kwargs["origin"],"Telegram")
        self.online.call.assert_not_called()
