"""
Vox SMS Coupon Generator Service 模块

短信优惠券生成服务
- 优惠券文案
- 发送时机
- 兑换追踪
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SMSCouponGeneratorService:
    """
    短信优惠券生成服务

    生成短信优惠券内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_sms_coupon(
        self,
        offer_type: str,
        discount_value: str,
        expiration_hours: int = 48,
    ) -> Dict[str, Any]:
        """
        生成短信优惠券

        Args:
            offer_type: 优惠类型
            discount_value: 折扣值
            expiration_hours: 过期小时数

        Returns:
            Dict: 短信优惠券
        """
        try:
            prompt = f"""请为"{offer_type}"生成折扣值为{discount_value}的短信优惠券（有效期：{expiration_hours}小时）。

请以JSON格式返回：
{{
    "offer_type": "优惠类型",
    "discount_value": "折扣值",
    "expiration_hours": {expiration_hours},
    "coupon_code": "优惠券代码",
    "sms_messages": [
        {{
            "message_type": "消息类型",
            "text": "文本",
            "timing": "时机"
        }}
    ],
    "urgency_elements": ["紧迫性元素1"],
    "redemption_instructions": "兑换说明",
    "terms_conditions": "条款条件"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "offer_type": offer_type,
                "discount_value": discount_value,
                "expiration_hours": expiration_hours,
                **result,
            }

        except Exception as e:
            logger.error(f"生成短信优惠券失败: {e}")
            return {
                "offer_type": offer_type,
                "discount_value": discount_value,
                "expiration_hours": expiration_hours,
                "coupon_code": "",
                "sms_messages": [],
                "urgency_elements": [],
                "redemption_instructions": "",
                "terms_conditions": "",
            }


sms_coupon_generator_service = SMSCouponGeneratorService()