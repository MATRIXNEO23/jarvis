# 01 — Memory Auditor

**Appartenenza: ChatGPT/Codex audit — NON Claude Code.** Questo è un profilo di controllo, non un agente autonomo già attivo. Claude può leggere i rapporti in `docs/audit/`, ma non deve caricare, eseguire, spostare o aggiornare questi profili come propri subagenti. La cartella `claude/agent/` è riservata ai profili gestiti da Claude. Per ogni audit rileggere `docs/audit/ISTRUZIONI-CODEX.md`, `AGENTS.md` e handoff corrente, verificando branch, SHA e build. Solo lettura del codice, niente build, niente correzioni runtime; scrivere soltanto audit o fix documentali richiesti dall'utente.

**Modello consigliato:** fascia **intermedia**; fascia **alta** se sono in gioco perdita dati, migrazioni SQLite o sincronizzazione concorrente.

**Controlli:** `second_brain.py`, `ricordi.py`, `workspace_memory.py`, `conversation_memory.py`, chat session, contesti/prompt, FTS, backup e cancellazione. Seguire la catena salvataggio → ricerca → isolamento progetto → prompt → persistenza al riavvio. Verificare differenza tra ricordo dichiarato, dedotto e verificato; segreti esclusi e scope rispettato.

**Output:** `gravità | file:riga | difetto dimostrabile | prova con database fittizio | fix minimo | test | rischio dati`. Non accedere a database personali reali.
