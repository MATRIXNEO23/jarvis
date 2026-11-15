# Handoff Lumi — stato corrente (aggiornato 15/11/2026)

Documento d'ingresso per chi riprende il lavoro (Claude, Codex o altri). Leggere prima
`AGENTS.md` (regole dell'utente, prevalgono su tutto), poi questo file, poi le sezioni recenti
di `docs/ARCH-01-F5-CHECKPOINT.md` (decisioni datate) e `docs/PIANO-DIVISIONE-JARVIS.md`.
Aggiornare questo file a ogni consegna o decisione importante.

## Dove sta il codice
- Repository `MATRIXNEO23/jarvis`, ramo di lavoro **`feature/jarvis-kobold-f5-profiles-20261109`**.
  `main` contiene solo `Download/` (pacchetti pubblicati) e sorgenti storici: non modificarlo a mano.
  (Esiste un ramo `f5n5` creato per errore, identico; l'utente può cancellarlo.)
- Applicazione: Lumi (ex Jarvis), assistente vocale Windows in Python/Tk.
  Target: HP Pavilion i3-2100, 10 GB RAM, Windows 10 — tutto deve restare leggero.
- Ultimo pacchetto pubblicato: **Lumi-046-PROVA.zip** (in `main/Download`, voce in cima a `Download/README.md`).

## Come si lavora (vincoli dell'utente)
- Un passo alla volta: spiegare il problema e la correzione, **chiedere conferma prima di ogni modifica**;
  quando ci sono più strade proporre opzioni con una raccomandazione. Non inventare comandi o comportamenti.
- Non rompere funzioni e comandi esistenti. Test verdi non bastano: controllare la coerenza (comandi in
  conflitto, musica, add-on, Telegram, «cervello locale», modalità vocali).
- Test solo su Windows (CI). In locale (Linux) solo controlli di modifica, che non valgono come prova.
- Build/pubblicazione solo su richiesta esplicita. Zero costi, solo API ufficiali, segreti cifrati DPAPI
  nel profilo, mai nel repo. Risposte brevi e semplici all'utente (italiano).

## CI, build e pubblicazione
- Ogni push lancia: «unit and GPT protocol» (tutti i test su Windows), diagnostica servizi, Telegram,
  tokenizer, e **F5N.2** (pacchetto + prova reale UIA/OCR, ~20 min). Per commit di sola documentazione
  annullare F5N.2 (`gh run cancel`).
- Numero build: `.github/workflows/f5n-koboldcpp-native-dll-windows.yml` (`--number N`, artifact
  `lumi-0NN-prova-candidate`, file `Lumi-0NN-PROVA.zip`). Prossima: 047.
- Pubblicare: dopo F5N.2 verde scrivere `tools/publish_request.json` (run_id, artifact, file, bytes, sha256
  presi dal log della build, source_commit, title, description) e fare push: il workflow di pubblicazione copia
  lo zip in `main/Download` e aggiorna il README. Verificare con `git ls-tree -l origin/main Download/<file>`.

## Mappa dei moduli recenti
- `jarvis.py`: avvio e collegamento; `main()` contiene ancora ~4.400 righe (vedi piano di divisione).
- `lumi_contesto.py` (`Contesto`, `Vivo`): riferimenti condivisi; `tools/sposta_funzioni.py` sposta funzioni
  annidate di `main()` in moduli con codice invariato (`d.nome` = valore attuale).
- `lumi_parti/` (voce, documenti_progetti, modello_memoria, interfaccia), `telegram_addon/lumi_ui.py`,
  `local_model/conversazione_lumi.py`: funzioni spostate da `jarvis.py`.
- Test che estraggono funzioni da `main()`: estrattore comune in `tests/test_activity_status.py`
  (`find_main_function`, `moved_functions`, `GlobalCallbacks` che riporta `d.x` a `x`). Se si sposta una
  funzione letta dai test, usare `--anche-test` e adattare gli estrattori propri dei test.
- Modello locale: add-on incluso «Modello locale» (`local_model/ModelloLocale.jaddon`, acceso di serie,
  `model_gate.addon_on`). Motore in processo separato opzionale (`local_model/motore_processo.py`, casella
  in Impostazioni → GPT e memoria, spenta di serie; «riavvia il modello»).
- Controllo PC: `controllo_pc/` + base comune `controllo_comune/` (finestre, UIA, OCR via `LumiControl.exe` C#).
- Voce: `voice_control.py` (Vosk), `risposte.py` (sì/no e numeri senza «Lumi»), `la_mia_voce.py`
  (addestratore e pausa tra le parole), `audio_player.py` (voce con controllo di blocco).
- Chat: `chat_ruoli.py` (chi ha scritto ogni messaggio: utente, jarvis, comando, azione, errore, sistema);
  HUD (`animated_hud.py`) con «CHAT» + pulsante «DIAGNOSTICA ▸» (finestra filtrabile).
  `chat_elenco.py` (archivio per progetto in `jarvis_chat_sessions.sqlite3`), `chat_bolle.py` (bolle e pulsanti).
- Build: una sola alla fine di tutti i passi (prossima 047), su richiesta già data il 15/11.

## Lezioni da non ripetere
- `locals()` dentro una comprensione ha un ambito suo (Lumi non partiva): salvarlo prima.
- Passaggio tra processi: JSON solo ASCII (surrogati tipo `\udc8d` bloccavano il motore separato).
- Prima di dare la colpa a un programma esterno confrontare con l'ultima build che funzionava (Netflix:
  era la pausa tra le parole senza tetto introdotta nella 041).
- Molti test leggono funzioni da `jarvis.py` anche senza scrivere «jarvis.py»: spostare con lo strumento.
- Il ruolo dei messaggi non va indovinato dal testo in giro per il codice: usare `chat_ruoli`.

## In corso e prossimi passi (ordine concordato il 15/11)
1. **Fatto (CI verde)**: ruoli dei messaggi (`chat_ruoli`, ruolo «comando» con intestazione della fonte).
2. **Fatto (CI verde, non ancora in build)**: chat unica locale+GPT con elenco chat per progetto (`chat_elenco.py`,
   ☰ / + / Rinomina / Elimina) e bolle con copia/leggi/rigenera, ultimi 100 disegnati (`chat_bolle.py`).
3. **Fatto (CI verde)**: riga di stato a 5 colori e stop immediato, `stato_lumi.py` («Lumi, fermati» + pulsante; «stop/pausa/play» solo audio-video; «annulla» invariato).
4. **Fatto (vedi CI)**: «Chat continua» e sezione «Contesto» del modello locale (`contesto_lumi.py`); parte online rimandata al passo 8.
5. **Fatto (vedi CI)**: allegati (`allegati.py`: 📎, trascinamento, Ctrl+V; pezzi utili senza modello; solo modello locale finché non c'è il passo 8).
6. **Fatto (vedi CI)**: pulizia dati su disco (`pulizia_dati.py`, Cestino, doppia conferma per i file importanti).
7. **Fatto (vedi CI)**: scheda di sé (`scheda_lumi.py`) e riquadro comandi per modalità con tutorial brevi (`aiuto_comandi.py`).
8. **Fatto in parte (vedi CI)**: servizi online con caselle, chiavi DPAPI, ordine e ripiego locale (`servizi_online.py`); orchestratore con strumenti ancora da progettare.
9. **Fatto (vedi CI)**: Diagnostica per Claude (`diagnostica_claude/`, MCP locale), import di una chat da ChatGPT/Claude (`chat_import.py`), GitHub sola lettura (`github_lettura.py`).
Dettagli e motivazioni: sezioni datate in fondo a `docs/ARCH-01-F5-CHECKPOINT.md`.
10. Bug voce online Microsoft: corretto (attesa iniziale 10 s, niente alternanza nella stessa risposta), da provare sul Pavilion.
11. Tutorial con correzione dei comandi, lettere perse (S), parole incerte in dettatura, classificatore opzionale, frasi variate (decisioni 15/11 10:50 nel checkpoint).
