# Gemma locale — checkpoint in corso, 4 novembre 2026

Autorizzazione: utente richiede pianificazione e installazione/integrazione per lo scopo; chiarisce motore tipo Kobold integrato come add-on, CPU/RAM configurabili, modello residente, unica console Jarvis. Online interruttore e conferma per ogni inferenza. Non chiedere di nuovo queste decisioni.

Base verificata via Git: build/jarvis-005,7203fef3357cb880161d20dd5304ccee92a0c0bb. Nuovo ramo feature/gemma-local-20261104. Nessuna modifica delle copie locali precedenti release-work/voice-work e dati utente. Main radice storica non usata. Letti RECUPERO, AGENTS correnti main, indice sorgenti, handoff/lezioni e implementazioni mirate. Ramo005 ha documenti storici con intestazione004: sorgente/005 verificati separatamente.

Documenti: GEMMA-LOCALE-SPEC-20261104.md e superpowers/plans/2026-11-04-gemma-locale.md. Piano riesaminato prima del codice. Adattatore progettato per riuso delle azioni già presenti; niente framework/servizi a pagamento. Accuratezza Gemma non dimostrata in generale; precisazione successiva utente: richiesta esplicita di apertura immediata, proposta indiretta da chiarire. Test soltanto Windows.

Stato: pianificazione pronta; Task1 e2 da iniziare con test e stub comportamentale. Nessun test nuovo eseguito, nessun modello reale chiamato da questo ambiente, nessun pacchetto006 creato. Prima modifica prevista local_model/* e test; pubblicare red Windows, poi implementare. Mancata clonazione iniziale risolta: clone completo gemma-work disponibile; jarvis/.git precedente era incompleto e non usato.

Task1/2 RED pronto: stub ModelService.call non esegue richieste; sei test di comportamento chiedono routing/consenso e devono fallire su asserzioni osservabili, non import. Workflow Windows local-model.yml separato, nessuna build. Scelta utente: apertura esplicita immediata se autorizzata; indiretta da chiarire.

## Blocco prima del RED Windows

La revisione automatica ha rifiutato git push: destinazione pubblica e autorizzazione alla pubblicazione non considerata esplicita. Non aggirare il rifiuto con GitHub API o altri trasporti. Nessun test Windows nuovo eseguito; il RED è atteso, non osservato. Non continuare implementazione dipendente dal test fino al via alla pubblicazione e al riscontro CI. Il tool create_branch, già chiamato prima di ricevere il rifiuto, ha creato feature/gemma-local-20261104 dalla005 senza questi file; non considerarlo checkpoint pubblicato. Nessuna build/pacchetto006.

Modifica da approvare: piano, specifica, handoff, rimandi nei tre documenti di continuità, stub innocuo ModelService.call (nessun processo/inferenza), sei test Windows e workflow dedicato; nessun peso, binario, credenziale, log personale. Un commit locale e i suoi edit successivi sono presenti; verificare diff prima di riprendere. App005 e dati non modificati. File di revisione GEMMA-PROPOSTA.patch nel checkout, creato da git diff della base005. La pubblicazione serve prima ai test e alla continuità, non installa nulla sul PC.
