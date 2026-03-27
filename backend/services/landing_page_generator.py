"""
Vox Landing Page Copy Generator Service 模块

落地页文案生成服务
- 页面文案
- 标题优化
- 转化优化
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class LandingPageCopyGeneratorService:
    """
    落地页文案生成服务

    生成落地页推广文案
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_landing_page_copy(
        self,
        product_name: str,
        goal: str = "conversion",
    ) -> Dict[str, Any]:
        """
        生成落地页文案

        Args:
            product_name: 产品名称
            goal: 目标

        Returns:
            Dict: 落地页文案
        """
        try:
            prompt = f"""请为"{product_name}"生成落地页文案。

目标：{goal}

请以JSON格式返回：
{{
    "hero_headline": "主标题",
    "hero_subheadline": "副标题",
    "value_propositions": ["价值主张1", "价值主张2"],
    "social_proof": "社会证明",
    "cta_text": "按钮文案"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_name": product_name,
                "goal": goal,
                **result,
            }

        except Exception as e:
            logger.error(f"生成落地页文案失败: {e}")
            return {
                "product_name": product_name,
                "goal": goal,
                "hero_headline": "",
                "hero_subheadline": "",
                "value_propositions": [],
                "social_proof": "",
                "cta_text": "",
            }


landing_page_copy_generator_service = LandingPageCopyGeneratorService()