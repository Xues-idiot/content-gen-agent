"""
Vox Brand Voice Guidelines Generator Service 模块

品牌声音指南生成服务
- 语调规范
- 写作风格
- 内容示例
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BrandVoiceGuidelinesGeneratorService:
    """
    品牌声音指南生成服务

    生成品牌声音指南内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_brand_voice_guidelines(
        self,
        brand_name: str,
        industry: str,
        personality_traits: List[str] = None,
    ) -> Dict[str, Any]:
        """
        生成品牌声音指南

        Args:
            brand_name: 品牌名称
            industry: 行业
            personality_traits: 个性特征列表

        Returns:
            Dict: 品牌声音指南
        """
        if personality_traits is None:
            personality_traits = ["professional", "friendly"]
        traits_str = ", ".join(personality_traits)

        try:
            prompt = f"""请为"{brand_name}"（{industry}行业）生成品牌声音指南（个性特征：{traits_str}）。

请以JSON格式返回：
{{
    "brand_name": "品牌名称",
    "industry": "行业",
    "personality_traits": {personality_traits},
    "voice_characteristics": ["声音特征1"],
    "tone_guidelines": [
        {{
            "situation": "情况",
            "tone": "语调"
        }}
    ],
    "vocabulary": {{
        "preferred_words": ["首选词汇1"],
        "words_to_avoid": ["避免的词汇1"]
    }},
    "writing_style": "写作风格",
    "do_donts": {{
        "do_list": ["宜1"],
        "dont_list": ["忌1"]
    }},
    "content_examples": [
        {{
            "example_type": "示例类型",
            "good_example": "好的示例",
            "bad_example": "坏的示例"
        }}
    ],
    "channel_specific_voice": "渠道特定声音"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "brand_name": brand_name,
                "industry": industry,
                "personality_traits": personality_traits,
                **result,
            }

        except Exception as e:
            logger.error(f"生成品牌声音指南失败: {e}")
            return {
                "brand_name": brand_name,
                "industry": industry,
                "personality_traits": personality_traits,
                "voice_characteristics": [],
                "tone_guidelines": [],
                "vocabulary": {},
                "writing_style": "",
                "do_donts": {},
                "content_examples": [],
                "channel_specific_voice": "",
            }


brand_voice_guidelines_generator_service = BrandVoiceGuidelinesGeneratorService()