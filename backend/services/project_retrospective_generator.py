"""
Vox Project Retrospective Generator Service 模块

项目回顾生成服务
- 做得好的
- 需要改进的
- 行动计划
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProjectRetrospectiveGeneratorService:
    """
    项目回顾生成服务

    生成项目回顾内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_project_retrospective(
        self,
        project_name: str,
        team_size: int,
        project_duration: str,
    ) -> Dict[str, Any]:
        """
        生成项目回顾

        Args:
            project_name: 项目名称
            team_size: 团队规模
            project_duration: 项目持续时间

        Returns:
            Dict: 项目回顾
        """
        try:
            prompt = f"""请为"{project_name}"（团队规模：{team_size}，持续时间：{project_duration}）生成项目回顾。

请以JSON格式返回：
{{
    "project_name": "项目名称",
    "team_size": {team_size},
    "project_duration": "项目持续时间",
    "retrospective_date": "回顾日期",
    "attendees": ["参与者1"],
    "what_went_well": [
        {{
            "item": "项目",
            "evidence": "证据",
            "impact": "影响"
        }}
    ],
    "what_could_be_improved": [
        {{
            "item": "项目",
            "evidence": "证据",
            "action": "行动"
        }}
    ],
    "action_items": [
        {{
            "action": "行动",
            "owner": "负责人",
            "due_date": "截止日期",
            "priority": "优先级"
        }}
    ],
    "key_lessons": ["关键教训1"],
    "metrics_outcomes": {{
        "delivered": "已交付",
        "budget": "预算",
        "timeline": "时间线",
        "quality": "质量"
    }},
    "team_recognition": "团队认可",
    "next_project_recommendations": ["下一个项目建议1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "project_name": project_name,
                "team_size": team_size,
                "project_duration": project_duration,
                **result,
            }

        except Exception as e:
            logger.error(f"生成项目回顾失败: {e}")
            return {
                "project_name": project_name,
                "team_size": team_size,
                "project_duration": project_duration,
                "retrospective_date": "",
                "attendees": [],
                "what_went_well": [],
                "what_could_be_improved": [],
                "action_items": [],
                "key_lessons": [],
                "metrics_outcomes": {},
                "team_recognition": "",
                "next_project_recommendations": [],
            }


project_retrospective_generator_service = ProjectRetrospectiveGeneratorService()