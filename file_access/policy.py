"""Persist user-selected roots and exceptions. Never changes Windows ACLs."""
from __future__ import annotations
import json
import os
from pathlib import Path
import threading
from .windows import resolved_path, volume_identity


def contains(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def safe_path(value) -> Path:
    if not isinstance(value, (str, Path)):
        raise ValueError('Percorso non valido.')
    text = str(value)
    if (not text or len(text) > 32000 or any(ord(c) < 32 for c in text)
            or text.startswith(('\\\\', '//')) or ':' in text[2:]):
        raise ValueError('Usa un percorso di una cartella su disco locale o rimovibile.')
    path = Path(os.path.abspath(text))
    if not Path(text).is_absolute():
        raise ValueError('Indica un percorso assoluto.')
    return path


class AccessPolicy:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._lock = threading.RLock()
        self.revision = 0
        self._rules = []
        self.error = ''
        self._stamp = None
        self.reload()

    def reload(self):
        with self._lock:
            self._rules = []
            self.error = ''
            try:
                if not self.path.exists():
                    return
                if self.path.is_symlink() or self.path.stat().st_size > 64000:
                    raise ValueError('File regole non valido.')
                value = json.loads(self.path.read_text(encoding='utf-8'))
                if (set(value) != {'schema', 'rules'} or value['schema'] != 1
                        or not isinstance(value['rules'], list) or len(value['rules']) > 200):
                    raise ValueError('Regole non riconosciute.')
                seen = set()
                for row in value['rules']:
                    if (not isinstance(row, dict) or set(row) != {'path', 'allow', 'volume', 'device', 'inode'}
                            or type(row['allow']) is not bool
                            or not isinstance(row['volume'], str)
                            or type(row['device']) is not int or type(row['inode']) is not int):
                        raise ValueError('Regola cartella non valida.')
                    key = str(safe_path(row['path'])).casefold()
                    if key in seen:
                        raise ValueError('Regole duplicate.')
                    seen.add(key)
                    self._rules.append(dict(row))
            except (OSError, ValueError, TypeError, KeyError):
                self._rules = []
                self.error = 'Regole Accesso file non leggibili: riapri Configura e seleziona le cartelle.'
            finally:
                self.revision += 1
                self._stamp = self._signature()

    def _signature(self):
        try:
            stat = self.path.stat()
            return stat.st_mtime_ns, stat.st_size, stat.st_ino
        except OSError:
            return None

    def ensure_current(self):
        if self._signature() != self._stamp:
            self.reload()

    def rules(self):
        with self._lock:
            return [dict(r) for r in self._rules]

    def configure(self, rules):
        """UI-owned only: store exact folder identity, volume and simple flag."""
        if not isinstance(rules, list) or len(rules) > 200:
            raise ValueError('Troppe regole cartelle.')
        fresh = {}
        previous = {str(Path(r["path"])).casefold(): r for r in self.rules()}
        for path, allow in rules:
            existing = previous.get(str(safe_path(path)).casefold())
            if existing is not None and existing["allow"] == allow:
                fresh[str(safe_path(path)).casefold()] = existing
                continue
            if type(allow) is not bool:
                raise ValueError('Spunta non valida.')
            actual = resolved_path(safe_path(path))
            if not actual.is_dir():
                raise ValueError('Seleziona una cartella esistente.')
            info = actual.stat()
            fresh[str(actual).casefold()] = {'path': str(actual), 'allow': allow,
                'volume': volume_identity(actual), 'device': info.st_dev, 'inode': info.st_ino}
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix('.tmp')
            if self.path.is_symlink() or temporary.is_symlink():
                raise ValueError('Configurazione non sicura: percorso collegato.')
            data = json.dumps({'schema': 1, 'rules': list(fresh.values())}, ensure_ascii=False, indent=2)
            with temporary.open('w', encoding='utf-8') as stream:
                stream.write(data+'\n')
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
            self._rules = list(fresh.values())
            self.error = ''
            self.revision += 1
            self._stamp = self._signature()

    def valid_roots(self):
        self.ensure_current()
        valid = []
        with self._lock:
            rows = self.rules()
        for row in rows:
            if not row["allow"]:
                valid.append(row)
                continue
            try:
                path = Path(row['path'])
                stat = path.stat()
                if (stat.st_dev, stat.st_ino) != (row['device'], row['inode']):
                    continue
                if volume_identity(path) != row['volume'] or resolved_path(path) != path:
                    continue
                valid.append(row)
            except OSError:
                continue
        return valid

    def permits(self, path: Path, *, resolved: bool = False) -> bool:
        try:
            lexical = safe_path(path)
            actual = lexical if resolved else resolved_path(lexical)
            rows = self.valid_roots()
            def allowed(target):
                matches = [r for r in rows if contains(Path(r['path']), target)]
                if not matches:
                    return False
                winner = max(matches, key=lambda r: len(Path(r['path']).parts))
                return winner['allow']
            return allowed(lexical) and allowed(actual)
        except (OSError, ValueError):
            return False

    def may_descend(self, path: Path) -> bool:
        # An explicitly reincluded child may be reachable through excluded parents,
        # but those parents and their unrelated siblings are not listed as results.
        if self.permits(path):
            return True
        return any(r['allow'] and contains(path, Path(r['path'])) for r in self.valid_roots())
