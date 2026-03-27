"""
Vox Performance Review Generator Service 模块

绩效评估生成服务
- 评估表
- 反馈建议
- 发展计划
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PerformanceReviewGeneratorService:
    """
    绩效评估生成服务

    生成绩效评估内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_performance_review(
        self,
        employee_name: str,
        department: str,
        review_period: str = "2025 Annual",
        position: str = "Staff",
    ) -> Dict[str, Any]:
        """
        生成绩效评估

        Args:
            employee_name: 员工姓名
            department: 部门
            review_period: 评估周期
            position: 职位

        Returns:
            Dict: 绩效评估
        """
        try:
            prompt = f"""请为"{employee_name}"（{department}部门，职位：{position}，周期：{review_period}）生成绩效评估。

请以JSON格式返回：
{{
    "employee_name": "员工姓名",
    "department": "部门",
    "review_period": "评估周期",
    "position": "职位",
    "overall_rating": "总体评级",
    "achievements": ["成就1"],
    "areas_for_improvement": ["改进领域1"],
    "goal_progress": [
        {{
            "goal": "目标",
            "progress": "进度",
            "rating": "评级"
        }}
    ],
    "competency_ratings": ["能力评级1"],
    "development_plan": "发展计划",
    "manager_feedback": "经理反馈",
    "next_period_goals": ["下期目标1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "employee_name": employee_name,
                "department": department,
                "review_period": review_period,
                "position": position,
                **result,
            }

        except Exception as e:
            logger.error(f"生成绩效评估失败: {e}")
            return {
                "employee_name": employee_name,
                "department": department,
                "review_period": review_period,
                "position": position,
                "overall_rating": "",
                "achievements": [],
                "areas_for_improvement": [],
                "goal_progress": [],
                "competency_ratings": [],
                "development_plan": "",
                "manager_feedback": "",
                "next_period_goals": [],
            }


performance_review_generator_service = PerformanceReviewGeneratorService()