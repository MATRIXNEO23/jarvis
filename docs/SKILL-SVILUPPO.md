# Skill per lo sviluppo — nota riutilizzabile

Aggiornamento: 3 novembre 2026.

Queste skill guidano l'assistente durante lo sviluppo. Non sono add-on di Jarvis, non modificano il modello e non sono componenti da includere nello ZIP dell'applicazione. Sono installate come skill personali e conservate qui anche come copie versionate riutilizzabili.

## Le quattro skill

| Skill | Quando usarla | Risultato cercato |
|---|---|---|
| [Brainstorming](../.agents/skills/brainstorming/SKILL.md) | Requisiti incompleti, nuove funzionalità o scelte che cambiano il risultato | Leggere contesto e codice, chiarire obiettivo/vincoli, distinguere richieste e proposte, fare domande soltanto sui dubbi reali |
| [Writing Plans](../.agents/skills/writing-plans/SKILL.md) | Lavoro articolato con obiettivi già chiariti | Piano proporzionato con passi verificabili, file/interfacce reali, dipendenze, controlli attesi e punti di ripresa |
| [Systematic Debugging](../.agents/skills/systematic-debugging/SKILL.md) | Errori, test falliti o comportamenti inattesi | Raccogliere evidenze, riprodurre, cercare la causa, verificare un'ipotesi e correggere senza tentativi casuali |
| [Verification Before Completion](../.agents/skills/verification-before-completion/SKILL.md) | Prima di dichiarare corretto, funzionante o completato un intervento | Eseguire i controlli pertinenti, leggerne gli esiti e dichiarare risultati e limiti dimostrati |

L'ordine non è una cerimonia obbligatoria per ogni piccola richiesta: chiarire ciò che manca, pianificare quando serve, indagare i difetti quando presenti e verificare prima di dichiarare successo. Non riaprire decisioni già raccolte né ripetere controlli senza un motivo concreto.

## Fonte e adattamenti

Fonte: [obra/superpowers](https://github.com/obra/superpowers), revisione fissata `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`. Licenza MIT conservata in ogni cartella.

- Systematic Debugging: adattati il nome della skill di verifica collegata e il fallback al test minimo con gli strumenti del progetto quando la skill TDD facoltativa non è installata.
- Verification Before Completion: procedura originale, con nota di provenienza.
- Brainstorming: nome del collegamento a Writing Plans adattato all'installazione autonoma; esplicitata la precedenza di istruzioni utente/progetto e decisioni già raccolte.
- Writing Plans: resi facoltativi i richiami ad altre skill di esecuzione/worktree non installate; preservato il metodo autorizzato del progetto. Richiesto di verificare percorsi, interfacce e comandi reali prima di inserirli nel piano, distinguendo proposte e ipotesi.
- Le altre skill Superpowers non sono installate implicitamente. Archify già presente resta separata.

## Come riutilizzarle

Le cartelle complete sono in `.agents/skills/`, una per skill. Per un altro progetto copiarvi la cartella della skill desiderata, mantenendo SKILL.md, risorse collegate e LICENSE. Per il flusso comprensione/pianificazione conservare insieme Brainstorming e Writing Plans; per il flusso diagnosi/verifica conservare insieme Systematic Debugging e Verification Before Completion.

Negli ambienti Codex che supportano la scoperta delle skill di repository, `.agents/skills/` è una posizione riconosciuta. La presenza nella repository non equivale all'installazione personale in ogni applicazione o account. In ChatGPT una skill personale disponibile può essere richiamata con `@nome-skill`; nei client Codex compatibili usare il selettore delle skill o `$nome-skill`. Se il client non scopre le cartelle, chiedere all'assistente di leggere lo SKILL.md e i riferimenti pertinenti: non dichiarare che sia stata caricata senza verificarlo.

Richiamo pratico: «Usa le skill in .agents/skills per chiarire i requisiti mancanti, pianificare sui file reali, diagnosticare i problemi e verificare gli esiti. Rispetta AGENTS.md, le decisioni salvate e l'ambito già autorizzato».

## Verifiche e limiti

Installazione personale delle quattro skill verificata dopo il salvataggio persistente; manifest controllati con il validatore del gestore delle skill. Queste verifiche riguardano installazione e struttura, non provano un miglioramento universale delle risposte o l'assenza di allucinazioni.

Systematic Debugging: sintassi del piccolo helper controllata e prove isolate con comando npm simulato per nessun test, test pulito e test che crea un file. Nessun test del runtime Jarvis.

Brainstorming: sintassi dei file JavaScript/shell verificata; prova isolata di avvio locale, autenticazione e pagina di esempio. L'helper facoltativo di arresto ha restituito `stale_pid` nell'ambiente di installazione; la procedura di prova ha terminato il proprio processo. Perciò quel server visuale non è abilitato per il lavoro reale qui: prima va riverificata l'identificazione/arresto del processo. Per comprensione e pianificazione bastano le istruzioni, senza server o browser. Usare gli strumenti visuali già supportati dall'ambiente quando utili; non avviare automaticamente il companion. Per eventuali prove future disabilitare la telemetria con `SUPERPOWERS_DISABLE_TELEMETRY=1`.

Le skill riducono errori di metodo soltanto se applicate bene. Restano necessarie evidenze reali, distinzione tra ipotesi e fatti, rispetto dei permessi e verifiche nell'ambiente corretto. Non promettere «zero allucinazioni».

## Stato di Jarvis

Questa aggiunta riguarda soltanto strumenti e documentazione di sviluppo: nessuna modifica al runtime, nuova build o pubblicazione ZIP. Resta valido il [punto di ripresa della ricerca](HANDOFF-RIPRESA-RICERCA-20261102.md): correzioni dialogo 8066852 già verificate, reset del contesto e priorità Windows Search ancora da completare, poi verifiche Windows e prossimo candidato secondo le autorizzazioni correnti. Non promuovere lo ZIP d06e233 a versione corretta.

## Ricerca mirata per Jarvis — Find Skills for Work, 3 novembre 2026

Find Skills for Work è stata installata come skill personale adattata da Vercel e verificata nel salvataggio persistente. Usa strumenti di ricerca e gestione skill disponibili in Work; non è il file upstream inalterato. La sua installazione non ha ripreso né modificato Jarvis.

Questa ricerca è **una selezione di candidate, non un'autorizzazione all'installazione**. Le quattro skill di sviluppo già presenti e Archify restano utilizzabili. Il punto di ripresa runtime resta continuità R01–R04 nella review completa.

| Priorità | Candidata e fonte originale | Utilità concreta per Jarvis | Limiti e adattamenti prima dell'uso in Work |
|---|---|---|---|
| Prima | [Test-Driven Development](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/test-driven-development/SKILL.md), obra/superpowers | Riprodurre perdita del contesto, falsa conferma o rischio di salvataggio con una prova che fallisce, poi verificare la correzione minima | Esempi TypeScript/npm da tradurre alla suite unittest e CI Windows esistenti. Applicare alle modifiche concordate; non cancellare o riscrivere il codice esistente sulla base delle prescrizioni generiche dell'originale |
| Prima | [Requesting Code Review](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/requesting-code-review/SKILL.md), obra/superpowers | Revisione indipendente di una modifica confrontata con requisiti e intervallo sorgenti, con rilievi precisi per gravità | Collegare la richiesta di revisore agli strumenti Work disponibili. Template di sola lettura; proposte su requisiti non concordati restano proposte e non autorizzano funzioni nuove |
| Dopo l'affidabilità | [Python Performance Optimization](https://github.com/wshobson/agents/blob/7e2fb559cf4b824b27f1fec49fe88f7511066d26/plugins/python-development/skills/python-performance-optimization/SKILL.md), wshobson/agents | Misurare CPU, RAM e tempi di UI, ricerca e voce per il Pavilion, poi intervenire sui colli di bottiglia dimostrati | Partire dagli strumenti standard Python quando sufficienti. line_profiler, memory_profiler e py-spy sono opzioni esterne da verificare separatamente; nessuna installazione automatica, NumPy o processo aggiuntivo imposto al prodotto |

### Fonti e valutazione

- Originali letti: TDD e guida writing-good-tests.md; Requesting Code Review e template code-reviewer.md; Python Performance Optimization e references/details.md per strumenti e dipendenze. Le tecniche avanzate restano condizionali e non sono state collaudate qui.
- Revisioni: obra/superpowers 2ce8aa15d05bd57213e6f746f953aafb7ded7a8b; wshobson/agents 7e2fb559cf4b824b27f1fec49fe88f7511066d26. Licenze MIT lette nelle due fonti.
- Gli esempi di TDD rafforzano il percorso già previsto da Systematic Debugging e Verification Before Completion; il beneficio aggiuntivo è rendere esplicita la prova fallita prima della correzione e la qualità delle asserzioni.
- Il metodo Requesting Code Review era già stato usato come riferimento nella review di Jarvis: qui è candidato a skill personale stabile, non una funzione nuova del programma.
- Python Testing Patterns è stata individuata nel catalogo, ma non è prioritaria: è orientata a pytest e si sovrappone ai controlli già presenti. Non serve cambiare framework per aggiungere prove utili.
- Le candidate sono strumenti di sviluppo, non modelli da eseguire dentro Jarvis. Non promettono accuratezza STT, assenza di allucinazioni o miglioramenti prestazionali senza prove.
- **Non eseguiti:** installazione di queste tre candidate, forward test di eventuali adattamenti Work, nuove prove runtime Jarvis, benchmark Pavilion o build.
- **Raccomandazione:** valutare l'installazione delle prime due come adattamenti proporzionati a Work e al repository; mantenere la terza per una successiva fase di misurazione. Nessun bisogno di aggiungere molte altre skill prima di applicare quelle già disponibili.
