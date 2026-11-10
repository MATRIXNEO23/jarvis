# Musica

Add-on facoltativo di Lumi. Si attiva in Impostazioni > Gestisci add-on > Musica > Attiva; «Configura» apre le sue impostazioni. Spento, Lumi resta com'era: nessuna barra, nessun comando musica.

## Uso
- «Lumi, metti …» (anche «suona», «riproduci», «fammi sentire»): cerca il brano nella **cartella musica** per nome del file (anche nelle sottocartelle; MP3, WAV, WMA, M4A) e lo suona dentro Lumi; i brani trovati con quel nome formano la coda.
- Se non è nella cartella: apre nel browser la ricerca YouTube. Con la **chiave API YouTube** facoltativa apre direttamente il primo video (quota gratuita circa 100 ricerche al giorno; se finisce o la chiave non va, si torna ai risultati).
- «pausa», «riprendi», «ferma la musica», «prossima», «alza/abbassa il volume della musica». Con YouTube questi comandi usano i tasti multimediali di Windows (se due programmi suonano, Windows comanda l'ultimo che ha suonato).
- Barra sotto il nucleo: titolo, pausa/riprendi, stop, avanti, volume (il volume vale per i brani locali).

L'audio di YouTube non viene preso né riprodotto dentro Lumi: le regole di YouTube lo vietano; il video si apre sempre nel lettore di YouTube.

## File
- `Musica.jaddon`: descrizione per il gestore add-on (azione locale `music.local`).
- `commands.py`: frasi riconosciute. `library.py`: elenco e ricerca dei brani. `player.py`: lettore MCI di Windows.
- `youtube.py`: indirizzi YouTube, API facoltativa, tasti multimediali. `service.py`: logica. `bar.py`: barra. `ui.py`: configurazione. `config.py`: dati.
- Dati nel profilo di Lumi: `addon-data/musica/config.json` (cartella, volume) e `youtube-key.dpapi` (chiave cifrata per l'utente Windows).
