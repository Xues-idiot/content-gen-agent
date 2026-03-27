"""
Vox Advertisement Copy Generator Service 模块

广告文案生成服务
- 广告标题
- 广告正文
- 行动号召
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class AdvertisementCopyGeneratorService:
    """
    广告文案生成服务

    生成广告文案内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_advertisement_copy(
        self,
        product_service: str,
        ad_format: str,
        target_platform: str,
    ) -> Dict[str, Any]:
        """
        生成广告文案

        Args:
            product_service: 产品/服务
            ad_format: 广告格式
            target_platform: 目标平台

        Returns:
            Dict: 广告文案
        """
        try:
            prompt = f"""请为"{product_service}"生成{ad_format}格式的广告文案（目标平台：{target_platform}）。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "ad_format": "广告格式",
    "target_platform": "目标平台",
    "headline_options": ["标题选项1"],
    "primary_text": "主要文案",
    "secondary_text": "次要文案",
    "cta_button_text": "CTA按钮文本",
    "cta_url": "CTA URL",
    "description": "描述",
    "display_url": "显示URL",
    "keywords": ["关键词1"],
    "hashtags": ["#标签1"],
    "variations": [
        {{
            "variation_name": "变体名称",
            "headline": "标题",
            "body": "正文",
            "cta": "CTA"
        }}
    ],
    "character_count": {{
        "headline": 字符数,
        "primary_text": 字符数,
        "description": 字符数
    }},
    "compliance_notes": "合规说明",
    "brand_safety_guidelines": "品牌安全指南"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_service": product_service,
                "ad_format": ad_format,
                "target_platform": target_platform,
                **result,
            }

        except Exception as e:
            logger.error(f"生成广告文案失败: {e}")
            return {
                "product_service": product_service,
                "ad_format": ad_format,
                "target_platform": target_platform,
                "headline_options": [],
                "primary_text": "",
                "secondary_text": "",
                "cta_button_text": "",
                "cta_url": "",
                "description": "",
                "display_url": "",
                "keywords": [],
                "hashtags": [],
                "variations": [],
                "character_count": {},
                "compliance_notes": "",
                "brand_safety_guidelines": "",
            }


advertisement_copy_generator_service = AdvertisementCopyGeneratorService()