# Correzione contesto Gemma — 8 novembre 2026

## Richiesta e autorizzazione
Dopo l'audit della latenza, l'utente ha approvato la proposta con «Ok procediamo» e ha chiesto di preservare funzioni esistenti e configurabilità. Modifica al componente locale già presente; nessuna nuova add-on, dipendenza, processo o generazione di riassunto. Build e pubblicazione non sono autorizzate da questo passo.

## Comportamento e configurazione
- Nuovo **Token cronologia e ricordi (Gemma)** nel pannello Memoria e inattività: intero128–600, valore iniziale250. Salva lo applica alla richiesta successiva senza ricaricare il modello. Valori iniziali modifica i campi del pannello, richiede Salva.
- Il limite riguarda il contributo di storia+richiamo oltre domanda e istruzioni, non l'intero input. Finestra del modello, output riservato e margine rimangono separati e verificati col tokenizer reale.
- L'ultima coppia è protetta: se troppo lunga si usa l'estrattore locale esistente con il riferimento richiesto. Altre coppie entrano soltanto entro budget. Esclusione dal prompt non cancella né RAM né archivio.
- I dati richiamati variabili stanno nell'ultimo turno user prima della domanda attuale; istruzioni e storia precedente restano stabili. Catalogo, ID, validatori, sanitizzazione ruoli e controllo finale dell'adapter restano presenti.
- Il parametro legacy in caratteri non cambia valore o significato. `memory.json` conserva il vecchio schema; solo il nuovo budget è in `memory.native.json` nella stessa cartella del profilo. La lettura non riscrive i file; un sidecar assente usa250, uno invalido segnala errore. I salvataggi sono atomici per file, non una transazione multipla: dopo un errore di Salva correggere il problema e ripetere, senza assumere applicate tutte le preferenze.
- Telegram usa ancora il suo prompt isolato. Non modificati scelta GPT/Gemma, microfono, autorizzazioni, cancellazione, epoche UI, isolamento progetti o dati persistenti.

## File e scelte
`local_model/memory_preferences.py` conserva il campo e il sidecar; `native_conversation_session.py` applica budget/posizione; `memory_ui.py` espone il campo. Help in `local_model/README.md` e `docs/GEMMA-IMPOSTAZIONI-20261104.md`. Tests nel file `tests/test_native_prompt_policy.py`, integrati nella prova Windows esistente. Piano: [2026-11-08-gemma-prompt-budget.md](superpowers/plans/2026-11-08-gemma-prompt-budget.md).
Le impostazioni legacy non vengono riutilizzate con unità diverse. Nessun aumento automatico del contesto. Deduplica/ricerca archivio e nuova telemetria runtime rinviate: non necessarie alla correzione autorizzata.

## Prove osservate
- RED628e908/run42499660390:7test,2failure su budget/prefisso,4errori per campo API/UI assente; sanificazione ruoli già OK.
- Runtime58b8059: run42499942818SUCCESS,7test mirati con sessione/estrattore reali e inferenza catturata; UI Tk reale per Salva/Reset/validazione. Poi DLL e modello reali:1load,3generazioni,29/47/82token input corrispondenti al backend e riferimento tardivo ripristinato da SQLite. Nessun account, microfono o dato personale usato.
- Nativeperformance42499942823SUCCESS: stesso storico sintetico705token con limite600,349con limite250, due coppie recenti intere e riferimento preservato. Ricordo A/B con297token conserva276token di prefisso, contro205nell'audit prima della modifica. Non usare i tempi di runner diversi per stimare percentuali di accelerazione.
- Review indipendente in sola lettura: nessun difetto runtime bloccante individuato. Un gap di verifica è stato corretto: nuovo assert diretto contributo storia+ricordi<=budget usando tokenizer reale e riferimento tardivo anche con128. Recheck statico senza rilievi residui; Recheck Windows finale c91ebb5:focused e DLL42500290904SUCCESS; budget reale/prestazioni42500290988SUCCESS. Esiti dettagliati sotto.

## Limiti e consegna
Tutte le prove funzionali su Windows; nessun test Linux. Fixture e runner non sono Pavilion/Windows10/HDD/account reali. Nessuna garanzia di ritorno a30secondi o di assenza universale di bug. Serve collaudo PC a parità di modello, finestra e output effettivo dopo eventuale pubblicazione autorizzata.
La012 pubblicata resta invariata. Nessun nuovo ZIP o aggiornamento del PC. Stato corrente: sorgenti verificati su Windows, non nuova versione installabile.

## Esito finale della prova nativa e del recheck
Sorgente verificato c91ebb52293db078c9bb494925d4754ce3e85a2f; runtime invariato da58b80596fdd1033c6c3b4129e93cc91f84b3e9d2. [Contesto e impostazioni](https://github.com/MATRIXNEO23/jarvis/actions/runs/42500290904) SUCCESS:7test, incluso riferimento tardivo128/250, Salva/Reset/UI Tk e profilo. DLL/modello reali:1load/3richieste/3generazioni, tokenizer coerente con backend e ripristino SQLite/riferimento.
[Budget e prestazioni](https://github.com/MATRIXNEO23/jarvis/actions/runs/42500290988) SUCCESS:11richieste/11generazioni,1load,0selezioni durante generate. Il tokenizer reale verifica sia il limite fisico sia il contributo storia+richiamo, con stessa base istruzioni/domanda.

| Caso, stesso storico sintetico | Input completo | Contributo storia/ricordi | Limite configurato | Scambi interi | Omessi dal solo prompt |
|---|---:|---:|---:|---:|---:|
|Politica600|705|498|600|3|0|
|Politica250|349|142|250|2|1|

Il riferimento alla scatola blu è presente nel prompt ridotto. Gli scambi esclusi dal prompt non vengono cancellati dagli archivi. Il limite250non viene riempito forzatamente: gli scambi precedenti entrano interi oppure l'ultimo viene estratto, senza generare un riassunto. Richiamo A→B conserva276token comuni su297; il log del backend registra21token processati, contro92nell'audit precedente con richiamo in testa. I tempi di runner differenti non dimostrano lo stesso risparmio sul PC. Anche nel confronto della stessa esecuzione gli output differiscono (13/21token), quindi non presentare27,32→12,73secondi come percentuale controllata di accelerazione.

[Evidenze persistenti](evidence/gemma-bounded-context-20261108.json):quantità, tempi, provenance pubblica e dati di console senza conversazioni personali. Nessun file profilo o credenziale incluso. Review indipendente e recheck mirato conclusi senza rilievi residui; nessuna esecuzione Linux o modifica del revisore.

## Suite finale, consegna dei sorgenti e prossimo passo
[Run42500291039](https://github.com/MATRIXNEO23/jarvis/actions/runs/42500291039) SUCCESS sul sorgente c91ebb5:1006test OK per Windows/Python3.11(job128791362256) e3.12(job128791362277), più12controlli diagnostica/Tk. Lettura dei log e conteggi confermata; prove native42500290904/42500290988entrambeSUCCESS. Nessun errore nuovo da correggere, nessuna ripetizione ulteriore richiesta.
La suite include i percorsi esistenti voce/testo, progetti, GPT/Gemma, Telegram con confini rete/audio controllati, cancellazione e autorizzazioni. Questo non certifica account/microfono/hardware personali né ogni comportamento possibile. Il problema Telegram sul PC rimane quello documentato nell'handoff012, in attesa del rapporto reale; nessun altro fix Telegram viene dichiarato qui.
Ramo audit/native-prompt-performance-20261108, [PR59](https://github.com/MATRIXNEO23/jarvis/pull/59) draft:base fix/service-diagnostics-20261108. Sorgenti e prove salvati, nessun merge indiscriminato su main, nessun nuovo ZIP o pubblicazione Download. Prossimo passo eventuale build numerata soltanto su istruzione dell'utente, poi collaudo sul suo PC senza sovrascrivere012/profilo.

## Pubblicazione autorizzata
Nuova richiesta esplicita «Me la pubblichi?». In preparazione013dal sorgente76054b7; gate limitato PR59,1006test attesi per ZIP estratto,012immutabile e profilo preservato. Esiti e pubblicazione ancora da verificare.
