# Telegram (add-on)

Messaggi e note vocali Telegram dei contatti che spunti, con risposte automatiche facoltative.
Si gestisce tutto da **Impostazioni > Gestisci add-on > Telegram** (non più da Integrazioni):
- **Attiva/Disattiva**: spento = nessuna risposta automatica (il collegamento si ferma).
- **Configura account (ID, hash, numero)…**: finestra dentro Lumi; il codice di Telegram
  (e l'eventuale password in due passaggi) si inserisce in un pop-up. Niente `configura_telegram.bat`.
- Contatti spuntati, cronologia, consenso GPT, invio vocale: nella stessa sezione.
- **Cosa serve installare**: Telethon e FFmpeg con stato, link modificabile e «Installa».
- **API ID e API hash**: pulsante «Crea la chiave» (my.telegram.org) e guida in F1 > Chiavi API.

Chi aveva già configurato Telegram ritrova l'add-on **attivo** (migrazione automatica).

## File
- `Telegram.jaddon`: descrizione dell'add-on per il gestore.
- `login.py`: accesso all'account dentro Lumi (Telethon), salvataggio cifrato DPAPI tramite
  `telegram_security.py` (stesso file di prima, nel profilo).
- Il resto del codice Telegram resta nei moduli `telegram_*.py` nella cartella principale.
