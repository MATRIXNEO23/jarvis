# JRV-AUD-003 — salvataggio e chiusura senza perdere modifiche

Obiettivo: non scartare testo digitato dopo lo snapshot salvato, mantenendo salvataggi nuovi, consenso allo scarto e finestre estranee protette. Base784edad7dc128783f5bee7729c5c6f6e6e0170f8, comprende001/002. Ramo separato, PR dipendente dalla35; nessuna build, merge o profilo utente modificato.

Causa da riprodurre: ManagedDocuments.save_and_close salva la lettura corrente, poi passa discard_confirmed=True; ClassicNotepadBridge.close azzera il dirty bit e posta WM_CLOSE senza verificare quel testo. Un cambiamento durante il salvataggio può essere perso. close_clean contiene lo stesso consenso artificiale ma non è chiamato dalla UI corrente.

Scelta tecnica: distinguere il contenuto salvato dal consenso esplicito allo scarto. Il bridge mette temporaneamente Edit in sola lettura, confronta il contenuto con la copia salvata, poi chiude; conserva il blocco fino alla chiusura confermata e ripristina stato originale/dirty se rimane aperto. Rilettura senza blocco lascia una seconda race; bloccare durante tutto l'I/O su HDD trattiene inutilmente la digitazione. Nessuna dipendenza nuova o sospensione di processi. Scritture programmatiche di software estraneo non rientrano nella garanzia di blocco della digitazione.

- [x] Red Windows: orchestratore/worker/bridge reali con finestra nascosta e controllo Edit Windows appartenenti solo al test. Modifica dopo il salvataggio e WM_CHAR dopo dirty-clear. File reali temporanei. Nessun Notepad utente avviato.
- [x] Correzione minima in managed_documents.py e notepad_controller.py; save_only/scarto immutati. close_clean deve verificare una copia realmente salvata.
- [x] Preparati test di salvataggio immutato/versioni, scarto esplicito, finestra estranea, fallimento lettura/lock/PostMessage/timeout, ripristino modificabilità e titolo cambiato. Esito Green da acquisire.
- [ ] Review indipendente; suite completa Windows3.11/3.12 e probe esistenti. Checkpoint remoto con SHA/run/esiti/limiti.

Review focus: TOCTOU tra confronto e WM_CLOSE; editor bloccato dopo eccezione; clear dirty su testo cambiato; firma bridge e fixture storiche; chiusura impropria dopo salvataggio fallito. Recupero: ramo isolato, nessuna modifica della build distribuita, file preesistenti mai sovrascritti.

Fonti Microsoft: https://learn.microsoft.com/en-us/windows/win32/controls/em-setreadonly (blocca modifiche utente, risultato nonzero, stile letto con GetWindowLong/GWL_STYLE); https://learn.microsoft.com/en-us/windows/win32/controls/em-setmodify (flag di modifica). Fixture Win32 non riproduce il dialogo nativo di Notepad: prova manuale Windows10/Pavilion ancora richiesta.

Red confermato: commitf92eef2ddf2fe7f2bf8de151a3458727a819f21f, run42330339439;684 test per Python3.11/3.12, due fallimenti comportamentali senza errori. Il controllo Windows accetta WM_CHAR dopo il dirty-clear e la modifica durante I/O viene chiusa invece di conservata. Candidata runtime ora preparata, Green e review da completare. Non eseguiti test funzionali Linux.
