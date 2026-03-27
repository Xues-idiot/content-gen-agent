"""
Vox Social Media Calendar Generator Service 模块

社交媒体日历生成服务
- 内容排期
- 主题规划
- 发布时间
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SocialMediaCalendarGeneratorService:
    """
    社交媒体日历生成服务

    生成社交媒体内容日历
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_social_media_calendar(
        self,
        platform: str,
        month: str = "2026-04",
        num_posts: int = 20,
    ) -> Dict[str, Any]:
        """
        生成社交媒体日历

        Args:
            platform: 平台
            month: 月份
            num_posts: 帖子数量

        Returns:
            Dict: 社交媒体日历
        """
        try:
            prompt = f"""请为{platform}平台生成{month}月的内容日历（{num_posts}条帖子）。

请以JSON格式返回：
{{
    "platform": "平台",
    "month": "月份",
    "num_posts": 帖子数量,
    "content_themes": ["内容主题1"],
    "posting_schedule": [
        {{
            "date": "日期",
            "day": "星期",
            "time": "发布时间",
            "content_type": "内容类型",
            "topic": "主题",
            "caption": "配文",
            "hashtags": ["标签1"],
            "call_to_action": "行动号召"
        }}
    ],
    "campaign_ideas": ["营销活动创意1"],
    "seasonal_content": ["季节性内容1"],
    "best_performing_times": "最佳发布时间"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "platform": platform,
                "month": month,
                "num_posts": num_posts,
                **result,
            }

        except Exception as e:
            logger.error(f"生成社交媒体日历失败: {e}")
            return {
                "platform": platform,
                "month": month,
                "num_posts": num_posts,
                "content_themes": [],
                "posting_schedule": [],
                "campaign_ideas": [],
                "seasonal_content": [],
                "best_performing_times": "",
            }


social_media_calendar_generator_service = SocialMediaCalendarGeneratorService()