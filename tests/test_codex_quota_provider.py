"""Windows-only proof of the zero-inference quota boundary."""
import copy
import os
import unittest

from codex_quota.provider import Provider, QuotaUnavailable, ReadOnlyRPC


class Transport:
    def __init__(self, reply=None, error=None):
        self.calls = []
        self.error = error
        self.reply = reply or {'result': {'rateLimits': {'limitId': 'codex',
            'primary': {'usedPercent': 25, 'windowDurationMins': 300,
                        'resetsAt': 2000000000}}, 'accessToken': 'must-not-escape'}}

    def call(self, method, params, *, timeout):
        if method != 'account/rateLimits/read':
            raise AssertionError('Inference/login/mutating method invoked')
        self.calls.append((method, params, timeout))
        if self.error:
            raise self.error
        return copy.deepcopy(self.reply)


@unittest.skipUnless(os.name == 'nt', 'Windows-only user requirement')
class QuotaProviderTests(unittest.TestCase):
    def test_connected_read_sends_only_quota_rpc_and_returns_only_quota_fields(self):
        transport = Transport()
        provider = Provider(transport, session_key='opaque-test-session')
        self.assertTrue(provider.available())
        result = provider.read_limits(timeout=3)
        self.assertEqual(transport.calls, [('account/rateLimits/read', {}, 3)])
        self.assertEqual(result, {'rateLimits': transport.reply['result']['rateLimits']})
        self.assertNotIn('must-not-escape', repr(result))

    def test_unconnected_provider_never_starts_transport_or_login(self):
        transport = Transport()
        for provider in (Provider(), Provider(transport), Provider(transport, session_key='')):
            self.assertFalse(provider.available())
            with self.assertRaises(QuotaUnavailable):
                provider.read_limits()
        self.assertFalse(transport.calls)

    def test_boundary_rejects_every_non_read_operation_before_transport(self):
        transport = Transport()
        rpc = ReadOnlyRPC(transport)
        for method in ('turn/start', 'thread/start', '/v1/responses', 'streamResponse',
                       'account/login/start', 'account/rateLimitResetCredit/consume',
                       'account/sendAddCreditsNudgeEmail'):
            with self.subTest(method=method), self.assertRaises(ValueError):
                rpc.call(method, {})
        with self.assertRaises(ValueError):
            rpc.call('account/rateLimits/read', {'prompt': 'forbidden'})
        self.assertFalse(transport.calls)

    def test_error_reply_never_exposes_error_text_or_credentials(self):
        provider = Provider(Transport({'error': {'message': 'secret-test-token'}}), session_key='s')
        with self.assertRaises(QuotaUnavailable) as error:
            provider.read_limits()
        self.assertNotIn('secret-test-token', str(error.exception))

    def test_timeout_is_bounded_and_never_retries(self):
        transport = Transport(error=TimeoutError('secret-test-token'))
        provider = Provider(transport, session_key='s')
        with self.assertRaises(QuotaUnavailable) as error:
            provider.read_limits()
        self.assertNotIn('secret-test-token', str(error.exception))
        self.assertEqual(len(transport.calls), 1)

    def test_snapshot_missing_is_unavailable_not_zero(self):
        for result in ({}, {'rateLimits': None}, {'rateLimits': []}):
            with self.subTest(result=result), self.assertRaises(QuotaUnavailable):
                Provider(Transport({'result': result}), session_key='s').read_limits()

    def test_invalid_timeout_does_not_cross_transport(self):
        transport = Transport()
        provider = Provider(transport, session_key='s')
        for timeout in (0, -1, 11, float('inf'), float('nan')):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                provider.read_limits(timeout=timeout)
        self.assertFalse(transport.calls)
