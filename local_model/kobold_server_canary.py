"""ARCH-01 F4: optional probe of an already-running LOCAL KoboldCpp server.

This module is deliberately NOT imported by Jarvis or NativeChatAdapter.
Construction never connects; generation requires an explicit caller, a pinned
model name and a preformatted raw prompt. No model loading, background
worker, data persistence, code execution, actions, external network or retry.

Only Python standard library; opt-in lab tool, NOT a production backend.
"""
from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler, ProxyHandler, Request, build_opener,
)


_MAX_RESPONSE = 1024 * 1024
_MAX_REQUEST_PROMPT = 120000


class KoboldCanaryError(RuntimeError):
    """Safe, non-sensitive canary transport or response error."""


class _DenyRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise KoboldCanaryError("Redirect rifiutato per il server locale.")


def _check_base_url(value):
    if not isinstance(value, str):
        raise KoboldCanaryError("Indirizzo locale non valido.")
    try:
        parts = urlsplit(value)
        port = parts.port
    except ValueError as exc:
        raise KoboldCanaryError("Porta server non valida.") from None
    # No hostname resolution: 'localhost' can be remapped by machine policy.
    # No credentials, paths, fragments, or query may ever override endpoints.
    if (parts.scheme != "http" or parts.hostname != "127.0.0.1"
            or port is None or not 1 <= port <= 65535
            or parts.username is not None or parts.password is not None
            or parts.path not in ("", "/") or parts.query or parts.fragment):
        raise KoboldCanaryError("Consentito soltanto http://127.0.0.1:porta")
    return "http://127.0.0.1:" + str(port)


def _text(value, name, maximum):
    if type(value) is not str or not value.strip() or len(value) > maximum:
        raise KoboldCanaryError(name + " non valido.")
    if "\x00" in value:
        raise KoboldCanaryError(name + " non valido.")
    return value


def _positive_number(value, name, maximum):
    if type(value) not in (int, float) or not 0 < value <= maximum:
        raise KoboldCanaryError(name + " non valido.")
    return value


class KoboldServerCanary:
    """Explicit read-only probe + explicitly requested generation on loopback.

    An optional custom opener exists for hermetic tests. Production constructor
    disables environment proxies and HTTP redirects to avoid private prompt
    exfiltration. A caller must first terminate the integrated GGUF model
    before manually running a separate KoboldCpp process on a low-RAM PC.
    """

    def __init__(self, base_url="http://127.0.0.1:5001", *,
                 opener=None, timeout=5, bearer_token=None):
        self.base_url = _check_base_url(base_url)
        self.timeout = _positive_number(timeout, "Timeout", 30)
        if bearer_token is not None:
            _text(bearer_token, "Password locale", 4096)
            if "\n" in bearer_token or "\r" in bearer_token:
                raise KoboldCanaryError("Password locale non valida.")
        self._token = bearer_token
        self._opener = opener if opener is not None else build_opener(
            ProxyHandler({}), _DenyRedirects())

    def _request(self, endpoint, *, payload=None, timeout=None):
        if endpoint not in ("/api/v1/model", "/api/v1/generate",
                            "/api/extra/perf"):
            raise KoboldCanaryError("Endpoint non consentito.")
        uri = self.base_url + endpoint
        headers = {"Accept": "application/json"}
        if self._token is not None:
            headers["Authorization"] = "Bearer " + self._token
        if payload is None:
            request = Request(uri, headers=headers, method="GET")
        else:
            raw = json.dumps(payload, ensure_ascii=False,
                             separators=(",", ":")).encode("utf-8")
            if len(raw) > _MAX_REQUEST_PROMPT * 4:
                raise KoboldCanaryError("Richiesta troppo estesa.")
            headers["Content-Type"] = "application/json"
            request = Request(uri, data=raw, headers=headers, method="POST")
        try:
            with self._opener.open(
                    request, timeout=self.timeout if timeout is None else timeout
            ) as response:
                raw = response.read(_MAX_RESPONSE + 1)
        except KoboldCanaryError:
            raise
        except (HTTPError, URLError, OSError, TimeoutError, ValueError):
            # Never include URL parameters, request body, auth token or traces.
            raise KoboldCanaryError(
                "KoboldCpp locale non raggiungibile o risposta HTTP non valida."
            ) from None
        if len(raw) > _MAX_RESPONSE:
            raise KoboldCanaryError("Risposta KoboldCpp troppo grande.")
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError, TypeError):
            raise KoboldCanaryError("KoboldCpp ha restituito JSON non valido.") from None
        if not isinstance(decoded, dict):
            raise KoboldCanaryError("Formato risposta KoboldCpp non valido.")
        return decoded

    def probe(self):
        """Read-only identity of the already-loaded model."""
        answer = self._request("/api/v1/model")
        name = answer.get("result")
        if type(name) is not str or not 1 <= len(name) <= 256 or not name.strip():
            raise KoboldCanaryError("Identità modello KoboldCpp non disponibile.")
        if name == "koboldcpp/protected-model":
            raise KoboldCanaryError(
                "Server protetto: modello non verificabile senza password locale.")
        return name

    def perf(self):
        """Read-only native performance snapshot (fields depend on version)."""
        return self._request("/api/extra/perf")

    def generate(self, prompt, *, expected_model, max_context_length=1024,
                 max_length=256, stop_sequence=(), timeout=180):
        """Send one explicit, preformatted raw prompt to the pinned model.

        No automatic formatting or re-routing: caller must supply the *exact*
        Gemma or Qwen template, only after validating it separately. This
        method never accepts, executes, persists or authorizes tool actions.
        """
        prompt = _text(prompt, "Prompt locale", _MAX_REQUEST_PROMPT)
        expected_model = _text(expected_model, "Nome modello", 256)
        if (type(max_context_length) is not int
                or not 256 <= max_context_length <= 32768):
            raise KoboldCanaryError("Context Size non valido.")
        if (type(max_length) is not int or not 1 <= max_length < max_context_length
                or max_length > 4096):
            raise KoboldCanaryError("Max Output non valido.")
        if (not isinstance(stop_sequence, (tuple, list))
                or len(stop_sequence) > 12
                or any(type(s) is not str or not 1 <= len(s) <= 256
                       for s in stop_sequence)):
            raise KoboldCanaryError("Stop sequence non valida.")
        timeout = _positive_number(timeout, "Timeout", 600)
        loaded = self.probe()
        if loaded != expected_model:
            raise KoboldCanaryError(
                "Il modello del server è diverso da quello selezionato: invio bloccato.")
        result = self._request(
            "/api/v1/generate",
            payload={
                "prompt": prompt,
                "max_context_length": max_context_length,
                "max_length": max_length,
                "stop_sequence": list(stop_sequence),
            },
            timeout=timeout,
        )
        replies = result.get("results")
        if (not isinstance(replies, list) or len(replies) != 1
                or not isinstance(replies[0], dict)
                or type(replies[0].get("text")) is not str):
            raise KoboldCanaryError("Generazione KoboldCpp non interpretabile.")
        return replies[0]["text"]
