"""
Vox Cross Sell Opportunity Generator Service 模块

交叉销售机会生成服务
- 机会识别
- 产品推荐
- 销售策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CrossSellOpportunityGeneratorService:
    """
    交叉销售机会生成服务

    生成交叉销售机会内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_cross_sell_opportunity(
        self,
        customer_name: str,
        current_products: List[str],
        num_opportunities: int = 5,
    ) -> Dict[str, Any]:
        """
        生成交叉销售机会

        Args:
            customer_name: 客户名称
            current_products: 当前产品列表
            num_opportunities: 机会数量

        Returns:
            Dict: 交叉销售机会
        """
        products_str = ", ".join(current_products[:5])

        try:
            prompt = f"""请为"{customer_name}"（当前产品：{products_str}）生成{num_opportunities}个交叉销售机会。

请以JSON格式返回：
{{
    "customer_name": "客户名称",
    "current_products": {current_products},
    "num_opportunities": {num_opportunities},
    "opportunities": [
        {{
            "product": "产品名称",
            "upsell_potential": "追加销售潜力",
            "cross_sell_reason": "交叉销售原因",
            "estimated_value": "估计价值",
            "priority": "优先级"
        }}
    ],
    "recommended_approach": "推荐方法",
    "timing_recommendation": "时机建议",
    "objection_handling": "异议处理",
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
                "customer_name": customer_name,
                "current_products": current_products,
                "num_opportunities": num_opportunities,
                **result,
            }

        except Exception as e:
            logger.error(f"生成交叉销售机会失败: {e}")
            return {
                "customer_name": customer_name,
                "current_products": current_products,
                "num_opportunities": num_opportunities,
                "opportunities": [],
                "recommended_approach": "",
                "timing_recommendation": "",
                "objection_handling": "",
                "success_metrics": [],
            }


cross_sell_opportunity_generator_service = CrossSellOpportunityGeneratorService()
