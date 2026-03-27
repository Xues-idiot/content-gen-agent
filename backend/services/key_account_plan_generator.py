"""
Vox Key Account Plan Generator Service 模块

关键客户计划生成服务
- 账户策略
- 目标设定
- 资源规划
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class KeyAccountPlanGeneratorService:
    """
    关键客户计划生成服务

    生成关键客户计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_key_account_plan(
        self,
        account_name: str,
        planning_period: str,
        num_objectives: int = 5,
    ) -> Dict[str, Any]:
        """
        生成关键客户计划

        Args:
            account_name: 账户名称
            planning_period: 计划周期
            num_objectives: 目标数量

        Returns:
            Dict: 关键客户计划
        """
        try:
            prompt = f"""请为"{account_name}"生成{planning_period}的{num_objectives}个目标的的关键客户计划。

请以JSON格式返回：
{{
    "account_name": "账户名称",
    "planning_period": "计划周期",
    "num_objectives": {num_objectives},
    "account_overview": "账户概述",
    "strategic_ objectives": ["战略目标1"],
    "account_team": {{
        "account_executive": "客户主管",
        "support_team": "支持团队",
        "internal_stakeholders": ["内部利益相关者1"]
    }},
    "stakeholder_map": ["利益相关者地图1"],
    "competitive_position": "竞争地位",
    "growth_opportunities": ["增长机会1"],
    "action_plan": [
        {{
            "quarter": "季度",
            "initiatives": ["举措1"],
            "success_metrics": ["成功指标1"]
        }}
    ],
    "resource_requirements": "资源需求",
    "risk_mitigation": "风险缓解",
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
                "account_name": account_name,
                "planning_period": planning_period,
                "num_objectives": num_objectives,
                **result,
            }

        except Exception as e:
            logger.error(f"生成关键客户计划失败: {e}")
            return {
                "account_name": account_name,
                "planning_period": planning_period,
                "num_objectives": num_objectives,
                "account_overview": "",
                "strategic_objectives": [],
                "account_team": {},
                "stakeholder_map": [],
                "competitive_position": "",
                "growth_opportunities": [],
                "action_plan": [],
                "resource_requirements": "",
                "risk_mitigation": "",
                "success_criteria": [],
            }


key_account_plan_generator_service = KeyAccountPlanGeneratorService()
