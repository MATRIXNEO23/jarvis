"""Shared model routing; no UI, executable launch or tool execution here.

Consent is a per-call owner decision, never a model-generated permission.
Transports retain their own bounded timeouts. Configuration changes revoke
in-flight results; an already submitted inference cannot be un-sent.
"""
import queue
import threading
from gpt_client import GPTUnavailable


class ModelService:
    def __init__(self, online, local, *, local_enabled=False,
                 online_enabled=False, consent=None):
        self.online = online
        self.local = local
        self.local_selected = bool(local_enabled)
        self.online_enabled = bool(online_enabled)
        self.consent = consent
        self.events = queue.Queue()
        self._lock = threading.RLock()
        self._inference_lock = threading.Lock()
        self._epoch = 0
        self._closed = False

    def configure(self, *, local_enabled, online_enabled):
        if type(local_enabled) is not bool or type(online_enabled) is not bool:
            raise ValueError('Stato modello non valido.')
        with self._lock:
            self.local_selected = local_enabled
            self.online_enabled = online_enabled
            self._epoch += 1

    def _check(self, epoch, *, online=False):
        if self._closed or epoch != self._epoch:
            raise GPTUnavailable('Richiesta annullata: configurazione modello cambiata.')
        if online and not self.online_enabled:
            raise GPTUnavailable('Modello online disattivato.')

    def call(self, action, *, timeout=120, **arguments):
        force_online = arguments.pop('force_online', False)
        origin = arguments.pop('origin', 'proprietario')
        if type(force_online) is not bool or origin not in ('proprietario', 'Telegram'):
            raise GPTUnavailable('Origine o selezione modello non valida.')
        with self._lock:
            epoch = self._epoch
            self._check(epoch)
            local = self.local_selected
        # Account management is distinct from inference and never implies
        # future approval to spend model quota.
        if action != 'ask':
            if action not in ('status', 'sign_in', 'disconnect', 'cancel_sign_in'):
                raise GPTUnavailable('Operazione modello non supportata.')
            if action == 'status' and local:
                return {'status': 'connected', 'sharing': True,
                        'profileLabel': 'Gemma locale', 'provider': 'local'}
            with self._lock:
                self._check(epoch, online=True)
            return self.online.call(action, timeout=timeout, **arguments)
        with self._inference_lock:
            with self._lock:
                self._check(epoch)
            reason = 'Richiesta esplicita al modello online.'
            if local and not force_online:
                try:
                    result = self.local.ask(timeout=timeout, **arguments)
                except (RuntimeError, OSError) as exc:
                    # Do not forward raw prompts, local paths or backend errors
                    # into consent labels or public diagnostics.
                    reason = 'Il modello locale non ha completato la richiesta.'
                else:
                    with self._lock:
                        self._check(epoch)
                    return result
            with self._lock:
                self._check(epoch, online=True)
            if not callable(self.consent) or self.consent(
                    reason=reason, origin=origin, timeout=timeout) is not True:
                raise GPTUnavailable('Uso del modello online non autorizzato.')
            # Consent is consumed by this invocation only. OFF while waiting
            # must prevent the transport call even after a positive response.
            with self._lock:
                self._check(epoch, online=True)
            result = self.online.call(action, timeout=timeout, **arguments)
            with self._lock:
                self._check(epoch, online=True)
            return result

    def stop(self):
        with self._lock:
            self._closed = True
            self._epoch += 1
        self.local.stop()
        self.online.stop()
