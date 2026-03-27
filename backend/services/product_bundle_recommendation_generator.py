"""
Vox Product Bundle Recommendation Generator Service 模块

产品捆绑推荐生成服务
- 捆绑组合
- 定价策略
- 营销文案
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductBundleRecommendationGeneratorService:
    """
    产品捆绑推荐生成服务

    生成产品捆绑推荐内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_product_bundle_recommendation(
        self,
        primary_product: str,
        num_products: int = 3,
        bundle_theme: str = "essentials",
    ) -> Dict[str, Any]:
        """
        生成产品捆绑推荐

        Args:
            primary_product: 主要产品
            num_products: 产品数量
            bundle_theme: 捆绑主题

        Returns:
            Dict: 产品捆绑推荐
        """
        try:
            prompt = f"""请为"{primary_product}"生成包含{num_products}个产品的{bundle_theme}主题捆绑推荐。

请以JSON格式返回：
{{
    "primary_product": "主要产品",
    "num_products": {num_products},
    "bundle_theme": "捆绑主题",
    "bundle_name": "捆绑包名称",
    "bundle_tagline": "捆绑包标语",
    "products_in_bundle": [
        {{
            "product_name": "产品名称",
            "regular_price": "常规价格",
            "bundled_price": "捆绑价格",
            "reason_for_inclusion": "包含原因"
        }}
    ],
    "bundle_pricing": {{
        "total_regular_price": "总常规价格",
        "bundle_price": "捆绑价格",
        "savings_amount": "节省金额",
        "savings_percentage": "节省百分比"
    }},
    "marketing_messaging": {{
        "headline": "标题",
        "subheadline": "副标题",
        "key_benefits": ["关键好处1"],
        "urgency_elements": ["紧迫性元素1"]
    }},
    "cross_sell_recommendations": ["交叉销售推荐1"],
    "display_placement_suggestions": ["展示放置建议1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "primary_product": primary_product,
                "num_products": num_products,
                "bundle_theme": bundle_theme,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品捆绑推荐失败: {e}")
            return {
                "primary_product": primary_product,
                "num_products": num_products,
                "bundle_theme": bundle_theme,
                "bundle_name": "",
                "bundle_tagline": "",
                "products_in_bundle": [],
                "bundle_pricing": {},
                "marketing_messaging": {},
                "cross_sell_recommendations": [],
                "display_placement_suggestions": [],
            }


product_bundle_recommendation_generator_service = ProductBundleRecommendationGeneratorService()