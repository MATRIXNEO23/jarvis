# Stato attività Jarvis
Aggiornato il 2026-11-01 dopo verifica concreta. Fermo prima dell'implementazione della nuova add-on.

## Punto di partenza certo
**BASE-UTENTE-20261101:** Jarvis-Timer-Audio-Fix2-20261031.zip, sorgenti b936879a431370d206152be7b089baf587d15499. L'utente conferma la build attualmente usata; l'audit ha verificato ZIP reale, 155 file contro sorgenti, riproduzione byte-identica e test inclusi.
[Registro con download/checksum](../Download/REGISTRO-VERSIONI.md) · [rapporto e log](VERIFICA-CONCRETA-BASE-20261101.md).

| Attività | Stato reale | Prova e prossimo passo |
|---|---|---|
| Audit della base | Completato | 373 test locali OK, 5 skip Windows; sintassi PASS; CI storica Windows/Linux riletta e codice coincidente |
| Identificazione sorgenti | Completata | Tutti i 155 file uguali a b936879; non al ramo successivo 5e61e53 |
| Guide e riferimenti | Allineamento alla base b936879 | [Prima-installazione](../Prima-installazione/README.md); separati avvio auto_listen della base e standby del ramo successivo |
| Metodo e recupero | Regole e checkpoint salvati | [AGENTS](../AGENTS.md), [RECUPERO](../RECUPERO.md), [handoff](HANDOFF-CODEX-ARCHIFY-20261031.md) |
| Ramo successivo a86c2c9/5e61e53 | Separato, non adottato automaticamente | Correzione nucleo e 386 test documentati, assenti dalla ZIP base |
| Add-on web: requisiti | Raccolti | [Piano](PIANO-ADDON-WEB-E-DIAGNOSTICA-20261101.md), voce naturale, ricerca e azione nel sito |
| Add-on web: progetto tecnico | Da completare sulla base b936879 | Contratto, ricerca/riuso, permessi, integrazione e revisione finita prima del codice |
| Add-on web: codice/test nuovi/pacchetto | Non iniziati | Nessuna nuova distribuzione |
| Diagnostica nuova/reset/ritorno versione/UI | Requisiti pianificati | Non confondere con funzioni già presenti nella base |
| Riordino operativo | Candidati e contraddizioni individuati | Nessun sorgente, launcher, pacchetto o dato cancellato |
| RAM/CPU target, nuovi login/audio/Windows | Non misurati/eseguiti dall'audit | Riscontro utente e CI hanno ambiti distinti |

## Decisioni preservate
Comando preciso locale senza GPT; interpretazione esterna quando necessaria e consentita; chiarimenti contestuali. Nessuna funzione extra non concordata. Utente decide risultati e non programma; assistente realizza il lavoro tecnico autorizzato. Add-on per Pavilion i3-2100/10 GB/Windows 10, caricamento a richiesta e test propri. Dati, compatibilità e controllo manuale microfono preservati. Consegna soltanto con pacchetto verificato e link funzionante in Download.

## Prossimo passo unico
Alla ripresa leggere questi riferimenti e progettare l'add-on sulla base b936879 preservata. La revisione tecnica resta da completare, senza implementare finché non arriva il successivo via dell'utente. Non ripetere la ricerca della base o attribuire alla ZIP i 386 test successivi. Per ripristino usare il registro, non scansionare tutti i commit/artifact.
