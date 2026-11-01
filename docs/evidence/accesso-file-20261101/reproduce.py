"""Development-only baseline observations; never installed with Jarvis.

Run with the extracted b936879 source directory as the sole argument.
All created files and add-on records live in a TemporaryDirectory.
No OS launches, GPT calls, network, or reads of personal files.
"""
import json
from pathlib import Path
import sys
import tempfile


def main():
    source = Path(sys.argv[1]).resolve(strict=True)
    sys.path.insert(0, str(source))
    from addon_manager import AddonError, AddonManager, validate_manifest
    from capability_registry import CapabilityRejected
    from dialogue_focus import is_ambiguous_short_reply
    from live_capabilities import LiveCapabilityRegistry
    from local_engine import LocalEngine
    from voice_control import speech_to_local_command

    manifest = {
        "schema_version": 1, "id": "probe", "name": "Prova temporanea",
        "version": "1.0.0", "description": "Solo fixture locale",
        "actions": [{"id": "addon.probe.status", "description": "Stato",
                     "example": "stato sistema", "core_action": "system.status"}],
    }
    facts = {}
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        downloads = root / "Downloads"
        documents = root / "Documents"
        downloads.mkdir()
        documents.mkdir()
        (downloads / "campione-interno.txt").write_text("fixture", encoding="utf-8")
        (documents / "campione-esterno.txt").write_text("fixture", encoding="utf-8")
        (downloads / "cartella-campione").mkdir()
        engine = LocalEngine(download_dir=downloads, db_path=root / "tasks.db",
                             windows=False)
        report = engine.execute("cerca file campione")
        assert report.status == "completed"
        assert "campione-interno.txt" in report.message
        assert "campione-esterno.txt" not in report.message
        assert "cartella-campione" not in report.message
        facts["search_scope"] = "Downloads files only; excludes outside file and directory name"

        package = root / "probe.jaddon"
        package.write_text(json.dumps(manifest), encoding="utf-8")
        manager = AddonManager(LiveCapabilityRegistry(), root / "addons")
        manager.install(package)
        manager.set_enabled("probe", True)
        assert manager.resolve("addon.probe.status", {}).handler == "local"
        try:
            manager.resolve("addon.probe.status", {"query": "campione"})
        except CapabilityRejected:
            facts["addon_arguments"] = "Nonempty arguments rejected even for active addon"
        else:
            raise AssertionError("Expected baseline to reject parameters")

        manifest["actions"][0]["core_action"] = "files.search"
        try:
            validate_manifest(manifest)
        except AddonError:
            facts["general_file_provider"] = "files.search manifest target rejected"
        else:
            raise AssertionError("Expected baseline to reject new provider")

    assert speech_to_local_command("cerca file campione") is None
    facts["voice_exact_search"] = "No speech_to_local_command mapping for cerca file"
    assert is_ambiguous_short_reply("il secondo")
    facts["short_reply"] = (
        "il secondo classified ambiguous; application guard inspected separately, "
        "not exercised by this probe"
    )
    print(json.dumps({"source_commit": "b936879a431370d206152be7b089baf587d15499",
                      "observed": facts, "checks": 5,
                      "scope": "Local baseline only; no new add-on or Windows test"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
