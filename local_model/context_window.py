"""Bounded, extractive selection of the immediate previous exchange.

No summarizer, model call, persistence or inferred authorizations.
"""
import re

_STOP = frozenset('perché perche come cosa detto della delle degli questo questa quello quella quale quali sono con del che una uno hai spiegami continua'.split())


def _fragment(text, limit):
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(' ', 1)[0].strip() or text[:limit]


def _anchored_fragment(text, limit, question):
    if len(text) <= limit:
        return text
    folded = text.casefold()
    quotes = re.findall(r'["«“]([^"»”]{1,200})["»”]', question)
    positions = [(folded.rfind(q.casefold()), len(q)) for q in quotes
                 if q.casefold() in folded]
    if not positions:
        terms = set(re.findall(r'\w{4,}', question.casefold())) - _STOP
        positions = [(m.start(), len(m.group())) for m in re.finditer(r'\w{4,}', folded)
                     if m.group() in terms]
    at, length = positions[-1] if positions else (0, 0)
    start = max(0, min(len(text)-limit, at - max(0, (limit-length)//2)))
    end = min(len(text), start+limit)
    # Trim partial boundary words without trimming the selected reference.
    if start and text[start-1].isalnum() and text[start].isalnum():
        space = text.find(' ', start, at)
        if space >= 0:
            start = space + 1
    if end < len(text) and text[end-1].isalnum() and text[end].isalnum():
        space = text.rfind(' ', at+length, end)
        if space >= 0:
            end = space
    return text[start:end].strip()


def select_recent_pairs(pairs, fits, question, *, user_fits=lambda text: True):
    """Protect newest pair; shrink only it, then try older complete pairs.

    fits evaluates the complete formatted prompt and all independent budgets.
    Returns history plus metrics containing no conversational content.
    """
    if not pairs:
        return [], {'whole': 0, 'extracted': 0, 'omitted': 0}
    latest = pairs[-1]
    history = []
    extracted = 0
    if fits([latest]):
        history = [latest]
    else:
        user, answer = latest[0][1], latest[1][1]
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', answer) if s.strip()]
        terms = set(re.findall(r'\w{4,}', question.casefold())) - _STOP
        # Prefer the most recent sentence sharing a reference, then neighbors.
        hits = [i for i, s in enumerate(sentences)
                if terms & set(re.findall(r'\w{4,}', s.casefold()))]
        quotes = re.findall(r'["«“]([^"»”]{1,200})["»”]', question)
        quoted = [i for i, sentence in enumerate(sentences)
                  if any(q.casefold() in sentence.casefold() for q in quotes)]
        anchor = quoted[-1] if quoted else (hits[-1] if hits else 0)
        indices = sorted(set([anchor, max(0, anchor-1), min(len(sentences)-1, anchor+1),
                              0, len(sentences)-1]))
        # Anchor must survive progressive shrinking; final order remains original.
        cap = min(4096, max(len(user), len(answer)))
        for _ in range(12):
            u = _fragment(user, min(256, max(8, cap // 4)))
            for _shrink in range(12):
                if user_fits(u):
                    break
                u = _fragment(u, max(1, len(u)//2))
            if not user_fits(u):
                u = ''
            a = _anchored_fragment(sentences[anchor], cap, question) if sentences else ''
            if u and a:
                chosen = {anchor: a}
                remaining = cap - len(a)
                for i in indices:
                    if i != anchor and remaining > 24:
                        fragment = _fragment(sentences[i], remaining)
                        chosen[i] = fragment
                        remaining -= len(fragment) + 1
                a = ' […] '.join(chosen[i] for i in sorted(chosen))
                candidate = (("user", "[Estratto domanda precedente] " + u),
                             ("assistant", "[Estratto risposta precedente; parti omesse] " + a))
                if fits([candidate]):
                    history = [candidate]
                    extracted = 1
                    break
            cap //= 2
            if cap < 8:
                break
    # Never substitute an older subject for a missing immediate antecedent.
    if history:
        for pair in reversed(pairs[:-1]):
            if fits([pair] + history):
                history.insert(0, pair)
    return history, {'whole': len(history)-extracted, 'extracted': extracted,
                     'omitted': len(pairs)-len(history)}
