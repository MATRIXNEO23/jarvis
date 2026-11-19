"""Tutto ciò che parla con i servizi online (061, riordino passo 2).

- gpt_client.py, gpt_bridge.mjs, installa_gpt.ps1/.bat: il ponte con ChatGPT dal browser;
- servizi_online/: i servizi con chiave API e la catena di risposta;
- servizi_ricerca/: i servizi di ricerca sul web.
Gli altri moduli li raggiungono con `from online import servizi_online` o `__import__("online").servizi_online`;
per questo i due pacchetti si caricano qui.
"""
from . import servizi_online, servizi_ricerca  # noqa: F401
