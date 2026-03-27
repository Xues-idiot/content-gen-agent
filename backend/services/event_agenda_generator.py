"""
Vox Event Agenda Generator Service 模块

活动议程生成服务
- 活动流程
- 时间安排
- 环节设计
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class EventAgendaGeneratorService:
    """
    活动议程生成服务

    生成活动议程内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_event_agenda(
        self,
        event_name: str,
        event_type: str,
        duration_hours: float = 2.0,
        num_participants: int = 50,
    ) -> Dict[str, Any]:
        """
        生成活动议程

        Args:
            event_name: 活动名称
            event_type: 活动类型
            duration_hours: 活动时长（小时）
            num_participants: 参与人数

        Returns:
            Dict: 活动议程
        """
        try:
            prompt = f"""请为"{event_name}"（类型：{event_type}，时长：{duration_hours}小时，人数：{num_participants}人）生成活动议程。

请以JSON格式返回：
{{
    "event_name": "活动名称",
    "event_type": "活动类型",
    "duration_hours": 时长,
    "num_participants": 人数,
    "agenda_items": [
        {{
            "time": "时间",
            "session_name": "环节名称",
            "description": "环节描述",
            "speaker": "主持人/演讲者"
        }}
    ],
    "logistics": ["后勤安排1"],
    "materials_needed": ["所需物料1"],
    "success_metrics": "成功指标"
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
                "event_type": event_type,
                "duration_hours": duration_hours,
                "num_participants": num_participants,
                **result,
            }

        except Exception as e:
            logger.error(f"生成活动议程失败: {e}")
            return {
                "event_name": event_name,
                "event_type": event_type,
                "duration_hours": duration_hours,
                "num_participants": num_participants,
                "agenda_items": [],
                "logistics": [],
                "materials_needed": [],
                "success_metrics": "",
            }


event_agenda_generator_service = EventAgendaGeneratorService()