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
INTERVALLO = 30 * 60          # secondi: massimo un aggiornamento ogni 30 minuti


class ErroreMeteo(RuntimeError):
    """Messaggio già pronto da dire all'utente."""


def _get(url: str, timeout: float = 8.0) -> dict:
    request = Request(url, headers={"User-Agent": "Lumi-meteo"})
    with urlopen(request, timeout=timeout) as response:          # nosec: URL fissi Open-Meteo
        return json.loads(response.read(200_000).decode("utf-8"))


def categoria(code) -> str:
    """Codice WMO (weathercode) → sole | nuvola | pioggia | neve | temporale."""
    try:
        code = int(code)
    except (TypeError, ValueError):
        return "nuvola"
    if code in (0, 1):
        return "sole"
    if code >= 95:
        return "temporale"
    if code in (71, 73, 75, 77, 85, 86):
        return "neve"
    if 51 <= code <= 67 or 80 <= code <= 82:
        return "pioggia"
    return "nuvola"


_TESTO = {"sole": "sereno", "nuvola": "nuvoloso", "pioggia": "pioggia", "neve": "neve",
          "temporale": "temporale"}


def frase(citta: str, temp: float, code) -> str:
    return "A %s ci sono %d gradi, %s." % (citta, round(temp), _TESTO[categoria(code)])


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
        return {"temp": float(now["temperature"]), "code": int(now["weathercode"])}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ErroreMeteo("Non riesco a leggere le previsioni adesso.") from exc


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
        return frase(city["nome"], now["temp"], now["code"])

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
        self.ultimo = {"citta": city["nome"], "temp": now["temp"], "code": now["code"]}
        self._quando = self._ora()
        return self.ultimo
