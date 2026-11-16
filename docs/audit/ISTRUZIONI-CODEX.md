# Istruzioni per Codex — audit tecnici di Lumi

Ruolo: fai **solo audit** (lettura e analisi). Non modificare il codice, non lanciare build e non fare push di codice. Le correzioni le fa Claude.

## Dove lavorare
- Repo: MATRIXNEO23/jarvis
- Ramo: `feature/jarvis-kobold-f5-profiles-20261109`
- Prima leggi `AGENTS.md` e la sezione «Ripresa» più recente di `docs/HANDOFF-LUMI-CORRENTE.md`.

## Dove scrivere l'audit
- Cartella: `docs/audit/`
- Nome file: `AUDIT-<build>-<NN>-<AAAAMMGG>.md`
  - `<build>` = build controllata (es. `051`)
  - `<NN>` = numero progressivo per quella build (`01`, `02`…)
  - es. `docs/audit/AUDIT-051-01-20261117.md`
- Un file per audit; non riscrivere quelli vecchi.
- Commit solo di quel file, con `[skip ci]` nel messaggio (così non riparte la build).

## Formato del file
```
# Audit <build>-<NN> — <data>
Commit controllato: <SHA>
Ambito: <file/funzioni controllati>

| # | Gravità (alta/media/bassa) | File:riga | Problema | Prova/riproduzione | Correzione proposta |
|---|---|---|---|---|---|

## Test automatici mancanti o deboli
## Dubbi da chiarire con l'utente
```
- Distingui fatti dimostrati da ipotesi.
- Niente segreti, credenziali o dati personali.

## Priorità attuali (build 051)
1. I 4 test mancanti indicati nell'handoff (Ripresa 16/11 03:40): «chiudi i risultati» chiude solo la finestra risultati; niente offerta tutorial se `pc_service.pending`; conferma preferenze con «sì» e `descrivi()`; `MusicService.prepara` in thread.
2. Rischi di regressione nelle correzioni del pacchetto 35d63f2.

## Risposte di Claude
Claude aggiunge in fondo allo stesso file la sezione `## Esito (Claude)`: per ogni punto, corretto (commit), scartato (motivo) oppure da chiedere all'utente.
