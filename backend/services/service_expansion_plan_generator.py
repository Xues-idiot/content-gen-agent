"""
Vox Service Expansion Plan Generator Service 模块

服务扩展计划生成服务
- 扩展机会
- 资源规划
- 风险评估
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ServiceExpansionPlanGeneratorService:
    """
    服务扩展计划生成服务

    生成服务扩展计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_service_expansion_plan(
        self,
        current_service: str,
        expansion_scope: str,
        num_phases: int = 4,
    ) -> Dict[str, Any]:
        """
        生成服务扩展计划

        Args:
            current_service: 当前服务
            expansion_scope: 扩展范围
            num_phases: 阶段数量

        Returns:
            Dict: 服务扩展计划
        """
        try:
            prompt = f"""请为"{current_service}"服务生成扩展到{expansion_scope}的{num_phases}阶段服务扩展计划。

请以JSON格式返回：
{{
    "current_service": "当前服务",
    "expansion_scope": "扩展范围",
    "num_phases": {num_phases},
    "expansion_summary": "扩展摘要",
    "expansion_phases": [
        {{
            "phase_name": "阶段名称",
            "duration": "持续时间",
            "new_capabilities": ["新能力1"],
            "resource_requirements": "资源需求",
            "expected_outcomes": ["预期成果1"]
        }}
    ],
    "market_opportunity": "市场机会",
    "investment_requirements": "投资需求",
    "risk_assessment": [
        {{
            "risk": "风险",
            "likelihood": "可能性",
            "mitigation": "缓解措施"
        }}
    ],
    "success_metrics": ["成功指标1"],
    "timeline_milestones": ["时间线里程碑1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "current_service": current_service,
                "expansion_scope": expansion_scope,
                "num_phases": num_phases,
                **result,
            }

        except Exception as e:
            logger.error(f"生成服务扩展计划失败: {e}")
            return {
                "current_service": current_service,
                "expansion_scope": expansion_scope,
                "num_phases": num_phases,
                "expansion_summary": "",
                "expansion_phases": [],
                "market_opportunity": "",
                "investment_requirements": "",
                "risk_assessment": [],
                "success_metrics": [],
                "timeline_milestones": [],
            }


service_expansion_plan_generator_service = ServiceExpansionPlanGeneratorService()
