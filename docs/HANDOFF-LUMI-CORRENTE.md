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

## Ripresa 17/11 — build 055 pronta in codice (leggere per prima)
- Fatto (A-H della 055, un commit per blocco): catena unica testo/voce, consenso GPT a voce senza finestra, risultati ricerca in chat con dominio, «approfondisci online» scritto, modelli aggiunti senza copia + caselle 1/2/3 + profili per modello + GGUF corretto + salvataggio atomico, tendina RICERCA con quota (Tavily da API), Exa/Firecrawl/Linkup collegati, impostazioni modelli solo in «Modelli», versione 055 in diagnostica. Dettagli e scelte: docs/DECISIONI-E-LEZIONI.md, sezione «Build 055».
- Test nuovi: tests/test_055_catena.py, test_055_modelli.py, test_055_ricerca_ui.py, test_055_diagnostica_versione.py (non eseguiti su Linux). Test 052/054 adattati (elenco senza limite, quota «rilevate», catena con typed).
- NOT_TESTED: vedi elenco in DECISIONI-E-LEZIONI (prove dal vivo da fare con lumi-prove-diagnostica dopo la build; l'ultimo commit senza [skip ci] avvia la CI).
- Da fare dopo la prova: proposta (non implementata) dei comandi di ricerca semplici; risposte che si accavallano (ID per richiesta); _ □ X letteralmente sopra l'ingranaggio, se l'utente lo vuole; verifica del consumo reale di Exa/Firecrawl/Linkup (nessun endpoint verificato, restano «ricerche rilevate»).

## Ripresa nuova sessione — 17/11 03:30 (leggere per prima)
**Dove lavorare**
- Repo: GitHub MATRIXNEO23/jarvis, ramo `feature/jarvis-kobold-f5-profiles-20261109`. Sul PC non c'è una copia: in sessione cloud si aggiunge con add_repo (accesso push), si clona e si fa checkout del ramo.
- CI e build: GitHub Actions con `gh`. Il push sulla PR avvia test e build (workflow f5n, che va numerato a ogni build). Non lanciare workflow run.
- Subagenti (`.claude/agents/`, Sonnet): `lumi-sviluppo` (codice e test), `lumi-ci-build` (CI e build), `lumi-prove-diagnostica` (prove dal vivo, un comando alla volta, aspettando ogni risposta).
- Audit di Codex: `docs/audit/` (istruzioni in ISTRUZIONI-CODEX.md). Leggi solo il file FIX-* più recente, proponi le modifiche all'utente punto per punto e parti solo con il suo ok.

**Cartelle sul PC dell'utente (Windows, utente `matri`)**, da chiedere con device_request_folder_access:
- `C:\Users\matri\AppData\Local\Jarvis`: c'è `diagnostica_claude.json` (stato del ponte diagnostica). Non contiene log.
- `C:\Users\matri\AppData\Local\Jarvis-AccessoFile-Trial`: profilo dati di prova (JARVIS_TRIAL_HOME di avvia_lumi.bat). `addon-data\modello_locale\native.json` è fermo all'8/11.
- ATTENZIONE: la 054 sembra salvare impostazioni e profili (profili.json accanto a native.json) in una cartella diversa, non ancora individuata. Chiedere all'utente dove ha estratto la 054 e cercare lì.
- Modelli .gguf: `C:\Users\matri\Downloads` (9 modelli; Qwen3 1.7B Q4_K_M è stato aggiunto dall'utente). La copia fatta da «Aggiungi modello…» va eliminata.
- Log: su disco non ci sono `console.log` né `motore.log`. Si leggono con `lumi_console` e `lumi_log_motore` della diagnostica, filtrando.

**Stato build**
- 052: provata dal vivo. «chiudi i risultati», «cambia modello» e sì/no senza «Lumi» sono ok.
- 053: cancellazione divisa in chat, ricordi, progetti e tutto. Saltata come prova, perché è inclusa nella 054.
- 054 (run 43995895542, verde): nuova catena (prima i servizi online gratuiti, poi «Uso GPT?» a voce, poi Gemma), messaggio per la chiave Tavily mancante, «approfondisci» a Gemma, link cliccabili in chat, profili per famiglia a 3 slot, «I miei modelli», barra della quota per la ricerca. Prove dal vivo da fare.

**Correzioni da fare (055)**: vedi la sezione «Da fare per la 055» qui sotto, più:
- Bug 054: un modello aggiunto con «Aggiungi modello…» non compare nell'elenco né in «cambia modello». Lumi guarda solo la cartella del modello in uso.
- Ricerca: collegare davvero Exa, Firecrawl e Linkup (oggi c'è solo Tavily) e leggere la quota reale di Tavily via API.
- Proposta da preparare (non implementare): i comandi di ricerca e navigazione semplici per chiunque, confrontati con ChatGPT, Perplexity e gli assistenti vocali.
- Più avanti: le risposte che si accavallano quando arrivano più comandi insieme (ID per ogni richiesta). L'utente ha detto «ci pensiamo dopo».

## Bug 056 visti dall'utente (17/11, 18:30)
- Messaggio scritto doppio: «ciao» compare due volte come TU, alla stessa ora. Ipotesi: l'invio parte due volte (doppio binding di Invio/pulsante, oppure handle_text e conversation_chain insieme).
- In chat si vede «/nothink»: il suffisso del template Qwen3 finisce nel testo mostrato e salvato.
- Doppia risposta: «Smetto subito.» e «Risposta interrotta.». Ipotesi: la seconda richiesta annulla la prima.
- Dopo «Riavvio il modello» arriva «GEMMA / ERRORE > Generazione locale oltre il tempo richiesto». Probabilmente dipende dalle due richieste in parallelo; da verificare anche le impostazioni del modello, che l'utente forse ha cambiato.
- Le impostazioni dei modelli compaiono due volte, in Modelli e in Add-on: possibile conflitto (screenshot da ricevere).
- CAUSA DIMOSTRATA del blocco (motore.log, 18:45): con context_size 2048 il prompt arriva a 1500-1700 token. Sul Pavilion si elaborano circa 8 token/s, quindi ci vogliono 200 s e scatta il timeout con 0 token generati. Quando funzionava il contesto era 1024 (prompt di 400-600 token). Correzione temporanea fatta da Claude: context_size portato a 1024 in native.json e profili.json (Jarvis-Gemma-Trial), con riavvio. Ora «ciao» risponde (658/1024, 90 s, 20 token). Per la 056b: predefinito 1024 e prompt più piccolo per le domande brevi (638 token per un «ciao» sono troppi).
- Limite del prompt a 600 token (memory_preferences.prompt_max_tokens = 600): ESISTE, ma viene scavalcato. In native_conversation_session.py:304, quando c'è il catalogo delle azioni (intent_context), il budget si ricalcola con prompt_max_tokens=8192 e il catalogo può riempire tutto il contesto. Per questo con 2048 il prompt arriva a 1500 token. Correzione per la 056b: rispettare il tetto di 600 anche con il catalogo, riducendo o accorciando il catalogo, con un test sul numero di token.
- Pagina Modelli (screenshot 18:37):
  - è intitolata «Modello locale Gemma (sperimentale)» e mescola caselle 1/2/3, elenco, profili, «Anteprima multimodello», memoria e autorizzazioni GPT;
  - è duplicata nella pagina dell'add-on.
- «Configura Gemma locale»: il campo Modello GGUF punta ancora a gemma-2-2b-abliterated, mentre l'elenco dice «Qwen3 1.7B in uso». Due fonti di verità in conflitto: possibile causa del timeout. Valori: thread 2/2, contesto 2048, max output 128.
- «Memoria locale - impostazioni»: la pagina si disegna sopra la precedente (lettere fantasma a sinistra) e il testo esce dal bordo.
- Barra in alto da rifare (mockup approvato, tema azzurro): ogni voce è un tasto; Modello ▾ con ⏻ nello stesso tasto (via «MODELLO ON»); «Online» e «Ricerca» vicini; Telegram come tasto con on/off; icone meteo disegnate bene (sole, sole e nuvola, nuvola, pioggia, temporale, neve, nebbia, luna con le fasi).

## Ripresa 17/11 sera — 056b allargata (solo py_compile su Linux)
- Fatto: pagina «Modelli offline» unica (miei_modelli + NativeSettingsWindow(embed=True), memoria nel profilo), via anteprima F5 e pulsanti doppi; prompt «ciao» (prompt_breve); HUD in basso (_layout_bottom); aiuto Meteo/Modelli; contesto online proporzionato (contesto_online); inventario docs/INVENTARIO-DUPLICATI-056b.md; audit in docs/ANALISI-056.md.
- Test nuovi: test_056b_nessun_duplicato_impostazioni, _memoria_nel_profilo, _ciao_non_ripete, _hud_layout, _aiuto_meteo, _contesto_online.
- Audit: nessun ripristino applicato (regola utente 20:28), elenco in docs/ANALISI-056.md da far scegliere all'utente.
- Resta: CI test e build f5n da verificare; «meteo domani» non esiste (proposta); tutorial vocale del meteo non fatto (aiuto_comandi riguarda solo Controllo PC).

## Ripresa 17/11 notte — 056c implementata (approvata 17/11 21:21), solo py_compile su Linux
- Etichetta build: resta `--number 056` nel workflow f5n (da chiedere se serve «056c»).
- 1) `prompt_breve.adatta_storia(history, latest, ridotta)`: casella «Cronologia ridotta per domande brevi» (`MemoryPreferences.cronologia_ridotta`, accesa); per ogni domanda breve (<= 5 parole, senza «approfondisci/spiega…») resta solo l'ultimo scambio tagliato; spenta = comportamento 056b.
- 2) Valori di partenza (CAMBIATI dall'utente 17/11 21:26, non più 768/500): contesto 896, tetto del prompt 550, risposta massima 256 (`NativeModelConfig.context_size/max_output`, `MemoryPreferences.prompt_max_tokens`). `profili_famiglia._voce` scrive la memoria di partenza solo per i modelli NUOVI (slot 1 del modello in uso e profili già salvati non si toccano). Visibili e modificabili in Modelli; `native_ui.save` rifiuta il salvataggio se prompt + risposta superano il contesto, con messaggio chiaro.
- 3) Un solo blocco «Contesto e memoria del prompt» (native_ui `_build_memory`); chat continua e ricordi stanno in `memory.native.json` (profilo: `MEMORIA_CAMPI`). `contesto_lumi.carica/salva` senza path leggono lì (fallback al vecchio contesto.json); tolta `costruisci_sezione` e la chiamata in jarvis.py.
- 4) Meteo domani: `meteo/commands.py` («meteo domani [a città]», «che tempo farà domani»), `service.domani` (Open-Meteo daily), azione `addon.meteo.domani` (jaddon + addon_manager), aiuto in local_help, LEGGIMI, ui.
- 5) Barra: ordine Mic, Modello ▾, Online ▾, Ricerca ▾, Memoria, simbolo Telegram; ⏻ e simbolo disegnati su Canvas (`barra_tasti.IconaCanvas`), nome del modello solo nella tendina, ingranaggio e _ □ X invariati.
- 6) `meteo/icone.py` a contorno come l'anteprima; l'HUD mostra icona, città, temperatura e ora; ora e sveglia restano in basso.
- Test: tests/test_056c_barra_meteo.py (anche larghezza a 1366), tests/test_056c_cronologia_e_profilo.py; adeguati 056_meteo, 056b_barra_meteo, hud_quick_toggles, 056b_prompt_e_testo, memory_preferences.
- Domande aperte per l'utente: (a) «Mic» ora mostra solo ⏻ (azzurro/arancione): lo stato PTT/«non attivo» non è più scritto, va bene? (b) il conteggio dei messaggi Telegram non letti non è più nella barra (resta il colore): lo vuoi vicino al simbolo? (c) «domani» risponde con cielo, minima e massima: va bene la frase? (d) etichetta build 056 o 056c?

## Decisioni per la 056c (utente 17/11, 21:00-21:15, a voce)
1. Cronologia ridotta per TUTTE le domande brevi, non solo per i saluti, con la casella «Cronologia ridotta per domande brevi» (accesa) visibile nelle impostazioni.
2. Valori di partenza per ogni modello nuovo: contesto 768 e tetto del prompt 500, VISIBILI nella pagina Modelli. Ogni modello li cambia nel proprio profilo. Il resto dell'audit resta com'è (chat continua accesa, cronologia 200).
3. «Contesto» e «Memoria del prompt» uniti in un solo blocco, salvati nello stesso posto.
4. Aggiungere «meteo domani», con aiuto e frasi a voce.
5b. Barra della 056b vista dall'utente (foto delle 21:16):
   - è tagliata a destra (Telegram troncato) e non corrisponde al mockup;
   - ⏻ compare come un quadratino (il font non ha il simbolo);
   - il nome del modello è troppo lungo;
   - Telegram NON doveva diventare la scritta «Telegram»: va tenuto il SIMBOLO originale con i suoi colori di stato;
   - l'icona meteo (San Venanzo 7°) non si capisce ancora.
5. L'utente dice che i tasti della barra in alto NON sono come nel mockup approvato (dettagli da raccogliere con uno screenshot).

## 056b, aggiunte decise con l'utente (17/11, 19:10-20:09, a voce)
1. Una sola pagina «Modelli», senza «Gemma» nei nomi e senza finestre annidate:
   - in alto le caselle 1/2/3, l'elenco e «Aggiungi»;
   - sotto i 3 profili del modello selezionato;
   - sotto ancora TUTTE le impostazioni del modello, direttamente nella pagina: contesto, thread, risposta massima, ecc., più quelle della memoria che finiscono nel prompt (token di cronologia, messaggi recenti, sintesi). Oggi la memoria è in «Configura memoria locale»: esce da lì ed entra solo nel profilo.
   - Un solo Salva, che scrive SOLO nel profilo caricato del modello in uso.
   - Base: native.json (regola delle 19:04). Via «Anteprima multimodello». Nella pagina dell'add-on nessuna impostazione dei modelli.
2. Il second brain resta unico per tutti i modelli; accensione e cancellazione restano in Memoria.
3. Bug: dopo una domanda, al «ciao» successivo il modello ripete la risposta precedente. Da fare:
   - controllare il prompt reale;
   - segnare chiaramente la conversazione precedente;
   - tagliare le risposte vecchie lunghe;
   - meno cronologia per saluti e domande brevi;
   - dal second brain solo fatti salvati e solo se pertinenti, nessun ricordo per i saluti.
4. Regola fissa: ogni funzione nuova aggiorna anche l'aiuto dei comandi, i tutorial, le frasi a voce e il catalogo delle capacità. Per il meteo («che tempo fa a…», «meteo a…», «meteo domani») non era stato fatto.
5. REGRESSIONE 056: in basso l'ora e la sveglia non si vedono più (spinte fuori dalle icone meteo). Vanno ripristinate; se manca spazio, l'ora va accanto al meteo. Regola: un'aggiunta non deve rompere quello che c'è, quindi audit delle regressioni prima della build.
6. Contesto online proporzionato (sezione 19:01): incluso.

## 057, primo punto (utente 17/11 19:03)
Le impostazioni sono duplicate tra «Modello locale Gemma» (Configura Gemma locale) e la sezione multimodello/«I miei modelli»/profili, oltre che nella pagina dell'add-on. L'utente: i modelli andavano messi DENTRO la sezione del modello locale, senza crearne un'altra. Nella 057: una sola pagina «Modelli offline» (caselle, elenco, profili e configurazione del modello selezionato), via i doppioni. Nella 056b: solo l'unica fonte del modello in uso (native.json e profili coerenti).

Regola dell'utente (19:04): la BASE è quella funzionante a modello singolo (native.json + «Configura Gemma locale»). Più modelli e profili si AGGIUNGONO a quella base, non diventano una configurazione parallela.

057, file del programma (utente 20:11): la cartella del programma ha più di 100 file sparsi nella radice. Bisogna verificare quali servono davvero (import anche dinamici, launcher, pacchetto) e riordinarli in cartelle per responsabilità, senza rompere niente: prima l'inventario e una proposta da approvare, poi lo spostamento con test e prova del pacchetto estratto. Via dal pacchetto i file non usati, come da regola «Pacchetto per l'utente» in AGENTS.md.

## Richiesta utente 17/11 19:01: contesto online proporzionato
Una domanda breve («ciao») non deve mandare migliaia di token online. Proposta (da approvare): il contesto cresce con la richiesta. Domanda breve = solo istruzioni minime e l'ultimo scambio; «approfondisci» e richieste lunghe = fino a 6 scambi; allegati e scheda di Lumi solo se servono. Nel log e nella diagnostica, i token mandati per ogni richiesta. Restano valide le soglie del 15/11: 80% della quota e conferma oltre ~8.000 token.

## Dopo la 056: pulizia e riordino (richiesta utente 17/11, 16:42)
Da fare prima di nuove funzioni (navigazione autonoma inclusa):
- Riordinare menu e impostazioni per sezioni, in modo intuitivo, veloce e completo, senza duplicati né incoerenze.
- Trovare e risolvere i doppioni: due cose che fanno la stessa cosa o comandi in conflitto.
- Togliere i file inutili dal pacchetto (vedi le regole «Pacchetto per l'utente» in AGENTS.md).
- Metodo: prima un inventario (menu, impostazioni, comandi, file del pacchetto), poi una proposta da far approvare all'utente punto per punto, poi la modifica. Niente cancellazioni senza verifica degli import e senza ok.

## Ripresa 17/11 notte — 056b implementata (approvata 17/11 18:55), solo py_compile su Linux
- Etichetta build: resta `--number 056` nel workflow f5n (stessa build, nessun cambio al workflow).
- 1) `native_conversation_session.py`: tolto il budget 8192 e l'override del contatore esatto; vale `prompt_max_tokens` (600) anche col catalogo. Se il catalogo pieno non entra si prova `conversation_router.reduce_intent_context` (azioni pertinenti, poi sole 6 essenziali); se nemmeno così, resta il solo chat. `context_size` predefinito 1024 (native_config.py).
- 2) «Chat continua» accesa di serie (`contesto_lumi.Contesto`). Vale solo per la sessione offline; l'online resta a 6 scambi.
- 3) Causa del doppio «TU >»: `submit_gpt` scriveva «TU >» e poi `conversation_chain` → `submit_gemma_voice(typed=True)` lo riscriveva. Ora `chain_typed_once` alza `conversazione_lumi.TU_SCRITTO` durante la catena. Resta noto: dopo il «sì» a «Vado online?» un testo scritto riscrive il «TU >» (da verificare dal vivo).
- 4) «/nothink»: nel codice non veniva aggiunto da nessuna parte (lo produce il modello/template). Il prompt Qwen3 usa già il blocco `<think>` vuoto, quindi non si aggiunge nulla; `strip_nothink` lo toglie da domanda, risposta e stream.
- 5) `memory_ui.py`: pulisce i figli prima di disegnare, testo a capo con la larghezza della finestra.
- 6) Barra: `barra_tasti.TastoBarra` (stile unico, ⏻ azzurro/arancione). Ordine: Modello: nome ▾ ⏻ | Online ▾ | Ricerca ▾ | Mic ⏻ | Memoria ⏻ | Telegram ⏻. ⏻ Telegram = risposte automatiche, con i colori di stato del 15/11 (azzurro attivo, verde risposto, arancione bloccato, rosso disattivato) via `power_color`, non il semplice on/off. «MODELLO ON» e la `/` separatrice tolti.
- 7) `meteo/icone.py` ridisegnata (sole, sole+nuvola, nuvola, pioggia, temporale, neve, nebbia, luna con fase calcolata da `fase_lunare`); `meteo/service.py` legge `is_day`.
- Una sola fonte (19:04): base = native.json (il motore legge solo quello; profili.json è solo archivio degli slot). Causa del «Qwen3 in uso» con gemma2 caricato: il modulo «Configura Gemma locale» restava aperto con valori vecchi e al Salva riscriveva `model`. Ora `sync_modello` in native_ui.py (a FocusIn e prima di Salva) ricarica da native.json, e Salva copia i valori anche nello slot in uso del modello (`salva_in_slot`). Pagine non unite: riordino nella 057.\n- Test: tests/test_056b_prompt_e_testo.py, test_056b_una_fonte_modello.py, test_056b_barra_meteo.py; adeguati test_056_barra e test_054_profili_modelli. Prove dal vivo da fare dopo la build (misura i token del «ciao» con contesto 1024).

## Ripresa 17/11 sera — build 056 implementata (decisioni 17/11 16:38, solo punti A, B, C, C2, C3, D, E)
- Commit: 6345018 (A+E+C3), cffa904 (B+D), f0337c4 (C/C2 meteo), 7254cae (diagnostica, docs); l'ultimo avvia la CI. Solo py_compile su Linux: valgono i test della CI Windows e la build f5n.
- A: `conversation_chain` (jarvis.py): comandi già passati; Basso consumo = tutto al modello offline (`route="locale"`, niente classificatore); l'online solo dopo «Vado online?» (`ask_online`, riusa `online_yes/online_no` e `servizi_online.IN_ATTESA`, ora con terzo campo «approfondisci»). Codice/script: stessa conferma. «approfondisci» e pulsante «Approfondisci» (chat_bolle.py): `deepen_last`, ultima domanda in `last_question`; conferma in Basso consumo, diretto in Veloce. «cerca/approfondisci online»: conferma `ricerca_yes/no` prima di consumare quota. Il testo scritto lungo passa dalla stessa catena (tolto run_gpt("ask") da submit_gpt).
- B: `settings["modalita"]` (basso_consumo|veloce, validata in settings.py), slide `slide_modalita.py` (riusa `addon_righe.Interruttore`) al posto di «INTERFACCIA NEURALE»; `save_mode` salva e annulla se il salvataggio fallisce. Veloce = ramo online della 055, offline di riserva.
- C/C2: add-on `meteo/` (Meteo.jaddon, LEGGIMI, service.py Open-Meteo via urllib, commands.py, config.py città predefinita, runtime.py, icone.py, ui.py pagina add-on). Core action `weather.local` in addon_manager. Comando prima dei comandi PC, escluse «online», «clima», «domani». HUD: `JarvisHUD.set_weather` sotto il globo e sopra DISCO C/RETE, senza riquadro; `meteo_refresh` all'avvio (4 s) e un solo timer da 30 minuti; add-on spento = niente icona né rete. Nasce SPENTO.
- C3: dopo «cerca online» si apre `risposte.expect_choice` (120 s): «apri il 2» / «il secondo» apre l'URL (solo http/https) nel browser, senza conferma (`open_search_result`; `number_of` accetta «apri»).
- D: tolto «GPT ON» (animated_hud.py); ONLINE ▾ ora dopo MIC; nuova tendina MODELLO ▾ (`menu_modello.py`, riusa MenuModelli e `lumi_model_use`: un solo modello in memoria); un solo on/off, il pulsante MODELLO ON/OFF esistente.
- E: causa dimostrata nel codice: il `save()` dei pannelli Impostazioni riscriveva `attivi` dalle spunte vecchie. Ora `servizi_online.unisci_attivi` applica solo le spunte cambiate nel pannello sopra il file riletto (online e ricerca); `MenuModelli._save` segnala gli errori in chat. «Promessi sposi» a offline: coperto dal test di catena, NOT_TESTED dal vivo.
- Diagnostica: `lumi_stato` ha `modalita` e `meteo` (attivo, città, temperatura, icona); workflow f5n con `--number 056`.
- Test: tests/test_056_catena.py, test_056_barra.py, test_056_meteo.py, test_056_diagnostica.py; adeguati 054 catena, hud_quick_toggles, self_review, selected_conversation_model, 055 diagnostica/versione.
- NON fatto (sezione «Da decidere»): navigazione autonoma, «leggi il N», download, Extract, ricerche online (Tavily/Exa/…) e relative frasi. Proposta annotata: le spunte `usa_sempre`/`proponi_lunghe` dei pannelli hanno lo stesso rischio di valori vecchi.
- Prove dal vivo da fare (Codex): vedi docs/ANALISI-056.md, sezione «Prove dal vivo».

## Da fare per la 056 (decisioni utente 17/11, 15:30, a voce)
- La catena della 055 (prima online, poi locale) è SBAGLIATA: non l'aveva decisa l'utente. Ordine corretto, fisso:
  1. motore dei comandi: se è un comando lo esegue, senza passare da nessun modello;
  2. modello offline: risponde a tutto il resto;
  3. online solo per approfondimenti e per richieste esplicitamente online (ricerche), sempre con conferma a voce prima di andare online.
- Prima del codice serve un progetto breve, da approvare: chi fa cosa tra comandi, offline, servizi online, GPT e ricerche (Tavily e gli altri), quando si chiede conferma, cosa non si fa mai.
- Barra in alto:
  - togliere «GPT ON»: GPT sta solo nella tendina ONLINE;
  - nuova tendina MODELLO (offline) come le altre, con le 3 caselle per sceglierli al volo e un tastino on/off accanto, senza passare dalle impostazioni.
- Esiti delle prove fatte da Codex sulla 055: il file ESITI-055.md non c'è in Downloads; chiedere all'utente dove si trova.

## Da fare per la 055 (decisioni utente 17/11, notte)
- Decisioni dell'utente del 17/11 alle 05:04:
  - GPT (dal browser) va nella stessa lista dei servizi online, con la sua spunta e il suo ordine, e non più in un passaggio separato. FATTO 17/11 (approvato alle 05:05): la domanda «Uso GPT?» è sparita.
  - Pulsanti _ □ X: a destra, sopra l'ingranaggio. FATTO 17/11: colonna `_jarvis_window_corner` in animated_hud.py, window_chrome.py vi mette i pulsanti sopra l'ingranaggio (da vedere dal vivo).
- Ricerca: al posto dell'interruttore «RICERCA on/off» in alto, un menu a tendina come quello dei servizi online: elenco dei servizi di ricerca, ciascuno con la sua spunta e la sua barra di quota.
- Modelli: «Aggiungi modello…» non copia più il file, lo usa da dove si trova. Se il file sparisce, Lumi lo segnala. L'elenco e «cambia modello» devono vedere i modelli aggiunti (bug 054: Qwen3 copiato in modelli/ non compariva).
- Modelli: 3 posizioni fisse (1/2/3) con modelli preassegnati per passare velocemente dall'uno all'altro, con l'elenco completo sotto.
- Profili: 3 profili per OGNI singolo modello, non per famiglia.
- Impostazioni modelli: si trovano solo in «Modelli». La pagina dell'add-on tiene solo attiva/disattiva e il pulsante «Apri impostazioni modelli».
- Bug 054 (prova 17/11 03:41): «approfondisci la fotosintesi» apre ancora la finestra Windows «Conferma GPT online» (Sì/No). Va tolta: la scelta sì/no si fa a voce, senza «Lumi». Controllare anche perché «approfondisci» chiede GPT invece di andare a Gemma.
- Prove dal vivo 054 (17/11 03:45, diagnostica):
  - ok: «cerca online meteo Roma» con Tavily, 5 fonti in 3 s;
  - ok: «approfondisci la fotosintesi» passa al modello locale;
  - ko: la versione 054 non compare in lumi_stato né in lumi_online;
  - ko: «cambia modello» non elenca Qwen3 1.7B (bug noto);
  - ko: una domanda generica non passa dai servizi gratuiti né da «Uso GPT?». Va subito al locale e poi risponde «Non riesco a rispondere adesso», con timeout di 80 s.
- Prove 054, secondo giro (04:05):
  - Causa del ko sulla catena: il testo scritto passa da jarvis.py:3544 → run_gpt("typed_conversation"), senza servizi_online né offer_gpt. La catena c'è solo nel percorso vocale (~2320). Va unificata.
  - La finestra Sì/No nasce da confirm_gpt_inference (jarvis.py:2169, messagebox.askyesno), chiamata alle righe 2064, 2209, 2217 e 3304. Va sostituita con offer_gpt + chiedi a voce.
  - I link Tavily compaiono solo in console, non in chat.
  - «approfondisci online buchi neri»: nessuna risposta dopo 60 s.
  - Profili a 3 slot e barra quota: il codice c'è, ma non è collegato alla UI (solo «I miei modelli» in native_ui.py:53).
- Pulsanti _ □ X in alto a destra, sopra l'ingranaggio (non fatto nella 054).
- Prima delle correzioni: leggere il FIX di Codex in docs/audit/, proporre all'utente le modifiche punto per punto e partire solo con il suo ok.

## Ripresa 17/11 — build 052 preparata (decisioni dell'utente del 17/11 + audit Codex FIX-051-01)
Stato: codice e test scritti, **non eseguiti in locale** (regola: solo CI Windows). Esito CI/build: vedi sotto, aggiornato dopo il push. Nuovi test: `tests/test_052_*.py`, più aggiunte a `test_controllo_pc.py` e `test_musica.py`.

**Fatto**
- Audit 1 — `controllo_pc/service.py::_do_close`: ora controlla il valore di `backend.close(hwnd)` (errore «Non riesco a chiudere…» se False, anche per Lumi). Le finestre di Lumi hanno un `ruolo` (`controllo_comune/windows.py`: «principale» se il titolo inizia con «LUMI // Interfaccia», altrimenti «secondaria»). Una secondaria (risultati) si chiude da sola; «chiudi Lumi» punta sempre alla principale e chiede conferma. Test con backend simulato (`test_controllo_pc.py`).
- Audit 2 — `second_brain.clear_all()`: **codice NON toccato**, dubbio per l'utente. Il testo mostrato (`jarvis.py::clear_saved_memory`) dice «scambi, operazioni e correzioni vocali archiviate da Lia» e il pulsante «Cancella memoria generale (non progetti)»: non promette di cancellare i ricordi (tabella `ricordi` + indice `ricordi_fts`), che hanno una pagina propria (Ricordi, «dimentica»). Domanda: il pulsante deve cancellare anche i ricordi? Se sì: stessa transazione, `DELETE FROM ricordi` + `INSERT INTO ricordi_fts(ricordi_fts) VALUES('delete-all')`, test su DB temporaneo con riavvio.
- Audit 3 — i 4 test mancanti: niente «ti guido?» con `pc_service.pending`; preferenze («sì» salva su DB temporaneo e dopo riapertura, «no» annulla, nuova richiesta sostituisce); `MusicService.prepara` non blocca (scansione lenta e OSError); chiusura risultati. I test di `jarvis.py` estraggono le funzioni reali con AST (come `test_file_access.py`).
- 4 — «chiudi i risultati» (e varianti: «chiudi risultati», «chiudi la finestra dei risultati», «togli/nascondi i risultati», «chiudi l'elenco») è in `lumi_comandi.py`, il primo gestore locale (prima di Gemma e GPT). Chiude solo la finestra (`file_access/ui.py::chiudi_risultati`).
- 5 — script/codice: `servizi_online.richiesta_codice()`; in `submit_gemma_voice` e `start_conversation_gpt` vanno sempre all'online (orchestratore), senza la domanda «uso l'online?». Nessun servizio pronto → messaggio breve; se l'online fallisce niente ripiego su Gemma.
- 6 — risposta senza «Lumi»: **esisteva già in parte** (`risposte.expect_answer` usato da `lumi_comandi.chiedi`, Controllo PC, programmi, `intent_normalizer`; `expect_numbers` per la griglia). Lacune chiuse: la conferma delle preferenze non apriva la finestra del «sì» (ora sì); aggiunta la scelta numerata generica `risposte.expect_choice` («1», «uno», «il secondo», «no») usata dall'elenco modelli e dalla finestra risultati file (1..9, 45-60 s). «stop», «niente» non vengono mai consumati dalla scelta.
- 7 — «cambia modello» / «scegli il modello» / «elenca i modelli»: `local_model/scelta_modello.py` elenca i `.gguf` (cartella del modello in uso + `addon-data/modello_locale/modelli`, al massimo 9, senza `mmproj`), li dice a voce e li scrive nella finestra risultati; il numero salva `native.json` (stesse regole delle impostazioni) e chiama `lumi_model_restart` già esistente (chiude il motore figlio; si ricarica col nuovo modello alla prossima domanda, non subito, per la RAM del Pavilion).
- 8/9 — `servizi_ricerca/` (stesso schema di `servizi_online`: un file per servizio, chiavi DPAPI in `servizi_ricerca.keys`, impostazioni `servizi_ricerca.json`, sezione «Servizi di ricerca» in Impostazioni > Modelli, link per le chiavi come da richiesta). **Solo Tavily è collegato**; Exa, Firecrawl, Linkup sono voci predisposte (chiave, link, ordine, spunta; la ricerca le salta). Motivo: non posso provare le loro API da qui e non ho voluto scrivere adattatori a memoria. «cerca online …» / «approfondisci online …» (solo questi due; «approfondisci» senza «online» resta a Gemma) provano il primo servizio pronto e passano al successivo su errore o crediti finiti; riassunto + link nella finestra risultati (doppio clic copia il link), a voce solo un riassunto breve, il browser non si apre.
- 10 — diagnostica: nuovi strumenti `lumi_ricerca` (servizi di ricerca, mai la chiave) e `lumi_modelli` (elenco .gguf e modello in uso). Gli altri comandi nuovi si provano con `lumi_prova_comando`.

**KoboldCpp nel build** (`.github/workflows/f5n-koboldcpp-native-dll-windows.yml`): commit fisso `6d2fedf8624e5f05926af3191f9efdcb13c4133c` (branch concedo), compilato `make koboldcpp_noavx2`. Qwen3 1.7B: il passo F5N.6 del workflow scarica e carica Qwen3-1.7B Q4_K_M come modello di prova (famiglia `qwen3`, template `qwen3_template_f5`): è la prova CI da consultare, non l'ho rieseguita. Gemma 3: **non dimostrato**: `local_model/chat_templates.py` mappa l'architettura `gemma3` sul template gemma2, ma nelle prove CI c'è solo Gemma 2 2B (nessun GGUF Gemma 3); da provare dal vivo con un file Gemma 3 prima di promettere il supporto. Da qui GitHub non è raggiungibile: non ho potuto leggere data/versione di quel commit.

**Dubbi / decisioni da prendere**
- `clear_all()`: vedi sopra (ricordi sì o no).
- Il cambio modello ricarica alla prossima domanda: va bene o vuoi il caricamento subito?
- Codice online senza la domanda «uso l'online?»: scelta mia per rispettare «sempre online»; se vuoi mantenere il consenso per richiesta, va aggiunta una domanda con solo sì/«annulla».
- Exa/Firecrawl/Linkup: serve una prova con chiave reale per scrivere gli adattatori.
- Hardening di `esegui_python` (audit P2) non fatto: fuori dalle decisioni del 17/11.

**Da provare dal vivo (build 052)**: «chiudi i risultati» dopo una ricerca file (deve chiudere solo la finestra, subito); «scrivimi uno script che …» con online acceso e spento; «cambia modello» → elenco a voce e in finestra, «2» senza «Lumi», riavvio e messaggio col nuovo modello; «Lumi, ricordati che preferisco risposte brevi» → «sì» senza «Lumi»; Impostazioni > Modelli > Servizi di ricerca (link e chiave Tavily, pulsante Prova); «cerca online …» e «approfondisci online …» con Tavily (poi con chiave sbagliata per vedere il passaggio al successivo); `lumi_ricerca` e `lumi_modelli` dalla diagnostica; musica all'avvio senza blocchi.

## Ripresa 17/11 — build 054: catena GPT/online, ricerca senza chiave, «approfondisci»
- Ordine deciso dall'utente: online gratuiti, poi GPT con «Uso GPT? sì/no» (senza «Lumi», nessuna finestra), poi modello locale; mai silenzio. Codice: jarvis.py (start_conversation_gpt, offer_gpt, resume_gpt, send_to_gpt, local_after_gpt, azioni gpt_yes/gpt_no/gpt_offer), local_model/conversazione_lumi.py (evento online_gpt).
- «cerca online» senza chiave Tavily: messaggio col link; errori mostrati in chat. «approfondisci» senza «online»: Gemma.
- Profili per famiglia (054): `local_model/profili_famiglia.py` (riconoscimento da nome file e metadati GGUF, 3 slot per famiglia, ultimo slot ricordato, migrazione: la prima volta lo slot 1 prende i valori attuali di native.json, 2 e 3 i default; dati in addon-data/modello_locale/profili.json). Usato da `scelta_modello.salva_scelta` (voce e «Usa questo», stessa funzione `lumi_model_use` in jarvis.py) e da `motore_processo.prepare` (migrazione all'avvio). Punto 4: nella sezione «I miei modelli» ci sono slot 1/2/3, «Salva in questo profilo» e «Ripristina default» (`local_model/miei_modelli.py`, dentro la finestra «Configura Gemma locale»); il cambio slot dice quali campi chiedono il riavvio del motore.
- «I miei modelli»: elenco con il modello in uso evidenziato, Aggiungi (copia a blocchi con barra, file .copia temporaneo), Usa questo, Rimuovi (Cestino con conferma, mai il modello in uso). Non è nella pagina dell'add-on (`ModelloLocale.jaddon`): solo nella finestra di configurazione. DA FARE: pagina add-on.
- Servizi di ricerca: barra quota con lo stesso stile di ONLINE, ma solo stima dai contatori locali (limite Tavily 1000/mese, scritto «stima»); lettura dell'uso da API di Tavily NON collegata (non verificabile da qui). Interruttore RICERCA ON/OFF in alto accanto a MODELLO, salvato in servizi_ricerca.json.
- DA FARE: spostare _ □ X nell'angolo in alto a destra sopra l'ingranaggio (window_chrome li impagina già come – □ × ma nel riquadro del titolo; serve verifica a schermo).
- «cerca online»/«approfondisci online»: risultati direttamente in chat (non più nella finestra risultati): riassunto, «Fonti:» con `[titolo](url)` e anteprima; `chat_link.py` rende i link cliccabili (sottolineati, cursore a mano, clic = browser) dentro `write_line`; vale per ogni messaggio con link. Test: tests/test_054_chat_link.py.
- Test: tests/test_054_catena_gpt.py (+ adattati due test di test_selected_conversation_model.py). Non eseguiti in locale; vale la CI Windows. Da provare dal vivo con GPT attivo non collegato e collegato.

## Ripresa 17/11 — correzione CI 055 (run 44009240767 rossa)
- Cause e correzioni: (1) `gpt_voice_consent_epoch` era `nonlocal` e i test che estraggono le funzioni non lo avevano: ora l'epoca sta su `confirm_gpt_inference.consent_epoch` (~88 NameError); (2) `profili_famiglia._scrivi_temp` con newline="\n" (su Windows il testo raddoppiava \r); (3) `window_chrome` fissa all'import le classi Tk per `isinstance` (TypeError con tkinter.Tk simulato).
- Test aggiornati perché il comportamento 055 è cambiato davvero: elenco modelli con quello in uso per primo; modello nuovo parte dai default (profili per modello, tornando al vecchio rivale 3 thread); Exa/Firecrawl/Linkup collegati; invio testo passa da `conversation_chain`; test ricerca con servizio spuntato; test voce/PTT estraggono anche `conversation_chain`. Nuovo: tests/test_055_correzioni_ci.py.
- Il fix «dopo il sì a Uso GPT? la domanda va subito a GPT» NON è implementato: l'utente non l'ha ancora approvato (proposta da annotare).
- Secondo giro (run 44011730454): i test del trasporto GPT simulavano il consenso con messagebox.askyesno, rimosso dalla 055 per scelta; nuovo tests/consenso_finestra.py (stessa logica 054) usato dalle fixture test_activity_status e test_file_refinement. La conferma a voce vera resta provata in test_055_*.
- Esito CI: vedi commit successivo/Run nel messaggio di consegna. Niente test su Linux, solo py_compile.

## Ripresa 17/11 mattina — GPT nella lista, pulsanti sopra l'ingranaggio (055)
- GPT dal browser è la voce «ChatGPT (tuo account)» (id chatgpt_account) della lista servizi online, con spunta e posizione. `conversation_chain` prova i servizi in ordine e poi il locale; tolti offer_gpt, resume_gpt, send_to_gpt, le azioni gpt_yes/gpt_no/gpt_offer e il passaggio «online_gpt». Codice/script restano sempre online. Nessuna finestra Sì/No nella catena; il consenso a voce resta solo per Telegram e ricerca file.
- lumi_online mostra posizione, tipo e gpt_collegato per ogni servizio. Test: tests/test_055_gpt_in_lista.py (cima, fondo, senza spunta, non collegato) e test aggiornati 054/selected/055_catena. Solo py_compile su Linux.

- Aggiunta approvata 17/11 05:13: pulsante «Copia configurazione per Codex» in Impostazioni → Diagnostica per Claude (diagnostica_claude/ui.py: configurazione_codex, percorso_codex), con riga sotto il pulsante; LEGGIMI e ISTRUZIONI-PROVE-CODEX.md punto 1 aggiornati. Test in test_055_gpt_in_lista.py.

## Ripresa 17/11 — build 053: cancellazione memoria a sezioni (da provare dal vivo)
- Decisione utente: la cancellazione si sceglie per sezione. Impostazioni > Memoria generale ha 4 pulsanti (Cancella chat / ricordi / progetti / tutto) e a voce «cancella le chat», «cancella i ricordi», «cancella i progetti», «cancella tutto». Ogni volta sì/no con messaggio semplice.
- Codice: cancella_memoria.py (sezioni, messaggi, frasi, esegui); SecondBrain.clear_ricordi() (tabella + FTS nella stessa transazione, opzionale per progetti); menu_laterale.cancella_tutti_i_progetti() (chat, cartelle nel Cestino, ricordi del progetto) riusata da cancella_vecchi_progetti; jarvis.py clear_saved_memory(section) e memory_wipe_command (voce, prima di preference_command); catalogo comandi: sezione «Memoria». Chiude il P1 di FIX-051-01 su clear_all.
- Test: tests/test_cancella_memoria.py (solo DB/cartelle temporanee). Workflow f5n alzato a 053. Da fare: prova dal vivo (pulsanti e frasi a voce).

## Ripresa 16/11 23:58 — build 051 pronta, prove dal vivo da fare
- CI Windows verde sul pacchetto 35d63f2 (run su 185fbc8). Build 051 riuscita: artefatto lumi-051-prova-candidate, run 43811765732. Corretto il workflow: anche il nome dell'artefatto va aggiornato a ogni build (era rimasto 050).
- Il push sulla PR avvia già la build: non lanciarne un'altra con workflow run (doppioni annullati).
- Nuovi subagenti Sonnet in .claude/agents: lumi-ci-build (test/build) e lumi-prove-diagnostica (prove dal vivo, restituisce solo una tabella). Usarli per risparmiare quota.
- Accesso concesso alla cartella dati %LOCALAPPDATA%\Jarvis: copiare i log nel workspace e filtrarli con la shell, invece di leggerli tramite la diagnostica.
- Da fare: prove dal vivo sulla 051, a cominciare da «chiudi i risultati»; poi nessun «ti guido?» durante un sì/no, conferma preferenze, musica in sottofondo, servizi online/orchestratore, ChatGPT, script Python, GPT con «no», romanzo lungo, Esporta JSON. Audio in ritardo: lo verifica l'utente.
- Per la 052: i 4 test automatici mancanti (vedi nota sotto), possibile compito per GPT/Codex.

## Ripresa 16/11 03:40 (limite d'uso quasi finito) — pacchetto di correzioni in corso
Fatto nel codice (questo commit, CI Windows NON ancora eseguita): Lumi risponde prima di GPT; «no» a GPT passa all'online; modelli online scelti da Lumi (Servizio.preferiti/solo_free, riserva su 400/404); «chiudi i risultati» chiude solo quella finestra (non Lumi); niente «ti guido?» mentre c'è un sì/no del Controllo PC; libreria musicale letta in sottofondo all'avvio (MusicService.prepara); finestra risultati vuota nascosta; righe add-on vecchie senza TclError; conferma preferenze in parole semplici e col «sì»; percorsi della guida aggiornati al nuovo menu.
Da fare poi, in ordine: (1) test automatici mancanti per le correzioni di questo commit — controllo_pc «chiudi i risultati» su finestra secondaria di Lumi chiude solo quella (mai «Lumi stessa»), on_handled senza offerta tutorial se pc_service.pending, conferma preferenze con «sì» e descrivi(), MusicService.prepara in thread; (2) CI Windows; (3) build 051; (4) prove dal vivo con la diagnostica (online/orchestratore, ChatGPT account, Python, GPT acceso + «no», romanzo, Esporta JSON). Restano: «sposta il mouse al centro», «non salvare», «leggi i messaggi di Telegram» non riconosciuti (comandi da concordare con l'utente); «che modello usi?» con «Lumi,» davanti → Gemma dice «Google» (controllare scheda_breve); cronologia per Gemma con messaggi lunghi (accorciare ogni messaggio ~300 caratteri); romanzo/file lunghi (online: intero con Gemini o a pezzi; Gemma: brani pertinenti); audio in ritardo (riferito dall'utente); Gemma lenta 30-60 s ed emoji; due «Nuova chat» vuote nel menu.
