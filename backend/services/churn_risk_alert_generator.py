"""
Vox Churn Risk Alert Generator Service 模块

流失风险警报生成服务
- 风险指标
- 警报阈值
- 保留策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ChurnRiskAlertGeneratorService:
    """
    流失风险警报生成服务

    生成流失风险警报内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_churn_risk_alert(
        self,
        customer_name: str,
        risk_factors: List[str],
        risk_level: str = "medium",
    ) -> Dict[str, Any]:
        """
        生成流失风险警报

        Args:
            customer_name: 客户名称
            risk_factors: 风险因素
            risk_level: 风险等级

        Returns:
            Dict: 流失风险警报
        """
        factors_str = ", ".join(risk_factors[:3])

        try:
            prompt = f"""请为"{customer_name}"生成风险等级为{risk_level}的流失风险警报（风险因素：{factors_str}）。

请以JSON格式返回：
{{
    "customer_name": "客户名称",
    "risk_factors": {risk_factors},
    "risk_level": "风险等级",
    "risk_score": "风险评分",
    "alert_summary": "警报摘要",
    "triggered_indicators": ["触发的指标1"],
    "recommended_actions": [
        {{
            "action": "行动",
            "priority": "优先级",
            "expected_impact": "预期影响"
        }}
    ],
    "retention_offer": "保留优惠",
    "success_probability": "成功概率",
    "next_steps": ["下一步1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "customer_name": customer_name,
                "risk_factors": risk_factors,
                "risk_level": risk_level,
                **result,
            }

        except Exception as e:
            logger.error(f"生成流失风险警报失败: {e}")
            return {
                "customer_name": customer_name,
                "risk_factors": risk_factors,
                "risk_level": risk_level,
                "risk_score": "",
                "alert_summary": "",
                "triggered_indicators": [],
                "recommended_actions": [],
                "retention_offer": "",
                "success_probability": "",
                "next_steps": [],
            }


churn_risk_alert_generator_service = ChurnRiskAlertGeneratorService()