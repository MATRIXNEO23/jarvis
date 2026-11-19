# Base comune di controllo (mouse, tastiera, elementi delle finestre)

Usata dagli add-on di controllo (oggi Controllo PC; domani Controllo browser), che restano
indipendenti: si può tenerne acceso uno solo. **Con tutti gli add-on di controllo spenti
Lumi non tocca né mouse né tastiera** (`gate.py`: ogni funzione che muove o scrive lo verifica).

- `windows.py`: finestre (elenco, primo piano, chiusura normale, minimizza/ingrandisci),
  puntatore visibile, clic, scrittura Unicode, tasti, rotellina (una tacca alla volta).
- `uia.py` + `uia_host/` (C# `LumiControl.exe`, compilato in CI in `uia_bin/`): lettura
  elementi (`list <hwnd>`) ed elemento col fuoco (`focused`) con UI Automation, sola lettura.
- `gate.py`: registro degli add-on che usano la base.
