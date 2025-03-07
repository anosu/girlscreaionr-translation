import json
from pathlib import Path


def write_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
