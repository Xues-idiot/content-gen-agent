"""
Vox Grant Proposal Generator Service 模块

资助提案生成服务
- 项目描述
- 预算说明
- 预期成果
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class GrantProposalGeneratorService:
    """
    资助提案生成服务

    生成资助提案内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_grant_proposal(
        self,
        project_title: str,
        funding_organization: str,
        grant_amount: str = "¥100,000",
    ) -> Dict[str, Any]:
        """
        生成资助提案

        Args:
            project_title: 项目标题
            funding_organization: 资助机构
            grant_amount: 资助金额

        Returns:
            Dict: 资助提案
        """
        try:
            prompt = f"""请为"{project_title}"项目生成资助提案（资助机构：{funding_organization}，金额：{grant_amount}）。

请以JSON格式返回：
{{
    "project_title": "项目标题",
    "funding_organization": "资助机构",
    "grant_amount": "资助金额",
    "project_summary": "项目概要",
    "problem_and_need": "问题与需求",
    "project_goals": ["项目目标1"],
    "methodology": "研究方法",
    "timeline": "时间安排",
    "budget_justification": "预算说明",
    "budget_breakdown": [
        {{
            "category": "类别",
            "amount": 金额,
            "justification": "说明"
        }}
    ],
    "expected_outcomes": ["预期成果1"],
    "evaluation_plan": "评估计划",
    "sustainability": "可持续性",
    "team_qualifications": "团队资质"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "project_title": project_title,
                "funding_organization": funding_organization,
                "grant_amount": grant_amount,
                **result,
            }

        except Exception as e:
            logger.error(f"生成资助提案失败: {e}")
            return {
                "project_title": project_title,
                "funding_organization": funding_organization,
                "grant_amount": grant_amount,
                "project_summary": "",
                "problem_and_need": "",
                "project_goals": [],
                "methodology": "",
                "timeline": "",
                "budget_justification": "",
                "budget_breakdown": [],
                "expected_outcomes": [],
                "evaluation_plan": "",
                "sustainability": "",
                "team_qualifications": "",
            }


grant_proposal_generator_service = GrantProposalGeneratorService()