"""
Vox Product Comparison Generator Service 模块

产品比较生成服务
- 功能对比
- 规格对比
- 购买指南
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductComparisonGeneratorService:
    """
    产品比较生成服务

    生成产品比较内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_product_comparison(
        self,
        product_category: str,
        num_products: int = 3,
        comparison_criteria: List[str] = None,
    ) -> Dict[str, Any]:
        """
        生成产品比较

        Args:
            product_category: 产品类别
            num_products: 产品数量
            comparison_criteria: 比较标准

        Returns:
            Dict: 产品比较
        """
        if comparison_criteria is None:
            comparison_criteria = ["price", "features", "quality"]
        criteria_str = ", ".join(comparison_criteria)

        try:
            prompt = f"""请为{product_category}类别生成{num_products}个产品的比较（比较标准：{criteria_str}）。

请以JSON格式返回：
{{
    "product_category": "产品类别",
    "num_products": {num_products},
    "comparison_criteria": {comparison_criteria},
    "products": [
        {{
            "product_name": "产品名称",
            "pros": ["优点1"],
            "cons": ["缺点1"]
        }}
    ],
    "comparison_table": {{
        "criteria": ["标准1"],
        "products": ["产品1"]
    }},
    "recommendations": ["推荐1"],
    "buying_guide": "购买指南"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_category": product_category,
                "num_products": num_products,
                "comparison_criteria": comparison_criteria,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品比较失败: {e}")
            return {
                "product_category": product_category,
                "num_products": num_products,
                "comparison_criteria": comparison_criteria,
                "products": [],
                "comparison_table": {},
                "recommendations": [],
                "buying_guide": "",
            }


product_comparison_generator_service = ProductComparisonGeneratorService()