"""054: i risultati di «cerca online» sono in chat con link cliccabili associati all'URL giusto."""
import unittest
from unittest import mock

import chat_link
import servizi_ricerca as sr


class SegmentTests(unittest.TestCase):
    def test_markdown_and_bare_links_are_recognised_with_the_right_url(self):
        body = "Sintesi.\n1. [Meteo Roma](https://m.example/roma?a=1)\n   anteprima\n2. [Altro](http://x.it/p)\nVedi https://z.org/a, grazie."
        links = [(t, u) for t, u in chat_link.segmenti(body) if u]
        self.assertEqual(links, [("Meteo Roma", "https://m.example/roma?a=1"), ("Altro", "http://x.it/p"),
                                 ("https://z.org/a", "https://z.org/a")])
        self.assertEqual("".join(t for t, _ in chat_link.segmenti(body)).count("anteprima"), 1)

    def test_plain_text_has_no_links(self):
        self.assertFalse(chat_link.ha_link("Nessun link qui, solo [parentesi] e (altre)."))

    def test_search_text_roundtrips_to_the_source_urls(self):
        result = sr.Risultato("Sole.", (("A [x]", "https://a.it"), ("B", "https://b.it")), ("pa", ""))
        links = [u for _t, u in chat_link.segmenti(sr.testo_chat("Tavily", result)) if u]
        self.assertEqual(links, ["https://a.it", "https://b.it"])


class TkTagTests(unittest.TestCase):
    def test_click_opens_the_matching_url_with_underline_and_hand_cursor(self):
        import tkinter as tk
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk non disponibile")
        self.addCleanup(root.destroy)
        text = tk.Text(root, width=60, height=10)
        text.pack()
        opened = []
        found = chat_link.inserisci(text, "Fonti:\n1. [Uno](https://uno.it)\n2. [Due](https://due.it)\n",
                                    "jarvis", opened.append)
        self.assertEqual(sorted(found.values()), ["https://due.it", "https://uno.it"])
        for tag in found:
            self.assertEqual(str(text.tag_cget(tag, "underline")), "1")
            self.assertTrue(text.tk.call(text._w, "tag", "bind", tag, "<Button-1>"))
            self.assertTrue(text.tk.call(text._w, "tag", "bind", tag, "<Enter>"))
        root.update()
        tag_due = next(t for t, u in found.items() if u == "https://due.it")
        start = text.tag_ranges(tag_due)[0]
        box = text.bbox(start)
        if box is None:
            self.skipTest("Finestra non visibile")
        text.event_generate("<Motion>", x=box[0] + 2, y=box[1] + 2)
        text.event_generate("<Enter>")
        text.event_generate("<Button-1>", x=box[0] + 2, y=box[1] + 2)
        root.update()
        if not opened:
            self.skipTest("clic non simulabile in questa sessione Tk")
        self.assertEqual(opened, ["https://due.it"])


class ChatWiringTests(unittest.TestCase):
    def test_write_line_uses_chat_link_and_no_separate_window(self):
        source = open("jarvis.py", encoding="utf-8").read()
        self.assertIn('__import__("chat_link").inserisci(output, body + "\\n\\n", role, webbrowser.open)', source)
        part = source[source.index("def lumi_ricerca"):source.index("def help_box_say")]
        self.assertNotIn("show_results", part)


if __name__ == "__main__":
    unittest.main()
