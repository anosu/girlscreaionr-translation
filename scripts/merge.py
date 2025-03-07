import re
from pathlib import Path

from utils import read_json, write_json


def pre_process(text: str) -> str:
    return text.replace(r'\n', '<br>')


class Merger:
    def __init__(self, translation_dir: str | Path, cache_dir: str | Path):
        self.translation_dir = Path(translation_dir)
        self.cache_dir = Path(cache_dir)

    def run(self):
        self.merge_novels()
        self.merge_words()

    def merge_novels(self):
        for file in self.cache_dir.glob('*.json'):
            match = re.search(r'\d+', file.stem)
            if not match:
                continue
            novel_id = match.group()
            cache: list[dict[str, int | str]] = read_json(file)
            translation = {
                pre_process(msg['pre_jp']): pre_process(msg['post_zh_preview'])
                for msg in cache
            }
            write_json(self.translation_dir / f'novels/{novel_id}/zh_Hans.json', translation)

    def merge_words(self):
        words_path = self.translation_dir / 'words/zh_Hans.json'
        words: dict[str, str] = read_json(words_path)
        cache: list[dict[str, int | str]] = read_json(self.cache_dir / 'words.json')
        words.update({
            msg['pre_jp']: msg['post_zh_preview']
            for msg in cache
        })
        write_json(words_path, words)


if __name__ == '__main__':
    Merger(
        translation_dir='.',
        cache_dir='GalTransl/sampleProject/transl_cache'
    ).run()
