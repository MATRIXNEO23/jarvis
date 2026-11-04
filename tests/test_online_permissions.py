import tempfile
import unittest
from pathlib import Path

from local_model.online_permissions import OnlinePermissionPolicy


class OnlinePermissionsTests(unittest.TestCase):
    def test_unknown_features_are_denied_even_with_confirmation(self):
        p = OnlinePermissionPolicy()
        self.assertEqual(p.decide("web.search"), "local_only")
        self.assertEqual(p.decide("web.search", confirmed=True), "local_only")

    def test_consent_only_for_specific_function_and_request(self):
        p = OnlinePermissionPolicy()
        p.set_mode("web.search", "ask")
        self.assertEqual(p.decide("web.search"), "request_consent")
        self.assertEqual(p.decide("web.search", confirmed=True), "online_permitted")
        self.assertEqual(p.decide("web.search"), "request_consent")
        self.assertEqual(p.decide("telegram.send", confirmed=True), "local_only")

    def test_explicitly_allowed_is_scoped(self):
        p = OnlinePermissionPolicy()
        p.set_mode("web.search", "allowed")
        self.assertEqual(p.decide("web.search"), "online_permitted")
        self.assertEqual(p.decide("web.navigate"), "local_only")

    def test_persistence_and_corrupt_data_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "permissions.json"
            p = OnlinePermissionPolicy()
            p.set_mode("web.search", "ask")
            p.save(path)
            self.assertEqual(OnlinePermissionPolicy.load(path).mode("web.search"), "ask")
            path.write_text('{"version":1,"rules":{"web.search":"always_yes"}}', encoding="utf-8")
            with self.assertRaises(ValueError):
                OnlinePermissionPolicy.load(path)

    def test_invalid_capability_and_mode_rejected(self):
        p = OnlinePermissionPolicy()
        for name in ("", "../foo", "web search", "__proto__"):
            with self.assertRaises(ValueError):
                p.set_mode(name, "allowed")
        with self.assertRaises(ValueError):
            p.set_mode("web.search", "auto")


if __name__ == "__main__":
    unittest.main()
