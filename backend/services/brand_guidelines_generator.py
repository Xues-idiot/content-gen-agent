"""
Vox Brand Guidelines Generator Service 模块

品牌指南生成服务
- 视觉规范
- 用语规范
- 应用示例
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BrandGuidelinesGeneratorService:
    """
    品牌指南生成服务

    生成品牌指南内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_brand_guidelines(
        self,
        brand_name: str,
        industry: str,
        brand_personality: str = "专业、创新",
    ) -> Dict[str, Any]:
        """
        生成品牌指南

        Args:
            brand_name: 品牌名称
            industry: 行业
            brand_personality: 品牌个性

        Returns:
            Dict: 品牌指南
        """
        try:
            prompt = f"""请为"{brand_name}"（{industry}行业，品牌个性：{brand_personality}）生成品牌指南。

请以JSON格式返回：
{{
    "brand_name": "品牌名称",
    "industry": "行业",
    "brand_personality": "品牌个性",
    "brand_mission": "品牌使命",
    "brand_vision": "品牌愿景",
    "core_values": ["核心价值1"],
    "brand_voice": {{
        "tone": "语调",
        "vocabulary": ["用语1"],
        "examples": ["示例1"]
    }},
    "logo_usage": "Logo使用规范",
    "color_palette": ["主色调1"],
    "typography": "字体规范",
    "imagery_style": "图片风格",
    "do_and_donts": {{
        "do": ["可以做1"],
        "donts": ["不要做1"]
    }}
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
                "brand_personality": brand_personality,
                **result,
            }

        except Exception as e:
            logger.error(f"生成品牌指南失败: {e}")
            return {
                "brand_name": brand_name,
                "industry": industry,
                "brand_personality": brand_personality,
                "brand_mission": "",
                "brand_vision": "",
                "core_values": [],
                "brand_voice": {},
                "logo_usage": "",
                "color_palette": [],
                "typography": "",
                "imagery_style": "",
                "do_and_donts": {"do": [], "donts": []},
            }


brand_guidelines_generator_service = BrandGuidelinesGeneratorService()