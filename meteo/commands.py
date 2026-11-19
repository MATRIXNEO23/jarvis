"""Frasi del meteo: «che tempo fa a Roma», «meteo Milano», «com'è il tempo a Tokyo»,
e (057) «meteo domani», «meteo domani a Roma», «che tempo farà domani»; (058) «meteo settimana».

Escluse le frasi con «online» (restano ricerche) e quelle sul «clima» (es. «com'è il clima a
Tokyo in primavera»): le seconde sono domande più complesse, non il tempo di adesso."""
from __future__ import annotations

import re

_WAKE = re.compile(r"^\s*(?:(?:ehi|hey|ok)\s+)?lumi[\s,!.:]*", re.I)
_CODA = re.compile(r"(?:\s+(?:oggi|adesso|ora|in\s+questo\s+momento|per\s+favore))+[\s.!?]*$", re.I)
_CITTA = r"(?:\s+(?:(?:a|ad|in|di|per|su|nella\s+città\s+di)\s+)?(?P<citta>[^\d,;:]{2,40}?))?[\s.!?]*$"
_PATTERN = re.compile(
    r"^(?:(?:che|quale)\s+tempo\s+fa|com['’]è\s+il\s+tempo|come\s+è\s+il\s+tempo|"
    r"(?:dimmi\s+)?(?:il\s+|le\s+)?(?:meteo|previsioni(?:\s+del\s+tempo)?))" + _CITTA, re.I)
_DOMANI = re.compile(r"\s*\bdomani\b\s*", re.I)
_SETTIMANA = re.compile(r"\s*\b(?:(?:per|nella|della|questa|la|nei\s+prossimi\s+sette\s+giorni)\s+)*"
                        r"settimana\b\s*", re.I)
_GIORNO = re.compile(r"\s*\b(?:(?:di|per|il|del|nel|per\s+il)\s+)?(?P<g>luned[iì]|marted[iì]|mercoled[iì]|"
                     r"gioved[iì]|venerd[iì]|sabato|domenica|weekend|fine\s+settimana)\b\s*", re.I)
_PARTE = re.compile(r"\s*\b(?:(?:di|per)\s+)?(?P<p>stasera|stanotte|domattina|stamattina|stamani|"
                    r"questa\s+sera|questa\s+notte|domani\s+mattina)\b\s*", re.I)
_PARTI = {"stamani": "stamattina", "questa sera": "stasera", "questa notte": "stanotte",
          "domani mattina": "domattina"}
_COMPLETO = re.compile(r"\s*\b(?:completo|completa|dettagliato|con\s+tutti\s+i\s+dettagli)\b\s*", re.I)
_DETTAGLI_METEO = re.compile(r"^(?:dimmi\s+)?(?:i\s+)?dettagli\s+(?:del\s+)?meteo", re.I)
_CITTA_FINALE = r"(?:\s+(?:a|ad|in|di|per)\s+(?P<citta>[^\d,;:]{2,40}?))?[\s.!?]*$"
_DETTAGLIO = re.compile(
    r"^(?:(?:dimmi|com['’]è|qual\s+è|quanto\s+è)\s+)?(?:(?:il|la|lo|l['’])\s*)?"
    r"(?P<d>temperatura\s+(?:adesso|ora|attuale|esterna)|vento|umidit[àa]|"
    r"alba\s+e\s+tramonto|tramonto\s+e\s+alba|alba|tramonto)" + _CITTA_FINALE, re.I)
_PIOGGIA = re.compile(
    r"^(?:pioverà|piovera|piove|ci\s+sarà\s+(?:la\s+)?pioggia)(?:\s+(?P<q>domani|oggi|stasera))?"
    + _CITTA_FINALE, re.I)
_OMBRELLO = re.compile(
    r"^(?:(?:mi\s+)?serve\s+(?:l['’]\s*ombrello|la\s+giacca|il\s+giubbotto)|"
    r"devo\s+(?:prendere|portare)\s+l['’]\s*ombrello|(?:prendo|porto)\s+l['’]\s*ombrello)"
    + _CITTA_FINALE, re.I)
_FREDDO = re.compile(
    r"^(?:fa|c['’]è)\s+(?P<t>freddo|caldo)(?:\s+(?:oggi|adesso|ora|fuori))*" + _CITTA_FINALE, re.I)
_RIEPILOGO = re.compile(
    r"^(?:com['’]è\s+la\s+giornata(?:\s+(?:oggi|di\s+oggi))?|"
    r"come\s+sarà\s+la\s+giornata(?:\s+(?:oggi|di\s+oggi))?)[\s.!?,]*$", re.I)
_BUONGIORNO = re.compile(r"^(?:(?:ehi|hey|ok)\s+)?(?:lumi[\s,]+buongiorno|buongiorno[\s,]+lumi)[\s.!?]*$", re.I)
_FARA = re.compile(r"\bfarà\b|\bfara\b", re.I)
_MESI = ("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
         "settembre", "ottobre", "novembre", "dicembre")
_MESE_RX = "|".join(_MESI)
_NUMERI = {"un": 1, "uno": 1, "una": 1, "due": 2, "tre": 3, "quattro": 4, "cinque": 5, "sei": 6,
           "sette": 7, "otto": 8, "nove": 9, "dieci": 10}
# 059: «dopodomani», «tra 3 giorni», «tra una settimana», «il 25», «25 dicembre»
_DOPODOMANI = re.compile(r"\s*\bdopodomani\b\s*", re.I)
_TRA = re.compile(r"\s*\b(?:tra|fra)\s+(?:(?P<n>\d{1,3}|un|uno|due|tre|quattro|cinque|sei|sette|otto|"
                  r"nove|dieci)\s+giorn[oi]|(?P<s>una|1|due|2)\s+settiman[ae])\b\s*", re.I)
_DATA_MESE = re.compile(r"\s*\b(?:(?:per|di|del|nel)\s+)?(?:(?:il|l['’])\s*)?(?P<n>\d{1,2})(?:º|°)?\s+"
                        r"(?:di\s+)?(?P<m>" + _MESE_RX + r")\b\s*", re.I)
_DATA_IL = re.compile(r"\s*\b(?:(?:per|di|del|nel)\s+)?(?:il|l['’])\s*(?P<n>\d{1,2})(?:º|°)?\b\s*", re.I)
_ESCLUSE = re.compile(r"\bonline\b|\bclima\w*|\bprimavera\b|"
                      r"\bestate\b|\bautunno\b|\binverno\b", re.I)


def parse_command(text: str):
    """("meteo", città o None) se è una richiesta di meteo attuale; altrimenti None."""
    if not isinstance(text, str) or len(text) > 120:
        return None
    value = _CODA.sub("", " ".join(_WAKE.sub("", text).strip().split()))
    if _ESCLUSE.search(value):
        return None
    raw = " ".join(_WAKE.sub("", text).strip().split())
    if _BUONGIORNO.match(" ".join(text.split())) or _RIEPILOGO.match(raw):
        return "riepilogo", None
    for rx, kinds in ((_DETTAGLIO, None), (_PIOGGIA, None), (_OMBRELLO, None), (_FREDDO, None)):
        found = rx.match(raw)
        if found:
            city = (found.group("citta") or "").strip(" .!?") or None
            if rx is _DETTAGLIO:
                return "dettaglio:" + " ".join(found.group("d").casefold().split()), city
            if rx is _PIOGGIA:
                return ("domanda:pioggia_domani" if (found.group("q") or "").casefold() == "domani"
                        else "domanda:pioggia_oggi"), city
            if rx is _OMBRELLO:
                return "domanda:ombrello", city
            return "domanda:" + found.group("t").casefold(), city
    if _DETTAGLI_METEO.match(value):    # «dettagli meteo», «dettagli del meteo a Roma»
        value = "meteo" + _DETTAGLI_METEO.sub("", value)
        value = " ".join(value.split())
        extra = "completo"
    elif _COMPLETO.search(value) and re.match(r"^(?:dimmi\s+)?(?:il\s+)?meteo\b", value, re.I):
        value = " ".join(_COMPLETO.sub(" ", value).split())
        extra = "completo"
    else:
        extra = None
    if extra:
        found = _PATTERN.match(value)
        if not found:
            return None
        return "completo:tutto", ((found.group("citta") or "").strip(" .!?") or None)
    kind = "meteo"
    parte = _PARTE.search(value)
    giorno = None if parte else _GIORNO.search(value)
    if re.match(r"^(?:dimmi\s+)?(?:il\s+|le\s+)?(?:meteo|previsioni(?:\s+del\s+tempo)?|"
                r"(?:che|quale)\s+tempo\s+far?[àa]?|com['’]è\s+il\s+tempo)\b", value, re.I):
        data = _data(value)
        if data is not None:
            kind, value = data
    if kind != "meteo":
        pass
    elif parte:                           # «meteo stasera», «meteo domattina»
        name = " ".join(parte.group("p").casefold().split())
        kind = "parte:" + _PARTI.get(name, name)
        value = " ".join(_FARA.sub("fa", _PARTE.sub(" ", value)).split())
    elif giorno:                        # «che tempo farà sabato», «meteo weekend»
        name = " ".join(giorno.group("g").casefold().split())
        kind = "giorno:" + name
        value = " ".join(_FARA.sub("fa", _GIORNO.sub(" ", value)).split())
    elif _SETTIMANA.search(value):        # 058: «meteo settimana», «che tempo farà questa settimana»
        kind = "settimana"
        value = " ".join(_FARA.sub("fa", _SETTIMANA.sub(" ", value)).split())
    elif _DOMANI.search(value):           # 057: «meteo domani», «che tempo farà domani a Roma»
        kind = "domani"
        value = " ".join(_FARA.sub("fa", _DOMANI.sub(" ", value)).split())
    match = _PATTERN.match(value)
    if not match:
        return None
    city = (match.group("citta") or "").strip(" .!?")
    return kind, (city or None)


def _data(value: str):
    """059: (tipo, testo senza la data) per dopodomani / tra N giorni / il 25; None se non c'è."""
    trovato = _DOPODOMANI.search(value)
    if trovato:
        return "data:+2", " ".join(_FARA.sub("fa", _DOPODOMANI.sub(" ", value)).split())
    trovato = _TRA.search(value)
    if trovato:
        if trovato.group("n"):
            n = trovato.group("n").casefold()
            giorni = int(n) if n.isdigit() else _NUMERI[n]
        else:
            s = trovato.group("s").casefold()
            giorni = 7 * (_NUMERI.get(s) or int(s))
        return "data:+%d" % giorni, " ".join(_FARA.sub("fa", _TRA.sub(" ", value)).split())
    for rx in (_DATA_MESE, _DATA_IL):
        trovato = rx.search(value)
        if trovato:
            n = int(trovato.group("n"))
            if not 1 <= n <= 31:
                return None
            mese = trovato.groupdict().get("m")
            spec = "data:#%d" % n + (("/%d" % (_MESI.index(mese.casefold()) + 1)) if mese else "")
            return spec, " ".join(_FARA.sub("fa", rx.sub(" ", value)).split())
    return None
