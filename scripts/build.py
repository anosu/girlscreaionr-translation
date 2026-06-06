import hashlib
import json
from pathlib import Path

trans_dir = Path(".")


def get_hash(obj) -> str:
    canonical_str = json.dumps(
        obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    return hashlib.md5(canonical_str.encode()).hexdigest()


def hash_file(path: Path) -> str:
    return get_hash(json.loads(path.read_text(encoding="utf-8")))


manifest = {
    "names": hash_file(trans_dir / "names/zh_Hans.json"),
    "words": hash_file(trans_dir / "words/zh_Hans.json"),
    "novels": {
        int(f.parent.name): hash_file(f)
        for f in trans_dir.glob("novels/*/zh_Hans.json")
    },
}

manifest["hash"] = get_hash(manifest)

manifest_path = trans_dir / "manifest.json"
manifest_path.write_text(
    json.dumps(manifest, sort_keys=True, ensure_ascii=False, indent=4), encoding="utf-8"
)
