import hashlib
import json
from pathlib import Path

trans_dir = Path(".")
language = "zh_Hans"


def get_hash(obj: dict[str, str]) -> str:
    md5 = hashlib.md5()
    for key in sorted(obj.keys()):
        md5.update(f"{key}\x00{obj[key]}\x00".encode())
    return md5.hexdigest()


def hash_file(path: Path) -> str:
    return get_hash(json.loads(path.read_text(encoding="utf-8")))


manifest = {
    "names": hash_file(trans_dir / f"names/{language}.json"),
    "words": hash_file(trans_dir / f"words/{language}.json"),
    "novels": {
        int(f.parent.name): hash_file(f)
        for f in trans_dir.glob(f"novels/*/{language}.json")
    },
}

manifest["hash"] = get_hash(manifest)

manifest_path = trans_dir / f"manifest/{language}.json"
manifest_path.write_text(
    json.dumps(manifest, sort_keys=True, ensure_ascii=False, indent=4), encoding="utf-8"
)
