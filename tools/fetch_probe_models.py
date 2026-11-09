"""Fetch public GGUF probe models for Windows CI only; verify publisher SHA-256.

One small Q4_K_M model per supported family, chosen for the Pavilion target
(i3-2100, no AVX2). Revision and hash come from the Hugging Face API at run
time and are recorded; the download is rejected on size/hash mismatch. These
are not the user's files (``matches_user_file: not_verified``).
"""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

MODELS = {
    "gemma2": ("bartowski/gemma-2-2b-it-GGUF", "gemma-2-2b-it-Q4_K_M.gguf",
               1_000_000_000, 2_200_000_000),
    "qwen25": ("Qwen/Qwen2.5-1.5B-Instruct-GGUF", "qwen2.5-1.5b-instruct-q4_k_m.gguf",
               700_000_000, 1_500_000_000),
    "qwen3": ("bartowski/Qwen_Qwen3-1.7B-GGUF", "Qwen_Qwen3-1.7B-Q4_K_M.gguf",
              800_000_000, 1_700_000_000),
}


def fetch(key, destination):
    repo, name, low, high = MODELS[key]
    with urllib.request.urlopen("https://huggingface.co/api/models/" + repo + "?blobs=true",
                                timeout=30) as response:
        data = json.load(response)
    revision = data["sha"]
    item = next((x for x in data["siblings"] if x["rfilename"] == name), None)
    if item is None:
        candidates = [x["rfilename"] for x in data["siblings"]
                      if "q4_k_m" in x["rfilename"].lower()]
        raise RuntimeError(f"{key}: {name} not in {repo}; Q4_K_M files: {candidates}")
    expected, size = item["lfs"]["sha256"], item["lfs"]["size"]
    if len(revision) != 40 or len(expected) != 64 or not low < size < high:
        raise RuntimeError(f"{key}: unexpected publisher metadata (size={size})")
    path = Path(destination) / (key + ".gguf")
    digest, count = hashlib.sha256(), 0
    with urllib.request.urlopen("https://huggingface.co/" + repo + "/resolve/" + revision
                                + "/" + name, timeout=120) as response, path.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            count += len(chunk)
            if count > size:
                raise RuntimeError(f"{key}: GGUF exceeds publisher size")
            digest.update(chunk)
            out.write(chunk)
    if count != size or digest.hexdigest() != expected:
        path.unlink(missing_ok=True)
        raise RuntimeError(f"{key}: GGUF integrity mismatch")
    return {"repository": repo, "revision": revision, "file": name, "sha256": expected,
            "bytes": size, "local": path.name, "matches_user_file": "not_verified"}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("destination")
    p.add_argument("--models", default=",".join(MODELS))
    args = p.parse_args(argv)
    Path(args.destination).mkdir(parents=True, exist_ok=True)
    sources = {key: fetch(key, args.destination) for key in args.models.split(",")}
    (Path(args.destination) / "probe-models-source.json").write_text(
        json.dumps(sources, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(sources, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
