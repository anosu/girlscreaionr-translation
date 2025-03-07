import UnityPy


def parse_bundle(data: bytes) -> tuple[str, str]:
    env = UnityPy.load(data)
    for obj in env.objects:
        if obj.type.name == 'TextAsset':
            asset = obj.read()
            return asset.name, bytes(asset.script).decode()


def parse_script(script: str) -> list[dict[str, str | None]]:
    messages = []
    for line in script.split('\n'):
        if line.startswith('title'):
            name, message = '', line.split(',')[1]
        elif line.startswith('message'):
            name, message = line.split(',')[1:3]
        elif line.startswith('msgvoicesync'):
            name, message = line.split(',')[2:4]
        else:
            continue
        messages.append({
            'name': name,
            'message': message.replace('<br>', r'\n')
        })
    return messages
