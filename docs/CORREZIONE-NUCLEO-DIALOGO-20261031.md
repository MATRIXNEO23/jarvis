# Correzione nucleo conversazionale — 31 ottobre 2026

Piano approvato dall'utente con «Sì», dopo la richiesta esplicita di conferma. Base: d332c10aed102c671841f2e45fcee73939b15b83, ramo feature/timer-settings-ui-20261031. Nessun merge della vecchia radice main e nessun nuovo add-on.

## Comportamento corretto
- conversation_context.py raccoglie record locali limitati, senza compattarli in anticipo. Recupera gli ultimi scambi SQLite anche con domande brevi e riavvio; per i progetti resta nella partizione selezionata. Nessuna migrazione di schema.
- La sovrapposizione tra coda persistita e RAM viene eliminata confrontando i prefissi che i vecchi archivi possono effettivamente contenere; i turni ripetuti fuori da tale sovrapposizione restano. Le differenze oltre i limiti originali di salvataggio non sono ricostruibili: questo non è un confronto semantico.
- Il costruttore del prompt applica una sola selezione finale: stesso livello di dettaglio per la finestra recente, con estratti iniziali/finali, domanda pendente separata e cataloghi opzionali subordinati alla riserva di memoria. Le istruzioni ripetitive sono state abbreviate conservando stile e contratti delle azioni.
- Il limite del bridge resta 5000 unità UTF-16: conteggio compatibile con Node, compresi emoji ed escaping JSON. Nessun aumento indiscriminato del prompt o chiamata aggiuntiva a GPT.
- Domande finali in risposte lunghe vengono conservate nella RAM e nei campi SQLite esistenti; gli archivi precedenti restano leggibili. Un vecchio testo già troncato non può essere recuperato retroattivamente.
- Un sì/no dopo il riavvio usa il chiarimento reale recuperato. Un'azione successiva annulla il riferimento a una vecchia domanda. Memoria e focus restano dati: non autorizzano comandi.
- Testo breve e voce hanno lo stesso timeout di 180 secondi; prima il testo breve riceveva 40 secondi.
- Avvio microfono sempre standby: il saluto differito non cambia una modalità già selezionata manualmente. La vecchia preferenza auto_listen resta salvata ma il controllo di avvio automatico è sospeso e indicato in UI. Il preparatore del profilo non forza più auto_listen=True, neppure se manca il vecchio marcatore. Nessuna cancellazione di impostazioni o salvataggi.

## Verifica locale
Python 3.12.14, Node 24.22.1: 386 test OK, 5 test Windows saltati; compileall, node --check e git diff --check PASS.

13 nuovi test verificano payload finali, dieci turni con riferimenti iniziali/intermedi, riavvio con SQLite reale, compatibilità permanente.recent, cataloghi pieni, Unicode/escaping, domande in coda, sovrapposizioni, cambio argomento/progetto, separazione memoria generale, assenza di autorizzazioni dalla cronologia, callback reali fino alla chiamata client e controllo manuale microfono. Lo smoke Windows è attivato sulla PR senza autenticazione o richieste al modello.

## Errori trovati e scartati durante questa fase
- Il primo passaggio sottostimava emoji/escaping: test di confine falliti, corretti usando UTF-16 e abbreviando istruzioni ridondanti.
- Il primo salvataggio di una domanda finale aggiungeva un frammento iniziale al focus: test di riavvio fallito, corretto riconoscendo il separatore di omissione.
- Non usare l'aumento dei soli limiti RAM come prova di miglioramento: verificare i dati nel payload finale.

## Limiti
La verifica automatica dimostra il trasporto del contesto, non la qualità semantica delle risposte GPT. Necessario collaudo con account collegato e hardware Windows 10/Pavilion. La selezione resta limitata (fino a dieci turni nel prompt, secondo spazio disponibile); non è una memoria illimitata. Nessun nuovo ZIP distribuito in questa fase. Risultati CI e commit registrati nell'handoff autorevole su main.
