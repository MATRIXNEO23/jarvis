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
        import servizi_online
        from servizi_online import quote
        settings = servizi_online.carica_impostazioni()
        keys = servizi_online.Chiavi()
        services = []
        for ident in settings["ordine"]:
            service = servizi_online.PER_ID[ident]
            state = quote.stato(ident, limite_utente=settings.get("limiti", {}).get(ident))
            services.append({"id": ident, "nome": service.nome, "spuntato": ident in settings["attivi"],
                             "chiave": bool(keys.leggi(ident)), "oggi": state.get("testo"),
                             "colore": state.get("colore")})
        return {"ok": True, "usa_sempre": settings["usa_sempre"],
                "proponi_lunghe": settings["proponi_lunghe"],
                "avviso_quota": settings.get("avviso_quota"),
                "conferma_token": settings.get("conferma_token"), "servizi": services}

    def ricerca(args):
        """Servizi di ricerca (052): spuntati, con chiave, collegati. Mai la chiave."""
        import servizi_ricerca
        settings = servizi_ricerca.carica_impostazioni()
        keys = servizi_ricerca.chiavi()
        pronti = {s.id for s in servizi_ricerca.pronti(settings, keys)}
        return {"ok": True, "servizi": [
            {"id": i, "nome": servizi_ricerca.PER_ID[i].nome, "spuntato": i in settings["attivi"],
             "chiave": keys.presente(i), "ricerca_collegata": servizi_ricerca.PER_ID[i].adattatore is not None,
             "pronto": i in pronti, "link_chiave": servizi_ricerca.PER_ID[i].chiavi}
            for i in settings["ordine"]]}

    def modelli(args):
        """Modelli locali (.gguf) che «cambia modello» elencherebbe, e quello in uso."""
        from local_model import scelta_modello
        models = scelta_modello.elenca_modelli()
        return {"ok": True, "in_uso": scelta_modello.modello_in_uso(),
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
            "prompt": prompt, "online": online, "telegram": telegram_,
            "ricerca": ricerca, "modelli": modelli}
