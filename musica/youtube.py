"""YouTube nel browser: pagina dei risultati, oppure il primo video con la
chiave facoltativa della YouTube Data API v3 (search.list, 100 punti/ricerca,
quota gratuita ~10.000 punti al giorno). L'audio NON viene preso da YouTube:
riproduzione sempre nel lettore di YouTube (regole del servizio)."""
from __future__ import annotations

import html
import json
import re
import urllib.parse
import urllib.request

_VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{6,20}$")


def results_url(query: str) -> str:
    return "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)


def first_video_id(query: str, api_key: str, opener=urllib.request.urlopen, timeout=8) -> str:
    return first_video_url(query, api_key, opener=opener, timeout=timeout).rsplit("=", 1)[1]


def first_video_url(query: str, api_key: str, opener=urllib.request.urlopen, timeout=8) -> str:
    """URL del primo video; solleva un'eccezione se la ricerca non riesce."""
    params = urllib.parse.urlencode({"part": "snippet", "type": "video", "maxResults": 1,
                                     "q": query, "key": api_key, "safeSearch": "none"})
    with opener("https://www.googleapis.com/youtube/v3/search?" + params, timeout=timeout) as response:
        data = json.loads(response.read(200_000).decode("utf-8"))
    items = data.get("items") or []
    video = (items[0].get("id") or {}).get("videoId") if items else None
    if not isinstance(video, str) or not _VIDEO_ID.fullmatch(video):
        raise ValueError("Nessun video trovato.")
    return "https://www.youtube.com/watch?v=" + video


def video_list(query: str, api_key: str, opener=urllib.request.urlopen, timeout=8,
               limit: int = 10) -> list[tuple[str, str]]:
    """[(id, titolo)] dei primi video: una sola ricerca (100 punti, come per uno solo),
    così finito un video ne parte un altro invece di chiudere il riquadro."""
    params = urllib.parse.urlencode({"part": "snippet", "type": "video", "maxResults": limit,
                                     "q": query, "key": api_key, "safeSearch": "none",
                                     "videoEmbeddable": "true"})
    with opener("https://www.googleapis.com/youtube/v3/search?" + params, timeout=timeout) as response:
        data = json.loads(response.read(400_000).decode("utf-8"))
    result, seen = [], set()
    for item in data.get("items") or []:
        video = (item.get("id") or {}).get("videoId")
        if not isinstance(video, str) or not _VIDEO_ID.fullmatch(video) or video in seen:
            continue
        seen.add(video)
        title = html.unescape(str((item.get("snippet") or {}).get("title") or ""))[:120]
        result.append((video, title or query))
    if not result:
        raise ValueError("Nessun video trovato.")
    return result


def url_for(query: str, api_key: str = "", opener=urllib.request.urlopen) -> tuple[str, str]:
    """(url, modo): «video» con chiave funzionante, altrimenti «risultati»."""
    if api_key:
        try:
            return first_video_url(query, api_key, opener=opener), "video"
        except Exception:
            pass
    return results_url(query), "risultati"


# Tasti multimediali di Windows: il browser li riceve anche in secondo piano.
MEDIA_KEYS = {"toggle": 0xB3, "pause": 0xB3, "resume": 0xB3, "next": 0xB0, "stop": 0xB2,
              "prev": 0xB1,
              "volume_up": 0xAF, "volume_down": 0xAE}


def send_media_key(action: str) -> bool:
    code = MEDIA_KEYS.get(action)
    if code is None:
        return False
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.keybd_event(code, 0, 0, 0)
        user32.keybd_event(code, 0, 2, 0)      # KEYEVENTF_KEYUP
        return True
    except (AttributeError, OSError):
        return False
