"""
Vox Software Development Plan Generator Service 模块

软件开发计划生成服务
- 开发阶段
- 里程碑
- 资源分配
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SoftwareDevelopmentPlanGeneratorService:
    """
    软件开发计划生成服务

    生成软件开发计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_software_development_plan(
        self,
        project_name: str,
        development_methodology: str,
        num_phases: int = 5,
    ) -> Dict[str, Any]:
        """
        生成软件开发计划

        Args:
            project_name: 项目名称
            development_methodology: 开发方法论
            num_phases: 阶段数量

        Returns:
            Dict: 软件开发计划
        """
        try:
            prompt = f"""请为"{project_name}"项目生成使用{development_methodology}方法的{num_phases}阶段软件开发计划。

请以JSON格式返回：
{{
    "project_name": "项目名称",
    "development_methodology": "开发方法论",
    "num_phases": {num_phases},
    "executive_summary": "执行摘要",
    "project_overview": "项目概述",
    "development_phases": [
        {{
            "phase_name": "阶段名称",
            "duration": "持续时间",
            "key_deliverables": ["关键可交付成果1"],
            "activities": ["活动1"],
            "resources": "资源",
            "milestones": ["里程碑1"]
        }}
    ],
    "team_structure": "团队结构",
    "tool_stack": ["工具栈1"],
    "quality_assurance_approach": "质量保证方法",
    "risk_management": "风险管理",
    "communication_plan": "沟通计划",
    "budget_breakdown": "预算明细",
    "success_criteria": ["成功标准1"]
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
                "development_methodology": development_methodology,
                "num_phases": num_phases,
                **result,
            }

        except Exception as e:
            logger.error(f"生成软件开发计划失败: {e}")
            return {
                "project_name": project_name,
                "development_methodology": development_methodology,
                "num_phases": num_phases,
                "executive_summary": "",
                "project_overview": "",
                "development_phases": [],
                "team_structure": "",
                "tool_stack": [],
                "quality_assurance_approach": "",
                "risk_management": "",
                "communication_plan": "",
                "budget_breakdown": "",
                "success_criteria": [],
            }


software_development_plan_generator_service = SoftwareDevelopmentPlanGeneratorService()
