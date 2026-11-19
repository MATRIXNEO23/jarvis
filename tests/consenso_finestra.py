"""Test: consenso GPT con finestra Sì/No simulata (comportamento 054).

Dalla 055 `confirm_gpt_inference` chiede a voce e in chat, senza finestra. Molti test del
trasporto GPT simulano la risposta dell'utente con `messagebox.askyesno`: questa funzione
sostituisce la conferma reale con la stessa logica di prima, così quei test continuano a
provare il percorso run_gpt -> invio. La conferma a voce vera è provata in test_055_*."""


def installa(env):
    def confirm_gpt_inference(detail):
        if (env["online_consent_pending"] or env["closing"] or env["busy_gpt"]
                or not env["gpt_spuntato"]() or not env["active_gpt"]):
            return False
        epoch = env["conversation_epoch"]
        env["online_consent_pending"] = True
        try:
            approved = env["messagebox"].askyesno(
                "Conferma GPT online", "Inviare a GPT online per questa richiesta?\n\n" + detail,
                parent=env.get("root"), default="no")
        finally:
            env["online_consent_pending"] = False
        return bool(approved and epoch == env["conversation_epoch"] and not env["closing"]
                    and env["gpt_spuntato"]() and env["active_gpt"] and not env["busy_gpt"])
    env["confirm_gpt_inference"] = confirm_gpt_inference
    return env
