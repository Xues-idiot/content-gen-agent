"""
Vox Award Nomination Generator Service 模块

奖项提名生成服务
- 提名材料
- 申报内容
- 展示文案
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class AwardNominationGeneratorService:
    """
    奖项提名生成服务

    生成奖项提名内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_award_nomination(
        self,
        nominee_name: str,
        award_name: str,
        category: str,
    ) -> Dict[str, Any]:
        """
        生成奖项提名

        Args:
            nominee_name: 被提名者名称
            award_name: 奖项名称
            category: 类别

        Returns:
            Dict: 奖项提名
        """
        try:
            prompt = f"""请为"{nominee_name}"生成"{award_name}"（类别：{category}）的提名材料。

请以JSON格式返回：
{{
    "nominee_name": "被提名者名称",
    "award_name": "奖项名称",
    "category": "类别",
    "nomination_letter": "提名信",
    "achievement_summary": "成就摘要",
    "key_accomplishments": ["关键成就1"],
    "impact_statement": "影响声明",
    "supporting_evidence": ["支持证据1"],
    "nominee_bio": "被提名者简介",
    "recommendations": ["推荐信1"],
    "media_kit": ["媒体资料1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "nominee_name": nominee_name,
                "award_name": award_name,
                "category": category,
                **result,
            }

        except Exception as e:
            logger.error(f"生成奖项提名失败: {e}")
            return {
                "nominee_name": nominee_name,
                "award_name": award_name,
                "category": category,
                "nomination_letter": "",
                "achievement_summary": "",
                "key_accomplishments": [],
                "impact_statement": "",
                "supporting_evidence": [],
                "nominee_bio": "",
                "recommendations": [],
                "media_kit": [],
            }


award_nomination_generator_service = AwardNominationGeneratorService()