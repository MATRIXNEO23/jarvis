"""ARCH-01 F4 RED: opt-in localhost KoboldCpp canary, no Lumi wiring.

No native GGUF, no real HTTP calls, no installed providers or credentials.
"""
import io
import json
import unittest
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler

from local_model.kobold_server_canary import (
    KoboldServerCanary, KoboldCanaryError,
)


class FakeOpener:
    def __init__(self, replies=None, fail=None):
        self.replies = list(replies or [])
        self.requests = []
        self.fail = fail

    def open(self, request, timeout=None):
        self.requests.append((request, timeout))
        if self.fail is not None:
            raise self.fail
        if not self.replies:
            raise AssertionError("Unexpected network call")
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        if isinstance(reply, bytes):
            return io.BytesIO(reply)
        return io.BytesIO(json.dumps(reply).encode("utf-8"))


class CanaryTests(unittest.TestCase):
    def test_constructor_does_not_connect_or_load_model(self):
        fake = FakeOpener()
        client = KoboldServerCanary(opener=fake)
        self.assertEqual(client.base_url, "http://127.0.0.1:5001")
        self.assertEqual(fake.requests, [])

    def test_only_literal_loopback_ipv4_is_allowed(self):
        bad = (
            "http://localhost:5001",
            "http://192.168.0.10:5001",
            "http://8.8.8.8:5001",
            "https://127.0.0.1:5001",
            "http://127.0.0.1.evil.test:5001",
            "http://127.0.0.1@evil.test:5001",
            "http://user:pass@127.0.0.1:5001",
            "http://127.0.0.1:5001/api",
            "http://127.0.0.1:5001?path=/",
            "file:///tmp/data",
            "http://127.0.0.1:0",
            "http://127.0.0.1:99999",
        )
        for url in bad:
            with self.subTest(url=url):
                with self.assertRaises((KoboldCanaryError, ValueError)):
                    KoboldServerCanary(url, opener=FakeOpener())
        self.assertEqual(
            KoboldServerCanary("http://127.0.0.1:7333", opener=FakeOpener()).base_url,
            "http://127.0.0.1:7333")

    def test_default_transport_bypasses_proxies_and_refuses_redirects(self):
        client = KoboldServerCanary()
        handlers = client._opener.handlers
        proxies = [h.proxies for h in handlers if isinstance(h, ProxyHandler)]
        # CPython can omit an explicitly empty ProxyHandler from the opener.
        # The security property is that no handler contains proxy targets.
        self.assertFalse(any(proxies))
        redirects = [h for h in handlers if isinstance(h, HTTPRedirectHandler)]
        self.assertEqual(len(redirects), 1)
        with self.assertRaises(KoboldCanaryError):
            redirects[0].redirect_request(
                None, None, 302, "Elsewhere", {},
                "https://evil.example/sensitive-prompt")

    def test_probe_gets_loaded_model_without_sending_prompt(self):
        fake = FakeOpener([{"result": "gemma2-2b-it-Q4.gguf"}])
        client = KoboldServerCanary(opener=fake)
        self.assertEqual(client.probe(), "gemma2-2b-it-Q4.gguf")
        req, timeout = fake.requests[0]
        self.assertEqual(req.full_url, "http://127.0.0.1:5001/api/v1/model")
        self.assertEqual(req.get_method(), "GET")
        self.assertIsNone(req.data)
        self.assertLessEqual(timeout, 10)

    def test_protected_model_identity_requires_local_password(self):
        fake = FakeOpener([{"result": "koboldcpp/protected-model"}])
        canary = KoboldServerCanary(opener=fake)
        with self.assertRaisesRegex(KoboldCanaryError, "password"):
            canary.generate("NON INVIARE", expected_model="koboldcpp/protected-model")
        self.assertEqual(len(fake.requests), 1)
        self.assertEqual(fake.requests[0][0].get_method(), "GET")

    def test_model_mismatch_blocks_generation_without_sending_prompt(self):
        fake = FakeOpener([{"result": "not-the-requested-model"}])
        client = KoboldServerCanary(opener=fake)
        with self.assertRaisesRegex(KoboldCanaryError, "modello"):
            client.generate(
                "CONTENUTO PRIVATO", expected_model="gemma2-2b-it-Q4.gguf")
        self.assertEqual(len(fake.requests), 1)
        self.assertNotIn("CONTENUTO PRIVATO", str(fake.requests))

    def test_raw_gemma_prompt_is_preserved_exactly_and_only_sent_explicitly(self):
        prompt = "<start_of_turn>user\\nCos'è un buco nero?<end_of_turn>\\n<start_of_turn>model\\n"
        prompt = prompt.replace("\\n", "\n")
        fake = FakeOpener([
            {"result": "Gemma-2"},
            {"results": [{"text": "È una regione dello spazio."}]},
        ])
        client = KoboldServerCanary(opener=fake)
        response = client.generate(
            prompt, expected_model="Gemma-2", max_context_length=1024,
            max_length=256, stop_sequence=("<end_of_turn>",), timeout=180)
        self.assertEqual(response, "È una regione dello spazio.")
        self.assertEqual(len(fake.requests), 2)
        req, timeout = fake.requests[1]
        self.assertEqual(timeout, 180)
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(req.full_url, "http://127.0.0.1:5001/api/v1/generate")
        data = json.loads(req.data.decode("utf-8"))
        self.assertEqual(data["prompt"], prompt)
        self.assertEqual(data["max_context_length"], 1024)
        self.assertEqual(data["max_length"], 256)
        self.assertEqual(data["stop_sequence"], ["<end_of_turn>"])
        self.assertFalse(any("api/admin" in a[0].full_url for a in fake.requests))

    def test_perf_read_only_and_malformed_response_is_rejected(self):
        fake = FakeOpener([{"last_process": 2.0}])
        client = KoboldServerCanary(opener=fake)
        self.assertEqual(client.perf(), {"last_process": 2.0})
        self.assertEqual(fake.requests[0][0].get_method(), "GET")
        self.assertTrue(fake.requests[0][0].full_url.endswith("/api/extra/perf"))
        for raw in ({"result": None}, {"result": []}, b"{bad-json",
                    {"result": "x" * 300}):
            with self.subTest(raw=str(raw)[:70]):
                client = KoboldServerCanary(opener=FakeOpener([raw]))
                with self.assertRaises(KoboldCanaryError):
                    client.probe()

    def test_invalid_payloads_fail_before_http(self):
        fake = FakeOpener()
        client = KoboldServerCanary(opener=fake)
        invalid = [
            dict(prompt="", expected_model="Gemma"),
            dict(prompt="hi", expected_model=""),
            dict(prompt="hi", expected_model="Gemma", max_length=0),
            dict(prompt="hi", expected_model="Gemma", max_context_length=0),
            dict(prompt="hi", expected_model="Gemma", stop_sequence=[""]),
            dict(prompt="hi", expected_model="Gemma", stop_sequence=["x" * 300]),
            dict(prompt="hi", expected_model="Gemma", timeout=0),
        ]
        for args in invalid:
            with self.subTest(args=str(args)[:70]):
                with self.assertRaises((ValueError, KoboldCanaryError)):
                    client.generate(**args)
        self.assertEqual(fake.requests, [])

    def test_network_errors_are_sanitized_and_not_retried(self):
        fake = FakeOpener(fail=URLError("token=PRIVATE; details"))
        client = KoboldServerCanary(opener=fake)
        with self.assertRaises(KoboldCanaryError) as raised:
            client.generate("PRIVATE CHAT", expected_model="Gemma")
        self.assertNotIn("PRIVATE", str(raised.exception))
        self.assertEqual(len(fake.requests), 1)

    def test_bad_generation_output_cannot_execute_or_become_chat(self):
        fake = FakeOpener([
            {"result": "Gemma"},
            {"results": [{"text": 123}]},
        ])
        client = KoboldServerCanary(opener=fake)
        with self.assertRaises(KoboldCanaryError):
            client.generate("Una domanda", expected_model="Gemma")
        self.assertEqual(len(fake.requests), 2)
        self.assertFalse(hasattr(client, "dispatch_model_capability"))


if __name__ == "__main__":
    unittest.main()
