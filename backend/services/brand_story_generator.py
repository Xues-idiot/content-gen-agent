"""
Vox Brand Story Generator Service 模块

品牌故事生成服务
- 品牌起源
- 品牌理念
- 创始人故事
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BrandStoryGeneratorService:
    """
    品牌故事生成服务

    生成品牌故事内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_brand_story(
        self,
        brand_name: str,
        industry: str,
        founding_year: int = 2020,
    ) -> Dict[str, Any]:
        """
        生成品牌故事

        Args:
            brand_name: 品牌名称
            industry: 行业
            founding_year: 成立年份

        Returns:
            Dict: 品牌故事
        """
        try:
            prompt = f"""请为"{brand_name}"品牌（{industry}行业，{founding_year}年创立）生成品牌故事。

请以JSON格式返回：
{{
    "brand_name": "品牌名称",
    "origin_story": "品牌起源故事",
    "mission": "品牌使命",
    "vision": "品牌愿景",
    "values": ["核心价值1", "核心价值2"],
    "founder_message": "创始人寄语"
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
                "founding_year": founding_year,
                **result,
            }

        except Exception as e:
            logger.error(f"生成品牌故事失败: {e}")
            return {
                "brand_name": brand_name,
                "industry": industry,
                "founding_year": founding_year,
                "origin_story": "",
                "mission": "",
                "vision": "",
                "values": [],
                "founder_message": "",
            }


brand_story_generator_service = BrandStoryGeneratorService()