"""
Vox Upsell Recommendation Generator Service 模块

追加销售推荐生成服务
- 推荐产品
- 定价方案
- 话术设计
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class UpsellRecommendationGeneratorService:
    """
    追加销售推荐生成服务

    生成追加销售推荐内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_upsell_recommendation(
        self,
        current_product: str,
        customer_segment: str,
        num_recommendations: int = 3,
    ) -> Dict[str, Any]:
        """
        生成追加销售推荐

        Args:
            current_product: 当前产品
            customer_segment: 客户细分
            num_recommendations: 推荐数量

        Returns:
            Dict: 追加销售推荐
        """
        try:
            prompt = f"""请为"{current_product}"的{customer_segment}客户生成{num_recommendations}个追加销售推荐。

请以JSON格式返回：
{{
    "current_product": "当前产品",
    "customer_segment": "客户细分",
    "num_recommendations": {num_recommendations},
    "recommendations": [
        {{
            "product_name": "产品名称",
            "pricing_tier": "定价层级",
            "price": "价格",
            "key_benefits": ["关键好处1"],
            "target_customer_profile": "目标客户画像"
        }}
    ],
    "pitch_messaging": {{
        "headline": "标题",
        "value_proposition": "价值主张",
        "objection_handling": ["异议处理1"]
    }},
    "timing_recommendations": "时机建议",
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
                "customer_segment": customer_segment,
                "num_recommendations": num_recommendations,
                **result,
            }

        except Exception as e:
            logger.error(f"生成追加销售推荐失败: {e}")
            return {
                "current_product": current_product,
                "customer_segment": customer_segment,
                "num_recommendations": num_recommendations,
                "recommendations": [],
                "pitch_messaging": {},
                "timing_recommendations": "",
                "success_metrics": [],
            }


upsell_recommendation_generator_service = UpsellRecommendationGeneratorService()