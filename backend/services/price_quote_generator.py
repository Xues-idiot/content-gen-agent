"""
Vox Price Quote Generator Service 模块

价格报价生成服务
- 定价策略
- 折扣方案
- 报价模板
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PriceQuoteGeneratorService:
    """
    价格报价生成服务

    生成价格报价内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_price_quote(
        self,
        customer_name: str,
        product_name: str,
        quantity: int = 1,
    ) -> Dict[str, Any]:
        """
        生成价格报价

        Args:
            customer_name: 客户名称
            product_name: 产品名称
            quantity: 数量

        Returns:
            Dict: 价格报价
        """
        try:
            prompt = f"""请为"{customer_name}"生成{product_name}（数量：{quantity}）的价格报价。

请以JSON格式返回：
{{
    "customer_name": "客户名称",
    "product_name": "产品名称",
    "quantity": {quantity},
    "quote_number": "报价单号",
    "quote_date": "报价日期",
    "valid_until": "有效期至",
    "pricing": {{
        "unit_price": "单价",
        "total_price": "总价",
        "currency": "货币"
    }},
    "discounts": [
        {{
            "discount_type": "折扣类型",
            "discount_value": "折扣值",
            "discount_amount": "折扣金额"
        }}
    ],
    "payment_terms": "付款条款",
    "delivery_terms": "交付条款",
    "included_features": ["包含的功能1"],
    "optional_add_ons": ["可选附加组件1"],
    "terms_conditions": "条款和条件",
    "next_steps": "下一步"
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
                "product_name": product_name,
                "quantity": quantity,
                **result,
            }

        except Exception as e:
            logger.error(f"生成价格报价失败: {e}")
            return {
                "customer_name": customer_name,
                "product_name": product_name,
                "quantity": quantity,
                "quote_number": "",
                "quote_date": "",
                "valid_until": "",
                "pricing": {},
                "discounts": [],
                "payment_terms": "",
                "delivery_terms": "",
                "included_features": [],
                "optional_add_ons": [],
                "terms_conditions": "",
                "next_steps": "",
            }


price_quote_generator_service = PriceQuoteGeneratorService()
