"""
Vox Cybersecurity Strategy Generator Service 模块

网络安全策略生成服务
- 威胁分析
- 安全控制
- 事件响应
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CybersecurityStrategyGeneratorService:
    """
    网络安全策略生成服务

    生成网络安全策略内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_cybersecurity_strategy(
        self,
        organization: str,
        risk_level: str,
        num_controls: int = 8,
    ) -> Dict[str, Any]:
        """
        生成网络安全策略

        Args:
            organization: 组织
            risk_level: 风险级别
            num_controls: 控制数量

        Returns:
            Dict: 网络安全策略
        """
        try:
            prompt = f"""请为{organization}生成风险级别为{risk_level}的{num_controls}个控制的网络安全策略。

请以JSON格式返回：
{{
    "organization": "组织",
    "risk_level": "风险级别",
    "num_controls": {num_controls},
    "executive_summary": "执行摘要",
    "threat_landscape": "威胁形势",
    "security_objectives": ["安全目标1"],
    "security_controls": [
        {{
            "control_name": "控制名称",
            "control_category": "控制类别",
            "implementation_status": "实施状态",
            "priority": "优先级",
            "expected_outcome": "预期结果"
        }}
    ],
    "incident_response_plan": "事件响应计划",
    "compliance_requirements": "合规要求",
    "security_metrics": ["安全指标1"],
    "budget_requirements": "预算需求",
    "training_awareness": "培训意识"
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
                "risk_level": risk_level,
                "num_controls": num_controls,
                **result,
            }

        except Exception as e:
            logger.error(f"生成网络安全策略失败: {e}")
            return {
                "organization": organization,
                "risk_level": risk_level,
                "num_controls": num_controls,
                "executive_summary": "",
                "threat_landscape": "",
                "security_objectives": [],
                "security_controls": [],
                "incident_response_plan": "",
                "compliance_requirements": "",
                "security_metrics": [],
                "budget_requirements": "",
                "training_awareness": "",
            }


cybersecurity_strategy_generator_service = CybersecurityStrategyGeneratorService()
