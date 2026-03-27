"""
Vox Team Performance Review Generator Service 模块

团队绩效审查生成服务
- 绩效指标
- 成就分析
- 发展建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TeamPerformanceReviewGeneratorService:
    """
    团队绩效审查生成服务

    生成团队绩效审查内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_team_performance_review(
        self,
        team_name: str,
        review_period: str,
        num_members: int = 10,
    ) -> Dict[str, Any]:
        """
        生成团队绩效审查

        Args:
            team_name: 团队名称
            review_period: 审查周期
            num_members: 成员数量

        Returns:
            Dict: 团队绩效审查
        """
        try:
            prompt = f"""请为{team_name}团队生成{review_period}的{num_members}名成员的团队绩效审查。

请以JSON格式返回：
{{
    "team_name": "团队名称",
    "review_period": "审查周期",
    "num_members": {num_members},
    "team_overview": {{
        "team_size": "团队规模",
        "total_revenue": "总收入",
        "quota_attainment": "配额完成率",
        "team_growth": "团队增长"
    }},
    "individual_performance": [
        {{
            "member_name": "成员姓名",
            "quota_attainment": "配额完成率",
            "key_accomplishments": ["关键成就1"],
            "development_areas": ["发展领域1"]
        }}
    ],
    "team_strengths": ["团队优势1"],
    "team_challenges": ["团队挑战1"],
    "coaching_recommendations": ["辅导建议1"],
    "training_needs": ["培训需求1"],
    "succession_planning": "继任计划",
    "recommended_actions": ["推荐行动1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "team_name": team_name,
                "review_period": review_period,
                "num_members": num_members,
                **result,
            }

        except Exception as e:
            logger.error(f"生成团队绩效审查失败: {e}")
            return {
                "team_name": team_name,
                "review_period": review_period,
                "num_members": num_members,
                "team_overview": {},
                "individual_performance": [],
                "team_strengths": [],
                "team_challenges": [],
                "coaching_recommendations": [],
                "training_needs": [],
                "succession_planning": "",
                "recommended_actions": [],
            }


team_performance_review_generator_service = TeamPerformanceReviewGeneratorService()
