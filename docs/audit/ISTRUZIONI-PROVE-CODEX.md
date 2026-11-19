# Prove dal vivo fatte da Codex con la diagnostica di Lumi

Divisione del lavoro (decisa dall'utente il 17/11/2026): Codex fa le prove dal vivo con il server MCP «lumi-diagnostica» e scrive solo gli esiti. Claude legge gli esiti e corregge il codice.

## 1. Collegare la diagnostica a Codex (una volta sola, sul PC)
1. In Lumi apri Impostazioni → «Diagnostica per Claude» → «Copia configurazione per Codex». Il pulsante copia negli appunti il blocco `[mcp_servers.lumi-diagnostica]` già pronto (command e args in apici singoli, `startup_timeout_sec = 30`, `tool_timeout_sec = 120`): non serve più copiarlo a mano.
2. Incolla il blocco in fondo a `C:\Users\<utente>\.codex\config.toml` (il percorso esatto è scritto sotto il pulsante).
3. Se il file ha già una sezione `[mcp_servers.lumi-diagnostica]`, sostituiscila.

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
