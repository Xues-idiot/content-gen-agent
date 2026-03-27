"""
Vox Brand Storytelling Generator Service 模块

品牌故事生成服务
- 品牌起源
- 使命叙事
- 情感连接
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BrandStorytellingGeneratorService:
    """
    品牌故事生成服务

    生成品牌故事内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_brand_storytelling(
        self,
        brand_name: str,
        story_type: str = "founder",
        emotional_tone: str = "inspiring",
    ) -> Dict[str, Any]:
        """
        生成品牌故事

        Args:
            brand_name: 品牌名称
            story_type: 故事类型
            emotional_tone: 情感基调

        Returns:
            Dict: 品牌故事
        """
        try:
            prompt = f"""请为"{brand_name}"生成{story_type}类型的{emotional_tone}情感基调的品牌故事。

请以JSON格式返回：
{{
    "brand_name": "品牌名称",
    "story_type": "故事类型",
    "emotional_tone": "情感基调",
    "story_headline": "故事标题",
    "story_arc": {{
        "setup": "背景设定",
        "conflict": "冲突",
        "resolution": "解决"
    }},
    "origin_story": "起源故事",
    "founder_narrative": "创始人叙事",
    "mission_impact": "使命影响",
    "customer_transformation": "客户转变",
    "values_in_action": "行动中的价值观",
    "vision_future": "愿景未来",
    "emotional_hooks": ["情感钩子1"],
    "storytelling_elements": {{
        "characters": ["角色1"],
        "settings": ["设定1"],
        "dialogue_samples": ["对话示例1"]
    }},
    "content_formats": ["内容格式1"]
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
                "story_type": story_type,
                "emotional_tone": emotional_tone,
                **result,
            }

        except Exception as e:
            logger.error(f"生成品牌故事失败: {e}")
            return {
                "brand_name": brand_name,
                "story_type": story_type,
                "emotional_tone": emotional_tone,
                "story_headline": "",
                "story_arc": {},
                "origin_story": "",
                "founder_narrative": "",
                "mission_impact": "",
                "customer_transformation": "",
                "values_in_action": "",
                "vision_future": "",
                "emotional_hooks": [],
                "storytelling_elements": {},
                "content_formats": [],
            }


brand_storytelling_generator_service = BrandStorytellingGeneratorService()