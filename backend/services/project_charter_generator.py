"""
Vox Project Charter Generator Service 模块

项目章程生成服务
- 项目授权
- 目标定义
- 利益相关方
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProjectCharterGeneratorService:
    """
    项目章程生成服务

    生成项目章程内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_project_charter(
        self,
        project_name: str,
        project_sponsor: str,
        project_manager: str,
    ) -> Dict[str, Any]:
        """
        生成项目章程

        Args:
            project_name: 项目名称
            project_sponsor: 项目发起人
            project_manager: 项目经理

        Returns:
            Dict: 项目章程
        """
        try:
            prompt = f"""请为"{project_name}"（发起人：{project_sponsor}，经理：{project_manager}）生成项目章程。

请以JSON格式返回：
{{
    "project_name": "项目名称",
    "project_sponsor": "项目发起人",
    "project_manager": "项目经理",
    "document_version": "文档版本",
    "date": "日期",
    "executive_summary": "执行摘要",
    "project_background": "项目背景",
    "project_objectives": ["项目目标1"],
    "scope": {{
        "in_scope": ["范围内1"],
        "out_of_scope": ["范围外1"]
    }},
    "deliverables": ["交付物1"],
    "milestones": [
        {{
            "milestone": "里程碑",
            "due_date": "截止日期",
            "dependencies": ["依赖1"]
        }}
    ],
    "budget": "预算",
    "resources": "资源",
    "stakeholders": [
        {{
            "name": "名称",
            "role": "角色",
            "interest_level": "利益程度",
            "influence_level": "影响力程度"
        }}
    ],
    "constraints": ["约束条件1"],
    "assumptions": ["假设1"],
    "risks": ["风险1"],
    "governance_structure": "治理结构",
    "communication_plan": "沟通计划",
    "approval_requirements": "审批要求",
    "signed_by": ["签名人1"]
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
                "project_sponsor": project_sponsor,
                "project_manager": project_manager,
                **result,
            }

        except Exception as e:
            logger.error(f"生成项目章程失败: {e}")
            return {
                "project_name": project_name,
                "project_sponsor": project_sponsor,
                "project_manager": project_manager,
                "document_version": "",
                "date": "",
                "executive_summary": "",
                "project_background": "",
                "project_objectives": [],
                "scope": {"in_scope": [], "out_of_scope": []},
                "deliverables": [],
                "milestones": [],
                "budget": "",
                "resources": "",
                "stakeholders": [],
                "constraints": [],
                "assumptions": [],
                "risks": [],
                "governance_structure": "",
                "communication_plan": "",
                "approval_requirements": "",
                "signed_by": [],
            }


project_charter_generator_service = ProjectCharterGeneratorService()