# Stato attività Jarvis
Punto di arresto salvato il 2026-11-01: metodo e documenti allineati; fermo prima dell'implementazione web come richiesto dall'utente.

| Attività | Stato reale | Fonte e prossimo passo |
|---|---|---|
| Metodo di sviluppo | Definito e allineato documentalmente | [AGENTS](../AGENTS.md): piano per aggiunta, revisione finita, test, memoria continua, consegna scaricabile |
| Recupero tra sessioni/argomenti | Istruzioni salvate, non testate con una nuova istanza | [RECUPERO](../RECUPERO.md), [handoff](HANDOFF-CODEX-ARCHIFY-20261031.md); richiede accesso al repository |
| Add-on web: requisiti | Raccolti e salvati | [Piano](PIANO-ADDON-WEB-E-DIAGNOSTICA-20261101.md), comprese domande/risposte brevi e ricerca interna al sito |
| Add-on web: fase 1 tecnica | Inventario preliminare svolto; revisione completa pendente, sospesa | Alla ripresa confrontare soluzioni esistenti, contratto/adattatore, permessi e modalità; poi presentare risultato prima del codice |
| Add-on web: fasi 2–8 | Da fare | Nessuna estensione, nuovo esecutore, suite web, misura RAM o ZIP pubblicato |
| Continuità dialogo precedente | CI documentata; utente riferisce miglioramento sul PC | SHA installato non verificato; consultare handoff per prove e collaudi reali residui |
| Istruzioni di installazione | Nove guide create e riferimenti controllati | [Prima-installazione](../Prima-installazione/README.md); nessuna nuova installazione Windows collaudata |
| Diagnostica/UI/recupero add-on richiesti | Requisiti e test pianificati | Controlli passivi già presenti distinti da nuove funzioni non realizzate |
| Riordino dei file operativi | Contraddizioni individuate, pulizia ulteriore da verificare | [Manutenzione](../Prima-installazione/08-Manutenzione.md); nessuna cancellazione di sorgenti/launcher |

## Decisioni da preservare
- GPT esterno e motore locale: comando preciso riconosciuto localmente senza chiamata GPT; interpretazione del modello per richieste non risolte, entro collegamento e modalità consentite; domanda solo se resta dubbio.
- L'utente decide obiettivi e compromessi e non deve programmare. Nessuna funzione extra senza proposta; domande specifiche sui dubbi sostanziali.
- Add-on modulari, risorse limitate per Pavilion i3-2100/10 GB/Windows 10, caricamento a richiesta dove possibile; test propri e integrazione prima della consegna.
- Configurazione ordinata e semplice, reset del solo add-on distinto da ritorno di versione, dati preservati e controllo manuale del microfono.
- Confrontare riuso/adattamento/sviluppo nuovo dopo ricerca web e verifica del codice esistente, con licenze/costi/dipendenze compatibili.
- Consegna dichiarabile soltanto dopo pacchetto verificato e link scaricabile controllato in Download/README.md. Nessuna nuova build in questa sessione documentale.

## Fonti del programma
[Indice sorgenti](INDICE-SORGENTI.md): codice evoluto nel ramo feature/timer-settings-ui-20261031, riferimento esaminato 5e61e53fbb58ccb5d95b85671604cc5f365d6e04. Radice main storica distinta. [Mappa Archify](architecture-core-20261031/jarvis-core.html) del nucleo a86c2c9: limiti di verifica nell'handoff.
Questo indice non sostituisce codice, piano e prove. Alla ripresa verificare eventuali aggiornamenti di ramo/SHA.

## Prossimo passo unico
Attendere la ripresa richiesta dall'utente; quindi completare la revisione tecnica della fase 1 del piano web, senza iniziare l'implementazione fino al successivo via. Nessun'altra raccolta dei requisiti da zero. Aggiornare piano/handoff prima e dopo ogni unità coerente e registrare prove/esiti nel [registro](DECISIONI-E-LEZIONI.md).

## Recupero di versioni funzionanti
[Registro versioni](../Download/REGISTRO-VERSIONI.md): 20 ZIP storici inventariati con riferimenti fissati. Nessun nuovo pacchetto e nessun punto PC promosso a stabile senza versione esatta. Il dialogo migliorato resta un feedback non collegato a SHA installato. Per «riprendi da lì» usare prima scheda/indice, poi verificare solo dati necessari e condizioni cambiate.
