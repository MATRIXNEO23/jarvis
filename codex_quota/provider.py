"""Read-only quota boundary. Never creates a model turn or signs in."""
from __future__ import annotations


class QuotaUnavailable(RuntimeError):
    pass


class ReadOnlyRPC:
    """Only this method can cross an injected, explicitly connected transport."""
    def __init__(self, transport):
        self._transport = transport

    def call(self, method, params, *, timeout=10.0):
        if method != 'account/rateLimits/read' or params != {}:
            raise ValueError('Only quota reads are permitted.')
        if not 0 < timeout <= 10:
            raise ValueError('Quota timeout must be within ten seconds.')
        return self._transport.call(method, params, timeout=timeout)


class Provider:
    def __init__(self, transport=None, *, session_key=None):
        self.session_key = session_key
        self._rpc = ReadOnlyRPC(transport) if transport is not None else None

    def available(self):
        return self._rpc is not None and isinstance(self.session_key, str) and bool(self.session_key)

    def read_limits(self, *, timeout=10.0):
        if not 0 < timeout <= 10:
            raise ValueError('Quota timeout must be within ten seconds.')
        if not self.available():
            raise QuotaUnavailable('Quota provider not connected.')
        try:
            reply = self._rpc.call('account/rateLimits/read', {}, timeout=timeout)
        except (OSError, TimeoutError, ValueError) as exc:
            raise QuotaUnavailable('Quota read unavailable; no model request sent.') from None
        if not isinstance(reply, dict) or 'error' in reply:
            raise QuotaUnavailable('Quota read not authorized or unavailable.')
        result = reply.get('result')
        if not isinstance(result, dict):
            raise QuotaUnavailable('Quota snapshot unavailable.')
        snapshot = {key:result[key] for key in ('rateLimits', 'rateLimitsByLimitId')
                    if isinstance(result.get(key), dict) and result[key]}
        if not snapshot:
            raise QuotaUnavailable('Quota snapshot unavailable.')
        return snapshot
