# WINDOWS — File, cartelle e programmi scelti
Aggiornato: 2026-11-01. **Stato: requisiti raccolti e fattibilità preliminare; implementazione non autorizzata.** Base b936879a431370d206152be7b089baf587d15499. Priorità rispetto alle altre idee ancora da concordare.

## Criterio confermato dall'utente
Jarvis deve essere il più leggero possibile sul Pavilion i3-2100/10 GB/Windows 10. Prima verificare cosa esiste nel programma e cosa Windows mette già a disposizione; riusare queste capacità quando soddisfano i requisiti. Non è un divieto assoluto di nuove dipendenze: aggiungerle solo quando necessarie o giustificate da un vantaggio concreto, valutando peso, affidabilità, semplicità e manutenzione. La valutazione tecnica spetta all'assistente, senza chiedere all'utente di scegliere librerie/protocolli. Modulo logico .jaddon e dipendenza esterna sono cose distinte: un'add-on può usare solo funzioni Windows e componenti già presenti.

## Risultati richiesti
- Accedere a cartelle, navigarle, cercare un file e aprirlo.
- Nelle impostazioni scegliere i programmi avviabili; Netflix e WhatsApp sono esempi, non app già verificate sul PC.
- Richiesta precisa riconosciuta localmente senza GPT. Parafrasi/ambiguità interpretate dal GPT esterno se consentito e collegato, poi azione definita validata/eseguita localmente; chiarimento se necessario.
- Le funzioni nuove e i programmi configurati devono comparire nell'elenco aggiornato «cosa puoi fare?» con descrizione; distinguere disponibili e disattivati.

## Cosa esiste già — lettura della base esatta
- local_engine.py: apertura Blocco note, Calcolatrice, Esplora file, C:, Download e browser. _open_app usa subprocess.Popen senza shell; _find_download cerca per nome solo sotto Download, massimo 3000 file esaminati/20 risultati, senza seguire symlink. Non è una ricerca generale su tutto il PC e non apre il risultato selezionato.
- settings.py e punti pertinenti jarvis.py: impostazioni già presenti; nei file letti non esiste un catalogo configurabile di programmi scelti dall'utente. Non presentarlo come disponibile.
- capability_registry.py: catalogo descrittivo e binding locali espliciti. live_capabilities.py: disponibilità corrente e registrazione add-on; catalogo non concede esecuzione arbitraria. LocalEngine.available_commands contiene anche un elenco statico: allineare le fonti quando si aggiungono azioni, non aggiornare solo il testo del modello.
- Percorso voce/GPT e registro già presenti, da estendere e verificare: non ricostruire tutto né presumere che qualsiasi parafrasi sia già gestita.
Queste sono letture del codice, non prove eseguite su Windows.

## Funzioni Windows verificate nelle fonti Microsoft
- [ShellExecute/Ex](https://learn.microsoft.com/en-us/windows/win32/shell/launch): avvio applicazioni/apertura di file con il gestore associato. Riutilizzabile per aprire un risultato e l'app registrata.
- [Get-StartApps](https://learn.microsoft.com/en-us/powershell/module/startlayout/get-startapps): nomi e AppID delle app del menu Start dell'utente. Candidato per popolare la scelta programmi insieme a collegamenti/percorso selezionato, senza promettere inventario universale. Installazione effettiva e avvio di Netflix/WhatsApp da verificare sul PC.
- [Windows Search SQL](https://learn.microsoft.com/en-us/windows/win32/search/-search-sql-windowssearch-entry): interrogazione dell'indice già esistente, compatibile con Windows 10. [Copertura dell'indice](https://learn.microsoft.com/en-us/windows/win32/search/-search-3x-wds-included-in-index): non tutti i contenuti sono indicizzati; filtri/formati incidono sui risultati. Prima verificare servizio e cartelle realmente coperte, senza abilitare indicizzazione globale automaticamente. Alternativa da valutare: ricerca locale su richiesta nelle cartelle scelte con limiti, avanzamento e annullamento.
Non scelto ancora il collegamento tecnico definitivo fra Python e questi servizi. La disponibilità di un servizio Windows non equivale a integrazione già realizzata o a costo nullo.

## Proposta tecnica preliminare e ordine di difficoltà
1. Programmi selezionati nelle impostazioni e apertura file/cartelle note: percorso più circoscritto, candidato iniziale.
2. Ricerca per nome in cartelle concordate, scelta fra risultati e apertura: successiva, con lavoro su HDD limitato alla richiesta.
3. Eventuale lettura/analisi del contenuto: separata; dipende dai formati e da cosa significa «verificare file».
Nessun nuovo modello locale richiesto per le operazioni di apertura/ricerca per nome. Evitare scanner o processi residenti senza necessità; considerare anche il peso dei programmi che l'utente apre, distinto dal costo di Jarvis. Consumo aggiuntivo non misurato, nessuna promessa numerica.

## Questioni da discutere
«Verificare file» significa trovarli/controllare nome, presenza e proprietà oppure anche leggerne il contenuto? In quali cartelle cercare? Come scegliere fra omonimi? Definire prima questi comportamenti, poi progetto/revisione e autorizzazione al codice. Avviare un'app è distinto dal controllarne tutte le funzioni interne.

## Prove da progettare prima della consegna
Voce/testo, comando preciso senza GPT e parafrasi col modello simulato/reale distinti; app scelta/disattiva/mancante, percorso cambiato, più risultati, permessi negati, ricerca annullata e catalogo coerente dopo modifiche. Non dichiarare una finestra aperta per il solo invio di un comando; definire osservazione/limiti di verifica. Regressioni pertinenti e pacchetto estratto; prova reale Windows e consumi Pavilion separati. Nessun nuovo test runtime o benchmark svolto in questa discussione.

## Recupero e prossimo passo
Base e ZIP funzionanti preservati: [registro versioni](../../Download/REGISTRO-VERSIONI.md). Quando esisterà una consegna collegare sorgenti, pacchetto/checksum, prove e ritorno versione senza perdita di dati. Ora discutere significato di «verificare» e comportamento desiderato; nessuna implementazione avviata.
