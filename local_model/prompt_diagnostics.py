"""Opt-in, RAM-only explanation of one exact Gemma conversation prompt.

No persistence, network, inference, desktop action or automatic logging.
Per-piece token counts are isolated estimates, not additive BPE accounting.
"""
from .native_provider import format_gemma_messages


def render_prompt_diagnostic(*, messages, sections, count, total_tokens, budget,
                             context_size, max_output, history_limit, mode,
                             restored, selection_metrics, warning=""):
    """Show exact serialized input and owner-provided provenance, on request."""
    raw = format_gemma_messages(messages)
    if not isinstance(total_tokens, int) or total_tokens < 1:
        raise ValueError("Conteggio prompt non valido.")
    if len(raw) > 120000:
        raise ValueError("Prompt diagnostico troppo esteso.")
    lines = [
        "DIAGNOSTICA PROMPT GEMMA — SOLO RAM, NON SALVATA",
        "Generato da: jarvis.py → conversation_router.native_intent_context_for_request",
        "              → NativeConversationSession.prepare_turn → format_gemma_messages",
        "Destinazione: NativeChatAdapter.call('ask') → KoboldCpp (locale)",
        "Modalità: " + ("CHAT naturale" if mode == "chat" else "JSON / azioni validate"),
        "Token totali prompt: " + str(total_tokens) + " / " + str(budget)
        + " (tokenizer nativo)" if callable(count) else
        "Token totali prompt: " + str(total_tokens) + " / " + str(budget)
        + " (conteggio prudenziale in caratteri; NON token)",
        "Context Size: " + str(context_size) + " | Max Output: " + str(max_output)
        + " | Margine sicurezza: 128",
        "Limite cronologia+ricordi: " + str(history_limit)
        + " | Coppie ripristinate dall'archivio: " + str(restored),
        "Selezione cronologia: " + ", ".join(
            str(key) + "=" + str(value) for key, value in sorted(selection_metrics.items())),
    ]
    if warning:
        lines.append("Avviso selezione: " + warning)
    lines.extend([
        "",
        "COMPONENTI E PROVENIENZA — token isolati approssimativi, NON sommabili",
        "(Il tokenizer può unire parole attraverso i confini; solo il totale sopra è esatto.)",
    ])
    for index, section in enumerate(sections, 1):
        label, source, text = section
        if not isinstance(text, str):
            raise TypeError("Sezione prompt non testuale.")
        if text and callable(count):
            estimate = count(text)
            token_info = str(estimate) + " token isolati circa"
        else:
            token_info = str(len(text)) + " caratteri" if text else "non incluso (0)"
        lines.extend([
            "",
            str(index) + ". " + label,
            "Origine: " + source,
            "Peso: " + token_info + "; lunghezza " + str(len(text)) + " caratteri",
            "Testo: " + (repr(text) if text else "(non inviato)"),
        ])
    lines.extend([
        "",
        "PROMPT EFFETTIVO, ESATTO, DOPO IL TEMPLATE GEMMA",
        "(Comprende delimitatori dei ruoli e testo passato al backend.)",
        "----- INIZIO -----",
        raw,
        "----- FINE -----",
        "",
        "PRIVACY: possono comparire domande, conversazioni e ricordi privati.",
        "Non viene scritto alcun file; copia negli appunti solo su tua richiesta.",
        "La diagnostica non modifica il prompt o le regole sui comandi.",
    ])
    return "\n".join(lines)
