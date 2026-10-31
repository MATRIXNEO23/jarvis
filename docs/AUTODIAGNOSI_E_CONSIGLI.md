# Jarvis — autodiagnostica e proposte di miglioramento

## Obiettivo

Jarvis deve poter ispezionare esclusivamente il proprio codice installato e
dare all'utente consigli motivati da elementi verificabili. Non deve creare
falsi allarmi, sostenere di aver dimostrato un difetto con la sola lettura del
codice, né apportare autonomamente modifiche o eseguire parti del programma
come test. L'utente preferisce affidare le correzioni a ChatGPT dopo avergli
comunicato le raccomandazioni.

## Comandi voce/chat

- «Jarvis, fai un'autodiagnosi»
- «Jarvis, autoanalizzati»
- «Jarvis, come potresti migliorarti?»
- «Jarvis, consigliami come potresti migliorarti»
- «Jarvis, suggerisci miglioramenti al tuo codice»
- «Jarvis, analizza il tuo codice»
- «Jarvis, analizza self_diagnostics.py» (singolo modulo)
- «Jarvis, dove sono i tuoi file?»

Il risultato viene mostrato nella cronologia della finestra Jarvis;
può essere copiato e incollato in ChatGPT per decidere quali modifiche
implementare. La risposta vocale riassume il numero di possibili miglioramenti
e illustra soltanto il primo, evitando letture interminabili.

## Che cosa può verificare

- Inventario limitato dei file sorgenti nella cartella dell'installazione e
  nella cartella test Python; controllo sintattico AST senza eseguire/importare
  alcun file.
- Elenco delle funzioni principali di un modulo e presenza dei moduli chiave.
- Segnalazioni prudenti di funzioni molto lunghe o ramificate, moduli estesi,
  eccezioni che potrebbero essere ignorate, chiamate shell=True da verificare.
- Fino a 8 raccomandazioni selezionate, con livello di priorità, file e
  numero di riga, indizio, proposta tecnica e test necessario a confermarla.
  Vengono limitate le segnalazioni provenienti dallo stesso file per non
  oscurare altre aree.

## Che cosa NON può dimostrare

- Che una funzione lavori davvero sul Pavilion, che Windows/Notepad/Telegram
  rispondano correttamente, che un bug suggerito esista realmente, o che
  l'applicazione sia sicura da malware.
- Non esegue unit test autonomamente, non importa moduli del programma, non
  installa librerie, non si collega a GitHub, non chiama GPT, non invia codice
  o dati su Internet.
- Non ispeziona database locali, Telegram, credenziali, file JSON di
  configurazione, documenti dei progetti, cartelle esterne o symlink.
- Non applica patch, non esegue Git, non sostituisce file, non si autoaggiorna.

Tutte le raccomandazioni sono ipotesi statiche. Devono essere valutate con
test riproducibili e, solo dopo una richiesta dell'utente, implementate da
ChatGPT su un ramo isolato con possibilità di rollback.

## Verifiche di regressione

La suite tests/test_self_review.py controlla gli intenti espliciti, il
rapporto file/riga/priorità, il limite massimo delle raccomandazioni, lo
scoping di singoli moduli, l'assenza di esecuzione di codice o perdita di
segreti e la gestione delle cartelle fuori dall'installazione.

Collaudo reale sul Pavilion rinviato: quando si farà, usare una sola
istanza, pronunciare «Jarvis, fai un'autodiagnosi», leggere il rapporto,
copiarlo in ChatGPT, poi verificare se gli indizi sono reali. Nessuna
integrazione automatica di correzioni.

Avviso antivirus: la segnalazione del precedente pacchetto Defender
Trojan:Script/Wacatac.B!ml resta non verificata e non risolta. CI
verde e controllo AST non dimostrano che uno ZIP sia privo di malware.
