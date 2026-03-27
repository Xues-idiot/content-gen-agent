"""
Vox Ad Copy Generator Service 模块

广告文案生成服务
- 广告文案
- 促销文案
- 行动号召
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class AdCopyGeneratorService:
    """
    广告文案生成服务

    生成广告推广文案
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_ad_copy(
        self,
        product_name: str,
        ad_type: str = "promotion",
        platform: str = "weibo",
    ) -> Dict[str, Any]:
        """
        生成广告文案

        Args:
            product_name: 产品名称
            ad_type: 广告类型
            platform: 平台

        Returns:
            Dict: 广告文案
        """
        try:
            prompt = f"""请为"{product_name}"生成一条{ad_type}类型的广告文案。

平台：{platform}

请以JSON格式返回：
{{
    "headline": "广告标题",
    "body": "广告正文",
    "cta": "行动号召",
    "hashtags": ["#标签1"]
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
                "ad_type": ad_type,
                "platform": platform,
                **result,
            }

        except Exception as e:
            logger.error(f"生成广告文案失败: {e}")
            return {
                "product_name": product_name,
                "ad_type": ad_type,
                "platform": platform,
                "headline": "",
                "body": "",
                "cta": "",
                "hashtags": [],
            }


ad_copy_generator_service = AdCopyGeneratorService()