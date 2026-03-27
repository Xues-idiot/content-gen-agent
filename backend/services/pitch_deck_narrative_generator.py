"""
Vox Pitch Deck Narrative Generator Service 模块

演讲台叙事生成服务
- 叙事结构
- 幻灯片故事
- 情感弧线
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PitchDeckNarrativeGeneratorService:
    """
    演讲台叙事生成服务

    生成演讲台叙事内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_pitch_deck_narrative(
        self,
        startup_name: str,
        industry: str,
        funding_stage: str,
    ) -> Dict[str, Any]:
        """
        生成演讲台叙事

        Args:
            startup_name: 初创公司名称
            industry: 行业
            funding_stage: 融资阶段

        Returns:
            Dict: 演讲台叙事
        """
        try:
            prompt = f"""请为"{startup_name}"（{industry}，{funding_stage}阶段）生成演讲台叙事。

请以JSON格式返回：
{{
    "startup_name": "初创公司名称",
    "industry": "行业",
    "funding_stage": "融资阶段",
    "narrative_arc": "叙事弧线",
    "slides": [
        {{
            "slide_number": 1,
            "title": "标题",
            "narrative_purpose": "叙事目的",
            "key_message": "关键信息",
            "visuals_suggestion": "视觉建议",
            "data_points": ["数据点1"]
        }}
    ],
    "story_elements": {{
        "hero": "主人公",
        "problem": "问题",
        "solution": "解决方案",
        "journey": "旅程",
        "transformation": "转变"
    }},
    "emotional_hooks": ["情感钩子1"],
    "memorable_moments": ["难忘时刻1"],
    "delivery_tips": ["演讲技巧1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "startup_name": startup_name,
                "industry": industry,
                "funding_stage": funding_stage,
                **result,
            }

        except Exception as e:
            logger.error(f"生成演讲台叙事失败: {e}")
            return {
                "startup_name": startup_name,
                "industry": industry,
                "funding_stage": funding_stage,
                "narrative_arc": "",
                "slides": [],
                "story_elements": {},
                "emotional_hooks": [],
                "memorable_moments": [],
                "delivery_tips": [],
            }


pitch_deck_narrative_generator_service = PitchDeckNarrativeGeneratorService()