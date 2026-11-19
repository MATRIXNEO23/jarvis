"""Descrizione di un servizio online: ogni servizio ha il suo file in servizi_online/servizi/.

Per cambiare indirizzo, modello di serie, limiti gratuiti o passi per la chiave di un
servizio si modifica solo il suo file (richiesta utente 15/11 sera).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Servizio:
    id: str
    nome: str
    base_url: str
    modello: str
    gratis: bool
    chiavi: str                       # pagina ufficiale dove si crea la chiave
    ordine: int = 99                  # posizione iniziale nell'elenco
    limite: str = ""                  # cosa offre gratis, in parole semplici
    richieste_giorno: int | None = None   # limite noto di richieste al giorno (None = sconosciuto)
    token_mese: int | None = None     # limite noto di token al mese
    passi: tuple = field(default_factory=tuple)   # come creare la chiave, per l'aiuto
    orchestratore: bool = True        # sa usare gli strumenti (lavori a più passi)
    uso: str = ""                     # a cosa è più portato, in parole semplici (16/11)
    tipo: str = "chiave"              # «chiave» (API) o «account» (ChatGPT col tuo piano)
    # Modelli migliori in ordine (16/11): Lumi usa il primo che il servizio offre davvero e,
    # se uno viene ritirato, passa al successivo. solo_free: solo modelli «:free» (OpenRouter).
    preferiti: tuple = field(default_factory=tuple)
    solo_free: bool = False
    # 058: come si chiede la «potenza» (ragionamento), dalla documentazione ufficiale. «effort» =
    # campo reasoning_effort (Gemini sull'endpoint OpenAI, Groq gpt-oss, OpenAI o-series/gpt-5);
    # «openrouter» = campo reasoning {effort}. Vuoto = non supportata: il parametro non si manda.
    ragionamento: str = ""
    ragionamento_modelli: tuple = field(default_factory=tuple)   # prefissi dei modelli che lo accettano (vuoto = tutti)
