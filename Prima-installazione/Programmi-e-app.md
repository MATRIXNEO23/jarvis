# Programmi e app — guida del componente nei sorgenti

Questa aggiunta non è ancora nella003 scaricabile. Codice e test Windows verificati nel ramo feature/program-apps-20261103; [rapporto](../docs/PROGRAMMI-APP-IMPLEMENTAZIONE-20261103.md). Nessun nuovo ZIP generato. I passi seguenti descrivono il componente e saranno applicabili al pacchetto che lo includerà.

Dipendenze: stessi Python3.11/3.12 x64 con Tk e Windows PowerShell5.1 del progetto; API Windows, nessun nuovo account o pagamento. Copiare l'intera cartella program_apps insieme al runtime corrispondente: il solo manifest .jaddon non aggiunge il nuovo codice alla003.

1. Impostazioni > Gestisci add-on > Programmi e app > Configura.
2. Aggiorna elenco; se una fonte non risponde viene indicata copertura incompleta. Per un programma mancante scegli Aggiungi programma (.exe/.lnk locale).
3. Spunta Consenti avvio; scegli la riga e scrivi facoltativamente la frase personale, per esempio «apri la posta». Salva. Se c'è un conflitto la configurazione precedente resta valida.
4. Attiva Programmi e app nel gestore; installazione e selezione non lo attivano automaticamente. Prova avvio usa soltanto i permessi salvati.
5. Voce o testo: «apri», «avvia» o «lancia» e nome/richiamo. Con più scelte rispondi al chiarimento col nome o numero; la scelta vecchia non riapre un'app dopo revoca/scadenza.

Dati nel profilo Jarvis attivo, addon-data/programmi_app/programs.json, separati dai sorgenti. Nessuna migrazione del profilo003; ritorno alla cartella003 senza cancellare profilo o nuovi dati. La003 non conosce il nuovo manifest: non copiare soltanto quel file nella sua cartella addons.

App non consentita: spunta e salva nelle impostazioni. App non disponibile/cambiata: aggiorna elenco e ricontrolla la selezione; non cambiare ACL di WindowsApps. Componente mancante: reinstallare pacchetto completo e cartella program_apps. Il controllo interno delle app, la loro chiusura e l'installazione/disinstallazione non fanno parte del componente.

Verifiche riproducibili Windows PASS; audio/account/app terze e consumi sul Pavilion restano prova PC del futuro pacchetto esatto. Nessuna promessa che l'elenco di questo PC o ogni launcher coincida con quello del runner.
