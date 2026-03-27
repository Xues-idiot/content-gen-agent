"""
Vox Google Search Ad Copy Generator Service 模块

Google搜索广告文案生成服务
- 广告标题
- 广告描述
- 关键词策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class GoogleSearchAdCopyGeneratorService:
    """
    Google搜索广告文案生成服务

    生成Google搜索广告文案内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_google_search_ad_copy(
        self,
        product_service: str,
        num_ad_groups: int = 3,
        primary_keyword: str = "",
    ) -> Dict[str, Any]:
        """
        生成Google搜索广告文案

        Args:
            product_service: 产品/服务
            num_ad_groups: 广告组数量
            primary_keyword: 主要关键词

        Returns:
            Dict: Google搜索广告文案
        """
        try:
            prompt = f"""请为"{product_service}"生成{num_ad_groups}个Google搜索广告组（主要关键词：{primary_keyword}）。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "num_ad_groups": {num_ad_groups},
    "primary_keyword": "主要关键词",
    "ad_groups": [
        {{
            "ad_group_name": "广告组名称",
            "keywords": ["关键词1"],
            "headlines": ["标题1"],
            "descriptions": ["描述1"],
            "final_url": "最终URL",
            "display_url": "显示URL"
        }}
    ],
    "ad_extensions": ["广告扩展1"],
    "negative_keywords": ["负面关键词1"]
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
                "num_ad_groups": num_ad_groups,
                "primary_keyword": primary_keyword,
                **result,
            }

        except Exception as e:
            logger.error(f"生成Google搜索广告文案失败: {e}")
            return {
                "product_service": product_service,
                "num_ad_groups": num_ad_groups,
                "primary_keyword": primary_keyword,
                "ad_groups": [],
                "ad_extensions": [],
                "negative_keywords": [],
            }


google_search_ad_copy_generator_service = GoogleSearchAdCopyGeneratorService()