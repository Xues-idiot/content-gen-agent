"""
Vox Sprint Planning Generator Service 模块

冲刺计划生成服务
- 冲刺目标
- 任务分配
- 燃尽图数据
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SprintPlanningGeneratorService:
    """
    冲刺计划生成服务

    生成冲刺计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_sprint_planning(
        self,
        sprint_name: str,
        sprint_number: int,
        duration_weeks: int = 2,
        num_stories: int = 8,
    ) -> Dict[str, Any]:
        """
        生成冲刺计划

        Args:
            sprint_name: 冲刺名称
            sprint_number: 冲刺编号
            duration_weeks: 持续周数
            num_stories: 用户故事数量

        Returns:
            Dict: 冲刺计划
        """
        try:
            prompt = f"""请为"Sprint {sprint_number}"（{sprint_name}，{duration_weeks}周，{num_stories}个故事）生成冲刺计划。

请以JSON格式返回：
{{
    "sprint_name": "冲刺名称",
    "sprint_number": 冲刺编号,
    "duration_weeks": 周数,
    "num_stories": 故事数,
    "sprint_goal": "冲刺目标",
    "start_date": "开始日期",
    "end_date": "结束日期",
    "user_stories": [
        {{
            "story_id": "故事ID",
            "title": "标题",
            "description": "描述",
            "story_points": "故事点数",
            "priority": "优先级",
            "assignee": "负责人",
            "acceptance_criteria": ["验收标准1"]
        }}
    ],
    "capacity_planning": {{
        "team_velocity": "团队速度",
        "total_story_points": "总故事点数",
        "buffer": "缓冲"
    }},
    "risks": ["风险1"],
    "dependencies": ["依赖1"],
    "retrospective_actions": ["回顾行动1"],
    "daily_standup_notes": "每日站会备注"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "sprint_name": sprint_name,
                "sprint_number": sprint_number,
                "duration_weeks": duration_weeks,
                "num_stories": num_stories,
                **result,
            }

        except Exception as e:
            logger.error(f"生成冲刺计划失败: {e}")
            return {
                "sprint_name": sprint_name,
                "sprint_number": sprint_number,
                "duration_weeks": duration_weeks,
                "num_stories": num_stories,
                "sprint_goal": "",
                "start_date": "",
                "end_date": "",
                "user_stories": [],
                "capacity_planning": {},
                "risks": [],
                "dependencies": [],
                "retrospective_actions": [],
                "daily_standup_notes": "",
            }


sprint_planning_generator_service = SprintPlanningGeneratorService()