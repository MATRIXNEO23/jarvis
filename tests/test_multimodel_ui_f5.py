"""Pure F5.2 validation tests; never create Tk or load a GGUF."""
import inspect
import unittest

from local_model.model_profiles_f5 import ProfileError, default_profiles
from local_model.multimodel_ui_f5 import apply_profile_draft, _FIELDS


def raw_fields(profile):
    return {key: str(getattr(profile, key)) for key, _ in _FIELDS}


class TestF52Draft(unittest.TestCase):
    def test_gemma_valid_draft(self):
        original = default_profiles()[0]
        values = raw_fields(original)
        values["context_size"] = "1536"
        values["max_output"] = "512"
        changed = apply_profile_draft(original, values)
        self.assertEqual(changed.context_size, 1536)
        self.assertEqual(changed.max_output, 512)
        self.assertEqual(original.context_size, 1024)

    def test_qwen_valid_draft(self):
        original = default_profiles()[1]
        values = raw_fields(original)
        values["temperature"] = "0.8"
        changed = apply_profile_draft(original, values)
        self.assertEqual(changed.family, "qwen")
        self.assertEqual(changed.temperature, 0.8)

    def test_invalid_values_do_not_change_source(self):
        original = default_profiles()[0]
        for key, value in (
            ("context_size", ""), ("context_size", "NaN"),
            ("max_output", "2048"), ("threads", "0"),
            ("temperature", "nan"), ("top_p", "inf"),
            ("seed", "-2")
        ):
            with self.subTest(key=key, value=value):
                data = raw_fields(original)
                data[key] = value
                with self.assertRaises(ProfileError):
                    apply_profile_draft(original, data)
                self.assertEqual(original, default_profiles()[0])

    def test_preview_does_not_import_or_call_backend(self):
        import local_model.multimodel_ui_f5 as ui
        source = inspect.getsource(ui)
        for forbidden in ("KoboldServerCanary(", "NativeGemmaBridge(",
                          ".generate(", ".load(", ".save(", "subprocess.",
                          "requests.", "urllib."):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
