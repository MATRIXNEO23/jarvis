# JRV-AUD-007 — verifica degli eventi vocali in coda

Richiesta corrente: verificare il possibile problema007. Questo passo contiene soltanto test e documentazione, senza correzioni runtime, build, merge o dati personali. Base7920c4d9c32049d49f848aef3af0006a037dfedf, con001–006 conservate; ramo verify/jrv-aud-007-voice-queue-20261107, PR dipendente dalla39.

Ipotesi statica: VoiceController._report verifica _generation prima dell'enqueue, ma trasmette solo(kind,value). Jarvis collega direttamente notify a output_queue.put; il poll consuma il testo con la modalità attuale e non verifica la generazione. change_voice_mode revoca conversation_epoch/pending, ma non gli eventi vocali già accodati.

- [ ] Usare VoiceController._report/Queue reali, callback change_voice_mode e intero loop dequeue/dispatch effettivi di poll (AST), mantenendo le guardie interne.
- [ ] OFF→ON in conversazione GPT/continuo/PTT: vecchio comando locale e vecchia richiesta modello devono essere ignorati. Una frase senza hotword originata in GPT non deve diventare comando passando a continuo. Uno status precedente non deve sostituire il nuovo.
- [ ] Controlli: restare in standby blocca l'evento; evento nuovo passa una volta; generazione vecchia non può più accodare dal produttore. Nessun microfono reale: sostituire solo avvio worker audio, confini azioni/modello e widget della fixture già esistente.
- [ ] Eseguire la suite Windows3.11/3.12; separare fallimenti comportamentali da errori fixture/022/023. Registrare trace generazione/modo e conteggi, senza invii o azioni reali.
- [ ] Review delle prove in sola lettura; evidenza remota e rapporto breve. Se confermato, descrivere la correzione minima come prossimo passo; non applicarla in questa verifica.

Limiti: nessun Vosk/microfono/account GPT/Telegram o PC Windows10/i3/HDD reale; il test osserva ingresso ai dispatcher, non apertura effettiva di programmi né consumi token. Non copre cambi progetto, frasi nuove dopo PTT release/press nella stessa modalità o cambio stato durante un dialogo modale. Non presentare queste ipotesi come bug dimostrati.

Correzione candidata solo da valutare dopo la prova: portare identità di generazione/contesto nel messaggio e validarla nel consumer prima di log, campione vocale e dispatch. Questa pagina non autorizza né contiene una modifica runtime.
