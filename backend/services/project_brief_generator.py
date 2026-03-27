"""
Vox Project Brief Generator Service 模块

项目简介生成服务
- 项目概述
- 目标设定
- 资源需求
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProjectBriefGeneratorService:
    """
    项目简介生成服务

    生成项目简介内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_project_brief(
        self,
        project_name: str,
        project_type: str,
        team_size: int = 5,
        deadline: str = "4 weeks",
    ) -> Dict[str, Any]:
        """
        生成项目简介

        Args:
            project_name: 项目名称
            project_type: 项目类型
            team_size: 团队规模
            deadline: 截止日期

        Returns:
            Dict: 项目简介
        """
        try:
            prompt = f"""请为"{project_name}"项目（类型：{project_type}，团队：{team_size}人，截止：{deadline}）生成简介。

请以JSON格式返回：
{{
    "project_name": "项目名称",
    "project_type": "项目类型",
    "team_size": 团队规模,
    "deadline": "截止日期",
    "executive_summary": "执行摘要",
    "project_goals": ["项目目标1"],
    "scope": {{
        "in_scope": ["范围内1"],
        "out_of_scope": ["范围外1"]
    }},
    "key_deliverables": ["关键交付物1"],
    "resource_requirements": ["资源需求1"],
    "risk_factors": ["风险因素1"],
    "success_criteria": "成功标准"
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
                "project_type": project_type,
                "team_size": team_size,
                "deadline": deadline,
                **result,
            }

        except Exception as e:
            logger.error(f"生成项目简介失败: {e}")
            return {
                "project_name": project_name,
                "project_type": project_type,
                "team_size": team_size,
                "deadline": deadline,
                "executive_summary": "",
                "project_goals": [],
                "scope": {"in_scope": [], "out_of_scope": []},
                "key_deliverables": [],
                "resource_requirements": [],
                "risk_factors": [],
                "success_criteria": "",
            }


project_brief_generator_service = ProjectBriefGeneratorService()