import time
import tkinter as tk
import unittest
from datetime import datetime, timedelta, timezone

import chat_bolle
import telegram_vista as tv

A = {"id": 11, "name": "Mario", "enabled": True}
B = {"id": 22, "name": "Anna", "enabled": False}


def iso(seconds_ago):
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)).isoformat(timespec="seconds")


class FakeWorkspace:
    def __init__(self):
        self.events = {11: []}
        self.read = set()

    def telegram_counts(self, peer):
        unread = sum(1 for e in self.events.get(peer, [])
                     if e["direction"] == "incoming" and (peer, e["message_id"]) not in self.read)
        return {"unread": unread}

    def telegram_activity(self, peer, limit=16):
        return tuple(reversed(self.events.get(peer, [])))[:limit]

    def mark_telegram_read(self, peer):
        for e in self.events.get(peer, []):
            self.read.add((peer, e["message_id"]))


class StatoTest(unittest.TestCase):
    def setUp(self):
        self.ws = FakeWorkspace()

    def s(self, auto=True):
        return tv.stato(auto, [A], self.ws.telegram_counts, self.ws.telegram_activity)

    def test_colori(self):
        self.assertEqual(self.s(auto=False)[0], tv.ROSSO)
        self.assertEqual(self.s()[:2], (tv.AZZURRO, 0))
        self.ws.events[11].append({"direction": "incoming", "kind": "text", "text": "ciao",
                                   "when": iso(10), "message_id": 1})
        self.assertEqual(self.s()[:2], (tv.AZZURRO, 1))            # appena arrivato
        self.ws.events[11][0]["when"] = iso(600)
        self.assertEqual(self.s()[:2], (tv.ARANCIONE, 1))          # nessuna risposta
        self.ws.events[11].append({"direction": "outgoing", "kind": "voice", "text": "eccomi",
                                   "when": iso(5), "message_id": 2})
        self.assertEqual(self.s()[:2], (tv.VERDE, 1))              # ha risposto
        self.ws.mark_telegram_read(11)
        self.assertEqual(self.s()[:2], (tv.AZZURRO, 0))            # guardato: torna azzurro


class VistaTest(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        self.root.withdraw()
        self.ws = FakeWorkspace()
        self.ws.events[11] = [
            {"direction": "incoming", "kind": "text", "text": "Ci sei?", "when": iso(300), "message_id": 1},
            {"direction": "outgoing", "kind": "voice", "text": "Sì, arrivo", "when": iso(200), "message_id": 2}]
        self.settings = {"telegram_contacts": [dict(A), dict(B)]}
        self.auto = tk.BooleanVar(master=self.root, value=True)
        self.saved, self.toggles, self.shown = [], [], []
        self.button = tk.Button(self.root)
        self.text = tk.Text(self.root)
        self.bolle = chat_bolle.Bolle(self.text, copy=print, read=print, regenerate=print)

        def save(rows):
            self.saved.append(rows)
            self.settings["telegram_contacts"] = rows
            self.auto.set(False)                                    # come il salvataggio vero
            return True

        self.view = tv.Telegram(
            self.root, self.button, workspace=lambda: self.ws, settings=lambda: self.settings,
            auto_var=self.auto,
            contacts=lambda: [c for c in self.settings["telegram_contacts"] if c["enabled"]],
            save_contacts=save, toggle_auto=lambda: self.toggles.append(self.auto.get()),
            open_manager=lambda: None,
            show_chat=lambda title, items, action: (self.shown.append(title),
                                                    self.bolle.messaggi(title, items, action)),
            send_voice=lambda *a: True, ask_text=lambda *a: None, period_ms=10 ** 7)

    def tearDown(self):
        self.view.close()
        self.root.destroy()

    def test_icona_chat_e_spunta_veloce(self):
        self.assertEqual(self.button.cget("text"), "✈ Telegram 1")
        self.assertEqual(self.button.cget("fg"), tv.VERDE)
        self.assertEqual([label for label, _ in self.view.voci_menu()], ["✈ Mario"])
        self.view.apri_chat(A)
        self.assertEqual(self.shown, ["✈ Mario"])
        content = self.text.get("1.0", "end")
        self.assertLess(content.index("Ci sei?"), content.index("Sì, arrivo"))
        self.assertEqual(self.button.cget("text"), "✈ Telegram")             # letto: torna azzurro
        self.assertEqual(self.button.cget("fg"), tv.AZZURRO)
        self.view.open()
        self.view.vars[22].set(True)
        self.view._toggle_contact(B)
        self.assertTrue(self.saved[-1][1]["enabled"])
        self.assertEqual(self.toggles, [True])                      # risposte riaccese
        self.assertEqual(len(self.view.voci_menu()), 2)

    def test_spente_rosso(self):
        self.auto.set(False)
        self.view.aggiorna(repeat=False)
        self.assertEqual(self.button.cget("fg"), tv.ROSSO)


if __name__ == "__main__":
    unittest.main()
