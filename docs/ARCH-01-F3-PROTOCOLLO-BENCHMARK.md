# ARCH-01 F3 — protocollo pratico di misurazione sulla macchina Windows dell'utente

**Stato:** guida e diagnostica dei prompt su branch F3; non significa prove già effettuate su HP Pavilion. La raccolta inizierà quando una build esplicitamente autorizzata con F3 sarà provata sul PC.
**Motivo:** KoboldCpp standalone sembra più rapido di Jarvis 014 nonostante lo stesso Gemma 2 2B Q4_K_M, e la 014 riporta ~400–500 token processati (talvolta ~60–76s di prefill) con memoria. Non assumere che il Second Brain sia sicuramente la causa prima di misurare.

## Parametri da bloccare
- PC: HP Pavilion Intel i3-2100 (solo AVX), 10 GB RAM, Windows 10; stesso GGUF Gemma 2 2B IT e identica quantizzazione.
- Config Jarvis e standalone: Context Size=1024, Max Output=256, threads=2, BLAS threads=2, temperatura/seed/sampler/template/stop per quanto ragionevolmente comparabili; eseguire un solo modello GGUF alla volta.
- Conservare la configurazione 014 come riferimento, non modificare o cancellare database Second Brain/progetti/archivi. Memoria disattivata **solo come toggle temporaneo di prova**, senza cancellare i ricordi.
- Usare domande uguali, stesso ordine, locale già caricato; distinguere richieste cold/warm e numero/forma dei messaggi ripristinati. Ripetere almeno 2–3 volte se il risultato sorprende.

## Gruppi di prova (stesso prompt utente)
1. **KoboldCpp originale, chat Lite** senza storie di altre sessioni: domanda semplice `Cos'è un buco nero?`, poi `Approfondisci quello che hai appena spiegato.`, poi `Riesci a riassumere quanto detto?`.
2. **Jarvis Console 014, Second Brain off** con conversazione locale; compare prompt/count senza ricordi generali.
3. **Jarvis Console F3, Second Brain on** con archivi invariati; acquisizione manuale diagnostica prompt. Non ripetere sequenze con approssimazioni diverse senza annotarlo.
4. **Jarvis Chat locali F2+F3** nella stessa configurazione, prima chat nuova; ripetere su una seconda istanza nuova per verificare isolamento. Qui l'unica fonte storica per Gemma è `ChatSessionsStore` della chat scelta, senza Second Brain.
5. In caso di errori JSON, una richiesta *informativa* e una *operativa* distinte, per verificare se `intent_context` ha aggiunto catalogo di azioni. Non usare richieste che modificano file o inviano messaggi per un benchmark: basta testare il routing con richieste innocue e verificare la validazione.

## Come catturare provenienza e peso
- Aprire Impostazioni > Gemma locale > `Diagnostica prompt...` > `Acquisisci prossima domanda`.
- Inviare una normale domanda a Gemma, lasciarla terminare, poi `Aggiorna` nel pannello.
- Leggere modalità `CHAT` o `JSON`, origine di istruzioni/personality/scambi/ricordi, numero ripristinato, totale token, e stringa effettivamente serializzata.
- Il costo per componente è una **stima isolata**, non la ripartizione esatta del totale: il tokenizer può cambiare ai confini tra segmenti, includendo i delimitatori Gemma.
- I ricordi privati sono visibili nel report: **non pubblicare prompt integrali né chiavi, contatti, dati personali**. Condividere solo token/tipo fonte e una versione anonimizzata.

## Modello tabella risultati
| Caso | Condizione | Prompt token (report) | Processed token (log) | Process s | Generated token | Generated s | Totale s | Note qualità/contesto |
|---|---|---:|---:|---:|---:|---:|---:|---|
| A | KoboldCpp originale | | | | | | | |
| B | Jarvis Console, Brain off | | | | | | | |
| C | Jarvis Console, Brain on | | | | | | | |
| D | Jarvis chat nuova isolata | | | | | | | |
| E | Jarvis stessa chat + approfondimento | | | | | | | |

**Attenzione:** `Processed` è il numero di token effettivamente valutati in quella chiamata, che può variare col riuso del prefisso; `prompt token` è il totale serializzato. I due numeri non sono identici per definizione. La sola differenza dei secondi *Generated* senza conto dei token generati non prova un'accelerazione.

## Regole decisionali
- Se F3 Console Brain ON ha molti più token di Brain OFF, verificare quantità/doppioni e provenienza nel report. Non comprimere alla cieca.
- Se lo stesso prompt ripetuto in KoboldCpp Processed diminuisce ma in Jarvis no, indagare differenze di prefisso/cache prima di cambiare modello.
- Se Jarvis Chat locali è più rapido ma perde riferimenti, la riduzione del contesto NON supera il gate qualità.
- Qualsiasi proposta di ottimizzazione è un'altra fase con nuovo branch, test + comparazione, rollback e approvazione; F3 non altera prompt, database o modello.

**Sicurezza:** F3 non richiede server esterno, chiavi API, impostazioni online o un secondo modello. I provider API gratuiti restano F8, non inclusi.
