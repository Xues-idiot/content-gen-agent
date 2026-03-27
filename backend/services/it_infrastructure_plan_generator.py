"""
Vox IT Infrastructure Plan Generator Service 模块

IT基础设施计划生成服务
- 基础设施需求
- 容量规划
- 升级路线图
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ITInfrastructurePlanGeneratorService:
    """
    IT基础设施计划生成服务

    生成IT基础设施计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_it_infrastructure_plan(
        self,
        organization: str,
        planning_period: str,
        num_components: int = 8,
    ) -> Dict[str, Any]:
        """
        生成IT基础设施计划

        Args:
            organization: 组织
            planning_period: 规划周期
            num_components: 组件数量

        Returns:
            Dict: IT基础设施计划
        """
        try:
            prompt = f"""请为{organization}生成{planning_period}的{num_components}个组件的IT基础设施计划。

请以JSON格式返回：
{{
    "organization": "组织",
    "planning_period": "规划周期",
    "num_components": {num_components},
    "executive_summary": "执行摘要",
    "current_infrastructure_overview": "当前基础设施概述",
    "infrastructure_components": [
        {{
            "component_name": "组件名称",
            "current_state": "当前状态",
            "required_upgrades": ["需要的升级1"],
            "capacity_planning": "容量规划",
            "budget_estimate": "预算估计",
            "implementation_timeline": "实施时间线"
        }}
    ],
    "technology_trends_consideration": "技术趋势考虑",
    "security_requirements": "安全要求",
    "compliance_requirements": "合规要求",
    "risk_assessment": "风险评估",
    "budget_summary": "预算摘要",
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
                "organization": organization,
                "planning_period": planning_period,
                "num_components": num_components,
                **result,
            }

        except Exception as e:
            logger.error(f"生成IT基础设施计划失败: {e}")
            return {
                "organization": organization,
                "planning_period": planning_period,
                "num_components": num_components,
                "executive_summary": "",
                "current_infrastructure_overview": "",
                "infrastructure_components": [],
                "technology_trends_consideration": "",
                "security_requirements": "",
                "compliance_requirements": "",
                "risk_assessment": "",
                "budget_summary": "",
                "success_metrics": [],
            }


it_infrastructure_plan_generator_service = ITInfrastructurePlanGeneratorService()
