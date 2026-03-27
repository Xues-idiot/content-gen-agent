"""
Vox Meeting Minutes Template Generator Service 模块

会议纪要模板生成服务
- 会议记录
- 决策追踪
- 行动分配
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class MeetingMinutesTemplateGeneratorService:
    """
    会议纪要模板生成服务

    生成会议纪要模板内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_meeting_minutes_template(
        self,
        meeting_type: str,
        num_agenda_items: int = 6,
    ) -> Dict[str, Any]:
        """
        生成会议纪要模板

        Args:
            meeting_type: 会议类型
            num_agenda_items: 议程项数量

        Returns:
            Dict: 会议纪要模板
        """
        try:
            prompt = f"""请为"{meeting_type}"类型会议生成包含{num_agenda_items}个议程项的会议纪要模板。

请以JSON格式返回：
{{
    "meeting_type": "会议类型",
    "num_agenda_items": 议程数,
    "document_header": "文档头部",
    "meeting_information": {{
        "meeting_title": "会议标题",
        "date": "日期",
        "time": "时间",
        "location": "地点",
        "chair": "主持人",
        "note_taker": "记录人",
        "attendees": ["参会人1"],
        "absentees": ["缺席人1"]
    }},
    "agenda_items": [
        {{
            "item_number": 1,
            "topic": "议题",
            "presenter": "发言 人",
            "discussion_points": ["讨论点1"],
            "decisions": ["决定1"],
            "action_items": ["行动项1"]
        }}
    ],
    "action_items_summary": [
        {{
            "action": "行动",
            "owner": "负责人",
            "due_date": "截止日期",
            "status": "状态"
        }}
    ],
    "decisions_log": ["决策1"],
    "next_meeting": "下次会议",
    "attachments": ["附件1"],
    "distribution": "分发"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "meeting_type": meeting_type,
                "num_agenda_items": num_agenda_items,
                **result,
            }

        except Exception as e:
            logger.error(f"生成会议纪要模板失败: {e}")
            return {
                "meeting_type": meeting_type,
                "num_agenda_items": num_agenda_items,
                "document_header": "",
                "meeting_information": {},
                "agenda_items": [],
                "action_items_summary": [],
                "decisions_log": [],
                "next_meeting": "",
                "attachments": [],
                "distribution": "",
            }


meeting_minutes_template_generator_service = MeetingMinutesTemplateGeneratorService()