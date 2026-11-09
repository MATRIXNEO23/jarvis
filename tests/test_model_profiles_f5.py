"""Windows CI unit tests for opt-in F5 profile validation. No GGUF needed."""
import unittest
from dataclasses import FrozenInstanceError, replace

from local_model.model_profiles_f5 import (
    LocalModelProfile, ProfileError, default_profiles, parse_profile,
)


class TestF5Profiles(unittest.TestCase):
    def test_presets_do_not_load_models(self):
        gemma, qwen = default_profiles()
        self.assertEqual((gemma.family, qwen.family), ("gemma", "qwen"))
        self.assertEqual((gemma.backend, qwen.backend), ("embedded", "koboldcpp"))

    def test_configurable_context_and_generation(self):
        profile = replace(default_profiles()[1], context_size=1536, max_output=512,
                          threads=2, blas_threads=2, temperature=0.8, top_p=0.92, seed=-1)
        self.assertEqual(profile.context_size, 1536)
        self.assertEqual(profile.max_output, 512)

    def test_rejects_unrecognized_family_and_backend(self):
        for field, value in (("family", "other"), ("backend", "remote")):
            with self.subTest(field=field), self.assertRaises(ProfileError):
                replace(default_profiles()[0], **{field: value})

    def test_rejects_invalid_ints_and_bounds(self):
        for field, value in (
            ("context_size", 0), ("context_size", True), ("max_output", 0),
            ("max_output", 999999), ("threads", 0), ("threads", 1.5),
            ("blas_threads", 65), ("seed", -2),
        ):
            with self.subTest(field=field, value=value), self.assertRaises(ProfileError):
                replace(default_profiles()[0], **{field: value})

    def test_rejects_invalid_sampler(self):
        for field, value in (
            ("temperature", float("nan")), ("temperature", 3),
            ("top_p", 0), ("top_p", float("inf")), ("top_p", "0.9"),
        ):
            with self.subTest(field=field), self.assertRaises(ProfileError):
                replace(default_profiles()[0], **{field: value})

    def test_rejects_output_larger_than_context(self):
        with self.assertRaises(ProfileError):
            replace(default_profiles()[0], max_output=2048)

    def test_rejects_secrets_and_unknown_fields(self):
        data = dict(vars(default_profiles()[0]), api_key="secret")
        with self.assertRaises(ProfileError) as cm:
            parse_profile(data)
        self.assertNotIn("secret", str(cm.exception))

    def test_rejects_bad_identifier(self):
        with self.assertRaises(ProfileError):
            replace(default_profiles()[0], profile_id="../unsafe")

    def test_profile_is_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            default_profiles()[0].context_size = 999

    def test_parse_valid_profile(self):
        p = default_profiles()[0]
        self.assertEqual(parse_profile(vars(p)), p)

    def test_does_not_import_runtime_or_network(self):
        import sys
        self.assertNotIn("jarvis", sys.modules)
        self.assertNotIn("local_model.kobold_server_canary", sys.modules)


if __name__ == "__main__":
    unittest.main()
