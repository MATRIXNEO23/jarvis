"""Read-only runtime observations for the local Jarvis executor.

No models, networking, subprocesses, test execution, log reading or file writes.
This captures *observed states*, not promises of functionality. Only fixed
codes and integer counts may be forwarded through the consented GPT handoff.
"""
from __future__ import annotations

from dataclasses import dataclass

EVENT_KINDS = (
    "gpt_failure", "voice_unavailable", "local_failure",
    "document_failure", "project_journal_failure", "telegram_disconnected",
    "diagnostic_failure",
)
CHECK_IDS = ("gpt_link", "voice_input", "local_engine", "project_memory")
CHECK_STATES = ("ready", "attention", "idle", "not_tested")
CHECK_CODES = {
    "gpt_link": frozenset((
        "gpt_disabled", "sdk_missing", "node_missing", "bridge_missing",
        "bridge_not_running", "gpt_not_connected", "gpt_connected_observed",
    )),
    "voice_input": frozenset((
        "voice_not_configured", "voice_standby", "voice_push_to_talk_idle",
        "voice_model_missing", "mic_not_observed", "mic_stream_observed",
    )),
    "local_engine": frozenset((
        "engine_not_initialized", "engine_store_not_found", "engine_store_present",
    )),
    "project_memory": frozenset((
        "project_memory_unavailable", "project_store_not_found",
        "project_store_present",
    )),
}
CODE_DESCRIPTIONS = {
    "gpt_disabled": "ChatGPT disattivato nelle impostazioni",
    "sdk_missing": "SDK Sign in with ChatGPT non trovato",
    "node_missing": "Node.js non trovato nel PATH",
    "bridge_missing": "File bridge GPT assente",
    "bridge_not_running": "Processo bridge non rilevato in questo momento",
    "gpt_not_connected": "Connessione GPT non confermata in questa sessione",
    "gpt_connected_observed": "Connessione GPT segnalata dalla sessione e bridge attivo",
    "voice_not_configured": "Controller vocale non inizializzato",
    "voice_standby": "Microfono in standby, scelta intenzionale",
    "voice_push_to_talk_idle": "Premi per parlare selezionato, nessuno stream richiesto",
    "voice_model_missing": "Cartella modello vocale non trovata",
    "mic_not_observed": "Ascolto selezionato ma stream audio non confermato",
    "mic_stream_observed": "Stream microfono aperto osservato dal controller",
    "engine_not_initialized": "Motore locale non inizializzato",
    "engine_store_not_found": "Archivio motore locale non individuato",
    "engine_store_present": "Oggetto motore e archivio locale presenti",
    "project_memory_unavailable": "Memoria progetti non inizializzata",
    "project_store_not_found": "Archivio memoria progetti non individuato",
    "project_store_present": "Oggetto memoria progetti e archivio presenti",
}


class RuntimeEventCounters:
    """Only categories, never raw messages, user texts, names or paths.

    Bounded in RAM and reset at restart. Not equivalent to reading historical
    Windows logs, nor a comprehensive diagnostic event trace.
    """
    def __init__(self) -> None:
        self._counts = {key: 0 for key in EVENT_KINDS}

    def record(self, category: str) -> None:
        if category in self._counts:
            self._counts[category] = min(99, self._counts[category] + 1)

    def snapshot(self) -> tuple[tuple[str, int], ...]:
        return tuple(self._counts.items())


@dataclass(frozen=True)
class RuntimeEvidence:
    checks: tuple[tuple[str, str, str], ...]
    incidents: tuple[tuple[str, int], ...]


def collect_runtime_evidence(
    *, gpt_enabled: bool, gpt_connected: bool,
    sdk_installed: bool, node_available: bool, bridge_file_present: bool,
    bridge_running: bool, voice_present: bool, voice_mode: str,
    voice_listening: bool, voice_model_present: bool,
    local_engine_present: bool, local_store_present: bool,
    workspace_present: bool, workspace_store_present: bool,
    counters: RuntimeEventCounters,
) -> RuntimeEvidence:
    """Analyze passed-in observations; caller samples real objects on UI thread.

    A connected or initialized component is NOT a successful end-to-end test.
    No side-effectful checks (e.g. a GPT request or mic open) are performed.
    """
    if not gpt_enabled:
        gpt = ("idle", "gpt_disabled")
    elif not sdk_installed:
        gpt = ("attention", "sdk_missing")
    elif not node_available:
        gpt = ("attention", "node_missing")
    elif not bridge_file_present:
        gpt = ("attention", "bridge_missing")
    elif gpt_connected and not bridge_running:
        gpt = ("attention", "bridge_not_running")
    elif not gpt_connected:
        gpt = ("idle", "gpt_not_connected")
    else:
        gpt = ("ready", "gpt_connected_observed")

    if not voice_present:
        voice = ("not_tested", "voice_not_configured")
    elif voice_mode == "standby":
        voice = ("idle", "voice_standby")
    elif not voice_model_present:
        voice = ("attention", "voice_model_missing")
    elif voice_mode == "premi_per_parlare" and not voice_listening:
        voice = ("idle", "voice_push_to_talk_idle")
    elif voice_listening:
        voice = ("ready", "mic_stream_observed")
    else:
        voice = ("attention", "mic_not_observed")

    engine = (("ready", "engine_store_present") if local_engine_present
              and local_store_present else
              ("attention", "engine_store_not_found") if local_engine_present else
              ("not_tested", "engine_not_initialized"))
    projects = (("ready", "project_store_present") if workspace_present
                and workspace_store_present else
                ("attention", "project_store_not_found") if workspace_present else
                ("not_tested", "project_memory_unavailable"))
    return RuntimeEvidence(
        tuple((name, *values) for name, values in (
            ("gpt_link", gpt), ("voice_input", voice),
            ("local_engine", engine), ("project_memory", projects))),
        counters.snapshot(),
    )


def safe_runtime_payload(evidence: RuntimeEvidence | None) -> dict:
    """Whitelist every outbound token. Never serialize untrusted observations."""
    if not isinstance(evidence, RuntimeEvidence):
        return {"scope": "not_collected", "checks": [], "incident_counts": {}}
    checks = []
    seen = set()
    for name, state, code in evidence.checks:
        if (name in CHECK_IDS and name not in seen
                and state in CHECK_STATES and code in CHECK_CODES[name]):
            checks.append({"component": name, "state": state, "evidence": code})
            seen.add(name)
    incidents = {key: 0 for key in EVENT_KINDS}
    for key, count in evidence.incidents:
        if key in incidents and type(count) is int:
            incidents[key] = max(0, min(99, count))
    return {
        "scope": "current_process_observation_only",
        "checks": checks[:len(CHECK_IDS)],
        "incident_counts": incidents,
    }


def format_runtime_evidence(evidence: RuntimeEvidence) -> str:
    lines = ["Stato locale osservato (non test funzionali end-to-end):"]
    for name, state, code in evidence.checks:
        if code in CHECK_CODES.get(name, ()) and state in CHECK_STATES:
            lines.append("- " + name + " [" + state + "]: " + CODE_DESCRIPTIONS[code])
    observed = [(kind, count) for kind, count in evidence.incidents
                if kind in EVENT_KINDS and type(count) is int and count > 0]
    if observed:
        lines.append("Eventi di errore osservati in questa istanza (solo conteggi):")
        lines.extend("- " + kind + ": " + str(min(count, 99))
                     for kind, count in observed)
    else:
        lines.append("Nessun evento di errore registrato in questa istanza; "
                     "questo non significa che non esistano errori.")
    lines.append("Non ho letto log Windows, file privati o documenti; non ho "
                 "testato le funzioni, eseguito comandi o contattato GPT.")
    return "\n".join(lines)

# Local-only telemetry: not included in the consented external audit payload.
TELEGRAM_PHASES = {
    'starting': 'Avvio listener', 'dependency': 'Verifica Telethon',
    'credentials': 'Caricamento credenziali', 'connecting': 'Connessione',
    'authorizing': 'Verifica sessione', 'contacts': 'Verifica contatti',
    'listening': 'Listener registrato, in attesa', 'received': 'Messaggio acquisito',
    'transcribing': 'Trascrizione vocale', 'model': 'Risposta del modello',
    'synthesis': 'Sintesi vocale', 'sending': 'Invio Telegram',
    'stopped': 'Listener fermo',
}
SERVICE_EVENTS = {
    'starting': ('starting', 'Avvio richiesto'),
    'dependency': ('dependency', 'Verifica dipendenza Telethon'),
    'credentials': ('credentials', 'Lettura credenziali protette'),
    'connecting': ('connecting', 'Connessione richiesta'),
    'connected': ('authorizing', 'Connessione stabilita'),
    'authorized': ('contacts', 'Sessione autorizzata'),
    'contacts_ready': ('contacts', 'Contatti selezionati verificati'),
    'listening': ('listening', 'Handler registrati, ricezione non ancora provata'),
    'update': (None, 'Aggiornamento grezzo osservato'),
    'message_update': (None, 'Aggiornamento di nuovo messaggio osservato'),
    'filtered_contact': (None, 'Messaggio escluso: contatto non autorizzato'),
    'filtered_non_private': (None, 'Messaggio escluso: chat non privata'),
    'filtered_outgoing': (None, 'Messaggio uscente escluso'),
    'duplicate': (None, 'Aggiornamento duplicato escluso'),
    'received': ('received', 'Messaggio autorizzato acquisito'),
    'transcribing': ('transcribing', 'Trascrizione vocale richiesta'),
    'input_empty': (None, 'Testo o trascrizione vuoti'),
    'rate_limited': (None, 'Risposta sospesa per limite frequenza'),
    'model_started': ('model', 'Risposta modello richiesta'),
    'reply_ready': (None, 'Risposta ottenuta'),
    'reply_empty': (None, 'Nessuna risposta utilizzabile dal modello'),
    'synthesis_started': ('synthesis', 'Creazione del vocale'),
    'send_started': ('sending', 'Invio del vocale richiesto'),
    'sent': ('listening', 'Ricevuta di invio ottenuta'),
    'stopped': ('stopped', 'Listener terminato'),
    'dependency_failed': (None, 'Dipendenza Telegram non disponibile'),
    'credentials_failed': (None, 'Caricamento credenziali fallito'),
    'connection_failed': (None, 'Connessione Telegram fallita'),
    'authorization_failed': (None, 'Sessione Telegram non autorizzata'),
    'contacts_failed': (None, 'Verifica contatti fallita'),
    'transcription_failed': (None, 'Trascrizione vocale fallita'),
    'model_failed': (None, 'Elaborazione modello fallita'),
    'synthesis_failed': (None, 'Creazione del vocale fallita'),
    'send_failed': (None, 'Invio del vocale fallito o incerto'),
    'listener_failed': (None, 'Listener interrotto'),
    'processing_failed': (None, 'Elaborazione del messaggio fallita'),
}
_PHASE_FAILURE = {'dependency': 'dependency_failed', 'credentials': 'credentials_failed',
    'connecting': 'connection_failed', 'authorizing': 'authorization_failed',
    'contacts': 'contacts_failed', 'transcribing': 'transcription_failed',
    'model': 'model_failed', 'synthesis': 'synthesis_failed', 'sending': 'send_failed'}


class ServiceEventLog:
    """64 events and fixed counters in RAM; accepts codes, never message text."""
    def __init__(self):
        from collections import deque
        from threading import Lock
        self._lock = Lock()
        self._events = deque(maxlen=64)
        self._counts = {code: 0 for code in SERVICE_EVENTS}
        self._phase = 'stopped'
        self._error = ''
        self._error_phase = ''

    def record(self, code):
        if type(code) is not str or code not in SERVICE_EVENTS:
            return
        import time
        with self._lock:
            phase, _ = SERVICE_EVENTS[code]
            if phase:
                self._phase = phase
            self._counts[code] = min(9999, self._counts[code] + 1)
            self._events.append((int(time.time()), code))
            if code.endswith('_failed') or code == 'reply_empty':
                self._error, self._error_phase = code, self._phase

    def failed(self):
        with self._lock:
            code = _PHASE_FAILURE.get(self._phase, 'listener_failed')
        self.record(code)

    def snapshot(self):
        with self._lock:
            return dict(phase=self._phase, counts=dict(self._counts),
                        events=tuple(self._events), last_error=self._error,
                        error_phase=self._error_phase)


def format_service_report(evidence, *, telegram=None, automatic=False,
                          credentials=False, contacts=0, selected='Gemma',
                          gemma='non_loaded', memory=False, telethon=None, ffmpeg=None):
    """Format only whitelisted observations. This report stays on the PC."""
    import time
    labels = {'gpt_link': 'GPT', 'voice_input': 'Microfono',
              'local_engine': 'Motore locale', 'project_memory': 'Archivio progetti'}
    gemma_states = {'non_loaded': 'non avviato (nessun caricamento richiesto)',
                    'ready': 'sessione presente, inferenza non testata qui',
                    'busy': 'sessione impegnata', 'unavailable': 'stato non disponibile'}
    lines = ['DIAGNOSTICA SERVIZI — osservazione locale, non un collaudo completo',
             'Modello selezionato: ' + ('GPT' if selected == 'GPT' else 'Gemma'),
             'Gemma: ' + gemma_states.get(gemma, gemma_states['unavailable']),
             'Memoria generale: ' + ('attiva' if memory else 'disattivata')]
    for name, state, code in evidence.checks:
        if name in labels and code in CHECK_CODES[name] and state in CHECK_STATES:
            lines.append(labels[name] + ': ' + CODE_DESCRIPTIONS[code])
    incidents = [(k,n) for k,n in evidence.incidents if k in EVENT_KINDS and type(n) is int and n>0]
    lines.extend('Eventi '+k+': '+str(min(n,99)) for k,n in incidents)
    lines += ['', 'Telegram — ricezione e risposta automatica',
              'Risposte automatiche richieste: ' + ('sì' if automatic else 'no'),
              'Credenziali protette presenti: ' + ('sì (validità non verificata qui)' if credentials else 'no'),
              'Contatti selezionati: '+str(max(0,min(250,contacts)) if type(contacts) is int else 0)]
    if telethon is not None:
        lines.append('Telethon: '+('installato' if telethon else 'assente — esegui installa_telegram.bat'))
    if ffmpeg is not None:
        lines.append('FFmpeg per i vocali: '+('rilevato nel PATH' if ffmpeg else 'non rilevato — controlla installa_telegram.bat'))
    if not telegram:
        lines.append('Listener non avviato. L’invio manuale non prova la ricezione automatica.')
    else:
        phase = telegram.get('phase', '')
        lines.append('Ultima fase osservata: '+TELEGRAM_PHASES.get(phase,'non disponibile'))
        counts = telegram.get('counts', {})
        def count(key):
            value = counts.get(key, 0)
            return max(0,min(9999,value)) if type(value) is int else 0
        for key,label in [('update','Aggiornamenti grezzi'),('message_update','Aggiornamenti nuovi messaggi'),
                          ('received','Messaggi autorizzati ricevuti'),('filtered_contact','Esclusi per contatto'),
                          ('duplicate','Duplicati esclusi'),('model_started','Richieste al modello'),
                          ('sent','Risposte con ricevuta di invio')]:
            lines.append(label+': '+str(count(key)))
        if not count('received'):
            lines.append('Nessuna ricezione autorizzata osservata in questo listener: causa non ancora determinata.')
        code=telegram.get('last_error','')
        if code in SERVICE_EVENTS:
            lines.append('Ultimo errore: '+SERVICE_EVENTS[code][1]+'; fase '+
                         TELEGRAM_PHASES.get(telegram.get('error_phase',''),'non disponibile'))
        lines.append('Ultimi eventi (massimo 64, nessun contenuto dei messaggi):')
        for stamp,code in telegram.get('events', ())[-64:]:
            if type(stamp) is int and 0 <= stamp <= 4102444800 and code in SERVICE_EVENTS:
                lines.append(time.strftime('%H:%M:%S',time.localtime(stamp))+' — '+SERVICE_EVENTS[code][1])
    lines += ['', 'Aggiorna per rileggere lo stato. Nessuna richiesta a GPT/Gemma, apertura del microfono o invio di prova.',
              'Registro solo in RAM: si azzera riavviando Jarvis o sostituendo il listener. Nessuna conversazione esportata.']
    return '\n'.join(lines)
