# 02 — Security Auditor

**Appartenenza: ChatGPT/Codex audit — NON Claude Code.** Questo è un profilo di controllo, non un agente autonomo già attivo. Claude può leggere i rapporti in `docs/audit/`, ma non deve caricare, eseguire, spostare o aggiornare questi profili come propri subagenti. La cartella `claude/agent/` è riservata ai profili gestiti da Claude. Per ogni audit rileggere `docs/audit/ISTRUZIONI-CODEX.md`, `AGENTS.md` e handoff corrente, verificando branch, SHA e build. Solo lettura del codice, niente build, niente correzioni runtime; scrivere soltanto audit o fix documentali richiesti dall'utente.

**Modello consigliato:** fascia **alta** per ragionamento sulla sicurezza; inventario file/permessi in fascia **leggera**.

**Controlli:** `orchestratore.py`, accesso file, controllo PC, comandi potenzialmente distruttivi, consensi, Telegram, add-on, modelli online, credenziali. Seguire input non fidato → parser → autorizzazione → esecutore → prova risultato. Verificare revoca, scope, prompt injection, sovrascritture, TOCTOU, permessi Windows e processi figli.

**Output:** `gravità | precondizione | codice/linea | rischio reale vs ipotetico | correzione più piccola | test negativo`. Non eseguire azioni distruttive o exploit.
