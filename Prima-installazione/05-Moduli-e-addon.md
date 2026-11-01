# 5. Impostazioni dei moduli inclusi
Le etichette seguenti sono lette dal riferimento 5e61e53. Pacchetti di altre fasi possono avere posizioni diverse.

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
