"""
Vox Cart Abandonment Email Generator Service 模块

购物车遗弃邮件生成服务
- 挽回邮件
- 激励措施
- 紧迫感营造
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CartAbandonmentEmailGeneratorService:
    """
    购物车遗弃邮件生成服务

    生成购物车遗弃邮件内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_cart_abandonment_email(
        self,
        store_name: str,
        cart_items: List[str],
        recovery_discount: str = "none",
    ) -> Dict[str, Any]:
        """
        生成购物车遗弃邮件

        Args:
            store_name: 商店名称
            cart_items: 购物车商品
            recovery_discount: 恢复折扣

        Returns:
            Dict: 购物车遗弃邮件
        """
        items_str = ", ".join(cart_items[:3])

        try:
            prompt = f"""请为"{store_name}"生成购物车遗弃邮件序列（商品：{items_str}...，恢复折扣：{recovery_discount}）。

请以JSON格式返回：
{{
    "store_name": "商店名称",
    "cart_items": {cart_items},
    "recovery_discount": "恢复折扣",
    "email_sequence": [
        {{
            "email_number": 1,
            "timing": "时机",
            "subject_line": "主题行",
            "preview_text": "预览文本",
            "headline": "标题",
            "body": "正文",
            "cta_text": "CTA文本",
            "incentive_offered": "提供的激励"
        }}
    ],
    "abandonment_reasons": ["遗弃原因1"],
    "personalization_approaches": ["个性化方法1"],
    "urgency_tactics": ["紧迫性策略1"],
    "social_proof_elements": ["社会证明元素1"],
    "retargeting_display_ads": ["再营销展示广告1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "store_name": store_name,
                "cart_items": cart_items,
                "recovery_discount": recovery_discount,
                **result,
            }

        except Exception as e:
            logger.error(f"生成购物车遗弃邮件失败: {e}")
            return {
                "store_name": store_name,
                "cart_items": cart_items,
                "recovery_discount": recovery_discount,
                "email_sequence": [],
                "abandonment_reasons": [],
                "personalization_approaches": [],
                "urgency_tactics": [],
                "social_proof_elements": [],
                "retargeting_display_ads": [],
            }


cart_abandonment_email_generator_service = CartAbandonmentEmailGeneratorService()