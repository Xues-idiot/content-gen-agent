"""
Vox Business Continuity Plan Generator Service 模块

业务连续性计划生成服务
- 风险场景
- 响应流程
- 恢复策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BusinessContinuityPlanGeneratorService:
    """
    业务连续性计划生成服务

    生成业务连续性计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_business_continuity_plan(
        self,
        organization: str,
        plan_scope: str,
        num_scenarios: int = 5,
    ) -> Dict[str, Any]:
        """
        生成业务连续性计划

        Args:
            organization: 组织
            plan_scope: 计划范围
            num_scenarios: 场景数量

        Returns:
            Dict: 业务连续性计划
        """
        try:
            prompt = f"""请为{organization}生成范围为{plan_scope}的{num_scenarios}个场景的业务连续性计划。

请以JSON格式返回：
{{
    "organization": "组织",
    "plan_scope": "计划范围",
    "num_scenarios": {num_scenarios},
    "executive_summary": "执行摘要",
    "plan_objectives": "计划目标",
    "key_personnel": ["关键人员1"],
    "emergency_contact_procedures": "紧急联系程序",
    "scenarios": [
        {{
            "scenario_name": "场景名称",
            "probability": "概率",
            "impact": "影响",
            "early_warnings": ["早期预警1"],
            "immediate_response": "即时响应",
            "recovery_steps": ["恢复步骤1"],
            "resources_needed": "所需资源",
            "recovery_time_objective": "恢复时间目标"
        }}
    ],
    "communication_plan": "沟通计划",
    "backup_procedures": "备份程序",
    "testing_schedule": "测试计划",
    "plan_maintenance": "计划维护",
    "training_requirements": "培训要求"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "organization": organization,
                "plan_scope": plan_scope,
                "num_scenarios": num_scenarios,
                **result,
            }

        except Exception as e:
            logger.error(f"生成业务连续性计划失败: {e}")
            return {
                "organization": organization,
                "plan_scope": plan_scope,
                "num_scenarios": num_scenarios,
                "executive_summary": "",
                "plan_objectives": "",
                "key_personnel": [],
                "emergency_contact_procedures": "",
                "scenarios": [],
                "communication_plan": "",
                "backup_procedures": "",
                "testing_schedule": "",
                "plan_maintenance": "",
                "training_requirements": "",
            }


business_continuity_plan_generator_service = BusinessContinuityPlanGeneratorService()
