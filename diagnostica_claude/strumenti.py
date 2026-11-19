"""Strumenti della diagnostica per le novità del 15/11 sera (impostazioni, add-on, ricordi,
chat). Ogni funzione riceve gli argomenti dello strumento MCP e ritorna un dict; il ponte la
esegue sul thread di Tk. Tutti i getter sono funzioni: leggono lo stato di Lumi al momento."""
from __future__ import annotations


def crea(*, navigazione, apri_impostazioni, addon_manager, cambia_addon, cervello, elenco_chat,
         sessione_gemma=lambda: None, telegram=lambda: None):
    def impostazioni(args):
        nav = navigazione()
        if nav is None:
            return {"ok": False, "errore": "impostazioni non ancora pronte"}
        category, item = args.get("categoria"), args.get("voce")
        if not category:
            return {"ok": True, "voci": nav.voci(), "aperta": list(nav.current)}
        if category not in nav.voci():
            return {"ok": False, "errore": "categoria sconosciuta", "voci": list(nav.voci())}
        apri_impostazioni()
        nav.apri_categoria(category)
        if item:
            if item not in nav.voci()[category]:
                return {"ok": False, "errore": "voce sconosciuta", "voci": nav.voci()[category]}
            nav.mostra(category, item)
        return {"ok": True, "aperta": list(nav.current)}

    def addon(args):
        manager = addon_manager()
        if manager is None:
            return {"ok": False, "errore": "archivio add-on non disponibile"}
        ident = args.get("id")
        if ident and "acceso" in args:
            changed = cambia_addon(str(ident), bool(args["acceso"]))
            state = next((a["enabled"] for a in manager.list_installed() if a["id"] == ident), None)
            return {"ok": state is not None, "cambiato": bool(changed), "acceso": state}
        return {"ok": True, "addon": [{"id": a["id"], "nome": a["name"], "acceso": a["enabled"]}
                                      for a in manager.list_installed()]}

    def ricordi(args):
        brain = cervello()
        if brain is None:
            return {"ok": False, "errore": "Second Brain spento"}
        rows = brain.ricordi(str(args.get("cerca") or ""), categoria=args.get("categoria") or None,
                             limit=100)
        return {"ok": True, "quanti": len(rows), "ricordi": rows}

    def chat(args):
        elenco = elenco_chat()
        if elenco is None:
            return {"ok": False, "errore": "elenco delle chat non disponibile"}
        count = max(1, min(int(args.get("scambi") or 6), 32))
        marks = elenco.store.models()
        current = elenco.current()
        chats = [{"id": c.id, "titolo": c.title, "modelli": sorted(marks.get(c.id, ())),
                  "aperta": c.id == current} for c in elenco.chats()]
        recent = [{"utente": u[1], "lumi": a[1]} for u, a in elenco.recent(count)]
        return {"ok": True, "chat": chats, "ultimi_scambi": recent}

    def prompt(args):
        session = sessione_gemma()
        if session is None:
            return {"ok": False, "errore": "modello locale non avviato (fai prima una domanda)"}
        if args.get("arma"):
            session.arm_prompt_diagnostic()
            return {"ok": True, "nota": "catturo il prossimo turno di Gemma"}
        report = session.prompt_diagnostic()
        return {"ok": report is not None, "prompt": report,
                **({} if report else {"errore": "nessun prompt catturato: usa arma=true"})}

    def online(args):
        from online import servizi_online
        from online.servizi_online import quote
        settings = servizi_online.carica_impostazioni()
        keys = servizi_online.Chiavi()
        services = []
        for ident in settings["ordine"]:
            service = servizi_online.PER_ID[ident]
            state = quote.stato(ident, limite_utente=settings.get("limiti", {}).get(ident))
            account = service.tipo == "account"      # GPT dal browser: nella lista come gli altri
            services.append({"id": ident, "nome": service.nome, "posizione": len(services) + 1,
                             "spuntato": ident in settings["attivi"], "tipo": service.tipo,
                             "chiave": None if account else bool(keys.leggi(ident)),
                             "gpt_collegato": servizi_online._account_pronto() if account else None,
                             "oggi": state.get("testo"), "colore": state.get("colore"),
                             "ultimo_errore": servizi_online.ULTIMO_ERRORE.get(ident)})
        return {"ok": True, "versione": __import__("impostazioni_menu").versione(),
                "usa_sempre": settings["usa_sempre"],
                "proponi_lunghe": settings["proponi_lunghe"],
                "avviso_quota": settings.get("avviso_quota"),
                "ultimo_contesto_online": dict(__import__("contesto_online").ULTIMO),
                "conferma_token": settings.get("conferma_token"), "servizi": services}

    def prova_servizio(args):
        """061: prova di UN servizio online nelle tre fasi. Parte in un thread: chiamare di nuovo per l'esito."""
        from online import servizi_online
        ident = str(args.get("servizio", ""))
        if not ident:
            return {"ok": False, "errore": "manca «servizio»", "servizi": list(servizi_online.PER_ID)}
        stato = servizi_online.avvia_prova(ident)
        return {"ok": stato.get("ok", True), "servizio": ident, **stato}

    def ricerca(args):
        """Servizi di ricerca (052): spuntati, con chiave, collegati. Mai la chiave."""
        from online import servizi_ricerca
        settings = servizi_ricerca.carica_impostazioni()
        keys = servizi_ricerca.chiavi()
        pronti = {s.id for s in servizi_ricerca.pronti(settings, keys)}
        def barra(i):
            try:
                info = servizi_ricerca.quota_servizio(i, keys) if keys.presente(i) else None
            except Exception:
                info = None
            return None if info is None else {"testo": info["testo"], "reale": not info.get("stima", True)}
        return {"ok": True, "versione": __import__("impostazioni_menu").versione(), "servizi": [
            {"id": i, "quota": barra(i), "nome": servizi_ricerca.PER_ID[i].nome, "spuntato": i in settings["attivi"],
             "chiave": keys.presente(i), "ricerca_collegata": servizi_ricerca.PER_ID[i].adattatore is not None,
             "pronto": i in pronti, "link_chiave": servizi_ricerca.PER_ID[i].chiavi}
            for i in settings["ordine"]]}

    def modelli(args):
        """Modelli locali (.gguf) che «cambia modello» elencherebbe, e quello in uso."""
        from local_model import scelta_modello
        from local_model import profili_famiglia, registro_modelli
        models = scelta_modello.elenca_modelli()
        in_uso = scelta_modello.modello_in_uso()
        slots = registro_modelli.caselle(models, in_uso)
        try:
            profilo = profili_famiglia.slot_ricordato(in_uso) if in_uso else None
        except (OSError, ValueError):
            profilo = None
        return {"ok": True, "in_uso": in_uso, "profilo_in_uso": profilo,
                "caselle": {str(n): (str(m) if m else None) for n, m in slots.items()},
                "mancanti": [str(p) for p in registro_modelli.mancanti()],
                "versione": __import__("impostazioni_menu").versione(),
                "cartelle": [str(f) for f in scelta_modello.cartelle_modelli()],
                "modelli": [{"numero": n, "nome": scelta_modello.nome_breve(m), "percorso": str(m)}
                            for n, m in enumerate(models, 1)]}

    def telegram_(args):
        view = telegram()
        if view is None:
            return {"ok": False, "errore": "vista Telegram non presente"}
        view.aggiorna(repeat=False)
        return {"ok": True, "icona": view.button.cget("text"), "colore": view.button.cget("fg"),
                "stato": getattr(view, "status_text", ""),
                "risposte_automatiche": bool(view.auto_var.get())}

    return {"impostazioni": impostazioni, "addon": addon, "ricordi": ricordi, "chat": chat,
            "prompt": prompt, "online": online, "prova_servizio": prova_servizio, "telegram": telegram_,
            "ricerca": ricerca, "modelli": modelli}
