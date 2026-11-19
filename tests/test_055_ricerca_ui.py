"""055 F: menu a tendina RICERCA, impostazioni modelli solo in «Modelli», quota Tavily dall'API,
adattatori Exa/Firecrawl/Linkup (API verificate sulla documentazione ufficiale il 17/11)."""
import unittest
from pathlib import Path
from unittest import mock

from online import servizi_ricerca as sr
from online.servizi_ricerca import quota
from online.servizi_ricerca.servizi import exa, firecrawl, linkup, tavily

ROOT = Path(__file__).resolve().parents[1]
JARVIS = (ROOT / "jarvis.py").read_text(encoding="utf-8")


class QuotaTests(unittest.TestCase):
    def setUp(self):
        quota._CACHE.clear()

    def test_tavily_quota_is_read_from_the_usage_endpoint(self):
        get = mock.Mock(return_value={"key": {"usage": 40, "limit": None},
                                      "account": {"current_plan": "Researcher", "plan_usage": 250, "plan_limit": 1000}})
        info = quota.reale("tavily", "tvly-x", get=get)
        get.assert_called_once_with("https://api.tavily.com/usage", "tvly-x", 8.0)
        self.assertEqual((info["mese"], info["limite"]), (250, 1000))
        self.assertFalse(info["stima"])
        self.assertIn("letto da Tavily", info["testo"])
        quota.reale("tavily", "tvly-x", get=get)                  # cache: nessuna seconda chiamata
        self.assertEqual(get.call_count, 1)

    def test_without_endpoint_or_on_error_the_label_is_ricerche_rilevate(self):
        self.assertIsNone(quota.reale("exa", "k", get=mock.Mock()))
        self.assertIsNone(quota.reale("tavily", "k", get=mock.Mock(side_effect=OSError("rete"))))
        info = quota.stato("exa", 0, oggi="2026-11-17", data={})
        self.assertIn("ricerche rilevate", info["testo"])

    def test_quota_servizio_falls_back_to_local_counters(self):
        keys = mock.Mock()
        keys.leggi.return_value = ""
        with mock.patch.object(quota, "reale", return_value=None), \
                mock.patch.object(quota, "stato", return_value={"usato": None, "testo": "ricerche rilevate: 0"}):
            self.assertIn("rilevate", sr.quota_servizio("exa", keys)["testo"])


class AdattatoriTests(unittest.TestCase):
    def test_exa(self):
        post = mock.Mock(return_value={"results": [{"title": "T", "url": "https://a.it/x", "highlights": ["uno", "due"]}]})
        res = exa.cerca("k", "q", False, 5, post)
        self.assertEqual(post.call_args.args[0], "https://api.exa.ai/search")
        self.assertEqual(post.call_args.args[2]["contents"], {"highlights": True})
        self.assertEqual(res.link, (("T", "https://a.it/x"),))
        self.assertIn("uno due", res.riassunto)

    def test_firecrawl_v2(self):
        post = mock.Mock(return_value={"success": True, "data": {"web": [
            {"title": "F", "url": "https://b.it", "description": "desc"}]}})
        res = firecrawl.cerca("k", "q", True, 5, post)
        self.assertEqual(post.call_args.args[0], "https://api.firecrawl.dev/v2/search")
        self.assertEqual(post.call_args.args[2], {"query": "q", "limit": 8})
        self.assertEqual((res.link, res.riassunto), ((("F", "https://b.it"),), "desc"))

    def test_linkup_sourced_answer(self):
        post = mock.Mock(return_value={"answer": "Risposta", "sources": [
            {"name": "L", "url": "https://c.it", "snippet": "s"}]})
        res = linkup.cerca("k", "q", False, 5, post)
        body = post.call_args.args[2]
        self.assertEqual((body["q"], body["depth"], body["outputType"]), ("q", "fast", "sourcedAnswer"))
        self.assertEqual((res.riassunto, res.link), ("Risposta", (("L", "https://c.it"),)))

    def test_all_four_services_are_connected(self):
        for service in sr.SERVIZI:
            self.assertIsNotNone(service.adattatore, service.id)
        self.assertEqual(tavily.SERVIZIO.id, "tavily")


class WiringTests(unittest.TestCase):
    def test_top_toggle_replaced_by_dropdown_with_checks_and_quota_bars(self):
        self.assertNotIn("toggle_ricerca_online", JARVIS)
        self.assertIn('"menu_tendine").MenuRicerca(', JARVIS)
        menu = (ROOT / "menu_tendine.py").read_text(encoding="utf-8")
        self.assertIn("Checkbutton", menu)
        self.assertIn("quota_servizio", menu)
        self.assertIn("create_rectangle", menu)

    def test_model_settings_live_only_in_modelli_and_addon_page_has_the_button(self):
        self.assertIn('text="Apri impostazioni modelli"', JARVIS)
        self.assertIn('"modello_locale": lambda box: build_model_addon_section(box)', JARVIS)
        self.assertIn("costruisci_sezione(\n            assistant_settings_frame", JARVIS)
        native_ui = (ROOT / "local_model" / "native_ui.py").read_text(encoding="utf-8")
        self.assertNotIn("costruisci_sezione", native_ui)

    def test_window_buttons_already_exist_and_sit_in_the_corner(self):
        chrome = (ROOT / "window_chrome.py").read_text(encoding="utf-8")
        for name in ('"minimize"', '"maximize"', '"close"'):
            self.assertIn(name, chrome)
        self.assertIn("_jarvis_window_anchor", chrome)
        self.assertIn("_jarvis_window_anchor", (ROOT / "animated_hud.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
