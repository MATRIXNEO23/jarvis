"""058: meteo esteso (Open-Meteo hourly + daily), senza IA e senza conferma.

Giorno preciso («che tempo farà sabato», «meteo weekend»), parte del giorno («meteo stasera»),
dettagli («vento», «umidità», «alba e tramonto»), domande («pioverà domani?», «serve
l'ombrello?», «fa freddo?») e riepilogo del mattino («buongiorno Lumi»). Funzioni pure sui dati
già scaricati: tutte restituiscono frasi brevi, adatte alla voce."""
from __future__ import annotations

from datetime import date

from .service import GIORNI, _TESTO, categoria

MESI = ("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre")
# nome → (giorno rispetto a oggi, ora d'inizio, ora di fine); indici orari = giorno * 24 + ora
FASCE = {"stasera": (0, 18, 24), "stanotte": (0, 22, 30), "domattina": (1, 6, 12),
         "stamattina": (0, 6, 12)}
ACCENTI = {"lunedi": "lunedì", "martedi": "martedì", "mercoledi": "mercoledì",
           "giovedi": "giovedì", "venerdi": "venerdì"}


def _ora_corrente(dati: dict) -> int:
    try:
        adesso = dati["current_weather"]["time"][:13]
        return [t[:13] for t in dati["hourly"]["time"]].index(adesso)
    except (KeyError, ValueError, TypeError):
        return 0


def _pioggia(prob) -> str:
    return "" if prob is None else ", probabilità di pioggia %d per cento" % round(prob)


def _giorno(dati: dict, i: int) -> dict:
    d = dati["daily"]
    prob = d.get("precipitation_probability_max") or []
    return {"data": d["time"][i], "max": float(d["temperature_2m_max"][i]),
            "min": float(d["temperature_2m_min"][i]), "code": int(d["weathercode"][i]),
            "prob": prob[i] if i < len(prob) else None}


def nome_con_data(data: str) -> str:
    d = date.fromisoformat(data[:10])
    return "%s %d %s" % (GIORNI[d.weekday()], d.day, MESI[d.month - 1])


def frase_giorno(citta: str, dati: dict, i: int) -> str:
    g = _giorno(dati, i)
    d = date.fromisoformat(g["data"][:10])
    return "%s %d a %s: %s, minima %d e massima %d gradi%s." % (
        GIORNI[d.weekday()].capitalize(), d.day, citta, _TESTO[categoria(g["code"], True)],
        round(g["min"]), round(g["max"]), _pioggia(g["prob"]))


def giorno(citta: str, dati: dict, nome: str) -> str:
    """«sabato», «giovedì» o «weekend» (sabato e domenica dei prossimi 7 giorni)."""
    nome = ACCENTI.get(nome.casefold(), nome.casefold())
    cercati = ("sabato", "domenica") if nome in ("weekend", "fine settimana") else (nome,)
    frasi = []
    for cerca in cercati:
        for i, t in enumerate(dati["daily"]["time"]):
            if GIORNI[date.fromisoformat(t[:10]).weekday()] == cerca:
                frasi.append(frase_giorno(citta, dati, i))
                break
    if not frasi:
        raise ValueError("giorno fuori dai 7 giorni")
    return " ".join(frasi)


def parte_del_giorno(citta: str, dati: dict, nome: str) -> str:
    giorno_rel, da, a = FASCE[nome]
    h = dati["hourly"]
    indici = [i for i in range(giorno_rel * 24 + da, giorno_rel * 24 + a) if i < len(h["time"])]
    if not indici:
        raise ValueError("fascia non disponibile")
    temps = [float(h["temperature_2m"][i]) for i in indici]
    probs = [h["precipitation_probability"][i] for i in indici
             if h.get("precipitation_probability") and h["precipitation_probability"][i] is not None]
    codes = [categoria(h["weathercode"][i], True)
             for i in indici]
    prevalente = max(set(codes), key=codes.count)
    return "%s a %s: %s, tra %d e %d gradi%s." % (
        nome.capitalize(), citta, _TESTO[prevalente], round(min(temps)), round(max(temps)),
        _pioggia(max(probs) if probs else None))


def dettaglio(citta: str, dati: dict, cosa: str) -> str:
    cosa = " ".join(cosa.casefold().split())
    now = dati["current_weather"]
    if cosa.startswith("temperatura"):
        return "Adesso a %s ci sono %d gradi." % (citta, round(float(now["temperature"])))
    if cosa == "vento":
        return "A %s il vento soffia a %d chilometri orari." % (citta, round(float(now["windspeed"])))
    if cosa.startswith("umidit"):
        valore = dati["hourly"]["relative_humidity_2m"][_ora_corrente(dati)]
        return "A %s l'umidità è del %d per cento." % (citta, round(float(valore)))
    alba, tramonto = dati["daily"]["sunrise"][0][-5:], dati["daily"]["sunset"][0][-5:]
    if cosa == "alba":
        return "A %s l'alba è alle %s." % (citta, alba)
    if cosa == "tramonto":
        return "A %s il tramonto è alle %s." % (citta, tramonto)
    return "A %s l'alba è alle %s e il tramonto alle %s." % (citta, alba, tramonto)


def domanda(citta: str, dati: dict, quale: str) -> str:
    now = dati["current_weather"]
    temp = round(float(now["temperature"]))
    if quale in ("pioggia_oggi", "pioggia_domani"):
        i = 1 if quale == "pioggia_domani" else 0
        g = _giorno(dati, i)
        quando = "domani" if i else "oggi"
        piove = categoria(g["code"], True) in ("pioggia", "temporale") or (g["prob"] or 0) >= 50
        if piove:
            return "Sì, %s a %s è probabile pioggia%s." % (quando, citta, _pioggia(g["prob"]))
        return "Probabilmente no: %s a %s è %s%s." % (
            quando, citta, _TESTO[categoria(g["code"], True)], _pioggia(g["prob"]))
    if quale == "ombrello":
        da = _ora_corrente(dati)
        probs = [p for p in (dati["hourly"].get("precipitation_probability") or [])[da:da + 12]
                 if p is not None]
        massima = max(probs) if probs else 0
        if massima >= 40:
            return "Sì, porta l'ombrello: nelle prossime ore la probabilità di pioggia arriva al %d per cento." % round(massima)
        return "No, l'ombrello non serve: probabilità di pioggia al massimo %d per cento." % round(massima)
    if quale == "caldo":
        return ("Sì, fa caldo: a %s ci sono %d gradi." if temp >= 26 else
                "No, non fa caldo: a %s ci sono %d gradi.") % (citta, temp)
    return ("Sì, fa freddo: a %s ci sono %d gradi." if temp <= 12 else
            "No, non fa freddo: a %s ci sono %d gradi.") % (citta, temp)


def riepilogo(citta: str, dati: dict) -> str:
    g = _giorno(dati, 0)
    parti = ["Buongiorno. Oggi è %s." % nome_con_data(g["data"]),
             "A %s: %s, minima %d e massima %d gradi%s." % (
                 citta, _TESTO[categoria(g["code"], True)], round(g["min"]), round(g["max"]),
                 _pioggia(g["prob"]))]
    if categoria(g["code"], True) in ("pioggia", "temporale") or (g["prob"] or 0) >= 40:
        parti.append("Porta l'ombrello.")
    elif g["max"] <= 12:
        parti.append("Metti una giacca pesante.")
    elif g["max"] - g["min"] >= 10:
        parti.append("Porta una giacca per le ore fresche.")
    return " ".join(parti)


def completo(citta: str, dati: dict):
    """«meteo completo»: tre frasi brevi a voce e, nella finestra dei risultati, gli stessi dati
    con alba e tramonto. Ritorna (frase, elenco)."""
    import time
    g = _giorno(dati, 0)
    now = dati["current_weather"]
    i = _ora_corrente(dati)
    umidita = round(float(dati["hourly"]["relative_humidity_2m"][i]))
    cielo = _TESTO[categoria(now.get("weathercode", g["code"]), now.get("is_day", 1) != 0)]
    temp, vento = round(float(now["temperature"])), round(float(now["windspeed"]))
    alba, tramonto = dati["daily"]["sunrise"][0][-5:], dati["daily"]["sunset"][0][-5:]
    prob = "" if g["prob"] is None else "%d per cento" % round(g["prob"])
    voce = ("Oggi è %s. A %s il cielo è %s e ci sono %d gradi, minima %d e massima %d. "
            "Vento a %d chilometri orari, umidità al %d per cento%s." % (
                nome_con_data(g["data"]), citta, cielo, temp, round(g["min"]), round(g["max"]),
                vento, umidita, (", probabilità di pioggia " + prob) if prob else ""))
    righe = [("Dato", "Giorno", nome_con_data(g["data"])), ("Dato", "Cielo", cielo),
             ("Dato", "Temperatura adesso", "%d gradi" % temp),
             ("Dato", "Minima e massima", "%d e %d gradi" % (round(g["min"]), round(g["max"]))),
             ("Dato", "Vento", "%d km/h" % vento), ("Dato", "Umidità", "%d%%" % umidita),
             ("Dato", "Probabilità di pioggia", prob or "non disponibile"),
             ("Dato", "Alba", alba), ("Dato", "Tramonto", tramonto)]
    return voce, {"token": "meteo-completo-" + str(time.monotonic()), "items": righe,
                  "summary": "Meteo completo di oggi a %s." % citta}
