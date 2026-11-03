# Prompt: omettere la memoria realmente vuota — 4 novembre 2026

Autorizzazione: «se è chiara la correzione procedi», dopo audit dei consumi. Incremento prudente concordato in aggiornamento: eliminare soltanto il blocco contesto semanticamente vuoto; mantenere personalità, regole operative e ricordi. Nessun taglio ancora a stile/catalogo, nessuna cancellazione memoria o nuova build automatica.

Base corretta: c08317da300adfbfc7b5896ce1f8706e374b33aa, che conserva la protezione «Jarvis» verificata su Windows. Ramo isolato fix/empty-prompt-context-20261104. Il root storico di main non è la base runtime.

Causa: build_conversation_prompt allega il blocco se la stringa raw è non vuota, anche quando compact_memory produce solo recent/evidence vuoti. build_chat_prompt lo allega anche senza contesto raw. Il controllo deve avvenire DOPO la compattazione/validazione reale, senza confondere assenza di chat recente con assenza di preferenze, progetto, domanda, file, avanzamento o prove.

Piano: riproduzione Red Windows sui payload reali; condizione minima nei due builder, invariata compact_memory e invariati i dati memorizzati; Green completo Windows3.11/3.12. Misura offline prima/dopo sui builder reali, inclusi confronti identici per contesti utili. Zero chiamate modello; distinguere lunghezza UTF-16 da token/usage/quota. Nessuna promessa percentuale sulla quota e nessun nuovo add-on, processo o SDK per una correzione esistente.

Red Windows osservato: source e3365c153a86282ac923e8bbaed6488992ea70fe, run41737236373, 4 test, 25 asserzioni fallite, zero errori. I payload contengono il blocco vuoto; le prove sui contesti utili passano. Ora modifica minima nei due builder: allegare contesto soltanto se il JSON già compattato ha almeno un valore utile. Il vecchio controllo della regola sulle email ora usa un ricordo reported_action concreto, anziché un oggetto vuoto: la protezione resta verificata quando ci sono dati da trattare come non attendibili. Prossimo passo: Green Windows completo e misura comparata con la base reale tramite git show, zero inferenze; poi aggiornare handoff.

## Misura Windows prima/dopo conclusa

Source ace23025780e1af1c42907e95ecadca706ecbe73, [run mirata41737540613](https://github.com/MATRIXNEO23/jarvis/actions/runs/41737540613) SUCCESS: 4 test e confronto con i moduli reali della base c08317d caricati tramite git show. Windows Python3.12, dati sintetici, nessun account o dato utente, zero inferenze.

| Caso sintetico con domanda breve e stato runtime | Prima | Dopo | Testo in meno |
| --- | ---: | ---: | ---: |
| Voce/router, memoria del profilo vuota | 3815 | 3589 | 226 |
| Chat pura, nessun contesto raw | 2268 | 1814 | 454 |
| Chat pura, memoria del profilo vuota | 2293 | 1814 | 479 |
| Voce con programmi e file attivi, memoria vuota | 4889 | 4889 | 0 |

Unità UTF-16 del bridge, NON token del modello o quota personale. Il risparmio non vale per ogni richiesta: nell’ultimo caso il vecchio builder aveva già escluso il blocco per mancanza di spazio. Anche la chat pura non è il percorso ordinario di ogni frase vocale; non attribuire il suo risparmio al router operativo. Quando il contesto è utile il testo viene mantenuto, senza promettere minore consumo.

Quindici confronti con dati utili danno payload identici alla base: chat recente, preferenza sola, progetto solo, risultati file soli, prova verificata sola, avanzamento solo, domanda sola, entrambe le modalità e caso voce con add-on. Personalità e regole operative rimangono le stesse; le regole relative ai ricordi viaggiano quando ci sono ricordi da interpretare. Nessun file memoria cancellato, nessun nuovo modello/processo/SDK.

Regressione completa [Windows41737540692](https://github.com/MATRIXNEO23/jarvis/actions/runs/41737540692) SUCCESS sul source ace23025780e1af1c42907e95ecadca706ecbe73. Python3.11/job126270490071: 558 test OK in91.796s; Python3.12/job126270490229: 558 test OK in123.422s. Sintassi Python/Node/PowerShell, probe nativo e indiceWindows live PASS; servizio e fixture ripristinati. La protezione del richiamo «Jarvis» è conservata e coperta dalla regressione. Build/controllo ZIP/artifact installabile/publisher SKIPPED.

Stato conclusivo: correzione implementata e verificata nei sorgenti, dati e ricordi conservati; nessun test funzionale Linux, inferenza di prova, account personale o collaudo microfono/Pavilion. L’installazione004 non viene aggiornata: prossima build soltanto su richiesta esplicita e con verifica ZIP estratto. Riduzioni di stile/catalogo o deduplica della memoria restano proposte separate, senza modifiche speculative.
