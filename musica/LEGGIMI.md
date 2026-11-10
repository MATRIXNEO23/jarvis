# Musica

Add-on facoltativo di Lumi. Si attiva in Impostazioni > Gestisci add-on > Musica > Attiva; «Configura» apre le sue impostazioni. Spento, Lumi resta com'era: nessuna barra, nessun comando musica.

## Uso
- «Lumi, metti …» (anche «suona», «riproduci», «fammi sentire»): cerca il brano nelle **cartelle musica** (se ne possono aggiungere più d'una in Configura) per nome del file (anche nelle sottocartelle; MP3, WAV, WMA, M4A) e lo suona dentro Lumi; i brani trovati con quel nome formano la coda.
- Se non è nella cartella: apre nel browser la ricerca YouTube. Con la **chiave API YouTube** facoltativa apre direttamente il primo video (quota gratuita circa 100 ricerche al giorno; se finisce o la chiave non va, si torna ai risultati).
- **Video** (MP4, WebM, M4V, MOV nella cartella) e **YouTube con la chiave API** si vedono nel riquadro al posto del globo (`video_bin/LumiVideo.exe`, Microsoft Edge WebView2, già presente in Windows 10/11 aggiornato). YouTube usa il lettore ufficiale incorporato: nessun audio estratto. Video non incorporabile o WebView2 assente → si apre il browser. Finito il video, il riquadro si chiude e la sua RAM viene liberata.
- **☰** nella barra: brani divisi per cartella; si naviga nelle cartelle e sottocartelle (▸ per aprire), doppio clic su un brano lo fa partire con i successivi della stessa cartella, **▶ Suona cartella** suona tutta la cartella scelta. Scrivendo in alto si cerca in tutte le cartelle.
- **Coda e playlist** (brani delle cartelle): «aggiungi in coda …» / «metti in coda …» aggiunge senza interrompere; nell'elenco ☰ ci sono «+ Coda», «+ Playlist...» (nome nuovo o esistente), «Togli» e la voce **★ Playlist**; «metti la playlist …» la suona. Le playlist stanno in `addon-data/musica/playlists.json`; eliminarle non tocca i file. Si possono creare più playlist con nome (anche vuote, con «+ Playlist...» senza selezione), rinominarle e mettere video YouTube (salvati come `yt:<id>|titolo`).
- **Coda** nella barra: elenco della coda attuale (cartelle o YouTube), ▲▼ per spostare, «Togli», campo «+ Aggiungi» (cerca nelle cartelle, o su YouTube mentre va YouTube) e «Salva come playlist...».
- **YouTube continua**: con la chiave API la ricerca prende fino a 10 video (stessa quota di uno); finito uno parte il successivo, ⏭/⏮ passano fra questi. Mentre va YouTube «aggiungi in coda …» cerca su YouTube (una ricerca della chiave) e mette il video dopo quello in corso e gli altri accodati.
- **▁ riduci** nella barra: toglie il video e resta solo la musica con la barra (YouTube resta in un riquadrino 200×200, minimo richiesto dal lettore). **▣ video** lo riporta.
- «pausa», «riprendi», «ferma la musica», «prossima», «torna indietro» / «brano precedente» (oltre 3 secondi torna all'inizio), «alza/abbassa il volume della musica». Un solo volume per brani, video e YouTube nel riquadro. Con YouTube questi comandi usano i tasti multimediali di Windows (se due programmi suonano, Windows comanda l'ultimo che ha suonato).
- Barra sotto il nucleo: titolo, pausa/riprendi, stop, avanti, volume (il volume vale per i brani locali).

L'audio di YouTube non viene preso né riprodotto dentro Lumi: le regole di YouTube lo vietano; il video si apre sempre nel lettore di YouTube.

## File
- `Musica.jaddon`: descrizione per il gestore add-on (azione locale `music.local`).
- `commands.py`: frasi riconosciute. `library.py`: elenco e ricerca dei brani. `player.py`: lettore MCI di Windows.
- `video.py`: avvio e comandi del riquadro video. `video_host/`: sorgente C# di LumiVideo (compilato in CI, nel pacchetto solo `video_bin/`).
- `youtube.py`: indirizzi YouTube, API facoltativa, tasti multimediali. `service.py`: logica. `bar.py`: barra. `ui.py`: configurazione. `config.py`: dati.
- Dati nel profilo di Lumi: `addon-data/musica/config.json` (cartella, volume) e `youtube-key.dpapi` (chiave cifrata per l'utente Windows).
