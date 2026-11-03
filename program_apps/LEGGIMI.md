# Programmi e app

Add-on per Windows10/11 dell'utente corrente. Richiede soltanto Python/Tk e Windows PowerShell già previsti da Jarvis; nessun servizio residente o nuovo account.

In Impostazioni > Gestisci add-on seleziona Programmi e app, Configura, Aggiorna elenco. Spunta Consenti avvio e Salva. L'installazione dell'add-on non autorizza alcuna app; attivalo dal gestore quando vuoi usarlo.

Il rilevamento legge Start, collegamenti Desktop/Start, App Paths e manifest Store del profilo corrente. Non cerca tutti gli eseguibili sui dischi. Errori di una fonte indicano copertura incompleta; nessun taglio a20 applicazioni. Per portatili o app mancanti usa Aggiungi programma (.exe/.lnk locale).

Seleziona una riga e scrivi facoltativamente Comando vocale personalizzato, ad esempio «apri la posta». Sono equivalenti «avvia la posta» e «lancia la posta»; rimane utilizzabile il nome originale. Una frase libera come «controlliamo la posta» funziona come scorciatoia. Conflitti con altri nomi/frasi o comandi esistenti vanno risolti prima di salvare. Prova avvio usa i permessi già salvati.

Comandi precisi locali senza GPT. Per parafrasi non comprese il modello già connesso può proporre il nome; Jarvis risolve e controlla i permessi localmente. Più app corrispondenti: domanda breve e finestra scorrevole, risposta nome/numero nella stessa richiesta. Elenchi non pronunciati. La conferma di Windows dell'avvio non garantisce che il contenuto della finestra sia visibile.

Codice: native.py/windows_apps.ps1 rilevamento e API Windows; service.py associazioni, frasi, permessi e richieste; ui.py configurazione e scelte; ProgrammiApp.jaddon descrizione fidata. Dati nel profilo Jarvis attivo, addon-data/programmi_app/programs.json: separati dai sorgenti e conservati fra aggiornamenti. Nuove app non selezionate; collegamento modificato o programma manuale cambiato richiede riconferma. Rimozione/disattivazione invalida le scelte pendenti, senza cancellare i programmi.

Questo componente avvia app; non chiude, installa o disinstalla programmi e non ne controlla le funzioni interne. Microfono e account personali, qualità delle trascrizioni e consumi sul PC richiedono collaudo distinto. I test sono nel repository, esclusi dal pacchetto operativo.
