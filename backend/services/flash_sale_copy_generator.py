"""
Vox Flash Sale Copy Generator Service 模块

闪购文案生成服务
- 紧迫感营造
- 优惠展示
- 行动号召
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class FlashSaleCopyGeneratorService:
    """
    闪购文案生成服务

    生成闪购文案内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_flash_sale_copy(
        self,
        product_name: str,
        discount_percentage: int,
        sale_duration_hours: int,
    ) -> Dict[str, Any]:
        """
        生成闪购文案

        Args:
            product_name: 产品名称
            discount_percentage: 折扣百分比
            sale_duration_hours: 销售持续时间（小时）

        Returns:
            Dict: 闪购文案
        """
        try:
            prompt = f"""请为"{product_name}"生成{discount_percentage}%折扣的限时{sale_duration_hours}小时闪购文案。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "discount_percentage": {discount_percentage},
    "sale_duration_hours": {sale_duration_hours},
    "email_subject_lines": ["邮件主题行1"],
    "headlines": ["标题1"],
    "main_copy": "主文案",
    "urgency_elements": ["紧迫感元素1"],
    "offer_details": "优惠详情",
    "scarcity_elements": ["稀缺性元素1"],
    "cta_buttons": ["CTA按钮1"],
    "social_media_posts": [
        {{
            "platform": "平台",
            "post_content": "帖子内容",
            "hashtags": ["标签1"]
        }}
    ],
    "banner_ad_copy": "横幅广告文案",
    "sms_messages": ["短信消息1"],
    "landing_page_headline": "着陆页标题",
    "countdown_timer_copy": "倒计时文案"
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
                "discount_percentage": discount_percentage,
                "sale_duration_hours": sale_duration_hours,
                **result,
            }

        except Exception as e:
            logger.error(f"生成闪购文案失败: {e}")
            return {
                "product_name": product_name,
                "discount_percentage": discount_percentage,
                "sale_duration_hours": sale_duration_hours,
                "email_subject_lines": [],
                "headlines": [],
                "main_copy": "",
                "urgency_elements": [],
                "offer_details": "",
                "scarcity_elements": [],
                "cta_buttons": [],
                "social_media_posts": [],
                "banner_ad_copy": "",
                "sms_messages": [],
                "landing_page_headline": "",
                "countdown_timer_copy": "",
            }


flash_sale_copy_generator_service = FlashSaleCopyGeneratorService()