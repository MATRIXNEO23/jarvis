# Prove dal vivo fatte da Codex con la diagnostica di Lumi

Divisione del lavoro (decisa dall'utente il 17/11/2026): Codex fa le prove dal vivo con il server MCP «lumi-diagnostica» e scrive solo gli esiti. Claude legge gli esiti e corregge il codice.

## 1. Collegare la diagnostica a Codex (una volta sola, sul PC)
1. In Lumi apri Impostazioni → «Diagnostica per Claude» → «Copia configurazione per Claude desktop».
2. Incolla il testo nel Blocco note. Ti servono due valori: `command`, cioè il percorso di python o dell'eseguibile, e `args`.
3. Apri `C:\Users\matri\.codex\config.toml` e aggiungi:

```toml
[mcp_servers.lumi-diagnostica]
command = 'INCOLLA QUI command'
args = ['INCOLLA', 'QUI', 'args']
startup_timeout_sec = 30
tool_timeout_sec = 120
```

Usa gli apici singoli: così le barre `\` dei percorsi Windows restano come sono.

4. Riavvia Codex e controlla che compaiano gli strumenti `lumi_stato`, `lumi_prova_comando` e gli altri.

## 2. Regole per le prove
- Un comando alla volta: aspetta la risposta prima di mandare il successivo. Se va in timeout, non rilanciarlo subito: guarda prima `lumi_console`.
- Niente Controllo PC, programmi o file con `lumi_prova_comando`: restano bloccati.
- Non cambiare le impostazioni e non cancellare dati.
- I log vanno filtrati: si riporta solo la riga decisiva, mai il log intero.
- Non modificare il codice. Codex prova e annota, le correzioni le fa Claude.

## 3. Dove scrivere gli esiti
Nel file `docs/prove/ESITI-<build>.md`, per esempio `ESITI-055.md`, una riga per prova:

`| frase o strumento | ok/ko | cosa è successo, in 1 riga | riga di log decisiva |`

In fondo, aggiungi una sezione «Non provato» con l'elenco di quello che non sei riuscito a provare e il motivo. Poi fai commit e push con `[skip ci]`.

## 4. Cosa provare
L'elenco delle prove di ogni build è nella sezione «Da provare dal vivo» di `docs/HANDOFF-LUMI-CORRENTE.md`.
