# Quota Codex — fattibilità, non ancora add-on installabile

provider.py contiene il confine di sola lettura: richiede un trasporto esplicitamente collegato e una session_key opaca. Non avvia processi, login o richieste al modello. La sola RPC ammessa è account/rateLimits/read; timeout massimo10s,nessun retry,errori sanitizzati e dati assenti distinti da0.

Non è ancora collegato a Jarvis né distribuito nella004. Non copiare questa cartella o un manifest isolato nella004: fonte autenticata/HUD/ciclo add-on sono passi successivi. Nessun QuotaCodex.jaddon installabile esiste in questa fase.

Prove di sviluppo: tests/test_codex_quota_provider.py e tools/probe_codex_quota.py,eseguite soltanto su Windows. --protocol-only usa una fixture dichiarata. --codex usa il binario ufficiale soltanto nel runnerCI,senza login,con credenziali inRAM e provider di formaSiwC con valore fittizio su loopback. Non legge la quota personale; gli esiti auth-required non significano account esaurito. Non modificare le variabili home dell’ambiente.

Confronto della soluzione ufficiale,misure/limiti e prossimo passo nei documenti BARRA-QUOTA-CODEX e QUOTA-CODEX-FATTIBILITA-20261103 in docs. Tutti gli intermedi importanti sono conservati nel ramo feature/codex-quota-20261103. Nessun servizio a pagamento o acquisto di crediti.
