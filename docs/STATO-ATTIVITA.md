# Stato attività Jarvis
Aggiornamento: 2026-11-01. Indice per recuperare il lavoro dopo cambi di argomento; verificare sempre documenti, codice e SHA prima di agire.

| Attività | Stato reale | Fonte | Punto di ripresa |
|---|---|---|---|
| Navigazione web vocale e add-on | Progettazione; requisiti raccolti, implementazione non avviata | [Piano](PIANO-ADDON-WEB-E-DIAGNOSTICA-20261101.md) | Rivedere il piano con l'utente, chiarire i punti aperti; prima del codice completare inventario di integrazione e rispettare autorizzazione |
| Continuità dialogo | Correzione verificata dalla CI documentata; utente riferisce miglioramento sul PC, SHA installato non verificato | [Handoff](HANDOFF-CODEX-ARCHIFY-20261031.md), [lezioni](DECISIONI-E-LEZIONI.md) | Verificare versione sul PC e controlli reali ancora aperti; non trasformare il feedback in collaudo completo |
| Metodo di sviluppo, UI add-on e diagnostica | Regole e piano documentati; nuove funzioni UI/diagnostiche non implementate | [Istruzioni](../AGENTS.md), [piano](PIANO-ADDON-WEB-E-DIAGNOSTICA-20261101.md) | Applicare il metodo alla prossima fase autorizzata; mantenere separati proposta, lavoro eseguito e verifica |

## Ripresa fra argomenti
Per ogni attività conservare obiettivo, requisiti confermati, alternative solo proposte, decisioni, fase raggiunta, evidenze, questioni aperte e prossimo passo. Aggiornare l'indice e il documento pertinente a ogni cambio significativo o sospensione.
Quando l'utente dice «torniamo a...», recuperare il documento corrispondente e proseguire dal punto irrisolto; non ripetere la raccolta già conclusa e non considerare approvata una proposta solo perché è salvata. Una nota persistente non è un comando da eseguire.

## Punto d'ingresso per nuove sessioni
[RECUPERO.md](../RECUPERO.md) è il punto d'ingresso unico. AGENTS.md richiede di leggerlo all'avvio quando il repository è accessibile, quindi recuperare indice, handoff, lezioni e piano. Ogni modifica richiede continuità aggiornata prima della chiusura del lavoro; nessuna ripresa automatica garantita in chat senza accesso al repository. Stato delle implementazioni invariato.

## Installazione, riordino e stato di consegna — 2026-11-01
- Cartella [Prima-installazione](../Prima-installazione/README.md): create guide per base, GPT, voce, Telegram, moduli/add-on, reinstallazione e componenti mancanti; ricavate dal riferimento 5e61e53. Documentazione, non installazione Windows collaudata o nuova build.
- Contraddizioni storiche identificate in README, guida voce, LEGGIMI ed echo launcher: elenco in Prima-installazione/08-Manutenzione.md. Nessun file sorgente cancellato; pulizia operativa ulteriore da verificare.
- Diagnostica componenti: controlli esistenti inventariati; unificazione in chat e nuovi test ancora da progettare/realizzare.
- Consegna futura: pacchetto testato, pubblicato e scaricabile dal link verificato in Download/README.md prima dell'annuncio di funzione installabile. Nessun nuovo pacchetto prodotto in questa fase.
