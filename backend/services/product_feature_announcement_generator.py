"""
Vox Product Feature Announcement Generator Service 模块

产品功能公告生成服务
- 功能介绍
- 更新说明
- 用户指南
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductFeatureAnnouncementGeneratorService:
    """
    产品功能公告生成服务

    生成产品功能公告内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_product_feature_announcement(
        self,
        product_name: str,
        feature_name: str,
        feature_type: str = "new",
    ) -> Dict[str, Any]:
        """
        生成产品功能公告

        Args:
            product_name: 产品名称
            feature_name: 功能名称
            feature_type: 功能类型

        Returns:
            Dict: 产品功能公告
        """
        try:
            prompt = f"""请为"{product_name}"的{feature_type}功能"{feature_name}"生成产品功能公告。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "feature_name": "功能名称",
    "feature_type": "功能类型",
    "announcement_headline": "公告标题",
    "feature_summary": "功能摘要",
    "key_benefits": ["关键好处1"],
    "how_it_works": "工作原理",
    "use_cases": ["用例1"],
    "pricing_availability": "定价/可用性",
    "user_guide_snippet": "用户指南片段",
    "screenshots_descriptions": ["截图描述1"],
    "related_features": ["相关功能1"],
    "support_resources": ["支持资源1"]
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
                "feature_name": feature_name,
                "feature_type": feature_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品功能公告失败: {e}")
            return {
                "product_name": product_name,
                "feature_name": feature_name,
                "feature_type": feature_type,
                "announcement_headline": "",
                "feature_summary": "",
                "key_benefits": [],
                "how_it_works": "",
                "use_cases": [],
                "pricing_availability": "",
                "user_guide_snippet": "",
                "screenshots_descriptions": [],
                "related_features": [],
                "support_resources": [],
            }


product_feature_announcement_generator_service = ProductFeatureAnnouncementGeneratorService()