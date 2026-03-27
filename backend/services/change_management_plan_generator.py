"""
Vox Change Management Plan Generator Service 模块

变更管理计划生成服务
- 变更影响
- 沟通计划
- 培训策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ChangeManagementPlanGeneratorService:
    """
    变更管理计划生成服务

    生成变更管理计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_change_management_plan(
        self,
        change_initiative: str,
        change_scope: str,
        num_stakeholders: int = 8,
    ) -> Dict[str, Any]:
        """
        生成变更管理计划

        Args:
            change_initiative: 变更举措
            change_scope: 变更范围
            num_stakeholders: 利益相关者数量

        Returns:
            Dict: 变更管理计划
        """
        try:
            prompt = f"""请为"{change_initiative}"（变更范围：{change_scope}）生成{num_stakeholders}个利益相关者的变更管理计划。

请以JSON格式返回：
{{
    "change_initiative": "变更举措",
    "change_scope": "变更范围",
    "num_stakeholders": {num_stakeholders},
    "executive_summary": "执行摘要",
    "change_objectives": ["变更目标1"],
    "stakeholder_analysis": [
        {{
            "stakeholder_name": "利益相关者名称",
            "role": "角色",
            "impact_level": "影响级别",
            "engagement_strategy": "参与策略"
        }}
    ],
    "impact_assessment": {{
        "operational_impact": "运营影响",
        "cultural_impact": "文化影响",
        "resource_impact": "资源影响"
    }},
    "communication_plan": ["沟通计划1"],
    "training_plan": ["培训计划1"],
    "resistance_management": "抵抗管理",
    "timeline_and_milestones": ["时间线和里程碑1"],
    "success_metrics": ["成功指标1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "change_initiative": change_initiative,
                "change_scope": change_scope,
                "num_stakeholders": num_stakeholders,
                **result,
            }

        except Exception as e:
            logger.error(f"生成变更管理计划失败: {e}")
            return {
                "change_initiative": change_initiative,
                "change_scope": change_scope,
                "num_stakeholders": num_stakeholders,
                "executive_summary": "",
                "change_objectives": [],
                "stakeholder_analysis": [],
                "impact_assessment": {},
                "communication_plan": [],
                "training_plan": [],
                "resistance_management": "",
                "timeline_and_milestones": [],
                "success_metrics": [],
            }


change_management_plan_generator_service = ChangeManagementPlanGeneratorService()
