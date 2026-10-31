# JARVIS — correzione dei progetti e diagnosi del programma

## Correzione nome e recupero

Archivio locale: %LOCALAPPDATA%\Jarvis\jarvis_workspaces.sqlite3
Cartelle: %LOCALAPPDATA%\Jarvis\projects\<UUID>

Comandi supportati da voce e casella chat senza necessità di GPT:
- «Jarvis, quali progetti ho salvati?»
- «Jarvis, rinomina il progetto corrente in Minecraft»
- «Jarvis, rinomina il progetto NomeSbagliato in Minecraft»
- «Jarvis, rinomina il progetto» → domanda successiva sul nuovo nome
- «Jarvis, elimina il progetto» → richiesta di conferma «confermo»
- «Jarvis, elenca i progetti eliminati»
- «Jarvis, ripristina il progetto NomeSbagliato»

Rinomina conserva UUID, cartella, storico SQLite, documenti, file e
continuità. Aggiorna il nome anche in PROGETTO.txt, CONTINUITA.md e STATO.json.

Elimina è **solo cestino logico recuperabile**: non cancella file o righe
della cronologia, toglie soltanto il progetto dall'elenco e dalle orbite.
È necessaria una seconda frase chiara «confermo»; una semplice frase vaga
come «sì» non basta. «Annulla» ferma la richiesta. Il gestore visivo ha
pulsanti Rinomina, Elimina (cestino), Mostra cestino e Ripristina.
La cancellazione permanente NON è implementata.

Se Jarvis non legge il suo database, deve dire che la memoria non è
disponibile, e non affermare che non esistono progetti.

## Diagnosi del proprio codice (solo lettura)

Frasi: «Jarvis, dove sono i tuoi file», «Jarvis, analizza il tuo codice»,
«Jarvis, analizza workspace_memory.py», «Jarvis, suggerisci correzioni
al tuo codice».

L'analisi è limitata, statica e offline: elenco dei file sorgenti
disponibili, controllo di sintassi AST dei moduli Python senza esecuzione,
individuazione dei moduli chiave, elenco delle funzioni/classi principali
e dei test presenti, segnalazione di errori di sintassi o file assenti.
I risultati sono mostrati nel registro e sintetizzati a voce.

NON è una prova di funzionamento del runtime né una code review completa
e non certifica la sicurezza antivirus. Non esegue test, codice, comandi
shell o modifiche; non legge database, configurazioni con credenziali e
non invia i sorgenti a un modello remoto. Nessuna API a consumo.

## Politica sulle modifiche, confermata dall'utente

In futuro l'automodifica potrebbe diventare possibile su richiesta
esplicita e con adeguati test/isolamento/backup/rollback. PER ORA Jarvis
deve soltanto analizzare e proporre, mentre ChatGPT eseguirà le correzioni
esplicitamente richieste dall'utente in branch isolati. Non introdurre
auto-patching, auto-update o auto-merge senza nuova decisione separata.

## Test e sicurezza del download

CI Python 3.11 e 3.12 su Linux e Windows. Sul Pavilion servono ancora
verifiche reali del microfono e del recupero dati. Prima di una futura
prova fare backup dell'intera cartella %LOCALAPPDATA%\Jarvis.

Distribuzione ZIP sospesa per segnalazione Microsoft Defender
Trojan:Script/Wacatac.B!ml sul pacchetto precedente: nessuna whitelist,
eccezione antivirus, disattivazione della protezione o aggiramento.
