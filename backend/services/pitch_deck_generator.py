"""
Vox Pitch Deck Generator Service 模块

融资路演PPT生成服务
- 商业计划
- 路演脚本
- 投资人问答
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PitchDeckGeneratorService:
    """
    融资路演PPT生成服务

    生成路演所需的内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_pitch_content(
        self,
        company_name: str,
        stage: str = "seed",
    ) -> Dict[str, Any]:
        """
        生成路演内容

        Args:
            company_name: 公司名称
            stage: 融资阶段

        Returns:
            Dict: 路演内容
        """
        try:
            prompt = f"""请为"{company_name}"生成融资路演内容。

阶段：{stage}

请以JSON格式返回：
{{
    "pitch_title": "演讲标题",
    "problem": "痛点",
    "solution": "解决方案",
    "market_opportunity": "市场机会",
    "business_model": "商业模式",
    "team": "团队介绍",
    "ask": "融资需求"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "company_name": company_name,
                "stage": stage,
                **result,
            }

        except Exception as e:
            logger.error(f"生成路演内容失败: {e}")
            return {
                "company_name": company_name,
                "stage": stage,
                "pitch_title": "",
                "problem": "",
                "solution": "",
                "market_opportunity": "",
                "business_model": "",
                "team": "",
                "ask": "",
            }


pitch_deck_generator_service = PitchDeckGeneratorService()