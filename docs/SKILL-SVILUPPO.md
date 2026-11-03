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
