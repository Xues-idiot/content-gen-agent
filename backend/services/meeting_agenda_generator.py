"""
Vox Meeting Agenda Generator Service 模块

会议议程生成服务
- 会议议程
- 讨论要点
- 行动事项
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class MeetingAgendaGeneratorService:
    """
    会议议程生成服务

    生成会议议程内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_meeting_agenda(
        self,
        meeting_title: str,
        meeting_type: str = "team-meeting",
        duration_minutes: int = 60,
    ) -> Dict[str, Any]:
        """
        生成会议议程

        Args:
            meeting_title: 会议标题
            meeting_type: 会议类型
            duration_minutes: 会议时长（分钟）

        Returns:
            Dict: 会议议程
        """
        try:
            prompt = f"""请为"{meeting_title}"会议（类型：{meeting_type}，时长：{duration_minutes}分钟）生成议程。

请以JSON格式返回：
{{
    "meeting_title": "会议标题",
    "meeting_type": "会议类型",
    "duration_minutes": 时长,
    "meeting_objectives": ["会议目标1"],
    "agenda_items": [
        {{
            "time_allocation": "时间分配",
            "topic": "议题",
            "discussion_points": ["讨论点1"],
            "owner": "负责人"
        }}
    ],
    "pre_materials": ["会前材料1"],
    "action_items": ["行动事项1"],
    "meeting_etiquette": "会议礼仪"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "meeting_title": meeting_title,
                "meeting_type": meeting_type,
                "duration_minutes": duration_minutes,
                **result,
            }

        except Exception as e:
            logger.error(f"生成会议议程失败: {e}")
            return {
                "meeting_title": meeting_title,
                "meeting_type": meeting_type,
                "duration_minutes": duration_minutes,
                "meeting_objectives": [],
                "agenda_items": [],
                "pre_materials": [],
                "action_items": [],
                "meeting_etiquette": "",
            }


meeting_agenda_generator_service = MeetingAgendaGeneratorService()