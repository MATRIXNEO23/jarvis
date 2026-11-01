# 6. Reinstallazione e dati
Separare reinstallazione del programma e azzeramento dei dati. Questa guida non esegue cancellazioni.

## Reinstallare mantenendo memoria e impostazioni
1. Chiudi tutte le finestre Jarvis e attendi che non stia scrivendo o inviando.
2. Copia in una cartella di backup privata %LOCALAPPDATA%\Jarvis e, se usato, %LOCALAPPDATA%\Jarvis-Telegram50-Trial. Conserva anche le cartelle dei documenti/progetti collocate fuori da questi percorsi.
3. Conserva il pacchetto e la versione precedenti. Non caricare il backup nel repository: contiene dati personali e file di autenticazione.
4. Estrai il pacchetto verificato nuovo in una cartella programma diversa.
5. Controlla che usi il profilo giusto. Il launcher di prova esaminato usa Trial; lo spostamento della cartella programma non cambia automaticamente il profilo.
6. Python/Node/Vosk/Telethon/FFmpeg già funzionanti non vanno reinstallati solo perché hai cambiato cartella programma.
7. Avvia, controlla impostazioni, progetti, memoria e account. Se lo stesso utente Windows conserva le credenziali, l'accesso potrebbe essere riutilizzabile; non è garantito su un PC o utente Windows diverso.

## Ripartire realmente da zero
1. Conserva comunque un backup privato e il vecchio pacchetto.
2. Individua il profilo che vuoi azzerare: base, Trial o entrambi. È una scelta esplicita, non va dedotta dal solo nome della cartella programma.
3. Con Jarvis chiuso, rinomina il profilo scelto invece di eliminarlo subito, aggiungendo per esempio -backup-20261101.
4. Ricorda che il Trial riusa SDK, account GPT e, quando disponibile, il modello voce del profilo base. Se vuoi ripartire da zero anche con quelli, deve essere incluso il profilo base; azzerare solo Trial non scollega l'account GPT condiviso.
5. Riapri il pacchetto verificato e segui dall'inizio Requisiti, GPT, Voce e Telegram, configurando il profilo corretto. Un nuovo Trial può copiare dal profilo base ancora presente: non è un reset totale se quel profilo rimane disponibile.
6. Su un altro PC o dopo reinstallazione Windows, prevedi nuovi login GPT/Telegram: le credenziali protette con DPAPI non sono semplicemente portabili. I documenti e gli altri dati hanno un trattamento diverso.

Non disinstallare Python/Node o cancellare cartelle di sistema come primo tentativo di riparazione: possono servire anche ad altri programmi.

## Tornare a una versione precedente
Chiudi quella nuova. Riusa il vecchio pacchetto con un profilo/database compatibile. Dopo una migrazione non fare aprire automaticamente un database nuovo a codice vecchio: ripristina coerentemente il backup della versione precedente. La copia Trial non riscrive da sola i database originali, ma gli account GPT possono essere condivisi.

## File importanti nel profilo
| File/cartella | Funzione |
|---|---|
| settings.json | Impostazioni, senza password |
| jarvis_workspaces.sqlite3 | Progetti e cronologia Telegram locale |
| second_brain.sqlite3 | Memoria generale e correzioni vocali |
| jarvis_preferences.sqlite3, jarvis_actions.sqlite3, tasks.db | Preferenze e registri/attività del motore |
| projects e documenti esterni | Continuità e artefatti dei progetti |
| telegram-auth.dpapi | Credenziali Telegram cifrate |
| gpt_account | Credenziali GPT cifrate nel profilo base |
| addons, addons-approvals.json | Registrazioni e autorizzazioni add-on |
| runtime\siwc, models | SDK e modello vocale |

Per un archivio SQLite copia il profilo a programma chiuso, oppure usa una procedura di backup SQLite coerente. Non mischiare file casuali tra profili per «riparare» un errore non identificato.

## Riferimento verificato per il ritorno
Base confermata Timer-Audio-Fix2 / b936879: [registro](../Download/REGISTRO-VERSIONI.md). L'audit confronta il DDL di second_brain.py e workspace_memory.py col successivo 5e61e53 e non rileva variazioni di schema in quel diff; non ha provato il ritorno su database personali. Conservare sempre una copia coerente del profilo della versione scelta. Riavviare la vecchia cartella non annulla automaticamente dati scritti dalla nuova.
