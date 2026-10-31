# JARVIS — revisione trasversale e correzioni (31 ottobre 2026)

**Stato:** ramo sperimentale `audit/full-jarvis-fixes-20261031`, PR #30, basato su `feature/telegram-bounded-history-50` (PR #29). Nessun merge automatico. Non è un eseguibile compilato: la ZIP GitHub contiene tutti i sorgenti Python e gli script Windows.

## Requisito microfono aggiornato

Su esplicita richiesta dell'utente, il **microfono è predisposto come attivo all'avvio** di Jarvis, in modalità conversazione GPT, se il modello Vosk e il dispositivo audio sono effettivamente disponibili. L'impostazione resta disattivabile manualmente; non ci sono passaggi automatici in standby in risposta ai carichi pesanti. Il launcher di prova abilita questa preferenza una sola volta anche su profili di test preesistenti; le scelte manuali successive sono rispettate. Lo stato HUD indica attivo soltanto dopo apertura reale dello stream, non sulla sola selezione del toggle.

## Ambiti verificati

Lettura strutturale dei componenti principali: interfaccia `jarvis.py`, avvio e impostazioni, `voice_control.py`, collegamento `gpt_client.py`/`gpt_bridge.mjs`, Notepad e salvataggio (`managed_documents.py`, `notepad_controller.py`, `document_store.py`), registro progetti e SQLite, memoria generale, Telegram e multi-contatto, add-on e capacità dichiarate, autodiagnosi e registro operativo, pianificatore, motore locale, HUD e gestione degli eventi. La revisione del codice non equivale a prova di tutte le interazioni reali Windows.

## Correzioni effettivamente implementate

1. **Documenti:** `document_execution.py` contiene il dispatch delle operazioni autorizzate e trasforma anche le eccezioni inattese in un evento `document_error` recuperabile dalla UI. I messaggi imprevisti riportano il solo tipo d'errore, non contenuto o percorso privato.
2. **GPT:** il metodo di arresto non richiama più l'avvio del servizio se il processo è già chiuso. I reader di processi vecchi non possono alterare lo stato e la readiness di un nuovo bridge.
3. **GUI:** il pump Tk gestisce un numero massimo di eventi per ciclo, evitando di occupare indefinitamente il thread grafico con backlog di notifiche; l'errore di riconciliazione dei documenti è riportato senza interrompere il timer.
4. **Telegram:** il database attivo e la copia iniziale di migrazione mantengono massimo 50 eventi per contatto. La copia rimuove i vecchi turni Telegram duplicati e recupera spazio con VACUUM; i progetti rimangono nel backup. La pulizia dalla UI spegne prima le risposte automatiche, informando che un invio già accettato dalla rete potrebbe comunque completarsi.
5. **Profilo di prova:** memoria generale, database attività/preferenze e manifest add-on sono copiati in cartella isolata senza sovrascrivere il Jarvis originale; le credenziali Telegram restano cifrate. I documenti di progetto non sono duplicati per evitare copie involontarie grandi.
6. **Motore locale:** elenco Download limitato a 30 elementi mantenuti in RAM anche quando la cartella ha migliaia di file; il conteggio degli altri elementi resta corretto.
7. **Voce:** un worker audio di generazione precedente, anche se termina con errore, non può impedire l'avvio della nuova modalità selezionata esplicitamente dall'utente.

## Test

- Suite Windows e Linux Python 3.11 / 3.12 via GitHub Actions.
- Test aggiuntivi: imprevisti nei worker documentali; processo GPT vecchio e shutdown; migrazione Telegram/backup; isolamenti dati; avvio microfono e persistenza della scelta; profilo di prova completo; limitazione dell'elenco Download.
- Test **non eseguiti** sul Pavilion: avvio e acquisizione microfono reali, operazioni Notepad sul desktop Windows, autorizzazione reale GPT, invio/ricezione Telegram, gestore add-on da UI. Nessuno di questi deve essere dichiarato PASS senza evidenza.

## Rischi residui e criteri di rilascio

- Il progetto mantiene un `jarvis.py` molto esteso; rifattorizzarlo integralmente adesso aumenterebbe il rischio di regressioni. I bug con percorsi verificabili sono stati corretti in modo isolato, senza riscrivere il programma.
- Il backup della prima migrazione conserva una seconda copia **limitata** a 50 eventi per contatto; la presenza di tale copia è necessaria al ripristino degli altri dati e non è un archivio di tutta la cronologia.
- Il collegamento GPT usa lo stesso SDK e l'account dell'utente installati sul PC, e la prova Telegram si collega all'account reale: nessuna chiamata live è simulata. Non fare test con contatti reali senza consenso.
- I file di progetto personali non vengono clonati nel profilo di prova: se occorre provarli è necessario un trasferimento separato, esplicito e controllato.
- I controlli AST dell'autodiagnosi non identificano necessariamente bug runtime, non leggono log Windows e non sostituiscono test di avvio.
- Una scansione antivirus è competenza dell'antivirus: non disattivare Microsoft Defender né aggiungere esclusioni per forzare Jarvis.

## Collaudo raccomandato

Chiudere il Jarvis precedente; estrarre la ZIP del ramo di audit in una nuova cartella; leggere `LEGGIMI_PROVA_TELEGRAM_50.txt`; usare **`AVVIA_TEST_TELEGRAM50.bat`**, non `avvia_jarvis.bat`, alla prima prova. La copia dati vive in `%LOCALAPPDATA%\Jarvis-Telegram50-Trial`, separata dall'archivio originale `%LOCALAPPDATA%\Jarvis`.

**Test CI superati ≠ autorizzazione al merge né alla sostituzione della versione stabile.** Richiedere prima collaudo end-to-end sul Pavilion.
