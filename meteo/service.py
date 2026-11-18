"""Open-Meteo con urllib (geocoding + previsione corrente), senza chiave e senza dipendenze.

Nessun polling: `aggiorna()` rispetta l'intervallo minimo di 30 minuti e non fa niente se
l'add-on è disattivato o manca la città predefinita.
"""
from __future__ import annotations

import json
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

GEOCODING = "https://geocoding-api.open-meteo.com/v1/search?name={nome}&count=1&language=it&format=json"
PREVISIONE = ("https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
              "&current_weather=true&timezone=auto")
PREVISIONE_DOMANI = ("https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                     "&daily=weathercode,temperature_2m_max,temperature_2m_min"
                     "&forecast_days=2&timezone=auto")
PREVISIONE_SETTIMANA = ("https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                        "&daily=weathercode,temperature_2m_max,temperature_2m_min"
                        "&forecast_days=7&timezone=auto")
PREVISIONE_COMPLETA = ("https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                       "&current_weather=true"
                       "&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,"
                       "weathercode,windspeed_10m"
                       "&daily=weathercode,temperature_2m_max,temperature_2m_min,"
                       "precipitation_probability_max,sunrise,sunset"
                       "&forecast_days=7&timezone=auto")
GIORNI = ("lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica")
INTERVALLO = 30 * 60          # secondi: massimo un aggiornamento ogni 30 minuti


class ErroreMeteo(RuntimeError):
    """Messaggio già pronto da dire all'utente."""


def _get(url: str, timeout: float = 8.0) -> dict:
    request = Request(url, headers={"User-Agent": "Lumi-meteo"})
    with urlopen(request, timeout=timeout) as response:          # nosec: URL fissi Open-Meteo
        return json.loads(response.read(200_000).decode("utf-8"))


def categoria(code, giorno: bool = True) -> str:
    """Codice WMO (weathercode) → sole | sole_nuvola | nuvola | pioggia | neve | temporale |
    nebbia; di notte (giorno=False) il cielo sereno o poco nuvoloso diventa «luna»."""
    try:
        code = int(code)
    except (TypeError, ValueError):
        return "nuvola"
    if code in (0, 1, 2):
        if not giorno:
            return "luna"
        return "sole" if code < 2 else "sole_nuvola"
    if code in (45, 48):
        return "nebbia"
    if code >= 95:
        return "temporale"
    if code in (71, 73, 75, 77, 85, 86):
        return "neve"
    if 51 <= code <= 67 or 80 <= code <= 82:
        return "pioggia"
    return "nuvola"


_TESTO = {"sole": "sereno", "luna": "sereno", "sole_nuvola": "poco nuvoloso", "nebbia": "nebbia",
          "nuvola": "nuvoloso", "pioggia": "pioggia", "neve": "neve",
          "temporale": "temporale"}


def frase(citta: str, temp: float, code, giorno: bool = True) -> str:
    return "A %s ci sono %d gradi, %s." % (citta, round(temp), _TESTO[categoria(code, giorno)])


def cerca_citta(nome: str, get=_get) -> dict:
    try:
        data = get(GEOCODING.format(nome=quote(nome.strip()[:60])))
    except (OSError, ValueError) as exc:
        raise ErroreMeteo("Non riesco a contattare il servizio meteo.") from exc
    found = (data.get("results") or [None])[0] if isinstance(data, dict) else None
    if not isinstance(found, dict) or "latitude" not in found or "longitude" not in found:
        raise ErroreMeteo("Non trovo la città «%s»." % nome.strip()[:40])
    return {"nome": str(found.get("name") or nome).strip()[:60],
            "lat": float(found["latitude"]), "lon": float(found["longitude"])}


def attuale(lat: float, lon: float, get=_get) -> dict:
    try:
        data = get(PREVISIONE.format(lat=lat, lon=lon))
        now = data["current_weather"]
        return {"temp": float(now["temperature"]), "code": int(now["weathercode"]),
                "giorno": int(now.get("is_day", 1)) != 0}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ErroreMeteo("Non riesco a leggere le previsioni adesso.") from exc


def domani(lat: float, lon: float, get=_get) -> dict:
    """Previsione di domani (Open-Meteo daily): {"max", "min", "code"}."""
    try:
        daily = get(PREVISIONE_DOMANI.format(lat=lat, lon=lon))["daily"]
        return {"max": float(daily["temperature_2m_max"][1]), "min": float(daily["temperature_2m_min"][1]),
                "code": int(daily["weathercode"][1])}
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        raise ErroreMeteo("Non riesco a leggere le previsioni di domani.") from exc


def frase_domani(citta: str, massima: float, minima: float, code) -> str:
    return "Domani a %s: %s, minima %d e massima %d gradi." % (
        citta, _TESTO[categoria(code, True)], round(minima), round(massima))


def settimana(lat: float, lon: float, get=_get) -> list:
    """058: i 7 giorni (Open-Meteo daily): [{"data", "max", "min", "code"}]."""
    try:
        daily = get(PREVISIONE_SETTIMANA.format(lat=lat, lon=lon))["daily"]
        giorni = [{"data": str(d), "max": float(a), "min": float(b), "code": int(c)}
                  for d, a, b, c in zip(daily["time"], daily["temperature_2m_max"],
                                        daily["temperature_2m_min"], daily["weathercode"])]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ErroreMeteo("Non riesco a leggere le previsioni della settimana.") from exc
    if not giorni:
        raise ErroreMeteo("Non riesco a leggere le previsioni della settimana.")
    return giorni


def nome_giorno(data: str) -> str:
    """«2026-11-19» -> «giovedì 19»; testo grezzo se la data non è leggibile."""
    from datetime import date
    try:
        d = date.fromisoformat(data[:10])
    except ValueError:
        return data
    return "%s %d" % (GIORNI[d.weekday()], d.day)


def frase_settimana(citta: str, giorni: list) -> str:
    """Riassunto breve a voce: temperature, cielo più frequente, giorni di pioggia o neve."""
    categorie = [categoria(g["code"], True) for g in giorni]
    prevalente = max(set(categorie), key=categorie.count)
    brutti = [nome_giorno(g["data"]).split()[0] for g, c in zip(giorni, categorie)
              if c in ("pioggia", "neve", "temporale")]
    testo = "Settimana a %s: da %d a %d gradi, per lo più %s" % (
        citta, round(min(g["min"] for g in giorni)), round(max(g["max"] for g in giorni)),
        _TESTO[prevalente])
    if brutti:
        testo += "; pioggia o maltempo " + ", ".join(brutti[:4])
    return testo + ". I sette giorni sono nella finestra dei risultati."


def elenco_settimana(citta: str, giorni: list) -> dict:
    """Voci per la finestra dei risultati (Tipo, Nome, Percorso): un giorno per riga."""
    return {"token": "meteo-" + str(time.monotonic()),
            "items": [("Giorno", nome_giorno(g["data"]),
                       "%s, minima %d, massima %d" % (_TESTO[categoria(g["code"], True)],
                                                       round(g["min"]), round(g["max"])))
                      for g in giorni],
            "summary": "Meteo dei prossimi 7 giorni a %s." % citta}


class ServizioMeteo:
    def __init__(self, abilitato, *, citta=lambda: None, get=_get, orologio=time.monotonic):
        self._abilitato, self._citta, self._get, self._ora = abilitato, citta, get, orologio
        self.ultimo = None            # {"citta", "temp", "code"} dell'ultimo aggiornamento
        self._quando = None

    def is_enabled(self) -> bool:
        return bool(self._abilitato())

    def risposta(self, nome=None) -> str:
        """Frase a voce per `nome` (qualsiasi città) o per la città predefinita."""
        city = cerca_citta(nome, self._get) if nome else self._citta()
        if not city:
            raise ErroreMeteo("Scegli la città predefinita nella pagina dell'add-on Meteo.")
        now = attuale(city["lat"], city["lon"], self._get)
        return frase(city["nome"], now["temp"], now["code"], now.get("giorno", True))

    def risposta_domani(self, nome=None) -> str:
        city = cerca_citta(nome, self._get) if nome else self._citta()
        if not city:
            raise ErroreMeteo("Scegli la città predefinita nella pagina dell'add-on Meteo.")
        d = domani(city["lat"], city["lon"], self._get)
        return frase_domani(city["nome"], d["max"], d["min"], d["code"])

    def risposta_settimana(self, nome=None):
        """(frase a voce, elenco per la finestra dei risultati) dei prossimi 7 giorni."""
        city = cerca_citta(nome, self._get) if nome else self._citta()
        if not city:
            raise ErroreMeteo("Scegli la città predefinita nella pagina dell'add-on Meteo.")
        giorni = settimana(city["lat"], city["lon"], self._get)
        return frase_settimana(city["nome"], giorni), elenco_settimana(city["nome"], giorni)

    def risposta_estesa(self, kind: str, nome=None):
        """058: giorno preciso, parte del giorno, dettagli, domande, riepilogo, «completo».
        `kind` = «tipo:valore» (es. «giorno:sabato»). Ritorna (frase, elenco o None)."""
        from . import dettagli
        city = cerca_citta(nome, self._get) if nome else self._citta()
        if not city:
            raise ErroreMeteo("Scegli la città predefinita nella pagina dell'add-on Meteo.")
        try:
            dati = self._get(PREVISIONE_COMPLETA.format(lat=city["lat"], lon=city["lon"]))
        except (OSError, ValueError) as exc:
            raise ErroreMeteo("Non riesco a leggere le previsioni adesso.") from exc
        tipo, _, valore = kind.partition(":")
        try:
            if tipo == "giorno":
                return dettagli.giorno(city["nome"], dati, valore), None
            if tipo == "parte":
                return dettagli.parte_del_giorno(city["nome"], dati, valore), None
            if tipo == "dettaglio":
                return dettagli.dettaglio(city["nome"], dati, valore), None
            if tipo == "domanda":
                return dettagli.domanda(city["nome"], dati, valore), None
            if tipo == "completo":
                return dettagli.completo(city["nome"], dati)
            return dettagli.riepilogo(city["nome"], dati), None
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise ErroreMeteo("Il servizio meteo non ha questo dato adesso.") from exc

    def aggiorna(self, forza: bool = False):
        """Dati per l'HUD (città predefinita). None se spento, senza città o errore di rete;
        entro 30 minuti dall'ultimo aggiornamento riusa quello senza rete (salvo `forza`)."""
        city = self._citta()
        if not self.is_enabled() or not city:
            self.ultimo = self._quando = None
            return None
        if (not forza and self.ultimo is not None and self._quando is not None
                and self._ora() - self._quando < INTERVALLO):
            return self.ultimo
        try:
            now = attuale(city["lat"], city["lon"], self._get)
        except ErroreMeteo:
            return self.ultimo
        self.ultimo = {"citta": city["nome"], "temp": now["temp"], "code": now["code"],
                       "giorno": now.get("giorno", True)}
        self._quando = self._ora()
        return self.ultimo
