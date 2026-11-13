"""Fetch the Italian Piper voices for the Jarvis repository (CI only).

Revision and SHA-256 come from the Hugging Face API at run time; every file is
verified on download and listed in ``voci.json`` (sizes, hashes, licence,
attribution). Nothing here runs on the user's PC.
"""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

VOICES = {
    "paola": {
        "repo": "rhasspy/piper-voices",
        "files": ("it/it_IT/paola/medium/it_IT-paola-medium.onnx",
                  "it/it_IT/paola/medium/it_IT-paola-medium.onnx.json"),
        "label": "Paola (Piper, media qualità)",
        "license": "Piper voice dataset 'paola' (rhasspy/piper-voices), see MODEL_CARD",
        "attribution": "it_IT-paola-medium, rhasspy/piper-voices",
    },
    "serena": {
        "repo": "committa/it_IT-serena-high",
        "files": ("it_IT-serena-high.onnx", "it_IT-serena-high.onnx.json"),
        "label": "Serena (Piper, alta qualità)",
        "license": "CC BY 4.0",
        "attribution": "it_IT-serena-high by Marco Baccarani (Committa), CC BY 4.0",
    },
}
MAX_BYTES = 400_000_000


def api(repo):
    with urllib.request.urlopen(
            "https://huggingface.co/api/models/" + repo + "?blobs=true", timeout=30) as r:
        return json.load(r)


def download(repo, revision, name, target, expected=None, size=None):
    digest, count = hashlib.sha256(), 0
    url = "https://huggingface.co/" + repo + "/resolve/" + revision + "/" + name
    with urllib.request.urlopen(url, timeout=180) as response, target.open("wb") as out:
        while True:
            chunk = response.read(1 << 20)
            if not chunk:
                break
            count += len(chunk)
            if count > MAX_BYTES:
                raise RuntimeError(name + ": file too large")
            digest.update(chunk)
            out.write(chunk)
    sha = digest.hexdigest()
    if (expected and sha != expected) or (size is not None and count != size):
        target.unlink(missing_ok=True)
        raise RuntimeError(name + ": integrity mismatch")
    return sha, count


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("destination")
    a = p.parse_args(argv)
    dest = Path(a.destination)
    dest.mkdir(parents=True, exist_ok=True)
    catalog = {"schema": 1, "voices": {}}
    for key, voice in VOICES.items():
        meta = api(voice["repo"])
        revision = meta["sha"]
        siblings = {s["rfilename"]: s for s in meta["siblings"]}
        entry = dict(label=voice["label"], license=voice["license"],
                     attribution=voice["attribution"], source_repo=voice["repo"],
                     source_revision=revision, files={})
        for name in voice["files"]:
            item = siblings.get(name)
            if item is None:
                raise RuntimeError(f"{key}: {name} not found in {voice['repo']}")
            lfs = item.get("lfs") or {}
            local = Path(name).name
            sha, count = download(voice["repo"], revision, name, dest / local,
                                  lfs.get("sha256"), lfs.get("size"))
            entry["files"][local] = {"sha256": sha, "bytes": count}
        catalog["voices"][key] = entry
    (dest / "voci.json").write_text(json.dumps(catalog, indent=2, ensure_ascii=False),
                                    encoding="utf-8")
    print(json.dumps(catalog, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
