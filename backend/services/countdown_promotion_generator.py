"""
Vox Countdown Promotion Generator Service 模块

倒计时促销生成服务
- 活动预热
- 紧迫感文案
- 激励机制
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CountdownPromotionGeneratorService:
    """
    倒计时促销生成服务

    生成倒计时促销内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_countdown_promotion(
        self,
        promotion_name: str,
        start_date: str,
        end_date: str,
        offer_type: str,
    ) -> Dict[str, Any]:
        """
        生成倒计时促销

        Args:
            promotion_name: 促销名称
            start_date: 开始日期
            end_date: 结束日期
            offer_type: 优惠类型

        Returns:
            Dict: 倒计时促销
        """
        try:
            prompt = f"""请为"{promotion_name}"（{start_date}至{end_date}，{offer_type}）生成倒计时促销内容。

请以JSON格式返回：
{{
    "promotion_name": "促销名称",
    "start_date": "开始日期",
    "end_date": "结束日期",
    "offer_type": "优惠类型",
    "campaign_headline": "活动标题",
    "countdown_messaging": {{
        "one_week_left": "还剩一周",
        "three_days_left": "还剩三天",
        "one_day_left": "还剩一天",
        "last_day": "最后一天"
    }},
    "urgency_elements": ["紧迫性元素1"],
    "daily_content_calendar": [
        {{
            "day": "天",
            "content": "内容",
            "cta": "CTA"
        }}
    ],
    "email_sequence": ["邮件序列1"],
    "social_media_posts": ["社交媒体帖子1"],
    "scarcity_tactics": ["稀缺性策略1"],
    "bonus_incentives": ["额外激励1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "promotion_name": promotion_name,
                "start_date": start_date,
                "end_date": end_date,
                "offer_type": offer_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成倒计时促销失败: {e}")
            return {
                "promotion_name": promotion_name,
                "start_date": start_date,
                "end_date": end_date,
                "offer_type": offer_type,
                "campaign_headline": "",
                "countdown_messaging": {},
                "urgency_elements": [],
                "daily_content_calendar": [],
                "email_sequence": [],
                "social_media_posts": [],
                "scarcity_tactics": [],
                "bonus_incentives": [],
            }


countdown_promotion_generator_service = CountdownPromotionGeneratorService()