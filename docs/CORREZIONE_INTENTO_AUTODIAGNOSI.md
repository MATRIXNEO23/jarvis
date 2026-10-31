# Jarvis — autodiagnosi richiesta, risposta di GPT invece del controllo locale

## Segnalazione reale (31 ottobre 2026)

Dal collaudo con screenshot: l'utente ha chiesto a Jarvis
un'autodiagnosi del proprio funzionamento e suggerimenti per eventuali fix;
Jarvis ha risposto in conversazione «non ho accesso al codice né ai log»,
senza analizzare i file installati.

La frase non prova che i sorgenti non fossero presenti. La build dispone
già di un modulo locale self_diagnostics.py che può leggere in sola lettura
i file Python presenti nella cartella di Jarvis, e source_review.py che
genera raccomandazioni con file, riga e priorità.

## Causa nel codice

- Il parser diagnostic_request() accettava solo frasi complete molto
  specifiche, non «fai un'autodiagnosi del tuo funzionamento e proponi
  eventuali fix» né altre richieste composte naturali: cadevano in GPT.
- Il pulsante «Chiedi a GPT» chiamava direttamente submit_gpt senza
  passare da try_self_diagnostic, bypassando il percorso locale.
- Il modello conversazionale non ha accesso diretto ai file installati
  nella macchina. La diagnosi è un'azione distinta del programma Jarvis,
  non una capacità del modello remoto.

## Correzione e comportamento atteso

- Il parser riconosce richieste **esplicite e positive** di diagnosi del
  codice/funzionamento seguite da una richiesta di fix/correzioni,
  senza confondere negazioni, citazioni o frasi programmate in futuro.
- Il riconoscimento locale avviene anche prima di avviare GPT tramite
  pulsante «Chiedi a GPT» e nella conversazione continua. La diagnosi
  funziona **senza login GPT e senza Internet**, leggendo esclusivamente
  sorgenti che Jarvis ha già sul proprio disco.
- Nel menu secondario «⋯» compare il pulsante **Autodiagnosi Jarvis**.
  Consente il collaudo senza formulazioni vocali o dipendenza dal modello.
- Il registro di Jarvis deve visualizzare: «DIAGNOSTICA > Analisi statica
  locale avviata...», poi un rapporto con i file ispezionati e le
  raccomandazioni (oppure l'errore reale se non accessibili).
- Il modulo non legge, per ora, i **log di esecuzione**. È importante non
  presentare l'analisi statica come diagnostica completa del runtime o
  capacità di controllare tutte le funzioni sul Pavilion.

## Test automatici e futuro test sul Pavilion

I test esaminano esempi equivalenti alla frase reale, le formulazioni
negative, la precedenza della diagnostica rispetto a GPT e la presenza
di un ingresso UI dedicato.

Per il test reale, usare preferibilmente prima il nuovo pulsante
«⋯ → Autodiagnosi Jarvis». Verificare che il registro mostri il
rapporto; poi chiedere a voce «Jarvis, fai un'autodiagnosi del tuo
funzionamento e proponi eventuali fix» e verificare che non risponda
nuovamente col disclaimer del GPT. Non eseguire modifiche automatiche;
il rapporto può essere copiato e discusso con ChatGPT.

Backup di tutta %LOCALAPPDATA%\Jarvis, una sola istanza attiva,
conservazione dei progetti. Rimane irrisolto l'eventuale precedente
rilevamento Defender Trojan:Script/Wacatac.B!ml: non disattivare
Defender né autorizzare eseguibili segnalati.
