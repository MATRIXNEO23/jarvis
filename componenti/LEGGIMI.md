# Componenti esterni e chiavi API

Installa da dentro Lumi quello che serve in più sul PC, senza lanciare i `.bat`.
- **Primo avvio**: finestra «Installa componenti» con le spunte; si riapre da
  Gestisci add-on > «Installa componenti...».
- **Sezione di ogni add-on**: i suoi componenti (stato, link ufficiale modificabile,
  «Salva link», «Apri link», «Installa») e le sue chiavi API («Crea la chiave»).
- Ogni installazione chiede conferma. Pacchetti Python con `pip --user` (stesso Python di Lumi),
  programmi con Gestione pacchetti di Windows (`winget`, fonti ufficiali), script inclusi
  (`installa_modello_voce.py`, `installa_gpt.ps1`). Senza winget resta il link.

## File
- `catalog.py`: elenco componenti/chiavi, controllo «presente», comandi d'installazione,
  link modificabili (salvati nel profilo in `componenti.json`).
- `ui.py`: finestra d'installazione e pannello requisiti per add-on.
