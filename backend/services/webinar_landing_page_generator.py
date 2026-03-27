"""
Vox Webinar Landing Page Generator Service 模块

网络研讨会着陆页生成服务
- 注册表单
- 活动详情
- 演讲者介绍
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class WebinarLandingPageGeneratorService:
    """
    网络研讨会着陆页生成服务

    生成网络研讨会着陆页内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_webinar_landing_page(
        self,
        webinar_title: str,
        event_date: str,
        presenter_name: str,
    ) -> Dict[str, Any]:
        """
        生成网络研讨会着陆页

        Args:
            webinar_title: 研讨会标题
            event_date: 活动日期
            presenter_name: 演讲者姓名

        Returns:
            Dict: 网络研讨会着陆页
        """
        try:
            prompt = f"""请为"{webinar_title}"（{event_date}，演讲者：{presenter_name}）生成网络研讨会着陆页。

请以JSON格式返回：
{{
    "webinar_title": "研讨会标题",
    "event_date": "活动日期",
    "presenter_name": "演讲者姓名",
    "page_headline": "页面标题",
    "event_overview": "活动概述",
    "key_benefits": ["关键好处1"],
    "what_youll_learn": ["你将学到1"],
    "presenter_bio": "演讲者简介",
    "event_details": {{
        "date": "日期",
        "time": "时间",
        "duration": "时长",
        "format": "格式",
        "location": "位置"
    }},
    "registration_form": {{
        "fields": ["字段1"],
        "required_fields": ["必填字段1"]
    }},
    "cta_buttons": ["CTA按钮1"],
    "testimonials": ["推荐1"],
    "faq": ["常见问题1"],
    "share_social_proof": "分享社会证明"
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
                "event_date": event_date,
                "presenter_name": presenter_name,
                **result,
            }

        except Exception as e:
            logger.error(f"生成网络研讨会着陆页失败: {e}")
            return {
                "webinar_title": webinar_title,
                "event_date": event_date,
                "presenter_name": presenter_name,
                "page_headline": "",
                "event_overview": "",
                "key_benefits": [],
                "what_youll_learn": [],
                "presenter_bio": "",
                "event_details": {},
                "registration_form": {},
                "cta_buttons": [],
                "testimonials": [],
                "faq": [],
                "share_social_proof": "",
            }


webinar_landing_page_generator_service = WebinarLandingPageGeneratorService()