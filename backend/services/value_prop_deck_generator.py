"""
Vox Value Prop Deck Generator Service 模块

价值主张演示文稿生成服务
- 核心价值
- 差异化
- 客户利益
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ValuePropDeckGeneratorService:
    """
    价值主张演示文稿生成服务

    生成价值主张演示文稿内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_value_prop_deck(
        self,
        product_name: str,
        target_audience: str,
        num_slides: int = 10,
    ) -> Dict[str, Any]:
        """
        生成价值主张演示文稿

        Args:
            product_name: 产品名称
            target_audience: 目标受众
            num_slides: 幻灯片数量

        Returns:
            Dict: 价值主张演示文稿
        """
        try:
            prompt = f"""请为"{product_name}"生成针对{target_audience}的价值主张演示文稿（{num_slides}张幻灯片）。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "target_audience": "目标受众",
    "num_slides": {num_slides},
    "deck_title": "演示文稿标题",
    "slides": [
        {{
            "slide_number": 1,
            "title": "标题",
            "content": "内容",
            "visual_suggestion": "视觉建议"
        }}
    ],
    "key_value_statements": ["关键价值陈述1"],
    "differentiation_points": ["差异化要点1"],
    "proof_points": ["证明要点1"],
    "customer_benefits": ["客户利益1"],
    "roi_calculations": ["ROI计算1"]
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
                "target_audience": target_audience,
                "num_slides": num_slides,
                **result,
            }

        except Exception as e:
            logger.error(f"生成价值主张演示文稿失败: {e}")
            return {
                "product_name": product_name,
                "target_audience": target_audience,
                "num_slides": num_slides,
                "deck_title": "",
                "slides": [],
                "key_value_statements": [],
                "differentiation_points": [],
                "proof_points": [],
                "customer_benefits": [],
                "roi_calculations": [],
            }


value_prop_deck_generator_service = ValuePropDeckGeneratorService()