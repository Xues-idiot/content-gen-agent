"""
Vox Local Listing Optimization Generator Service 模块

本地列表优化生成服务
- Google商家资料
- 本地SEO
- 评论管理
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class LocalListingOptimizationGeneratorService:
    """
    本地列表优化生成服务

    生成本地列表优化内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_local_listing_optimization(
        self,
        business_name: str,
        location: str,
        business_category: str,
    ) -> Dict[str, Any]:
        """
        生成本地列表优化

        Args:
            business_name: 商家名称
            location: 位置
            business_category: 商家类别

        Returns:
            Dict: 本地列表优化
        """
        try:
            prompt = f"""请为"{business_name}"（{location}，{business_category}）生成本地列表优化内容。

请以JSON格式返回：
{{
    "business_name": "商家名称",
    "location": "位置",
    "business_category": "商家类别",
    "google_business_profile": {{
        "business_name": "商家名称",
        "category": "类别",
        "description": "描述",
        "attributes": ["属性1"],
        "hours": "营业时间",
        "service_areas": "服务区域",
        "photos_suggestions": ["照片建议1"]
    }},
    "local_seo_keywords": ["本地SEO关键词1"],
    "business_description": "商家描述",
    "review_management": {{
        "response_templates": ["回复模板1"],
        "review_request_templates": ["评论请求模板1"],
        "sentiment_responses": ["情感回复1"]
    }},
    "local_citations": [
        {{
            "platform": "平台",
            "business_name_variant": "商家名称变体",
            "consistency_notes": "一致性说明"
        }}
    ],
    "local_content_ideas": ["本地内容创意1"],
    "qa_section_optimization": ["问答部分优化1"],
    "schema_markup": "Schema标记",
    "competitor_analysis": "竞争对手分析",
    "monthly_optimization_checklist": ["每月优化检查清单1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "business_name": business_name,
                "location": location,
                "business_category": business_category,
                **result,
            }

        except Exception as e:
            logger.error(f"生成本地列表优化失败: {e}")
            return {
                "business_name": business_name,
                "location": location,
                "business_category": business_category,
                "google_business_profile": {},
                "local_seo_keywords": [],
                "business_description": "",
                "review_management": {},
                "local_citations": [],
                "local_content_ideas": [],
                "qa_section_optimization": [],
                "schema_markup": "",
                "competitor_analysis": "",
                "monthly_optimization_checklist": [],
            }


local_listing_optimization_generator_service = LocalListingOptimizationGeneratorService()