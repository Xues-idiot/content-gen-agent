"""
Vox Agile Sprint Planning Generator Service 模块

敏捷冲刺计划生成服务
- 用户故事
- 冲刺目标
- 任务分配
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class AgileSprintPlanningGeneratorService:
    """
    敏捷冲刺计划生成服务

    生成敏捷冲刺计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_agile_sprint_planning(
        self,
        sprint_number: int,
        sprint_goal: str,
        num_stories: int = 8,
    ) -> Dict[str, Any]:
        """
        生成敏捷冲刺计划

        Args:
            sprint_number: 冲刺编号
            sprint_goal: 冲刺目标
            num_stories: 用户故事数量

        Returns:
            Dict: 敏捷冲刺计划
        """
        try:
            prompt = f"""请为冲刺{sprint_number}生成{num_stories}个用户故事的冲刺计划（目标：{sprint_goal}）。

请以JSON格式返回：
{{
    "sprint_number": {sprint_number},
    "sprint_goal": "冲刺目标",
    "num_stories": {num_stories},
    "sprint_duration": "冲刺持续时间",
    "user_stories": [
        {{
            "story_id": "故事ID",
            "story_title": "故事标题",
            "story_description": "故事描述",
            "acceptance_criteria": ["验收标准1"],
            "story_points": "故事点数",
            "assigned_to": "分配给",
            "priority": "优先级"
        }}
    ],
    "capacity_planning": {{
        "team_capacity": "团队容量",
        "available_story_points": "可用故事点数",
        "allocated_story_points": "分配的故事点数"
    }},
    "sprint_backlog": ["冲刺待办列表1"],
    "definition_of_done": ["完成的定义1"],
    "risks_and_assumptions": ["风险和假设1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "sprint_number": sprint_number,
                "sprint_goal": sprint_goal,
                "num_stories": num_stories,
                **result,
            }

        except Exception as e:
            logger.error(f"生成敏捷冲刺计划失败: {e}")
            return {
                "sprint_number": sprint_number,
                "sprint_goal": sprint_goal,
                "num_stories": num_stories,
                "sprint_duration": "",
                "user_stories": [],
                "capacity_planning": {},
                "sprint_backlog": [],
                "definition_of_done": [],
                "risks_and_assumptions": [],
            }


agile_sprint_planning_generator_service = AgileSprintPlanningGeneratorService()
