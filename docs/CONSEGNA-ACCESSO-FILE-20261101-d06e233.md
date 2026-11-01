# Consegna Accesso file — Jarvis-Accesso-File-0.1.0-20261101-d06e233.zip

Pubblicata in cima a Download su richiesta esplicita dell'utente. [Scarica ZIP](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Accesso-File-0.1.0-20261101-d06e233.zip). [Indice Download](../Download/README.md). Versioni precedenti conservate.

| Dato | Valore |
|---|---|
| Source | d06e233a98e4ea5b4e99a9d296b9570ce0c92d86 |
| Ramo di confezione | build/accesso-file-20261101-pass8 |
| Main della pubblicazione | 7d155e0d07e1593574ee1c9d83b8f6663d638f93 |
| Workflow | [41350638557](https://github.com/MATRIXNEO23/jarvis/actions/runs/41350638557) |
| Dimensione / contenuto | 266689 byte / 79 file |
| SHA-256 | ac130883d32518b430737f8f3d767a16a56e3cad9b3ae32f37d8f20799f42699 |
| Base PC preservata | Timer Audio Fix2, b936879 |
| Collaudo PC | Pendente sul pacchetto esatto |

## Contenuto
Comprende i passi verificati: risultati visuali e scelte vocali, navigazione relativa Explorer, avanzamento, raffinamento GPT di ricerca vuota con vincoli conservati, localizzazione da registrazioni/Store/App Paths/collegamenti e template del profilo corrente. Nessuna ricerca web ospitata o indice parallelo aggiunti. I sorgenti operativi, installazione/configurazione e LEGGIMI sono inclusi; strumenti, test ed evidenze di sviluppo restano nel repository.

## Prove effettive
466 test per Python 3.11.9 e 3.12.10 su Windows; sintassi Python/Node/PowerShell, probe nativo e indice Windows live PASS. Creazione ZIP, hash manifest, assenza file extra, launcher unico e import dal cwd estratto PASS. Altri 93 test (file, HUD, raffinamento, cartelle programmi) eseguiti dal pacchetto estratto PASS, quindi avvio/chiusura reale Tk in profilo temporaneo con servizi personali spenti PASS.
Publisher ha verificato artifact, CRC e hash prima di copiare in Download senza sovrascrivere altri ZIP. Dopo il push ha scaricato l'URL pubblico su Windows e ricontrollato byte/hash e prima voce Download/README. Metadata riletti da GitHub e coincidenti. [Evidenza completa](evidence/accesso-file-release-d06e233.json).

La prova non autentica il modello/account personale, non usa il microfono fisico e non misura consumi/desktop Pavilion. Il lancio Explorer è intercettato nei test; presenza del percorso e rispetto della policy sono verificati. Non dichiarare ogni app/launcher universalmente riconosciuto.

## Installazione e prima prova
1. Estrarre in una cartella nuova, mantenendo quella precedente.
2. Avviare soltanto avvia_jarvis.bat. Il profilo dati resta Jarvis-AccessoFile-Trial; dati e configurazione già presenti vengono conservati.
3. Accesso file deve essere attivo con radici consentite pertinenti. Se non era configurato: ingranaggio → Progetti e servizi → Gestisci add-on → Accesso file → Configura, Salva e Attiva.
4. Sul Pavilion fare una prova alla volta: chiedere la cartella di un programma effettivamente installato, verificare il percorso proposto e poi chiedere l'apertura. Distinguere directory dell'eseguibile, launcher e dati/salvataggi se resta un dubbio.
5. In caso di problema conservare messaggio e versione d06e233; chiudere il candidato e usare la cartella precedente senza cancellare profili.

## Confezione e continuità
Nessuna nuova funzione applicativa introdotta nella confezione: aggiornati workflow, checker e istruzioni per coprire l'app già verificata nel source d379368/checkpoint 5fe2dca.
Il connettore non espone dispatch e il checkout non ha credenziali CLI: avvio sul ramo di build dedicato autorizzato dalla richiesta dell'utente. Rimossa dopo la consegna l'eccezione di push del ramo; default nuovamente dispatch con build_candidate=true, nessuna futura pubblicazione da push ordinari. Mantenute le verifiche migliorate e il controllo HTTP del publisher.
Non rigenerare questo pacchetto senza un motivo concreto. Dopo feedback PC registrare versione, comportamento realmente provato e condizioni; finché manca, BASE-UTENTE resta b936879.
