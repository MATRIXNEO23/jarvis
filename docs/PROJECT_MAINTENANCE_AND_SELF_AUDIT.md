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
# Inventario statico: correzione014 in bozza

La diagnosi generale include i file diretti della radice e il codice nelle
cartelle `local_model`, `file_access`, `program_apps` e `sveglia`, comprese le
sottocartelle consentite. I test diretti della cartella tests vengono dopo il
runtime. Il controllo resta statico: non importa o esegue i file e non avvia
test, modelli o richieste GPT da solo.

Limiti:140file,140directory enumerate e260000byte per file. Raggiungere un
limite significa copertura parziale e viene segnalato anche se ci sono molti
altri errori. Un modulo non trovato nell'inventario non viene dichiarato
inesistente nel programma. Il selettore esplicito continua ad accettare i nomi
Python semplici della radice; questa correzione non aggiunge nuovi comandi.

Restano esclusi profili/dati configurati, cache, modelli, upstream, cartelle
nascoste sotto la radice esplicita (nomi con punto o attributo Hidden Windows),
link e junction, anche se puntano dentro l'installazione. Se codice e cartella
dati coincidono o il codice è dentro il profilo configurato, l'inventario viene
escluso con spiegazione. Non spostare o cancellare dati per aggirare il limite.

Errori di metadati, file spariti e directory non leggibili non interrompono il
controllo degli altri sorgenti. Le raccomandazioni sono segnali da verificare,
non una certificazione di assenza di bug o un audit universale di ogni lingua.
Il controllo non è una sandbox contro sostituzioni concorrenti malevole del
filesystem. Nessuna nuova dipendenza, scansione globale o attività residente.

Correzione014 verificata nei sorgenti:852test per Python3.11/3.12 su
Windows2022, run42357790841, con23nuovi controlli inclusi junction/Hidden/8.3
reali e copertura dei moduli del checkout. Nessuna nuova build installabile.
