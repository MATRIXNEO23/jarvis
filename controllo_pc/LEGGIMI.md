# Controllo PC (add-on)

Comanda finestre, mouse e tastiera **offline**, con le funzioni di Windows: nessun modello,
nessun servizio residente. Si installa **spento**: Impostazioni > Gestisci add-on > Controllo PC.

## Comandi (voce o testo)
- «finestre aperte», «cosa c'è aperto»: elenco numerato in console (mai letto a voce).
- «passa a Chrome», «vai su Blocco note», «passa alla 2», «passa a lavoro» (nome tuo).
- «chiudi la finestra Blocco note», «chiudi Chrome»: chiusura normale come la X
  (se c'è da salvare lo chiede il programma).
- «clicca su Cerca», «doppio clic su Foto», «premi il pulsante Invia».
- «scrivi ciao nel campo Cerca», «digita buongiorno» (nella finestra attuale).
- «premi Ctrl più C», «premi Alt+Tab», «premi invio».
- «scorri giù», «scorri su di 5».
- «cosa posso cliccare»: elenco dei pulsanti/campi della finestra.
- «chiama questa finestra lavoro»: dai un nome tuo alla finestra (anche in Configura).

Se la frase non corrisponde a nessuna finestra o elemento aperto, Lumi la lascia
agli altri comandi (es. «passa a GPT» resta il cambio di modello).

## Conferme
Le prime volte (2, modificabile in Configura) Lumi chiede «sì»; poi ricorda quell'azione
su quel programma. Le azioni delicate (Invia, Elimina, Non salvare, Paga, Alt+F4, Invio…)
chiedono **sempre**. «Dimentica azioni ricordate» in Configura azzera la memoria.

## Come trova i pulsanti
Con **UI Automation** di Windows (come i lettori di schermo): ogni programma dichiara
pulsanti, campi e menu con nome e posizione. Alcuni programmi (giochi, app disegnate
a mano) non li dichiarano: lì Lumi dice che non trova l'elemento. Lo sguardo sullo
schermo con un modello online è previsto come opzione **spenta**, con conferma prima
di usare un modello online (non ancora presente).

## File
- `commands.py`: frasi → azioni (regole precise).
- `service.py`: logica, conferme, nomi delle finestre.
- `windows.py`: finestre, mouse e tasti (ctypes, solo Windows).
- `uia_host/`: sorgente C# di `LumiControl.exe` (sola lettura degli elementi); nel
  pacchetto c'è il compilato in `uia_bin/`.
- `runtime.py`: punto d'ingresso usato da Lumi; `ui.py`: configurazione.
- Dati: `addon-data/controllo_pc/config.json` nel profilo (nomi delle finestre,
  azioni ricordate, numero conferme, mouse visibile).
