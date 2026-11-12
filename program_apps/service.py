"""Saved application consent, local language and revocable launch requests."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
import json
import os
from pathlib import Path
import re
import threading
import time
import uuid

from . import native


def normalized(text):
    return ' '.join(re.sub(r'[,.;:!?]+', ' ', str(text).casefold()).split())


def name_key(text):
    return re.sub(r"^(?:(?:il|lo|la|gli|le|un|una)\s+|l')", '', normalized(text)).strip()


def blocked(text):
    value = normalized(text)
    return bool(re.search(r'\b(non|mai|evita|senza)\b', value) or
                re.match(r'^(come|perch[eé]|quanto|cosa|dove)\b', value))


def launch_query(text):
    value = normalized(text)
    value = re.sub(r'^(?:(?:ehi|hey) )?lumi\s+', '', value)
    value = value.removesuffix(' per favore')
    match = re.fullmatch(r'(?:(?:per favore|gentilmente) )?'
        r'(?:(?:mi )?(?:puoi|potresti|vorrei|voglio)(?: che tu)? )?(?:mi )?'
        r'(?:aprimi|apri|aprire|avviami|avvia|avviare|lanciami|lancia|lanciare|'
        r'eseguimi|esegui|eseguire|fammi partire|fai partire|far partire|'
        r'metti in esecuzione|mettere in esecuzione)'
        r'(?: (.+))?', value)
    return name_key(match.group(1) or '') if match else None


def protected(text):
    from voice_control import speech_to_local_command
    from desktop_dictation import dictation_voice_action
    from project_voice import parse_project_voice
    from preference_voice import parse_preference_intent
    from self_diagnostics import diagnostic_request
    from telegram_outbound_flow import parse_telegram_send_intent
    from project_documents import parse_simple_save
    from document_language import classify_document_choice
    query = launch_query(text)
    try:
        project = parse_project_voice(text)
    except ValueError:
        project = None
    # Project's generic "apri X" grammar also accepts application names.
    # Only explicit project requests and non-launch project verbs are reserved.
    project_reserved = bool(project and (project.action!='open' or query is None
                            or re.search(r'\bprogett[oi]\b',normalized(text))))
    return bool(speech_to_local_command(text) or dictation_voice_action(text)
        or project_reserved or parse_preference_intent(text)
        or diagnostic_request(text) or parse_telegram_send_intent(text) or
        parse_simple_save(text) is not None or
        classify_document_choice(text,pending=True) in ('save','discard','cancel') or
        re.search(r'\b(file|cartella|cartelle|documento|documenti|blocco note|notepad|'
                  r'calcolatrice|calc|esplora risorse|esplora file|browser|download|'
                  r'disco locale|unità|unita|progett[oi]|timer|promemoria|telegram|dettatura)\b', normalized(text)) or
        normalized(text) in ('annulla', 'stop', 'basta', 'aiuto', 'comandi', 'stato sistema'))


@dataclass(frozen=True)
class ProgramResult:
    status: str
    message: str
    listing: dict | None = None


class ProgramService:
    def __init__(self, folder, enabled, *, discoverer=None, launcher=None, clock=time.monotonic):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        if self.folder.is_symlink():
            raise ValueError('Cartella dati Programmi e app non valida.')
        self.path = self.folder / 'programs.json'
        self.enabled = enabled
        self.discoverer = discoverer or native.discover
        self.launcher = launcher or native.launch
        self.clock = clock
        self._lock = threading.RLock()
        self._apps, self._preferences, self._available = {}, {}, set()
        self.warnings = []
        self._revision = 0
        self._pending = None
        self._context = None
        self._load()

    def _load(self):
        if not self.path.exists():
            return
        if self.path.is_symlink() or self.path.stat().st_size > 8_000_000:
            raise ValueError('Archivio programmi non valido.')
        data = json.loads(self.path.read_text(encoding='utf-8'))
        if data.get('schema') != 1:
            raise ValueError('Archivio programmi non riconosciuto.')
        self._apps = {row['id']: native.AppEntry(**row) for row in data['apps']}
        self._available = set(data['available']) & self._apps.keys()
        self._preferences = self._validate_preferences(data['preferences'], check_names=False)
        self.warnings = list(data.get('warnings', []))

    def _persist(self, apps, preferences, available, warnings):
        if self.path.is_symlink():
            raise ValueError('Archivio programmi non valido.')
        data = dict(schema=1, apps=[asdict(a) for a in apps.values()],
                    preferences=preferences, available=sorted(available), warnings=warnings)
        temporary = self.path.with_suffix('.tmp')
        if temporary.is_symlink():
            raise ValueError('Archivio temporaneo programmi non valido.')
        try:
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            os.replace(temporary, self.path)
        finally:
            if temporary.is_file():
                temporary.unlink()
        self._apps, self._preferences = apps, preferences
        self._available, self.warnings = set(available), list(warnings)
        self._revision += 1
        self.reset()

    def entries(self):
        with self._lock:
            return tuple(dict(asdict(app), available=app.id in self._available,
                              enabled=self._preferences.get(app.id, {}).get('enabled', False),
                              phrase=self._preferences.get(app.id, {}).get('phrase', ''))
                         for app in sorted(self._apps.values(), key=lambda a:(a.name.casefold(), a.id)))

    def _validate_preferences(self, values, apps=None, *, check_names=True):
        apps = self._apps if apps is None else apps
        if not isinstance(values, dict) or any(key not in apps for key in values):
            raise ValueError('Selezione programmi non valida.')
        clean, aliases = {}, {}
        for ident, value in values.items():
            if (not isinstance(value, dict) or set(value) != {'enabled', 'phrase'}
                    or type(value['enabled']) is not bool or not isinstance(value['phrase'], str)
                    or len(value['phrase']) > 160 or any(ord(c)<32 for c in value['phrase'])):
                raise ValueError('Comando o selezione programma non valido.')
            phrase = value['phrase'].strip()
            if phrase:
                if blocked(phrase) or protected(phrase):
                    raise ValueError('Questa frase è riservata a un comando esistente o contiene una negazione.')
                keys = {normalized(phrase), launch_query(phrase) or normalized(phrase)}
                for key in keys:
                    if key in aliases and aliases[key] != ident:
                        raise ValueError('Comando personalizzato già usato da un altro programma.')
                    if check_names and any(other.id != ident and name_key(other.name) == key for other in apps.values()):
                        raise ValueError('Il comando coincide con il nome di un altro programma.')
                    aliases[key] = ident
            clean[ident] = dict(enabled=value['enabled'], phrase=phrase)
        return clean

    def save_preferences(self, preferences):
        with self._lock:
            clean = self._validate_preferences(preferences)
            self._persist(dict(self._apps), clean, self._available, self.warnings)

    def refresh_catalog(self, cancelled=None):
        found, warnings = self.discoverer(cancelled)
        with self._lock:
            apps, prefs = dict(self._apps), {k:dict(v) for k,v in self._preferences.items()}
            available = set(self._available) if warnings else set()
            for app in found:
                previous = apps.get(app.id)
                if previous and previous.manual:
                    app = native.AppEntry(**dict(asdict(app), manual=True))
                if previous and previous.fingerprint != app.fingerprint and (app.kind=='lnk' or app.manual):
                    prefs[app.id] = dict(enabled=False, phrase=prefs.get(app.id,{}).get('phrase',''))
                apps[app.id] = app
                available.add(app.id)
            for app in apps.values():
                if app.manual:
                    try:
                        if native.fingerprint(app.target) == app.fingerprint:
                            available.add(app.id)
                    except OSError:
                        available.discard(app.id)
                    except ValueError:
                        available.discard(app.id)
            # New discovered names cannot silently take over an existing alias.
            try:
                self._validate_preferences(prefs, apps)
            except ValueError:
                warnings = list(warnings) + ['Nuovi nomi in conflitto: controlla i comandi personalizzati.']
                # Existing explicit aliases still refer to the same IDs; ambiguous
                # queries are resolved below by a choice, never by first match.
            self._persist(apps, prefs, available, warnings)
        return self.entries()

    def add_manual(self, path):
        candidate = native.manual_entry(path)
        with self._lock:
            apps = dict(self._apps)
            previous = apps.get(candidate.id)
            prefs = {k:dict(v) for k,v in self._preferences.items()}
            if previous and previous.fingerprint != candidate.fingerprint:
                prefs[candidate.id] = dict(enabled=False, phrase=prefs.get(candidate.id,{}).get('phrase',''))
            apps[candidate.id] = candidate
            self._persist(apps, prefs, self._available | {candidate.id}, self.warnings)
        return candidate.id

    def available(self):
        return self.enabled() is True

    def reset(self, context=None):
        self._pending = None
        self._context = context

    def _live_pending(self):
        pending = self._pending
        if pending and (pending['revision'] != self._revision or pending['expires'] < self.clock()
                        or not self.available()):
            self.reset(self._context)
        return self._pending

    def _matches(self, query):
        key = name_key(query)
        exact, partial = [], []
        for app in self._apps.values():
            preference = self._preferences.get(app.id, {})
            phrase = preference.get('phrase','')
            keys = {name_key(app.name)}
            if phrase:
                keys.add(launch_query(phrase) or normalized(phrase))
            if key in keys or normalized(query) == normalized(phrase) and phrase:
                exact.append(app.id)
            elif key and any(key in candidate for candidate in keys):
                partial.append(app.id)
        return exact or partial

    def _similar(self, query):
        key = name_key(query)
        if not 5 <= len(key) <= 80:
            return []
        matches = []
        for app in self._apps.values():
            preference = self._preferences.get(app.id, {})
            if app.id not in self._available or not preference.get('enabled'):
                continue
            phrase = preference.get('phrase', '')
            aliases = {name_key(app.name), launch_query(phrase) or normalized(phrase)}
            if any(candidate and SequenceMatcher(None, key, candidate).ratio() >= .82
                   for candidate in aliases):
                matches.append(app.id)
        return matches

    def _exact(self, query, ident):
        app = self._apps[ident]
        phrase = self._preferences.get(ident,{}).get('phrase','')
        return (name_key(query)==name_key(app.name) or bool(phrase and
            (normalized(query)==normalized(phrase) or
             name_key(query)==(launch_query(phrase) or normalized(phrase)))))

    def is_pending_answer(self, text):
        with self._lock:
            pending = self._live_pending()
            if not pending or blocked(text) or protected(text):
                return False
            value = normalized(text)
            if re.fullmatch(r'(?:il |la |numero )?\d+', value) or value in ('il primo','il secondo','il terzo','il quarto'):
                return True
            return len([key for key in self._matches(text) if key in pending['ids']]) == 1

    def parse_command(self, text):
        with self._lock:
            if not self.available():
                self.reset(self._context)
                return None
            value = normalized(text)
            if value in ('annulla', 'stop', 'basta') and self._live_pending():
                return 'cancel', {}
            if blocked(text) or protected(text):
                self.reset(self._context)
                return None
            pending = self._live_pending()
            if pending:
                if not pending['query']:
                    if any(key in pending['ids'] for key in self._matches(text) or self._similar(text)):
                        return 'launch', {'query':text}
                if pending['query'] and len(pending['ids']) == 1 and _is_yes(text):
                    return 'select', {'query': '1', 'token': pending['token']}
                number = re.fullmatch(r'(?:il |la |numero )?(\d+)', value)
                ordinal = {'il primo':1, 'il secondo':2, 'il terzo':3, 'il quarto':4}
                index = int(number.group(1)) if number else ordinal.get(value)
                matches = [key for key in self._matches(text) if key in pending['ids']]
                if pending['query'] and (index is not None or len(matches)==1):
                    return 'select', {'query':str(index) if index is not None else text,
                                      'token':pending['token']}
            query = launch_query(text)
            if query is not None:
                self.reset(self._context)
                if not query:
                    return 'choose', {}
                matches = self._matches(query)
                if not matches and self._similar(query):
                    return 'launch', {'query':query}
                if any(self._preferences.get(key,{}).get('enabled') or self._exact(query,key) for key in matches):
                    return 'launch', {'query':query}
                return None
            exact = [app.id for app in self._apps.values() if
                self._preferences.get(app.id,{}).get('phrase') and
                value == normalized(self._preferences[app.id]['phrase'])]
            if exact:
                self.reset(self._context)
                return 'launch', {'query':text}
            if pending and not re.match(r'^(quello|quella|questo|questa|intendevo|intendo|il programma|la app)\b',value):
                self.reset(self._context)
            return None

    def execute(self, operation, arguments):
        with self._lock:
            if not self.available():
                self.reset(self._context)
                return ProgramResult('rejected', 'Programmi e app non è attivo.')
            if operation == 'cancel':
                self.reset(self._context)
                return ProgramResult('completed', 'Avvio annullato.')
            if operation == 'choose' and arguments == {}:
                allowed = [key for key in self._apps if key in self._available
                           and self._preferences.get(key, {}).get('enabled')]
                self.reset(self._context)
                if not allowed:
                    return ProgramResult('rejected', 'Abilita almeno un programma in Programmi e app.')
                _expect_answer()
                self._pending = dict(token=uuid.uuid4().hex, ids=allowed, revision=self._revision,
                                     expires=self.clock()+120, query='')
                return ProgramResult('completed', 'Quale programma vuoi aprire?')
            if (operation not in ('launch','launch_id','select','suggest_id') or not isinstance(arguments,dict)
                    or set(arguments) - {'query','token'} or not isinstance(arguments.get('query'),str)
                    or not 1 <= len(arguments['query'].strip()) <= 300):
                return ProgramResult('rejected', 'Richiesta programma non valida.')
            query = arguments['query'].strip()
            if blocked(query):
                self.reset(self._context)
                return ProgramResult('rejected', 'Nessun programma avviato.')
            if operation == 'select':
                pending = self._live_pending()
                if not pending or arguments.get('token') != pending['token']:
                    return ProgramResult('rejected', 'Scelta scaduta o revocata; ripeti la richiesta di avvio.')
                if query.isdecimal() and pending['query']:
                    index = int(query)-1
                    matches = [pending['ids'][index]] if 0 <= index < len(pending['ids']) else []
                else:
                    matches = [key for key in self._matches(query) if key in pending['ids']]
            else:
                self.reset(self._context)
                matches = ([query] if query in self._apps else []) if operation in ('launch_id','suggest_id') else self._matches(query)
                if operation == 'launch' and not matches:
                    matches = self._similar(query)
            allowed = [key for key in matches if self._preferences.get(key,{}).get('enabled')]
            if not allowed:
                if not matches:
                    return ProgramResult('rejected', 'Programma non presente nel catalogo: aggiorna l’elenco in Programmi e app.')
                return ProgramResult('rejected', 'Programma presente ma non autorizzato: abilitalo in Programmi e app.')
            if operation == 'suggest_id' or len(allowed)>1 or (operation=='launch' and len(allowed)==1 and not self._exact(query,allowed[0])):
                token = uuid.uuid4().hex
                _expect_answer()
                self._pending = dict(token=token, ids=allowed, revision=self._revision,
                                     expires=self.clock()+120, query=query)
                message = ('Intendevi '+self._apps[allowed[0]].name+'? Di’ sì o annulla.'
                           if len(allowed) == 1 else
                           'Quale programma vuoi avviare? Scegli il nome o il numero.')
                return ProgramResult('completed', message,
                    dict(token=token, rows=[dict(number=i+1, id=key, name=self._apps[key].name,
                        kind=self._apps[key].kind, target=self._apps[key].target) for i,key in enumerate(allowed)]))
            self.reset(self._context)  # consume before crossing the native boundary
            key = allowed[0]
            if key not in self._available:
                return ProgramResult('rejected', 'Programma non disponibile: aggiorna l’elenco.')
            # The lock covers consent and activation; a stale queued proposal
            # cannot retain permission after a successful settings change.
            if not self.enabled():
                return ProgramResult('rejected', 'Add-on disattivato prima dell’avvio.')
            try:
                return ProgramResult('completed', self.launcher(self._apps[key]))
            except (OSError, ValueError) as exc:
                return ProgramResult('failed', 'Avvio non riuscito: '+str(exc)[:240])

    def context_hint(self):
        with self._lock:
            pending = self._live_pending()
            if not pending:
                return ''
            names = [self._apps[key].name[:45] for key in pending['ids'][:5]]
            return 'Avvio programma in attesa: '+pending['query'][:70]+'. Candidati: '+', '.join(names)

    def commands(self):
        if not self.available():
            return ''
        chosen = [row for row in self.entries() if row['enabled'] and row['available']]
        return ('Programmi e app: apri/aprimi/avvia/avviami/lancia NOME, oppure il comando personalizzato.\n'
                + '\n'.join(row['name']+(' — '+row['phrase'] if row['phrase'] else '') for row in chosen))


def _is_yes(text) -> bool:
    try:
        import risposte
        return risposte.is_yes(text)
    except ImportError:
        return normalized(text) in ('sì', 'si', 'confermo')


def _expect_answer() -> None:
    """La risposta (sì / numero) vale anche senza dire «Lumi»."""
    try:
        import risposte
        risposte.expect_answer()
    except ImportError:
        pass
