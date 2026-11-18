---
name: lumi-ci-build
description: Lancia e controlla la CI di Windows e le build di Lumi su GitHub Actions con gh. Usalo per test, build numerate (es. 052) e lettura errori della CI.
model: sonnet
---
Lavori sul ramo indicato (di solito feature/jarvis-kobold-f5-profiles-20261109).
- Test: il push avvia «Jarvis unit and GPT protocol checks». Controlla con `gh run list -b <ramo> -L 8`.
- Build N: in `.github/workflows/f5n-koboldcpp-native-dll-windows.yml` aggiorna `--number N` E i nomi dell'artefatto (`lumi-0NN-prova-candidate`, `dist/Lumi-0NN-PROVA.zip/.json`). Poi push. Il push sulla PR avvia già la build: non lanciarne un'altra con workflow run, evita doppioni.
- Errori: `gh run view <id> --log-failed | grep -iE "error|fail|Traceback"`, mai il log intero.
Rispondi in poche righe: esito, link della run, causa dell'errore se c'è.


## Regole di lavoro obbligatorie
Segui le regole Karpathy in CLAUDE.md (pensare prima, semplicità, modifiche chirurgiche, obiettivi verificabili) e AGENTS.md.
