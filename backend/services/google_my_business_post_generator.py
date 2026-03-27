"""
Vox Google My Business Post Generator Service 模块

Google我的商家帖子生成服务
- 本地推广
- 优惠信息
- 活动更新
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class GoogleMyBusinessPostGeneratorService:
    """
    Google我的商家帖子生成服务

    生成Google我的商家帖子内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_google_my_business_post(
        self,
        business_name: str,
        post_type: str,
        offer_details: str = "",
    ) -> Dict[str, Any]:
        """
        生成Google我的商家帖子

        Args:
            business_name: 商家名称
            post_type: 帖子类型
            offer_details: 优惠详情

        Returns:
            Dict: Google我的商家帖子
        """
        try:
            prompt = f"""请为"{business_name}"生成{post_type}类型的Google我的商家帖子。

请以JSON格式返回：
{{
    "business_name": "商家名称",
    "post_type": "帖子类型",
    "offer_details": "优惠详情",
    "headline": "标题",
    "body": "正文",
    "cta_text": "CTA文本",
    "cta_url": "CTA URL",
    "image_recommendation": "图片推荐",
    "posting_schedule": "发布计划"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "business_name": business_name,
                "post_type": post_type,
                "offer_details": offer_details,
                **result,
            }

        except Exception as e:
            logger.error(f"生成Google我的商家帖子失败: {e}")
            return {
                "business_name": business_name,
                "post_type": post_type,
                "offer_details": offer_details,
                "headline": "",
                "body": "",
                "cta_text": "",
                "cta_url": "",
                "image_recommendation": "",
                "posting_schedule": "",
            }


google_my_business_post_generator_service = GoogleMyBusinessPostGeneratorService()