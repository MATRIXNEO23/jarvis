"""Telegram dentro Lumi (15/11 sera, punto 5 della lista concordata).

- Icona «✈» nella fila in alto, con un numerino dei messaggi nuovi:
    azzurrina  risposte automatiche attive, niente di nuovo (o già guardato);
    verde      sono arrivati messaggi e Lumi ha risposto;
    arancione  messaggi senza risposta da più di ATTESA_RISPOSTA secondi (bloccato?);
    rossa      risposte automatiche spente.
  Torna azzurrina quando apri la chat di quel contatto.
- Clic sull'icona: tendina verticale con i contatti già caricati, ognuno con la sua spunta
  (autorizzato o no, senza ricaricare tutti i contatti), messaggi nuovi e «apri chat»;
  sotto «Risposte automatiche» e «Gestisci contatti…».
- Nel menu laterale una voce per ogni contatto autorizzato: apre la conversazione a bolle
  (solo i messaggi passati da Lumi con quel contatto) con «Manda un vocale a …».
Le chat personali complete restano fuori (pesanti e accesso a tutto l'account).
"""
from __future__ import annotations

import time
import tkinter as tk
from datetime import datetime, timezone

AZZURRO, VERDE, ARANCIONE, ROSSO = "#46ccfa", "#5fd38d", "#f2a33a", "#ff5c5c"
ATTESA_RISPOSTA = 120
BG, PANEL, TEXT, MUTED, CYAN = "#020d17", "#06192a", "#bfeeff", "#6f8fa3", "#46ccfa"


def _secondi_fa(when: str, now: float) -> float:
    try:
        moment = datetime.fromisoformat(str(when).replace("Z", "+00:00"))
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
        return now - moment.timestamp()
    except (TypeError, ValueError):
        return 0.0


def stato(auto_on: bool, contacts, counts, activity, now: float | None = None):
    """(colore, numero di messaggi nuovi, testo) per l'icona.

    counts(peer) -> {'unread'}; activity(peer) -> eventi recenti (il più nuovo per primo)."""
    now = time.time() if now is None else now
    if not auto_on:
        return ROSSO, 0, "Risposte automatiche spente"
    unread_total, waiting, answered = 0, False, False
    for contact in contacts:
        unread = counts(contact["id"]).get("unread", 0)
        if not unread:
            continue
        unread_total += unread
        events = list(activity(contact["id"]))
        last_in = next((e for e in events if e["direction"] == "incoming"), None)
        replied = bool(events) and events[0]["direction"] == "outgoing"
        if replied:
            answered = True
        elif last_in is not None and _secondi_fa(last_in["when"], now) > ATTESA_RISPOSTA:
            waiting = True
    if waiting:
        return ARANCIONE, unread_total, "Messaggi senza risposta"
    if answered:
        return VERDE, unread_total, "Messaggi nuovi, Lumi ha risposto"
    return AZZURRO, unread_total, ("Messaggi nuovi" if unread_total else "Attivo, niente di nuovo")


class Telegram:
    """Collega icona, tendina e conversazioni a bolle. Tutto sul thread di Tk."""

    def __init__(self, root, button, *, workspace, settings, auto_var, contacts,
                 save_contacts, toggle_auto, open_manager, show_chat, send_voice, ask_text,
                 period_ms: int = 5000):
        self.root = root
        self.button = button
        self.workspace = workspace          # () -> WorkspaceMemory | None
        self.settings = settings            # () -> dict delle impostazioni
        self.auto_var = auto_var
        self.contacts = contacts            # () -> contatti autorizzati
        self.save_contacts = save_contacts  # rows -> bool (salvataggio esistente)
        self.toggle_auto = toggle_auto
        self.open_manager = open_manager
        self.show_chat = show_chat          # (titolo, [(intestazione, ruolo, testo)], azione)
        self.send_voice = send_voice        # (peer, nome, testo) -> bool
        self.ask_text = ask_text
        self.period_ms = period_ms
        self.popup = None
        button.configure(command=self.toggle, power_command=self._power)
        root.bind_all("<Button-1>", self._click_anywhere, add="+")
        self.aggiorna()

    def _power(self):
        """056b: ⏻ del tasto Telegram = risposte automatiche accese/spente."""
        self.auto_var.set(not self.auto_var.get())   # la funzione legge la variabile già girata
        self.toggle_auto()
        self.aggiorna(repeat=False)

    # --- icona -------------------------------------------------------------------------------
    def _counts(self, peer):
        ws = self.workspace()
        try:
            return ws.telegram_counts(peer) if ws is not None else {}
        except Exception:
            return {}

    def _activity(self, peer, limit=16):
        ws = self.workspace()
        try:
            return ws.telegram_activity(peer, limit) if ws is not None else ()
        except Exception:
            return ()

    def aggiorna(self, repeat: bool = True):
        colour, unread, text = stato(bool(self.auto_var.get()), self.contacts(),
                                     self._counts, self._activity)
        try:
            self.button.configure(text=("✈ Telegram %d" % unread) if unread else "✈ Telegram",
                                  power_on=bool(self.auto_var.get()))
            self.status_text = text
        except tk.TclError:
            return
        if repeat:
            self.root.after(self.period_ms, self.aggiorna)

    # --- conversazione -----------------------------------------------------------------------
    def apri_chat(self, contact):
        events = list(reversed(self._activity(contact["id"], 50)))
        items = []
        for event in events:
            mine = event["direction"] == "outgoing"
            text = event.get("text") or ("(messaggio vocale)" if event.get("kind") == "voice"
                                         else "(%s)" % event.get("kind", "messaggio"))
            items.append(("◉  LUMI" if mine else "●  " + contact["name"],
                          "jarvis" if mine else "utente", text))
        ws = self.workspace()
        if ws is not None:
            try:
                ws.mark_telegram_read(contact["id"])
            except Exception:
                pass
        self.show_chat("✈ " + contact["name"], items,
                       ("✎ Manda un vocale a " + contact["name"], lambda: self.scrivi(contact)))
        self.aggiorna(repeat=False)

    def scrivi(self, contact):
        text = self.ask_text("Telegram", "Messaggio per %s (Lumi lo manda come vocale):" % contact["name"])
        if text and text.strip():
            if self.send_voice(contact["id"], contact["name"], text.strip()):
                self.root.after(4000, lambda: self.apri_chat(contact))

    def voci_menu(self):
        """Voci per il menu laterale: una per contatto autorizzato."""
        return [("✈ " + c["name"], lambda c=c: self.apri_chat(c)) for c in self.contacts()]

    # --- tendina -----------------------------------------------------------------------------
    def toggle(self):
        if self.popup is not None:
            self.close()
        else:
            self.open()

    def close(self):
        popup, self.popup = self.popup, None
        if popup is not None:
            try:
                popup.destroy()
            except tk.TclError:
                pass

    def _click_anywhere(self, event):
        if self.popup is None:
            return
        try:
            inside = str(event.widget).startswith(str(self.popup)) or event.widget is self.button
        except Exception:
            inside = False
        if not inside:
            self.close()

    def open(self):
        popup = tk.Toplevel(self.root, bg=PANEL, highlightthickness=1, highlightbackground="#1191c6")
        popup.overrideredirect(True)
        try:
            popup.attributes("-topmost", True)
        except tk.TclError:
            pass
        self.popup = popup
        self._fill(popup)
        popup.update_idletasks()
        x = self.button.winfo_rootx() + self.button.winfo_width() - popup.winfo_reqwidth()
        y = self.button.winfo_rooty() + self.button.winfo_height() + 2
        popup.geometry("+%d+%d" % (max(0, x), y))
        popup.bind("<Escape>", lambda _e: self.close())

    def _fill(self, popup):
        tk.Label(popup, text="Telegram — " + getattr(self, "status_text", ""), bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x", padx=10, pady=(8, 4))
        rows = list(self.settings().get("telegram_contacts", []))
        if not rows:
            tk.Label(popup, text="Nessun contatto caricato: usa «Gestisci contatti…».", bg=PANEL,
                     fg=MUTED, font=("Segoe UI", 9)).pack(fill="x", padx=10)
        self.vars = {}
        for contact in rows:
            line = tk.Frame(popup, bg=PANEL)
            line.pack(fill="x", padx=6, pady=1)
            var = tk.BooleanVar(value=contact.get("enabled") is True)
            self.vars[contact["id"]] = var
            unread = self._counts(contact["id"]).get("unread", 0) if contact.get("enabled") else 0
            tk.Checkbutton(line, text=contact["name"] + ("   (%d nuovi)" % unread if unread else ""),
                           variable=var, command=lambda c=contact: self._toggle_contact(c),
                           bg=PANEL, fg=TEXT, selectcolor=BG, activebackground=PANEL,
                           anchor="w", font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True)
            if contact.get("enabled"):
                link = tk.Label(line, text="apri chat", bg=PANEL, fg=CYAN, cursor="hand2",
                                font=("Segoe UI", 8, "underline"))
                link.pack(side="right", padx=6)
                link.bind("<Button-1>", lambda _e, c=contact: (self.close(), self.apri_chat(c)))
        tk.Frame(popup, bg="#164257", height=1).pack(fill="x", padx=8, pady=4)
        tk.Checkbutton(popup, text="Risposte automatiche", variable=self.auto_var,
                       command=self._toggle_auto, bg=PANEL, fg=TEXT, selectcolor=BG,
                       activebackground=PANEL, anchor="w", font=("Segoe UI", 9)).pack(fill="x", padx=8)
        manage = tk.Label(popup, text="Gestisci contatti…", bg=PANEL, fg=CYAN, cursor="hand2",
                          font=("Segoe UI", 9, "underline"), anchor="w")
        manage.pack(fill="x", padx=10, pady=(4, 8))
        manage.bind("<Button-1>", lambda _e: (self.close(), self.open_manager()))

    def _toggle_contact(self, contact):
        """Spunta veloce: salva con il salvataggio esistente (che per sicurezza ferma le
        risposte automatiche) e, se erano accese, le riaccende con la nuova lista."""
        was_on = bool(self.auto_var.get())
        rows = [dict(c) for c in self.settings().get("telegram_contacts", [])]
        for row in rows:
            if row["id"] == contact["id"]:
                row["enabled"] = bool(self.vars[contact["id"]].get())
        if self.save_contacts(rows) and was_on and any(r["enabled"] for r in rows):
            self.auto_var.set(True)
            self.toggle_auto()
        self.close()
        self.aggiorna(repeat=False)

    def _toggle_auto(self):
        self.toggle_auto()
        self.aggiorna(repeat=False)
