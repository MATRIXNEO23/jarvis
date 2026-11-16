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
8. **Fatto (vedi CI)**: servizi online (`servizi_online.py`) e orchestratore a passi con cartelle sicure e permessi (`orchestratore.py`).
9. **Fatto (vedi CI)**: Diagnostica per Claude (`diagnostica_claude/`, MCP locale), import di una chat da ChatGPT/Claude (`chat_import.py`), GitHub sola lettura (`github_lettura.py`).
Dettagli e motivazioni: sezioni datate in fondo a `docs/ARCH-01-F5-CHECKPOINT.md`.
10. Bug voce online Microsoft: corretto (attesa iniziale 10 s, niente alternanza nella stessa risposta), da provare sul Pavilion.
11. **Fatto in parte (vedi CI)**: La mia voce con parlato dal vivo, conflitti, correzioni a mano e togliibili, lettere perse; classificatore opzionale; frasi variate. Manca: parole incerte evidenziate in dettatura.

## Build 047 (15/11) — pubblicata
Lumi-047-PROVA.zip in Download su main: run 43713943448, 27.764.632 byte, SHA-256 336e853c…3be9, sorgente 51c6b3b. Contiene i passi 2–11. Da provare sul Pavilion.
## Build 050 (16/11 notte) — pubblicata
Run 43785822094, 28252117 byte, sha256 4dd5d642…bcd0a, verificata su main/Download. Prossimo: prove complete dal vivo con la diagnostica 1.1 (Claude desktop da riavviare con la configurazione della 050).

## Build 049 (15/11 sera) — pubblicata
Run 43755471110, 28245326 byte, sha256 717854610d655082fbbff3f83a2c8ec9616f3867cb9f1e44cecdf0ae3373d333, sorgente bf7518b; file su main/Download verificato (hash uguale). Da provare sul Pavilion.
Contiene tutto dal 048: lista voci, documenti, menu laterale, menu modelli, quote, Telegram, finestra unica, motore separato, Python, impostazioni a cascata, add-on con interruttore, simboli 🤖/📡, Esporta JSON, richiamo cronologia, frasi chi sei/cosa puoi fare, ricordi, strumenti diagnostica. Dopo: prove dal vivo con l'utente via diagnostica MCP (Claude desktop va riavviato per vedere gli strumenti nuovi).

## Build 048 (15/11) — pubblicata
Lumi-048-PROVA.zip: run 43719492123, 27.773.085 byte, SHA-256 22304bad…f302. Aggiunge tutorial guidato, cambio parola dei comandi, orchestratore online con cartelle sicure.
Resta da fare: parole incerte evidenziate in dettatura (passo 11).

## Stato lista 15/11 sera (16/11)
Fatti con test: 1, 2, 3, 4, 5, 7, 8, 9, 10 e del 6: navigazione impostazioni, Tutorial, Info, righe add-on con icona colorata e interruttore (vedi checkpoint). Prossimo: proporre all'utente memoria locale/online separate, poi le finestre separate rimaste. Build 049 solo su richiesta.

## Nuova lista concordata a voce (15/11 sera) — da fare in ordine, menu proposti all'utente pezzo per pezzo
Regola: niente iniziative sull'organizzazione dei menu; ogni argomento al suo posto (Interfaccia, Voce, Memoria, Modelli, Add-on); tutto in verticale come il riquadro d'aiuto; menu che si aprono con un clic e si chiudono da soli cliccando altrove; unica finestra che resta in primo piano: l'aiuto comandi.
1. Menu laterale come ChatGPT: progetti come cartelle (+ nuovo progetto), dentro le chat; chat fuori dai progetti spostabili dentro; le chat dello stesso progetto si vedono tra loro. Vecchi progetti: cancellati del tutto (deciso dall'utente), si riparte col sistema nuovo.
2. Menu a tendina dei modelli in alto, ACCANTO al pulsante GPT (che resta): servizi con chiave, più spunte tra i gratuiti, modello attivo evidenziato, barra della quota per servizio (azzurra, arancione oltre metà, rossa quasi finita). GPT dal browser nella stessa fila per le risposte normali; per i lavori a più passi solo i servizi che sanno farli, nell'ordine scelto.
3. Quote: avviso all'80% della quota del giorno, conferma se una richiesta manda più di ~8.000 token (soglie modificabili); per ogni servizio scritto quanto offre gratis (verificato sui siti ufficiali) e quanto è stato usato. Di serie si manda il meno possibile.
4. Link cliccabile per creare la chiave accanto a ogni campo (servizi online e GitHub) + sezione nell'aiuto «Come creare le chiavi», passo per passo.
5. Telegram: indicatore in alto (azzurrino attivo e niente di nuovo; verde messaggi arrivati e bot ha risposto; arancione bloccato/non ha risposto; rosso disattivato; torna azzurrino quando apri la chat Telegram); chat «Telegram» nel menu laterale con i messaggi passati dal bot, a bolle, e possibilità di scrivere (solo ai contatti autorizzati); spunte veloci dei contatti già autorizzati senza ricaricare tutti i contatti. Le chat personali vere: NO (pesante e accesso a tutto l'account).
6. Impostazioni riorganizzate: menu a tendina in cascata dentro la finestra principale (niente finestre separate), sezioni Interfaccia / Voce / Memoria (locale e online separati) / Modelli / Add-on (elenco verticale con icona, clic → menu dell'add-on) / Tutorial (elenco dei tutorial) / Info (versione di Lumi, build, licenze delle parti incluse).
7. Una sola finestra: niente console nera (avvio senza finestra, uscita in Diagnostica e in un file).
8. Motore del modello SEMPRE in un processo separato; la casella sparisce.
9. Orchestratore: esecuzione di codice Python solo nelle cartelle sicure, dopo aver mostrato lo script e con il sì, tempo massimo configurabile (1 minuto di serie), comandi pericolosi bloccati. PowerShell più avanti.
10. Conferme: «sì»/«no» senza dire «Lumi» (verificare che sia sempre così).
Già pronti, non ancora in build: correzione elenco voci (timeout PowerShell), documenti negli allegati (PDF con pypdf, Office, LibreOffice, RTF, HTML, EPUB).

## Ripresa 16/11 03:40 (limite d'uso quasi finito) — pacchetto di correzioni in corso
Fatto nel codice (questo commit, CI Windows NON ancora eseguita): Lumi risponde prima di GPT; «no» a GPT passa all'online; modelli online scelti da Lumi (Servizio.preferiti/solo_free, riserva su 400/404); «chiudi i risultati» chiude solo quella finestra (non Lumi); niente «ti guido?» mentre c'è un sì/no del Controllo PC; libreria musicale letta in sottofondo all'avvio (MusicService.prepara); finestra risultati vuota nascosta; righe add-on vecchie senza TclError; conferma preferenze in parole semplici e col «sì»; percorsi della guida aggiornati al nuovo menu.
Da fare poi, in ordine: (1) test automatici mancanti per le correzioni di questo commit — controllo_pc «chiudi i risultati» su finestra secondaria di Lumi chiude solo quella (mai «Lumi stessa»), on_handled senza offerta tutorial se pc_service.pending, conferma preferenze con «sì» e descrivi(), MusicService.prepara in thread; (2) CI Windows; (3) build 051; (4) prove dal vivo con la diagnostica (online/orchestratore, ChatGPT account, Python, GPT acceso + «no», romanzo, Esporta JSON). Restano: «sposta il mouse al centro», «non salvare», «leggi i messaggi di Telegram» non riconosciuti (comandi da concordare con l'utente); «che modello usi?» con «Lumi,» davanti → Gemma dice «Google» (controllare scheda_breve); cronologia per Gemma con messaggi lunghi (accorciare ogni messaggio ~300 caratteri); romanzo/file lunghi (online: intero con Gemini o a pezzi; Gemma: brani pertinenti); audio in ritardo (riferito dall'utente); Gemma lenta 30-60 s ed emoji; due «Nuova chat» vuote nel menu.
