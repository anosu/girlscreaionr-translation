import os
import re
import sys
from pathlib import Path

import httpx
import UnityPy

from gpt import Translator
from utils import write_json, read_json
from parse import parse_bundle, parse_script
from crypto import get_url_params, decrypt_master_text


class Updater:
    BASE_URL = 'https://cdn-r18.gc.dmmgames.com'
    ASSET_PATH = '/secure/data/production/webgl/resources/'
    NOVEL_PATTERN = re.compile(r'notinit/[^/]*/\w{3}_(\d{8}|\d{5,6}).dmm')
    ID_PATTERN = re.compile(r'\d{8}|\d{5,6}')

    def __init__(self, translation_dir: str | Path, download_dir: str | Path):
        self.translation_dir = Path(translation_dir)
        self.download_dir = Path(download_dir)
        self.client = httpx.Client()
        self.master = {
            'mQuestNovels': {},
            'mUnitWords': {},
            'mSubunitWords': {}
        }

    def run(self):
        self.fetch_master()
        self.update_quest()
        self.update_words()
        self.update_novels()

    def translate_names(self, names: list[str]):
        if len(sys.argv) < 4:
            raise ValueError('Not enough arguments')

        api_key, base_url, model = sys.argv[1:4]
        translator = Translator(api_key, base_url, model)

        name_dict = read_json(self.translation_dir / 'names/zh_Hans.json')
        names = [name for name in names if name not in name_dict]

        translations = {}
        chunked_names = [names[i:i + 5] for i in range(0, len(names), 5)]
        for chunk in chunked_names:
            print(f'Original: {chunk}')
            result = translator.translate('|'.join(chunk))
            translated = result.split('|')
            print(f'Translated: {translated}')
            print('-' * 50)
            assert len(translated) == len(chunk)
            translations.update({chunk[i]: translated[i] for i in range(len(chunk))})

        name_dict.update(translations)
        write_json(self.translation_dir / 'names/zh_Hans.json', name_dict)

        gpt_dict = {}
        for name, translation in translations.items():
            if len(name) < 3 or '？' in name or '?' in name:
                continue
            if '&' in name or '＆' in name or '　' in name or '（' in name:
                continue
            if 'Ａ' in name or 'Ｂ' in name or 'Ｃ' in name or 'Ｄ' in name:
                continue
            if 'A' in name or 'B' in name or 'C' in name or 'D' in name:
                continue
            gpt_dict[name] = translation
        self.write_gpt_dict(gpt_dict)

    def write_gpt_dict(self, gpt_dict: dict[str, str]):
        dict_path = self.translation_dir / '项目GPT字典.txt'
        lines = dict_path.read_text('utf-8').strip().split('\n')
        existed_keys = set(line.split('\t')[0] for line in lines if not line.startswith('//'))
        with dict_path.open('a', encoding='utf-8') as f:
            f.writelines(f'{key}\t{value}\n' for key, value in gpt_dict.items() if key not in existed_keys)

    def fetch_master(self):
        resp = self.client.get(f'{self.BASE_URL}/files/manifest/webgl/r18/master.json').json()
        master_asset = resp['d'][0]
        master_path = f'{self.ASSET_PATH}{master_asset["n"]}'
        params = get_url_params(master_path, master_asset['h'])
        print(f'Master hash: {params["h"]}')
        bundle = self.client.get(f'{self.BASE_URL}{master_path}', params=params)
        env = UnityPy.load(bundle.content)
        for obj in env.objects:
            data = obj.read()
            if data.name not in self.master:
                continue
            self.master[data.name] = decrypt_master_text(data.script)

    def update_novels(self):
        new_names = set()
        existed_novels = os.listdir(self.translation_dir / 'novels')
        assetbundles = self.client.get(f'{self.BASE_URL}/files/manifest/webgl/r18/assetbundle.json').json()
        for asset in assetbundles['d']:
            asset_name = asset['n']
            if not self.NOVEL_PATTERN.match(asset_name):
                continue

            novel_id = self.ID_PATTERN.search(asset_name).group()
            if novel_id in existed_novels:
                continue

            asset_path = f'{self.ASSET_PATH}{asset_name}'
            params = get_url_params(asset_path, asset['h'])
            bundle = self.client.get(f'{self.BASE_URL}{asset_path}', params=params)

            script_name, script_text = parse_bundle(bundle.content)
            script_messages = parse_script(script_text)

            write_json(self.download_dir / f'{script_name}.json', script_messages)
            new_names |= set(msg['name'] for msg in script_messages if msg['name'])

            print(f'Downloaded: {script_name}')

        if len(new_names):
            self.translate_names(list(new_names))

    def update_quest(self):
        quest_dict = {
            novel['m_quest_stage_id']: novel['before_novel_id']
            for novel in self.master['mQuestNovels']
        }
        write_json(self.translation_dir / 'dicts/quest.json', quest_dict)
        print('Updated quest')

    def update_words(self):
        messages = []
        existed = read_json(self.translation_dir / 'words/zh_Hans.json')
        for words in self.master['mUnitWords'] + self.master['mSubunitWords']:
            if words['scene_type'] == 3:
                continue
            ml_word = words['ml_word'][0]
            if ml_word not in existed:
                messages.append({'message': ml_word})

        if len(messages) > 0:
            write_json(self.download_dir / 'words.json', messages)
        print('Saved words')
