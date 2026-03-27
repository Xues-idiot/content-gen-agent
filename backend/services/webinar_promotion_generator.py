"""
Vox Webinar Promotion Generator Service 模块

网络研讨会推广生成服务
- 预热邮件
- 社交帖子
- 注册页面
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class WebinarPromotionGeneratorService:
    """
    网络研讨会推广生成服务

    生成网络研讨会推广内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_webinar_promotion(
        self,
        webinar_title: str,
        presenter_name: str,
        event_date: str,
    ) -> Dict[str, Any]:
        """
        生成网络研讨会推广

        Args:
            webinar_title: 研讨会标题
            presenter_name: 演讲者姓名
            event_date: 活动日期

        Returns:
            Dict: 网络研讨会推广
        """
        try:
            prompt = f"""请为"{webinar_title}"（演讲者：{presenter_name}，日期：{event_date}）生成研讨会推广内容。

请以JSON格式返回：
{{
    "webinar_title": "研讨会标题",
    "presenter_name": "演讲者姓名",
    "event_date": "活动日期",
    "registration_page": {{
        "headline": "标题",
        "subheadline": "副标题",
        "description": "描述",
        "key_benefits": ["关键好处1"],
        "presenter_bio": "演讲者简介",
        "who_should_attend": "谁应该参加",
        "registration_form_fields": ["注册表单字段1"]
    }},
    "email_sequence": [
        {{
            "email_type": "邮件类型",
            "timing": "时机",
            "subject": "主题",
            "content_summary": "内容摘要"
        }}
    ],
    "social_media_posts": [
        {{
            "platform": "平台",
            "post_content": "帖子内容",
            "hashtags": ["标签1"]
        }}
    ],
    "paid_ads": [
        {{
            "platform": "平台",
            "ad_headline": "广告标题",
            "ad_copy": "广告文案",
            "targeting": "定向"
        }}
    ],
    "promotional_video_script": "推广视频脚本",
    "follow_up_sequence": "跟进序列",
    "reminder_templates": ["提醒模板1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "webinar_title": webinar_title,
                "presenter_name": presenter_name,
                "event_date": event_date,
                **result,
            }

        except Exception as e:
            logger.error(f"生成网络研讨会推广失败: {e}")
            return {
                "webinar_title": webinar_title,
                "presenter_name": presenter_name,
                "event_date": event_date,
                "registration_page": {},
                "email_sequence": [],
                "social_media_posts": [],
                "paid_ads": [],
                "promotional_video_script": "",
                "follow_up_sequence": "",
                "reminder_templates": [],
            }


webinar_promotion_generator_service = WebinarPromotionGeneratorService()