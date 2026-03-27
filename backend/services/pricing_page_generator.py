"""
Vox Pricing Page Generator Service 模块

定价页面生成服务
- 定价方案
- 功能对比
- FAQ
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PricingPageGeneratorService:
    """
    定价页面生成服务

    生成定价页面内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_pricing_page(
        self,
        product_name: str,
        num_tiers: int = 3,
        billing_periods: List[str] = None,
    ) -> Dict[str, Any]:
        """
        生成定价页面

        Args:
            product_name: 产品名称
            num_tiers: 方案层级数量
            billing_periods: 计费周期列表

        Returns:
            Dict: 定价页面
        """
        if billing_periods is None:
            billing_periods = ["monthly", "annually"]
        billing_str = ", ".join(billing_periods)

        try:
            prompt = f"""请为"{product_name}"生成{num_tiers}个定价层级的定价页面（计费周期：{billing_str}）。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "num_tiers": {num_tiers},
    "billing_periods": {billing_periods},
    "page_headline": "页面标题",
    "intro_text": "介绍文本",
    "pricing_tiers": [
        {{
            "tier_name": "方案名称",
            "price": "价格",
            "billing_period": "计费周期",
            "description": "描述",
            "features": ["功能1"],
            "limitations": ["限制1"],
            "recommended_for": "推荐对象",
            "cta_text": "CTA文本",
            "popular_choice": true
        }}
    ],
    "feature_comparison_matrix": {{
        "features": ["功能1"],
        "tiers": ["层级1"]
    }},
    "add_ons": [
        {{
            "name": "名称",
            "price": "价格",
            "description": "描述"
        }}
    ],
    "enterprise_plan": {{
        "description": "描述",
        "custom_pricing": true,
        "features": ["功能1"],
        "contact_cta": "联系CTA"
    }},
    "money_guarantee": " money-back guarantee",
    "faq": [
        {{
            "question": "问题",
            "answer": "答案"
        }}
    ],
    "testimonials": ["推荐引言1"],
    "next_steps": ["下一步1"],
    "seasonal_promotions": ["季节性促销1"]
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
                "num_tiers": num_tiers,
                "billing_periods": billing_periods,
                **result,
            }

        except Exception as e:
            logger.error(f"生成定价页面失败: {e}")
            return {
                "product_name": product_name,
                "num_tiers": num_tiers,
                "billing_periods": billing_periods,
                "page_headline": "",
                "intro_text": "",
                "pricing_tiers": [],
                "feature_comparison_matrix": {},
                "add_ons": [],
                "enterprise_plan": {},
                "money_guarantee": "",
                "faq": [],
                "testimonials": [],
                "next_steps": [],
                "seasonal_promotions": [],
            }


pricing_page_generator_service = PricingPageGeneratorService()