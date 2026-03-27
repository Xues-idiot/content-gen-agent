"""
Vox Upsell Crosssell Generator Service 模块

追加销售交叉销售生成服务
- 推荐产品
- 捆绑策略
- 话术设计
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class UpsellCrosssellGeneratorService:
    """
    追加销售交叉销售生成服务

    生成追加销售交叉销售内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_upsell_crosssell(
        self,
        current_product: str,
        customer_tier: str,
        upsell_type: str = "premium",
    ) -> Dict[str, Any]:
        """
        生成追加销售交叉销售

        Args:
            current_product: 当前产品
            customer_tier: 客户层级
            upsell_type: 追加销售类型

        Returns:
            Dict: 追加销售交叉销售
        """
        try:
            prompt = f"""请为"{current_product}"的{customer_tier}客户生成{upsell_type}类型的追加销售/交叉销售内容。

请以JSON格式返回：
{{
    "current_product": "当前产品",
    "customer_tier": "客户层级",
    "upsell_type": "追加销售类型",
    "recommended_products": [
        {{
            "product_name": "产品名称",
            "product_type": "产品类型",
            "price_point": "价格",
            "recommendation_reason": "推荐原因"
        }}
    ],
    "bundle_packages": [
        {{
            "bundle_name": "捆绑包名称",
            "products_included": ["包含的产品1"],
            "bundle_price": "捆绑价格",
            "savings": "节省"
        }}
    ],
    "upsell_messaging": {{
        "headline": "标题",
        "value_proposition": "价值主张",
        "objection_handling": ["异议处理1"]
    }},
    "placement_recommendations": ["放置建议1"],
    "timing_strategies": ["时机策略1"],
    "personalization_tips": ["个性化提示1"],
    "success_metrics": ["成功指标1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "current_product": current_product,
                "customer_tier": customer_tier,
                "upsell_type": upsell_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成追加销售交叉销售失败: {e}")
            return {
                "current_product": current_product,
                "customer_tier": customer_tier,
                "upsell_type": upsell_type,
                "recommended_products": [],
                "bundle_packages": [],
                "upsell_messaging": {},
                "placement_recommendations": [],
                "timing_strategies": [],
                "personalization_tips": [],
                "success_metrics": [],
            }


upsell_crosssell_generator_service = UpsellCrosssellGeneratorService()