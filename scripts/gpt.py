from openai import OpenAI


class Translator:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=f'{base_url}/v1')
        self.system_prompt = """你是一个专业级日本Galgame本地化翻译引擎。请严格遵循以下规则：
        1. 仅将输入的日文名称（大多为人物名称）翻译为简体中文，直接输出结果不要任何解释
        2. 完全保留所有特殊符号（如&、数字、字母等）
        3. 使用自然流畅的Galgame风格中文，简洁明了
        4. 当有多个输入名称时会以“|”分隔，输出也保持同样的格式和顺序

        示例：
        输入：黒髪の少年
        输出：黑发少年
        
        输入：アルテ
        输出：阿尔特
        
        输入：騎士団　騎士たち
        输出：骑士团　骑士们
        
        输入：不審な男改め死の芸術家
        输出：可疑男子现为死亡艺术家
        
        输入：フラワーマン（二代目）
        输出：花丸（第二代）
        
        输入：囚われた死の芸術Ａ
        输出：被捕捉的死之艺术Ａ
        
        输入：取り巻きB|呉服屋女将|近隣住民|アングル＆モリゾ|エスティ―
        输出：随从B|和服店老板娘|附近居民|安格尔＆莫里索|艾斯蒂
        
        输入：ミケランジェロ＆ラファエロ
        输出：米开朗琪罗＆拉斐尔"""

    def translate(self, text):
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.2,
            top_p=0.95,
            stream=False
        )
        return resp.choices[0].message.content.strip()
