"""Classificatore leggero di intenzioni (passo 11, opzionale e SPENTO di serie).

Interviene solo quando le regole dei comandi non hanno capito e la frase starebbe per
andare al modello: confronta la frase con gli esempi dei comandi (pezzetti di 3 lettere,
somiglianza coseno, niente reti neurali, pochi KB) e, se una somiglia abbastanza, Lumi
chiede «Intendevi …?». Sì → esegue quel comando; no → la frase va al modello come prima.
Si accende in «La mia voce».
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

SOGLIA = 0.62
MARGINE = 0.06
IN_ATTESA = {"frase": None}


def _norm(text: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", " ", str(text).casefold()).split())


def _vettore(text: str) -> Counter:
    value = " " + _norm(text) + " "
    return Counter(value[i:i + 3] for i in range(len(value) - 2))


def _coseno(a: Counter, b: Counter) -> float:
    dot = sum(v * b.get(k, 0) for k, v in a.items())
    norm = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return dot / norm if norm else 0.0


def esempi() -> list[str]:
    items = []
    try:
        catalog = json.loads(Path(__file__).with_name("jarvis_commands.json").read_text(encoding="utf-8"))
        for action in catalog.get("actions", []):
            items += [e for e in action.get("examples", []) if isinstance(e, str)]
    except (OSError, ValueError):
        pass
    try:
        import la_mia_voce
        items += [p for p in la_mia_voce.PHRASES if len(p.split()) >= 2]
    except ImportError:
        pass
    seen, out = set(), []
    for item in items:
        if _norm(item) and _norm(item) not in seen:
            seen.add(_norm(item))
            out.append(item)
    return out


class Classificatore:
    def __init__(self, examples=None):
        self.examples = list(examples if examples is not None else esempi())
        self.vectors = [_vettore(e) for e in self.examples]

    def indovina(self, text: str):
        """(comando, punteggio) se una frase d'esempio somiglia abbastanza, altrimenti None."""
        if not text or len(text) > 200 or len(_norm(text).split()) < 2:
            return None
        vector = _vettore(text)
        scores = sorted(((_coseno(vector, v), e) for v, e in zip(self.vectors, self.examples)),
                        reverse=True)
        if not scores or scores[0][0] < SOGLIA or _norm(scores[0][1]) == _norm(text):
            return None
        if len(scores) > 1 and scores[0][0] - scores[1][0] < MARGINE and \
                _norm(scores[0][1]) != _norm(scores[1][1]):
            return None              # due comandi quasi uguali: meglio non chiedere a caso
        return scores[0][1], round(scores[0][0], 3)


def attivo() -> bool:
    try:
        import la_mia_voce
        return la_mia_voce._load().get("classificatore") is True
    except ImportError:
        return False


def imposta(on: bool) -> None:
    import la_mia_voce
    path = la_mia_voce._path()
    if path is None:
        return
    data = la_mia_voce._load()
    data["classificatore"] = bool(on)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


_ISTANZA = {"c": None}


def indovina(text: str):
    if not attivo():
        return None
    if _ISTANZA["c"] is None:
        _ISTANZA["c"] = Classificatore()
    return _ISTANZA["c"].indovina(text)
