# Analisi del codice per la 056 (17/11/2026)
Riferimento: docs/DECISIONI-056.md. Analisi in sola lettura, nessuna modifica.

## A. Offline prima
- Oggi la richiesta passa da `lumi_comandi.handle_text` e poi da `conversation_chain` (jarvis.py:2334), che prova prima `servizi_online.disponibili()` e solo dopo `local_after_gpt`. È l'ordine della 055: online prima.
- Modifica: comandi → `submit_gemma_voice(route="locale")` direttamente. L'online passa solo dalla conferma sì/no, riusando `pending`/`_YES` (lumi_comandi.py:99-121) e `gpt_consent_yes` (jarvis.py:2185).
- `richiesta_codice`: deve chiedere anche lei «Vado online?», al posto del messaggio che rimanda alle impostazioni.
- «approfondisci»: oggi va a Gemma (`servizi_ricerca.approfondisci_locale`, conversazione_lumi.py:346). Diventa: conferma, poi primo servizio online con l'ultima domanda, da conservare in jarvis.py.
- Pulsante «Approfondisci»: non esiste ancora. Va in chat_bolle.py, sotto la risposta, e chiama la stessa funzione.
- «cerca online» (`lumi_ricerca`, jarvis.py:4845): deve chiedere anche lei la conferma.
- Rischi: la regex di persona.py:54, i vecchi test Gemma, il timeout della risposta sì/no.

## B. Slide Basso consumo / Veloce
- Va al posto della scritta in animated_hud.py:282. Nuova impostazione, salvata con `save_settings`.
- «Veloce» riusa il ramo attuale della 055 di `conversation_chain`, senza doppioni.
- Rischio: il layout dell'HUD su schermi piccoli.

## C. Meteo
- Oggi non esiste un comando meteo (né in lumi_comandi.py, né in jarvis_commands.json, né in local_engine).
- Nuova azione `meteo` in `handle_text`, prima della riga 125: geocoding e previsioni da Open-Meteo con urllib, senza chiave.
- Conflitto: «cerca online meteo …» oggi corrisponde prima a `servizi_ricerca._COMANDO`. Il meteo deve escludere le frasi con «online» e le domande sul clima («clima … in primavera»).

## D. Barra in alto
- «GPT ON» si costruisce in animated_hud.py:674, nella lista `controls` accanto a «MODELLO ON/OFF» (`model_gate`). Va tolta la voce GPT, che resta solo in `menu_modelli.MenuModelli` (ONLINE).
- Tendina MODELLO: riusa `MenuModelli` come fa menu_ricerca. L'elenco viene da `scelta_modello.elenca_modelli`, il salvataggio da `salva_scelta` (stesso `on_use` di miei_modelli, jarvis.py:4960).
- On/off unico: è il pulsante «MODELLO» che esiste già.
- Rischi: scaricare il modello precedente al cambio (in memoria ne resta uno solo) e collegamenti a `toggle_gpt` rimasti senza destinazione.

## E. Mistral spuntato (causa probabile)
- Il pannello Impostazioni (servizi_online/__init__.py:470-484) tiene una copia di `settings` e delle sue spunte. Il suo `save()` riscrive `attivi` con quelle spunte vecchie e così annulla le modifiche fatte dalla tendina ONLINE.
- Stesso difetto in servizi_ricerca/__init__.py:251. In più `MenuModelli._save` nasconde gli `OSError` senza segnalarli.
- Correzione: `save()` ricarica con `carica_impostazioni()` prima di scrivere.

## Piano di prove (per Codex)
| frase o strumento | atteso |
|---|---|
| «chi ha scritto i Promessi sposi?» con tutto spento | risponde l'offline, `route=locale` |
| «approfondisci» dopo una risposta | «Vado online?», poi con «sì» il primo servizio online |
| «scrivimi uno script …» | chiede conferma prima di andare online |
| slide su Veloce, poi riavvio | `lumi_impostazioni` mostra ancora Veloce; una domanda va online senza conferma |
| «che tempo fa a Roma» | comando meteo nel log, senza modello e senza conferma |
| «cerca online meteo Roma» | conferma, poi ricerca |
| «com'è il clima a Tokyo in primavera» | ricerca online dopo la conferma |
| barra in alto | niente «GPT ON» |
| scelta di un modello dalla tendina MODELLO | `lumi_stato` mostra il nuovo modello, uno solo in memoria |
| Mistral spento dalla tendina, poi Impostazioni aperte e chiuse | `lumi_online` mostra Mistral ancora spento |

## Prove dal vivo da eseguire (aggiunte per C2 e C3, 17/11)
| strumento o frase | atteso |
|---|---|
| `lumi_addon` acceso «meteo», poi `lumi_stato` | `meteo.attivo` true; con città scelta compaiono città, temperatura e icona entro pochi secondi |
| Impostazioni > Add-on > Meteo, città «Roma», Salva | messaggio «Città salvata»; nell'HUD, sotto il globo e sopra DISCO C/RETE, icona + «Roma 18°», nessun riquadro |
| «che tempo fa a Tokyo» | risposta a voce e in chat «A Tokyo ci sono …», nel log nessun modello e nessuna conferma |
| `lumi_addon` spento «meteo» | l'icona sparisce, «che tempo fa a Roma» non risponde dal comando (va al modello), nessuna connessione a Open-Meteo |
| «com'è il clima a Tokyo in primavera» e «cerca online meteo Roma» | non risponde il comando meteo; la ricerca chiede «Vado online?» |
| dopo «cerca online …» dire «apri il 2» (anche «il secondo») | il risultato 2 si apre nel browser predefinito, senza conferma; «apri il 9» con 5 risultati: «Non c'è un risultato 9» |
| `lumi_stato` | mostra `modalita` e `meteo` |
Limite: due aggiornamenti dell'icona devono distare almeno 30 minuti (verificare dal log di rete o dal codice, non con attese reali).

## Audit regressioni 056b (17/11) - elenco per la scelta dell'utente, NESSUN ripristino applicato
Confronti: (A) base 3eb7e6e = genitore del primo multimodello F5.2 (f035575, 09/11); (B) riferimento indicato dall'utente MATRIXNEO23/jarvis-copia-qwen (main = stub + cartella Download; l'ultima build è `Lumi-050-PROVA.zip`, 16/11, estratta in sola lettura). Rispetto alla 050 identici a HEAD: `chat_templates.py`, `persona.py`, `memory_preferences.py`, `native_settings.py` (template, stile e memoria non sono cambiati dopo la 050). Funzioni (def) e etichette dei pulsanti: sparita solo `open_memory_preferences` (voluto); le altre etichette sono rinomine Jarvis->Lumi.
Unica eccezione già approvata e FATTA: ora e sveglia in basso (`animated_hud._layout_bottom`, test `test_056b_hud_layout.py`).

| # | Differenza | Prima (A/050) | Ora | Proposta (da scegliere) |
|---|---|---|---|---|
| 1 | `context_size` predefinito | 2048 | 1024 | tenere 1024 (Pavilion) o tornare a 2048; ora modificabile nella pagina Modelli/profilo |
| 2 | Tetto del prompt col contatore esatto | contesto - uscita - 128 (circa 1792) | min(600, ...) (056b approvata 18:55) | tenere 600 o alzare (es. 1200) |
| 3 | «Chat continua» | spenta | accesa di serie (056b) | tenere o spegnere di serie |
| 4 | Catalogo azioni | tetto 8192 | dentro il tetto, catalogo ridotto se non entra | tenere |
| 5 | Cronologia e ricordi | 250 token | 200 token | tenere o tornare a 250 |
| 6 | Stop del modello | solo `<end_of_turn>` (Gemma) | per famiglia (Gemma, Qwen) | tenere (serve a Qwen) |
| 7 | `/nothink` | non gestito | tolto da domanda, risposta e flusso | tenere |
| 8 | Test di generazione | ricarica il motore | non ricarica | tenere |
| 9 | Barra in alto | «INTERFACCIA NEURALE», MIC OFF / GPT OFF / MODELLO ON / MEMORIA OFF, ingranaggio 21 | slide modalità, tasti con on/off, ingranaggio 17 con _ □ X sopra | tenere (mockup approvato) |
| 10 | Modelli | un solo modello, finestra «Configura Gemma» | pagina unica con caselle, elenco, profili, impostazioni e memoria nel profilo | tenere (richiesta 19:04) |
| 11 | Stile/persona, fast forwarding | assenti nella base A | presenti (026), identici alla 050 | tenere |
Non confrontabile senza il PC: tempi di risposta e qualità reale (solo prove dal vivo).

Prove dal vivo per Codex: (1) Impostazioni > Modelli: una sola pagina; Salva poi cambiare profilo: valori e memoria cambiano. (2) Chat lunga poi «ciao»: risposta breve, non la precedente; `lumi_prompt` mostra «[Conversazione precedente: ...]» e nessun ricordo. (3) HUD in basso: ora, sveglia (imposta tra 2 minuti: compare «Ferma»), meteo, DISCO C, RETE visibili. (4) Online: «ciao» = log «ONLINE > contesto minimo ... ~N token»; «approfondisci» fino a 6 scambi; `lumi_online` mostra `ultimo_contesto_online`. (5) Aiuto (F1): sezioni Meteo e Modelli offline.
