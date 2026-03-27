"""
Vox Event Press Release Generator Service 模块

活动新闻稿生成服务
- 媒体邀请
- 活动预告
- 活动回顾
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class EventPressReleaseGeneratorService:
    """
    活动新闻稿生成服务

    生成活动新闻稿内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_event_press_release(
        self,
        event_name: str,
        event_date: str,
        event_type: str,
    ) -> Dict[str, Any]:
        """
        生成活动新闻稿

        Args:
            event_name: 活动名称
            event_date: 活动日期
            event_type: 活动类型

        Returns:
            Dict: 活动新闻稿
        """
        try:
            prompt = f"""请为"{event_name}"（{event_date}，{event_type}）生成活动新闻稿。

请以JSON格式返回：
{{
    "event_name": "活动名称",
    "event_date": "活动日期",
    "event_type": "活动类型",
    "headline": "标题",
    "subheadline": "副标题",
    "boilerplate": "电头",
    "media_invite": {{
        "invitation_text": "邀请文本",
        "rsvp_instructions": "RSVP说明"
    }},
    "event_details": {{
        "what": "什么",
        "when": "何时",
        "where": "何处",
        "why": "为何"
    }},
    "key_attractions": ["主要亮点1"],
    "confirmed_attendees": ["已确认参会者1"],
    "quote": "引言",
    "about_organizer": "关于组织者",
    "media_contact": "媒体联系"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "event_name": event_name,
                "event_date": event_date,
                "event_type": event_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成活动新闻稿失败: {e}")
            return {
                "event_name": event_name,
                "event_date": event_date,
                "event_type": event_type,
                "headline": "",
                "subheadline": "",
                "boilerplate": "",
                "media_invite": {},
                "event_details": {},
                "key_attractions": [],
                "confirmed_attendees": [],
                "quote": "",
                "about_organizer": "",
                "media_contact": "",
            }


event_press_release_generator_service = EventPressReleaseGeneratorService()