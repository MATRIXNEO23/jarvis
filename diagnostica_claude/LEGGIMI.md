# Diagnostica per Claude (add-on, spento di serie)

Permette all'app **Claude desktop** di leggere lo stato di Lumi e di provare comandi
**solo dentro Lumi**, tramite un server MCP locale.

- `ponte.py` — dentro Lumi: piccolo server su 127.0.0.1 (porta casuale, chiave casuale
  scritta in `%LOCALAPPDATA%\Jarvis\diagnostica_claude.json`), acceso solo se spunti
  «Diagnostica per Claude» nelle impostazioni. Si spegne togliendo la spunta o chiudendo Lumi.
- `server_mcp.py` — avviato da Claude desktop (stdio, protocollo MCP); parla con il ponte.

Cosa può fare Claude: leggere console, errori, `motore.log` e stato; scrivere un messaggio
in chat; provare un comando come se l'avessi scritto tu; riavviare il modello locale.
Dal 15/11 sera (`strumenti.py`): vedere e aprire le impostazioni in una categoria/voce
(`lumi_impostazioni`), vedere e accendere/spegnere gli add-on (`lumi_addon`), leggere i
ricordi (`lumi_ricordi`) e le chat con i simboli 🤖/📡 e gli ultimi scambi (`lumi_chat`).
In più: `lumi_prova_comando` con «attendi» aspetta e restituisce la risposta; `lumi_prompt`
cattura il prossimo prompt di Gemma (sezioni e token); `lumi_online` (servizi, chiavi, quote);
`lumi_telegram` (icona, colore, risposte automatiche).
Dal 17/11 (052): `lumi_ricerca` (servizi di ricerca: spunta, chiave presente, pronto; mai la chiave) e
`lumi_modelli` (i .gguf che «cambia modello» elenca e quello in uso). «cerca online …», «chiudi i
risultati», «cambia modello» e il numero scelto si provano con `lumi_prova_comando`.
Dal 17/11 (056): `lumi_stato` mostra anche `modalita` (basso_consumo o veloce) e `meteo` (add-on acceso, città, temperatura e icona nell'HUD). «che tempo fa a Roma», «approfondisci» e «apri il 2» si provano con `lumi_prova_comando`; «Vado online?» si risponde con sì/no.
Regola: ogni funzione nuova di Lumi porta con sé lo strumento per provarla da qui.
Cosa NON può fare: Controllo PC (finestre, mouse, tasti), aprire o chiudere programmi,
file, spegnere il PC. Questi comandi vengono rifiutati dal ponte.

Collegamento: Impostazioni → «Diagnostica per Claude» → «Copia configurazione per Claude
desktop», poi incollala in `claude_desktop_config.json` (Claude → Impostazioni →
Sviluppatore → Modifica configurazione) e riavvia Claude.
Per Codex: «Copia configurazione per Codex» copia il blocco TOML `[mcp_servers.lumi-diagnostica]`
(apici singoli, timeout 30 e 120 s) da incollare in `C:\Users\<utente>\.codex\config.toml`;
poi riavvia Codex (vedi docs/audit/ISTRUZIONI-PROVE-CODEX.md).
