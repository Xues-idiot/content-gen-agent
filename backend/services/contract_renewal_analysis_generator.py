"""
Vox Contract Renewal Analysis Generator Service 模块

合同续约分析生成服务
- 续约风险评估
- 价值分析
- 续约策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ContractRenewalAnalysisGeneratorService:
    """
    合同续约分析生成服务

    生成合同续约分析内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_contract_renewal_analysis(
        self,
        customer_name: str,
        contract_value: str,
        renewal_date: str,
    ) -> Dict[str, Any]:
        """
        生成合同续约分析

        Args:
            customer_name: 客户名称
            contract_value: 合同价值
            renewal_date: 续约日期

        Returns:
            Dict: 合同续约分析
        """
        try:
            prompt = f"""请为"{customer_name}"生成合同续约分析（合同价值：{contract_value}，续约日期：{renewal_date}）。

请以JSON格式返回：
{{
    "customer_name": "客户名称",
    "contract_value": "合同价值",
    "renewal_date": "续约日期",
    "renewal_probability": "续约概率",
    "risk_level": "风险等级",
    "value_analysis": {{
        "current_value": "当前价值",
        "potential_expansion": "潜在扩展",
        "cost_to_serve": "服务成本"
    }},
    "health_indicators": ["健康指标1"],
    "engagement_level": "参与度水平",
    "competitive_threats": ["竞争威胁1"],
    "renewal_strategy": "续约策略",
    "stakeholder_mapping": ["利益相关者映射1"],
    "action_plan": ["行动方案1"],
    "success_probability": "成功概率"
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
                "contract_value": contract_value,
                "renewal_date": renewal_date,
                **result,
            }

        except Exception as e:
            logger.error(f"生成合同续约分析失败: {e}")
            return {
                "customer_name": customer_name,
                "contract_value": contract_value,
                "renewal_date": renewal_date,
                "renewal_probability": "",
                "risk_level": "",
                "value_analysis": {},
                "health_indicators": [],
                "engagement_level": "",
                "competitive_threats": [],
                "renewal_strategy": "",
                "stakeholder_mapping": [],
                "action_plan": [],
                "success_probability": "",
            }


contract_renewal_analysis_generator_service = ContractRenewalAnalysisGeneratorService()
