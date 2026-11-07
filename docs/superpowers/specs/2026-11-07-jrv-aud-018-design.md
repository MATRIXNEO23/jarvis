# JRV-AUD-018 — impostazioni illeggibili senza riattivazioni o sovrascritture

Base011 `5994d1751fdf02037f2ce3082dbc19a072d4c4a3`,001–011 preservate. Priorità anticipata a018 perché protegge preferenze MIC/GPT, prima delle rifiniture packaging012/013. Utente autorizza correzioni minime preservando quanto funzionava; non autorizza build o reset dei propri dati.

Evidenza: load_settings intercetta OSError/ValueError/UnicodeError e restituisce DEFAULTS con gpt_enabled/auto_listen True, senza segnalazione. initial_launch riattiva ascolto secondo auto_listen; save_settings sostituisce il file anche dopo fallback illeggibile. JSONnonoggetto e tipoerrato dei due flag possono ottenere lo stesso risultato permissivo.

Contratto:

- File assente: mantenere default di prima installazione già concordati, senza avviso. Filevalido/legacy conchiavimancanti: stessa normalizzazione/preferenze di prima; nessuna migrazione di dati.
- File esistente illeggibile (JSONtroncato/UTF8/IO), radice nonoggetto o flaggpt_enabled/auto_listen presenti di tipononbooleano: fallback temporaneo prudente con GPT eauto_listen False e automazioni nonattivate. Originale nonrinominato/cancellato/modificato. Tipoerrato dei flag non è una preferenza valida; precedente test di fallback permissivo va aggiornato intenzionalmente, non indebolito.
- Aggiungere raccolta warning opzionale a load_settings, senza rompere chiamanti esistenti o aggiungere metadati serializzati. Main raccoglie e mostra il warning nella console iniziale una volta, con percorso e istruzione di chiudere/ripristinare da copia valida. Niente popup/conferme ripetitive o reset automatico.
- Prima di scrivere, save_settings valida anche il file esistente con lo stesso parser dei flag critici. NoncreazioneOK; se illeggibile rifiuta con OSError e istruzione di recupero prima di mkdir/tmp/replace. Vale anche per dict copiato e corruzione avvenuta dopo load; nessun backup/reset automatico. Callback attualmente nonprotetto di telegram_reconfigure deve presentare l'errore senza eccezioneTk silenziosa.
- Recupero manuale esplicito documentato: chiudere Jarvis, fare copia dell'originale, ripristinare un settings.json valido da backup. Per nuova configurazione, conservare/rinominare manualmente l'originale dopo copia; fileassente alriavvio riusa valori iniziali normali, quindi microfono/GPT possono tornare abilitati come prima installazione. Non promettere recupero magico delle preferenze perdute.

Solo stdlib, nessun nuovo archivio/schema/dipendenza. Lettura piccola aggiuntiva su save, prestazioniHDD nonmisurate. Non garantisce atomicità CAS contro editor esterno che cambia il file dopo la verifica; la scrittura atomica tmp/replace preesistente rimane. Nessuna modifica di impostazioni/credenziali/dati reali durante lo sviluppo. Test solo Windows, file/profilitemporanei e callback reali con servizi controllati.
