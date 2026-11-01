# Registro versioni e punti di ripristino Jarvis
Aggiornato il 2026-11-01. Questo è l'indice diretto per recuperare una versione senza analizzare tutta la cronologia o cercare artifact.

## Riferimento funzionante confermato
**BASE-UTENTE-20261101 — Jarvis-Timer-Audio-Fix2-20261031.zip.**
L'utente identifica come funzionante la build in cima a Download/README.md. Nome e file sono stati verificati e collegati alla sua conferma. Non serve chiedere di nuovo quale ZIP.

| Campo | Valore verificato |
|---|---|
| Pacchetto completo | [Jarvis-Timer-Audio-Fix2-20261031.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Audio-Fix2-20261031.zip) |
| Commit sorgente esatto | [b936879a431370d206152be7b089baf587d15499](https://github.com/MATRIXNEO23/jarvis/tree/b936879a431370d206152be7b089baf587d15499) |
| Dimensione e integrità | 406653 byte; Git blob SHA-1 6aa9e6f9eb040dc7390b4edb55c9ae175bd4e512 |
| SHA-256 | c37270265918c63ddb3a9cf6a2c0982d468dd1af83a1af330c5af1dfb20f9352 |
| Provenienza | Tutti i 155 file identici al tree sorgente; ZIP ricostruito byte-identico; log publisher coerente |
| Test locali audit | 373 raccolti: 368 eseguiti con successo, 5 Windows/Tk saltati; zero fallimenti/errori. Python 3.12.14 Linux; sintassi Python/Node PASS |
| Download diretto | HTTP 200, 406653 byte, confronto integrale con il pacchetto versionato PASS |
| CI storica | Run 41229501460 Windows/Linux 3.11/3.12: 373 per job; file identici al merge testato |
| Pubblicazione | Run 41229495866, log con sorgente/hash uguali alla copia scaricata |
| Prova PC | Conferma esplicita di Alberto del 2026-11-01: build attualmente usata funziona bene; ambito riferito, non prova diretta dell'agente di tutte le funzioni |
| Dati | Launcher profilo Trial separato; backup/profilo compatibile prima di ogni ritorno; credenziali cifrate non portabili liberamente |
| Avvio microfono | Nella base dipende da auto_listen, inizialmente attivo nel profilo Trial; non attribuirle lo standby del ramo successivo |
| Evidenze complete | [Rapporto e log](../docs/VERIFICA-CONCRETA-BASE-20261101.md) |

Questa è la base da preservare e usare per le aggiunte successive. Non sovrascrivere il pacchetto.
Il ramo 5e61e53/a86c2c9 contiene successive modifiche al nucleo e 386 test, ma non è il contenuto di questa ZIP: valutarlo separatamente, senza attribuire il miglioramento riferito a codice assente. L'audit non ha sostituito il programma sul PC.
Il ripristino è ora identificabile direttamente da ZIP, commit e checksum, con i limiti di compatibilità dati descritti sotto.

## Scheda obbligatoria per ogni punto di ripristino
Compilare una scheda compatta prima della promozione:
- ID leggibile/versione e data; stato: candidato, test automatici superati, collaudato sul PC nell'ambito indicato, oppure superato/non consigliato.
- Commit esatto dei sorgenti e riferimento immutabile recuperabile; nome/versione delle add-on.
- Percorso ZIP completo versionato in Download, commit che lo conserva, dimensione e SHA-256 del pacchetto. Il Git blob SHA è un identificatore diverso: non chiamarlo SHA-256.
- Link diretto nel README Download, verifica di download ed estrazione, contenuto/manifest del pacchetto, istruzioni di installazione e dipendenze/versioni.
- Test automatici: comando, ambiente, esito, commit e workflow; distinguere simulazioni da componenti reali.
- Prova dell'utente: data, pacchetto identificato, funzioni effettivamente provate, esito e limiti. «Funziona» non equivale a ogni funzione collaudata al cento per cento.
- Compatibilità del profilo/schema dati, backup privato necessario e procedura per tornare indietro senza perdere dati o usare database incompatibili. Nessuna credenziale o backup personale in repository.
- Motivo della scelta e link alla scheda decisione/errore, problemi noti e riferimento funzionante precedente.

Dopo il collaudo PC, aggiornare il puntatore in cima a questo file con il nome esatto. Non sovrascrivere lo ZIP di una versione funzionante con contenuti diversi. I rilasci nuovi usano nomi univoci, per esempio Jarvis-VERSIONE-SHA.zip.
Gli artifact CI sono prove o copie ausiliarie: il pacchetto di recupero deve essere conservato in Download nel repository, non soltanto in un artifact che può scadere. Conservare anche i sorgenti corrispondenti.

## Quando l'utente dice «riprendi da lì» o «torniamo a quella»
1. Aprire questo registro e la scheda identificata dal contesto. Se il riferimento è ambiguo, chiedere soltanto quale delle versioni nominate intende; non scegliere in silenzio.
2. Distinguere ripresa dello sviluppo da ripristino del programma sul PC. Individuare subito commit, ZIP e compatibilità dati dalla scheda.
3. Verificare presenza e integrità del pacchetto esatto; usare il riferimento immutabile se main si è spostato.
4. Per sviluppo: recuperare i sorgenti in un checkout/ramo separato o proporre un ripristino tracciato, conservando la cronologia. Nessun reset distruttivo o force-push implicito.
5. Per il PC: chiudere Jarvis, conservare profilo e pacchetto correnti, estrarre quello scelto in cartella separata e usare un profilo compatibile. Non cancellare dati né aprire un database nuovo con codice vecchio senza verifica.
6. Registrare l'operazione e le verifiche essenziali in piano/handoff. I test già documentati non vanno rifatti tutti senza un motivo; verificare soltanto integrità, ambiente cambiato e aspetti irrisolti.

La procedura consente recupero diretto dei riferimenti registrati. Richiede accesso al repository e file ancora conservati; non garantisce scritture mai completate o file rimossi. Nessun ripristino è stato eseguito creando questo registro.

## Inventario dei pacchetti già versionati
Fotografia del commit bb94afa1865fe0315021f783736be3cb77c4af84. Presenza, dimensioni e Git blob SHA verificati via API GitHub; non sono test di download, estrazione o funzionamento PC. I link fissati al commit evitano che un cambiamento di main confonda il riferimento.
| ZIP | Byte | Git blob SHA |
|---|---:|---|
| [Jarvis-AddOn-Registro-GPT-Test.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-AddOn-Registro-GPT-Test.zip) | 369432 | ea1fb192dc257be6defeae01ff3d39e905b776f3 |
| [Jarvis-Autodiagnosi-Ibrida-GPT.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Autodiagnosi-Ibrida-GPT.zip) | 313324 | d73a4bb98f75c5417e5af73afff9bf4eba49d0f9 |
| [Jarvis-Autodiagnosi-e-Miglioramenti.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Autodiagnosi-e-Miglioramenti.zip) | 300368 | 49b36bab7fe6522a749576909820c31c1268690f |
| [Jarvis-Contesto-e-Risposte-Brevi.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Contesto-e-Risposte-Brevi.zip) | 262463 | 14fa07cf4e3484fc4fb60f430b22bdd71584e965 |
| [Jarvis-Conversazione-Naturale.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Conversazione-Naturale.zip) | 290170 | b0d6ce6b042d35401646b7a68dc78a4eec27f8c8 |
| [Jarvis-Diagnostica-Runtime-GPT.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Diagnostica-Runtime-GPT.zip) | 330999 | a34d8a62bca7168fbf108c14025d8310273f068b |
| [Jarvis-Fix-Autodiagnosi-Vocale.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Fix-Autodiagnosi-Vocale.zip) | 304402 | f806bfe7f4680369c10d6721b57c4bdd87bea53b |
| [Jarvis-Fix-Diagnostica-Visibile.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Fix-Diagnostica-Visibile.zip) | 321915 | ad9c7b4a2b41229ccccd085d95739024eeb0a4f2 |
| [Jarvis-Full-Audit-Telegram50-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Full-Audit-Telegram50-20261031.zip) | 394717 | 68c0cd7e9b699c161fc5945453eb4984a3b7b559 |
| [Jarvis-Gestione-Progetti-e-Diagnostica.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Gestione-Progetti-e-Diagnostica.zip) | 256542 | bbe95ce13823042461b71068ba7b4f14e26e529d |
| [Jarvis-HUD-Riferimento-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-HUD-Riferimento-20261031.zip) | 394707 | 0c716780755ec9a4ae4b5f6bfa4c5e0db10755c2 |
| [Jarvis-Memoria-Affidabile.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Memoria-Affidabile.zip) | 282608 | 209b027df98c0177fa0af8465a33fd78a240cd02 |
| [Jarvis-Memoria-Automatica.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Memoria-Automatica.zip) | 234564 | 90ee4e0b5ebb850994d15fea757ad74e0244767d |
| [Jarvis-Progetti-Vocali-e-Salvataggio.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Progetti-Vocali-e-Salvataggio.zip) | 244349 | 16634118983f39d337ba6856b5fb9eb0892cb244 |
| [Jarvis-Recupero-Documenti.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Recupero-Documenti.zip) | 293782 | 84c550f6a45cf9d1f61702f3570f5c54e3ac119b |
| [Jarvis-Telegram-Contatti-Vocali-Test.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Telegram-Contatti-Vocali-Test.zip) | 345603 | 6d96e5bbd63f21b216a07895ea0d7099386b32e2 |
| [Jarvis-Timer-Audio-Corretto-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Audio-Corretto-20261031.zip) | 407889 | 5019a79d91b5fcbfe28fc9a65155c5fc47f25fb8 |
| [Jarvis-Timer-Audio-Fix2-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Audio-Fix2-20261031.zip) | 406653 | 6aa9e6f9eb040dc7390b4edb55c9ae175bd4e512 |
| [Jarvis-Timer-Impostazioni-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Impostazioni-20261031.zip) | 405091 | d6335a69325d02edf061603a2e4707ecf92e9c16 |
| [Jarvis-Timer-Vocale-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Vocale-20261031.zip) | 407868 | 5d10f8ab35cb6e31ccc89921b0aecefab760530c |

## Fonti rapide
[Handoff](../docs/HANDOFF-CODEX-ARCHIFY-20261031.md), [decisioni e lezioni](../docs/DECISIONI-E-LEZIONI.md), [stato attività](../docs/STATO-ATTIVITA.md), [sorgenti](../docs/INDICE-SORGENTI.md), [installazione e dati](../Prima-installazione/06-Reinstallazione-e-dati.md).

## Candidato Accesso file 63bfd04 — 2026-11-01

- ZIP persistente: Download/Jarvis-Accesso-File-0.1.0-20261101-63bfd04.zip
- Sorgenti: 63bfd048032f51ff5d52f87a14060f27fad720c0
- SHA-256: 43867ec86094eac5c7e9ef6f03674d9c5ad19cd6736f3594638eadfb85d6db0e
- Windows CI: run 41321679044, due job 3.11/3.12, pacchetto estratto e avvio UI.
- Collaudo PC: pendente. La base confermata BASE-UTENTE-20261101 b936879 resta invariata.
- Recupero: usare la cartella precedente Timer Audio Fix2; non cancellare profili o dati.
