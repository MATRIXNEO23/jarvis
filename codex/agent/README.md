# Codex / agent — profili di audit personali di ChatGPT

**Appartenenza: ChatGPT/Codex audit — NON Claude Code.** Questo è un profilo di controllo, non un agente autonomo già attivo. Claude può leggere i rapporti in `docs/audit/`, ma non deve caricare, eseguire, spostare o aggiornare questi profili come propri subagenti. La cartella `claude/agent/` è riservata ai profili gestiti da Claude. Per ogni audit rileggere `docs/audit/ISTRUZIONI-CODEX.md`, `AGENTS.md` e handoff corrente, verificando branch, SHA e build. Solo lettura del codice, niente build, niente correzioni runtime; scrivere soltanto audit o fix documentali richiesti dall'utente.

Questa cartella è di **ChatGPT (ruolo auditor/Codex)**. Non è una configurazione `Claude Code`: Claude mantiene autonomamente i propri agenti, ove previsti, sotto `claude/agent/`. I profili qui sono checklist operative richiamabili dall'assistente, **non** subagenti realmente avviati o installati nell'ambiente di ChatGPT. Il modello esatto viene scelto solo fra quelli effettivamente disponibili quando si svolge il lavoro; non sono garantite selezioni automatiche né risparmi di quota.

## Specialisti e costo consigliato

| Profilo | Fascia preferita | Escalation |
|---|---|---|
| 01 Memory Auditor | Intermedia | Alta per migrazioni, perdite dati e concorrenza SQLite |
| 02 Security Auditor | Alta | Inventario semplice delegabile a fascia leggera |
| 03 Code Reviewer | Intermedia | Alta per regressioni multi-modulo e race condition |
| 04 Performance Auditor | Leggera per metriche, intermedia per analisi | Alta per colli di bottiglia complessi |
| 05 Integration Tester | Leggera per matrice test/CI, intermedia per percorsi | Alta per incidenti sistemici |

**Risparmio:** prima consultare diff, test, log e codice deterministico; affidare ai livelli più costosi solo le ipotesi realmente difficili. Non trasmettere l'intero repository a ogni revisione. Nessuna azione automatica di spesa o esecuzione è autorizzata.

## Procedura

1. Rileggere istruzioni aggiornate in `docs/audit/ISTRUZIONI-CODEX.md` e fonti canoniche; identificare l'ultima build da controllare.
2. Applicare i cinque profili, anche sequenzialmente nella stessa sessione quando non esiste un runtime multiagente.
3. Consolidare evidenze senza duplicati e distinguere `CONFERMATO`, `RISCHIO`, `TEST MANCANTE`.
4. Salvare `docs/audit/AUDIT-<BUILD>-<NN>-<AAAAMMGG>.md`; su richiesta creare il corrispondente `FIX-<BUILD>-<NN>-<AAAAMMGG>.md`, solo difetti e fix brevi.
5. Claude resta responsabile delle correzioni e può aggiungere `## Esito (Claude)` all'audit; non deve modificare automaticamente `codex/agent/`.

Nessuna credenziale, dato personale, prova di exploit o modifica al codice di Lumi.

## Regola obbligatoria: i FIX sono consigli, non ordini per Claude

I file `FIX-*.md` sono **pareri tecnici dell'auditor**: non sono istruzioni esecutive né autorizzazioni a modificare Lumi. Claude deve **verificare indipendentemente** che ogni problema esista ancora nel commit corrente e valutare alternative e possibili regressioni. **Prima di qualsiasi modifica al codice, alle impostazioni, ai dati o ai workflow**, Claude deve spiegare all'utente in modo semplice: (1) il problema e la prova; (2) la correzione proposta e le alternative; (3) gli effetti e i rischi. Deve poi **chiedere e attendere l'approvazione esplicita dell'utente per il singolo intervento**. Se l'utente rifiuta o non risponde, non implementare. Un audit o un file FIX **non** costituisce tale approvazione. Build e pubblicazione richiedono autorizzazione separata. L'auditor può suggerire; solo l'utente decide cosa fare.
