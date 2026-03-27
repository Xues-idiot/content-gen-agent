"""
Vox Pricing Package Generator Service 模块

定价方案生成服务
- 方案设计
- 功能分级
- 定价心理
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PricingPackageGeneratorService:
    """
    定价方案生成服务

    生成定价方案内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_pricing_package(
        self,
        product_name: str,
        num_packages: int = 3,
        pricing_model: str = "subscription",
    ) -> Dict[str, Any]:
        """
        生成定价方案

        Args:
            product_name: 产品名称
            num_packages: 方案数量
            pricing_model: 定价模型

        Returns:
            Dict: 定价方案
        """
        try:
            prompt = f"""请为"{product_name}"生成{num_packages}个{pricing_model}类型的定价方案。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "num_packages": {num_packages},
    "pricing_model": "定价模型",
    "packages": [
        {{
            "package_name": "方案名称",
            "price": "价格",
            "billing_period": "计费周期",
            "description": "描述",
            "features": ["功能1"],
            "limitations": ["限制1"],
            "target_customer": "目标客户",
            "popular": true
        }}
    ],
    "pricing_psychology": {{
        "anchoring": "锚定",
        "decoy_effect": "诱饵效应",
        "bundling_strategy": "捆绑策略"
    }},
    "comparison_matrix": "比较矩阵",
    "discount_structure": "折扣结构",
    "enterprise_pricing": "企业定价",
    "free_trial_strategy": "免费试用策略",
    "faq_pricing": ["定价FAQ1"]
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
                "num_packages": num_packages,
                "pricing_model": pricing_model,
                **result,
            }

        except Exception as e:
            logger.error(f"生成定价方案失败: {e}")
            return {
                "product_name": product_name,
                "num_packages": num_packages,
                "pricing_model": pricing_model,
                "packages": [],
                "pricing_psychology": {},
                "comparison_matrix": "",
                "discount_structure": "",
                "enterprise_pricing": "",
                "free_trial_strategy": "",
                "faq_pricing": [],
            }


pricing_package_generator_service = PricingPackageGeneratorService()