# JARVIS — memoria affidabile e provenienza, fase 1

## Obiettivo

Tre ambiti separati, che non possono autorizzarsi a vicenda:

1. **Preferenze esplicite dell'utente**
   - File: %LOCALAPPDATA%\Jarvis\jarvis_preferences.sqlite3
   - Solo valori controllati e salvati DOPO «confermo»:
     lunghezza delle risposte, lingua di risposta, stile di interazione.
   - Nessuna estrazione automatica di preferenze da normali conversazioni,
     citazioni, testi di file o suggerimenti del modello.
   - Nuovo comando «Jarvis, ricorda che preferisco risposte brevi»;
     Jarvis deve chiedere conferma. «Mostra preferenze» elenca,
     «Dimentica preferenza risposte» richiede conferma prima di eliminare.
   - Una preferenza «voce» cambia soltanto il contesto conversazionale;
     NON attiva il microfono e non scavalca la scelta manuale di standby.

2. **Stato e documenti dei progetti**
   - File database: %LOCALAPPDATA%\Jarvis\jarvis_workspaces.sqlite3
   - Cartelle immutate: %LOCALAPPDATA%\Jarvis\projects\<UUID>\
   - Nome, stato, cronologia di progetto, step, artifact e file restano
     isolati per UUID: le preferenze globali non diventano contenuto di un
     progetto, né il contenuto di un progetto diventa memoria globale.
   - Aggiunta colonna additiva verified a project_steps; prima versione
     delle proiezioni è conservata e vengono rigenerati CONTINUITA.md,
     PASSI.md e STATO.json schema v2. Nessuna cancellazione dei precedenti.
   - **Completato ma non verificato:** registrazione di esito del programma
     che non prova il comportamento esterno; tale condizione è esplicita.
     Un passaggio a completed non basta a farlo diventare verified.

3. **Cronologia operazioni ed evidenze**
   - File: %LOCALAPPDATA%\Jarvis\jarvis_actions.sqlite3
   - Stato: requested → running → verified, reported, failed,
     interrupted oppure uncertain.
   - Registrazione prima della chiamata locale. Una richiesta non eseguita
     non diventa «completata».
   - Il lancio di un'applicazione o l'apertura di browser è **reported**:
     subprocess o browser hanno risposto, ma non è provato che la finestra
     sia effettivamente utilizzabile.
   - Una lettura locale con ID di esecuzione valido e risultato diretto
     può essere **verified** (es. lettura RAM/elenco Download). Il
     salvataggio TXT diventa verified solamente quando il file è realmente
     presente sul disco. Ciò verifica la presenza del file, non una
     validazione completa e indipendente del suo contenuto.
   - Al riavvio, operazioni lasciate requested/running diventano
     interrupted, senza ripetizione automatica né promozione a success.
   - Il vecchio tasks.db del motore locale è conservato intatto.

## Conversazioni e memoria storica

- second_brain.sqlite3 conserva gli scambi in un archivio distinto e i
  receipt legacy in una tabella diversa. NON esegue mai vecchi comandi.
- Un nuovo campo proof_kind nei receipt tratta i vecchi record senza
  prove classificate come legacy_unassessed, non come VERIFIED.
  Non vengono eliminati; restano consultabili come reported_action.
- Solo ricevute con prova esplicita possono essere mostrate come
  verified_action. Il numero di azioni verificate sullo schermo esclude
  quelle legacy non valutate.
- Le preferenze confermate entrano nel prompt come dati controllati,
  distinguibili da progetti, scambi e azioni; NON sono istruzioni con
  autorità per eseguire operazioni.
- Cancellare la vecchia memoria conversazionale non cancella
  automaticamente le preferenze nel loro archivio separato.
- Non è stato aggiunto alcun servizio a pagamento, modello in locale,
  telemetria o automatismo di esecuzione.

## Sicurezza e rollback

- Prima del collaudo sul Pavilion fare backup COMPLETO dell'intera
  %LOCALAPPDATA%\Jarvis con tutte le sottocartelle.
- Le migrazioni sono additive; nessun file, progetto o record di storico
  viene eliminato per correggere i dati precedenti.
- Mai avviare contemporaneamente due versioni di Jarvis che condividono
  gli stessi database.
- **Collaudo reale rinviato dall'utente:** al momento soltanto CI e test
  unitari. In seguito provare memoria dopo riavvio, nome progetto,
  preferenze con conferma, richiesta/esito verifica operazioni e
  distinzione fra finestra avviata e file realmente scritto.
- Rimane irrisolto il precedente avviso Microsoft Defender sul vecchio ZIP
  Trojan:Script/Wacatac.B!ml. CI e test unitari non certificano sicurezza.
  Non disattivare antivirus, non forzare download, non creare esclusioni.
