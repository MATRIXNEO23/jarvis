# Prova del motore incorporabile — 4 novembre 2026

## Accettazione richiesta dall’utente
Prestazioni almeno pari a Kobo sullo stesso Pavilion, stesso GGUF, prompt e parametri; nessun blocco osservato nel collaudo ripetuto. Context Size, Max Output, thread/batch thread e parametri effettivi del sampler configurabili, persistenti, ripristinabili. Questo criterio non è ancora superato. Non confondere compilazione, caricamento DLL, generazione, correttezza semantica e confronto prestazioni.

## Scelta della prima prova
Versione di riferimento riferita nella continuità: KoboldCpp1.121. Tag risolto via API al commit7e0eb2dc4a23f1a0fc42a7660ad43be7a4b9e759. Il codice init_library di koboldcpp.py carica koboldcpp_noavx2.dll con ctypes.CDLL; load_model/generate sono funzioni native con strutture per valore. Il Makefile offre già il target koboldcpp_noavx2. Usare direttamente questo backend conserva più fedelmente la base di confronto rispetto a sostituirlo con llama.cpp di altra revisione. È una scelta per prova tecnica, non attestazione di velocità uguale.

Compilatore w64devkit1.22.0 e flag LLAMA_PORTABLE=1/LLAMA_NOAVX2=1 ripresi dal workflow upstream Windows OldPC; build limitata al target CPU. Portabilità evita march=native del runner. Nel ramo x86 SIMPLECFLAGS contiene mavx, msse3 e mssse3; controllare anche dipendenze comuni e binario prima di attestare compatibilità universale. Il runner Windows ha CPU diversa dal Pavilion: il suo verde NON prova l’esecuzione sullo i3.

## Prova corrente
Workflow native-model.yml: checkout upstream fissato, compilazione DLL, caricamento diretto ctypes, verifica simboli e una chiamata senza modello al contatore iniziale. Nessun server HTTP, koboldcpp.exe, chat separata o modello scaricato. DLL conservata solo come artifact di sviluppo con licenze; nessuna build Jarvis006 pubblicata. La DLL upstream può contenere codice per altre funzioni: non dichiararla già ridotta al minimo.

## Passi dopo questa prova
1. ABI fissata con header C e strutture Python confrontate; evitare riscrittura ad occhio. Binding per caricamento, tokenizzazione, generazione, cache, annullamento e metriche. Processo Python proprietario isolato, se necessario per contenere un crash nativo: parte interna dell’add-on, nessun programma Kobo richiesto.
2. Riprendere le assegnazioni reali di load_model/generate, inclusi default e sampler order. Mappa delle impostazioni caricamento e generazione, salvate nel profilo, senza tagliare arbitrariamente controlli richiesti.
3. Prova generazione con Gemma2 e gestione vita del modello: nessuna deduzione dai soli simboli DLL. Accesso ai pesi/licenza da verificare prima di download automatici; non redistribuire il modello alla cieca.
4. Collegamento a console/voce/Telegram e gate online già progettati; niente conferme di azioni inventate.
5. Confronto ripetuto Kobo/add-on sul Pavilion, tempi iniziali e a caldo, token/s, RAM/CPU, stessi prompt/contesto/output/sampler/cache; controllo UI responsiva e recupero timeout. Solo dopo esito conforme considerare consegna installabile.

Fonti: https://github.com/LostRuins/koboldcpp/blob/7e0eb2dc4a23f1a0fc42a7660ad43be7a4b9e759/koboldcpp.py ; Makefile e .github/workflows/kcpp-build-release-win-oldpc.yaml alla stessa revisione. Copie riutilizzate richiedono attribuzioni/licenze AGPL e componenti associate. Nessuna valutazione legale generale effettuata.
