# Diagnostica per Claude (add-on, spento di serie)

Permette all'app **Claude desktop** di leggere lo stato di Lumi e di provare comandi
**solo dentro Lumi**, tramite un server MCP locale.

- `ponte.py` — dentro Lumi: piccolo server su 127.0.0.1 (porta casuale, chiave casuale
  scritta in `%LOCALAPPDATA%\Jarvis\diagnostica_claude.json`), acceso solo se spunti
  «Diagnostica per Claude» nelle impostazioni. Si spegne togliendo la spunta o chiudendo Lumi.
- `server_mcp.py` — avviato da Claude desktop (stdio, protocollo MCP); parla con il ponte.

Cosa può fare Claude: leggere console, errori, `motore.log` e stato; scrivere un messaggio
in chat; provare un comando come se l'avessi scritto tu; riavviare il modello locale.
Cosa NON può fare: Controllo PC (finestre, mouse, tasti), aprire o chiudere programmi,
file, spegnere il PC. Questi comandi vengono rifiutati dal ponte.

Collegamento: Impostazioni → «Diagnostica per Claude» → «Copia configurazione per Claude
desktop», poi incollala in `claude_desktop_config.json` (Claude → Impostazioni →
Sviluppatore → Modifica configurazione) e riavvia Claude.
