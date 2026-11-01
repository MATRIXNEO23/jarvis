## Cartella programma dal nome — nuovi sorgenti verificati, nessun nuovo ZIP
Riferimento d379368c0c9ebaee93816fa2ea739bae5cf5b0f0, [prove](../docs/ACCESSO-FILE-PASSO8-CARTELLE-PROGRAMMI-20261101.md). Nessun componente, runtime o pacchetto Python nuovo. Dopo una futura consegna richiesta, usa lo stesso Accesso file attivo con cartelle consentite: «dove è installato Nome» oppure «trovami la cartella del programma Nome», poi scelta/apertura vocale del risultato. Windows fornisce registrazioni e target dei collegamenti Desktop/Start; directory ed eseguibile possono avere nomi diversi dal nome pronunciato.
La cartella mostrata deve rientrare nelle spunte e nei permessi correnti. Target assente/di rete, consenso revocato e ruolo non risolto non diventano installazione certa. Per programmi simili chiarire quale, senza ricominciare la richiesta; il modello già collegato resta un aiuto se il locale non risolve. I template utente sono risolti con Windows, senza inserire manualmente il nome del profilo. Web non richiesto da questo percorso. Microfono reale e prestazioni del Pavilion restano collaudo del pacchetto effettivo. I vecchi ZIP sotto non ricevono automaticamente questo codice.

## Ricerca e modello — nuovo codice verificato, nessun nuovo ZIP
Raccordo sui sorgenti a279a4ee944c23a93545835ada740793055418fe, [prove](../docs/ACCESSO-FILE-PASSO6-MODELLO-20261101.md). Dopo una futura consegna esplicitamente richiesta, usa lo stesso Accesso file attivo con cartelle consentite e il GPT già configurato/collegato (guida [GPT](02-GPT.md)). Nessun nuovo componente, pacchetto Python o indice da installare.
Prova prevista nel pacchetto corrispondente: una ricerca precisa trovata resta locale; un indizio senza risultati può chiedere un raffinamento al modello, con stato nella riga HUD. Rispondere alla domanda breve mantiene l'obiettivo; «annulla ricerca» invalida la proposta. Con GPT spento/scollegato resta l'esito locale e il messaggio di indisponibilità; non cambiare modalità microfono per risolverlo. File mancanti del componente: reinstallare il pacchetto completo; non scaricare file singoli da fonti inventate. Il vecchio ZIP sotto non riceve questo comportamento automaticamente. Web retrieval e account/microfono personali non sono coperti dalle risposte controllate dei test.

# 5. Impostazioni dei moduli inclusi

## Candidato Accesso file 0.1.0 — installazione e prima prova
Usare lo ZIP candidato in [Download](../Download/README.md), sorgenti 7298fb632cd9b72386fd7a30f469b307ce7e6fa5; non sovrascrivere la cartella funzionante. Profilo separato LOCALAPPDATA/Jarvis-AccessoFile-Trial, dati precedenti copiati senza modificarli; launcher unico avvia_jarvis.bat. Nessuna dipendenza Python nuova per l’accesso file.
1. Estrarre in una cartella nuova e avviare avvia_jarvis.bat.
2. Ingranaggio → Progetti e servizi → Gestisci add-on → Accesso file → Configura. Il componente incorporato è inizialmente SPENTO; se manca la registrazione scegliere Installa e file_access/AccessoFile.jaddon.
3. Selezionare una cartella di prova, usare Spunta/Escludi (o spazio), Salva, poi Attiva dal gestore.
4. Con un TXT conosciuto: «cerca file PARTEDELNOME», «leggi file 1», «apri cartella 1» se il risultato è una cartella. Testo visto senza modifica; «spiega file 1» richiede GPT collegato e invia un estratto.
Formati, limiti, errori e profilo dati nel LEGGIMI del componente incluso nel pacchetto. Se manca file_access/windows_search.ps1, reinstallare dal pacchetto completo; indice Windows assente usa fallback, non serve un altro indicizzatore. Tornare alla vecchia cartella non richiede cancellare profili o dati. [Prove e limiti](../docs/ACCESSO-FILE-RAPPORTO-20261101.md).

Le etichette seguenti corrispondono al codice della base b936879; le funzioni ancora soltanto progettate sono indicate separatamente. Pacchetti di altre fasi possono avere posizioni diverse.

| Modulo | Preparazione | Dove configurare | Prova breve |
|---|---|---|---|
| GPT esterno | Guida GPT | Ingranaggio → GPT e memoria | Collegamento e domanda reale |
| Microfono | Guida Voce | Ingranaggio → Voce | Premi per parlare, trascrizione, azione |
| Risposte a voce | Voce SAPI Windows | Ingranaggio → Voce | Prova voce |
| Memoria generale | Nessuna dipendenza extra | GPT e memoria → Second Brain locale | Breve dialogo, chiusura e recupero dopo riavvio |
| Progetti | Incluso, SQLite standard | Progetti e servizi → Gestisci progetti / apri continuità | Creare progetto di prova e riaprirne la continuità |
| Telegram | Guida Telegram | Progetti e servizi | Configurazione e lettura contatti prima di invii |
| Add-on descrittive | File .jaddon verificato | Progetti e servizi → Gestisci add-on | Installare, osservare SPENTO, attivare e interrogare |
| Timer/allarmi | Incluso, audio Windows | Timer e allarmi | Prova suono e bip alternativo |
| Documenti/comandi Windows | Incluso, app Windows corrispondenti | Console e controlli documento | Documento di prova, salvataggio e chiusura |
| Dettatura desktop | Microfono configurato, finestra destinataria | Voce → Attiva dettatura | Testo innocuo in Blocco note |
| Diagnostica | Inclusa | Autodiagnosi Jarvis | Rapporto locale, distinguendo stato e prove reali |
| Nuova navigazione autonoma | Non ancora implementata | Non ancora disponibile | Nessuna istruzione d'installazione operativa |

## Memoria e progetti
Second Brain è inizialmente disattivato nei valori predefiniti. Abilitarlo consente memoria generale persistente; disattivarlo non cancella l'archivio già scritto. La memoria dei progetti è distinta. Non premere «Cancella memoria generale» per risolvere un componente mancante.
I dati si trovano nel profilo attivo. La copia Trial conserva i database ma non duplica automaticamente i documenti dei progetti.

## Add-on attuali
1. Apri Gestisci add-on e scegli Installa / aggiorna.
2. Seleziona il file .jaddon. Il programma controlla struttura/versione e lo registra SPENTO.
3. Seleziona il componente e attivalo con conferma.
4. Disattivazione/rimozione devono riflettersi nelle capacità della richiesta successiva.

La versione attuale dei .jaddon è descrittiva e può richiamare poche azioni già predisposte. Non installa da sola codice Python o un'estensione web. Il pacchetto dimostrativo è examples/addons/DiagnosticaSistema.jaddon sul ramo evoluto.
Le nuove funzioni «Ripristina impostazioni iniziali dell'add-on» e «Torna alla versione precedente» sono requisiti salvati, non pulsanti già implementati nel riferimento. Non cercarli come se fossero presenti.

## Timer
Scegli suono, volume e ripetizione nelle impostazioni; prova l'audio prima di affidargli un allarme. Il bip alternativo usa il volume di Windows. Una configurazione non prova che l'uscita audio sia udibile.

## Documenti e dettatura
Usa prima un file di prova e verifica la finestra destinataria della dettatura. Per i documenti conferma percorso e scelta tra salvataggio e uscita senza salvare. Non serve installare editor aggiuntivi per i normali file di testo.

## Nuovo modulo
Deve arrivare con scheda in questa cartella, dipendenze effettive, comandi di esempio, configurazione, risultato atteso, errori e procedura di recupero. Le funzioni proposte non vanno elencate come già utilizzabili.
