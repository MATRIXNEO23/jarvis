# Jarvis — autodiagnosi ibrida (motore locale + GPT esterno)

## Architettura reale

Jarvis NON contiene un LLM. Il computer Windows esegue un piccolo
motore Python: riconoscimento vocale, registrazione delle operazioni e
controlli locali. Il modulo gpt_client.py usa il ponte Node gpt_bridge.mjs
e il collegamento a ChatGPT già autorizzato: nessuna API a consumo, nessun
nuovo server, nessun download di modelli pesanti.

Il modello esterno non può aprire i file e i log del Pavilion direttamente.
Per esprimere un parere tecnico fondato su dati del programma, il motore
locale deve prima raccoglierli e passarne una rappresentazione limitata
al modello, dopo una decisione esplicita dell'utente.

## Flusso previsto

1. «Jarvis, fai un'autodiagnosi del tuo funzionamento e proponi eventuali
   fix» avvia inspect_jarvis() in sola lettura. Il rapporto completo
   resta nella console locale. Funziona anche senza GPT collegato.
2. Se la frase chiede consigli oltre alla diagnosi, Jarvis apre una
   conferma per l'invio al modello esterno. Rifiutando, niente è inviato.
3. Con consenso, diagnostic_handoff.py prepara un JSON ridotto:
   massimo sei segnali AST, file relativo, riga, priorità, osservazione
   e verifica. Include anche solamente i conteggi anonimi degli esiti
   delle ultime 20 operazioni (verificate/riferite/fallite/interrotte),
   letti dal registro locale: nessun nome, testo, percorso o identificativo
   dell'operazione viene trasmesso. Gli indicatori di disponibilità e i
   conteggi non dimostrano il corretto funzionamento. Non contiene
   codice sorgente integrale, credenziali, percorsi personali, file
   progetti, database, messaggi Telegram o log runtime.
4. Il testo passa solo al metodo GPTClient.call("ask", prompt=...).
   Il bridge esistente richiede la connessione già autorizzata.
   La risposta GPT è un consiglio, non una verifica.
5. Nessuna risposta del modello diventa un comando, una patch o il
   permesso di modificare file. L'utente può comunicare i consigli
   a ChatGPT e decidere cosa correggere.

## Richiesta successiva

Dopo una scansione locale: «Jarvis, valuta la diagnosi con GPT».
Anche in questo caso Jarvis chiede consenso. Senza connessione
GPT il rapporto locale resta disponibile.

## Limiti e prove

Non legge i log di runtime, errori Windows, contenuti Telegram,
password o progetti. Non prova il corretto funzionamento di ciascun
comando; l'AST non è uno scanner antivirus. La precedente segnalazione
Defender non è stata risolta.

La suite verifica anonimizzazione, limite dei dati, consenso prima
dell'invio al modello e separazione di consigli e azioni. Il collaudo
reale sul Pavilion resta da fare dopo un backup completo di
%LOCALAPPDATA%\Jarvis e con una sola istanza attiva. Nessuna esclusione
antivirus o esecuzione forzata di file segnalati.
