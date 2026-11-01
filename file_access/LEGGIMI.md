# Accesso file — candidato 0.1.0

Windows 10 x64, stessa base Timer Audio Fix2 b936879. Nessun pacchetto Python aggiuntivo, nessun modello o scanner residente. Nuovo codice: windows.py (API e ricerca Windows), policy.py (scelte cartelle), service.py (operazioni e dialogo), ui.py (configurazione/lettura). Manifest AccessoFile.jaddon; windows_search.ps1 fisso per l'indice. Il programma usa ancora il gestore add-on e il motore di Jarvis.

## Attivazione
1. Avvia Jarvis dalla nuova cartella, senza sovrascrivere quella funzionante.
2. Impostazioni → Gestisci add-on → Installa: scegli file_access/AccessoFile.jaddon. Rimane SPENTO.
3. Seleziona Accesso file → Configura: spunta un disco/cartella o Aggiungi cartella. Espandi solo per escludere zone. Salva.
4. Torna al gestore e attiva Accesso file.

Dati: cartella addon-data/accesso_file nel profilo già scelto da Jarvis (normalmente LOCALAPPDATA/Jarvis, oppure JARVIS_TRIAL_HOME). folders.json contiene identità delle cartelle/volumi e scelte. Non spostare o cancellare le preferenze precedenti. Disattivare non cancella configurazione o documenti; revoca risultati e attività pendenti. Per annullare una modifica non salvata chiudi Configura. Togli regola rimuove la sola eccezione/inclusione dalle impostazioni, non una cartella dal disco.

## Comandi
Gli elenchi e i risultati di ricerca/localizzazione restano in chat, senza lettura vocale automatica di nomi e percorsi. Selezione e apertura hanno soltanto una conferma breve; la normale voce conversazionale resta disponibile. Per aprire una cartella dall’elenco recente usa «apri cartella NUMERO», anche pronunciando «uno», «due», «numero tre» e così via fino a venti; se i risultati sono scaduti, ripeti prima l’elenco.
«Cerca file preventivo», «trovami cartella salvataggi», «elenca cartella documenti», «leggi file 1», «spiega file 1», «apri cartella 1», «annulla ricerca», «cosa puoi fare?». «Il secondo» seleziona il secondo risultato per 120 secondi, poi «leggi file selezionato». Nome/percorso diretto possibile, sempre controllato dalla stessa policy. Le parafrasi non riconosciute passano al GPT esterno nelle modalità che già lo consentono. Le chiacchiere non devono eseguire azioni.

I file aperti da questa versione sono mostrati internamente senza modifica: TXT, MD, JSON, LOG, CSV, INI, YAML/YML in UTF-8/UTF-16, massimo 256 KiB. PDF/Office/eseguibili non sono letti o avviati. Le cartelle si aprono con Esplora file; l'accettazione della richiesta non prova la visibilità della finestra. «Spiega file» invia solo un estratto al GPT esterno già collegato, come dati; dichiara che è un estratto. «Leggi file» mostra il testo localmente, senza inviarlo automaticamente al modello.

Ricerca: prima indice Windows quando risponde, poi ricerca diretta (prima le cartelle personali reali consentite) con limite 5000 elementi/10 secondi per passata e 20 risultati. La risposta dichiara ricerche parziali; ripeti con un indizio/ambito più preciso. Le cartelle escluse non producono risultati. Junction/reparse point non sono attraversati nelle scansioni; una cartella reindirizzata può essere selezionata tramite il suo percorso reale. Cartella/volume sostituito non eredita automaticamente il consenso. Unità di rete/MTP non dichiarate supportate.

Le registrazioni Windows danno indizi sulla cartella d'installazione di un programma; i candidati non garantiscono di individuare tutti i dati/salvataggi di ogni app. Nessuna promessa di ricerca semantica universale. Altre estensioni restano documentate nella scheda WINDOWS su main.

## Errori e recupero
Se manca file_access/windows_search.ps1 o la cartella del componente, reinstalla questo pacchetto completo. Se l'indice Windows non risponde, Jarvis usa la ricerca diretta: non occorre installare un altro indicizzatore. Le spunte non cambiano ACL/UAC; accesso negato resta negato. Per tornare alla base usa lo ZIP Timer Audio Fix2 conservato in Download; non cancellare il profilo dati. Questa versione non modifica i file cercati e non cambia la modalità microfono della base.

## Verifiche
Solo Windows: suite progetto, tests/test_file_access.py e probe tools/probe_file_access_windows.py. Fase nativa iniziale run 41319370085: API note/percorsi/volumi PASS, indice non disponibile nel runner (non collaudo positivo dell'indice). Aggiornamenti e prove successive in docs/ACCESSO-FILE-STATO.md. Microfono/account GPT reali, prestazioni Pavilion e qualità semantica non sono coperti da simulazioni.

Localizzazione: registrazioni classiche e pacchetti Store dell’utente corrente (Get-AppxPackage, nome Start da Get-StartApps). windows_shell.ps1 è un helper finito con JSON su stdin e timeout, non un servizio residente. Installazione registrata resta distinta da cartelle trovate per nome e dati del programma; nessuna garanzia per installazioni portabili o launcher non registrati.

Quando un’apertura o lettura ha prodotto più risultati, puoi rispondere con il nome esatto di una voce (maiuscole e spazi normalizzati) oppure con il numero: viene ripresa la stessa richiesta. Nomi duplicati richiedono il numero; elenchi scaduti, sostituiti o revocati non riprendono la vecchia azione. La scelta non crea una ricerca generale nuova. Questa correzione non aggiunge ancora il rilevamento della cartella Explorer corrente.
