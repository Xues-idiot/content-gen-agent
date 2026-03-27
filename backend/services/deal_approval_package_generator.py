"""
Vox Deal Approval Package Generator Service 模块

交易审批包生成服务
- 交易摘要
- 财务分析
- 风险评估
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class DealApprovalPackageGeneratorService:
    """
    交易审批包生成服务

    生成交易审批包内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_deal_approval_package(
        self,
        deal_name: str,
        account_name: str,
        deal_value: str,
    ) -> Dict[str, Any]:
        """
        生成交易审批包

        Args:
            deal_name: 交易名称
            account_name: 账户名称
            deal_value: 交易价值

        Returns:
            Dict: 交易审批包
        """
        try:
            prompt = f"""请为交易"{deal_name}"（账户：{account_name}，价值：{deal_value}）生成审批包。

请以JSON格式返回：
{{
    "deal_name": "交易名称",
    "account_name": "账户名称",
    "deal_value": "交易价值",
    "executive_summary": "执行摘要",
    "customer_background": "客户背景",
    "business_case": {{
        "problem_statement": "问题陈述",
        "proposed_solution": "提出的解决方案",
        "expected_outcomes": ["预期成果1"]
    }},
    "financial_summary": {{
        "total_value": "总价值",
        "pricing_tiers": "定价层级",
        "margin_impact": "利润率影响",
        "payment_terms": "付款条款"
    }},
    "competitive_position": "竞争地位",
    "risk_assessment": [
        {{
            "risk": "风险",
            "likelihood": "可能性",
            "mitigation": "缓解措施"
        }}
    ],
    "strategic_rationale": "战略理由",
    "approval_recommendation": "审批建议",
    "required_signoffs": ["需要签字1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "deal_name": deal_name,
                "account_name": account_name,
                "deal_value": deal_value,
                **result,
            }

        except Exception as e:
            logger.error(f"生成交易审批包失败: {e}")
            return {
                "deal_name": deal_name,
                "account_name": account_name,
                "deal_value": deal_value,
                "executive_summary": "",
                "customer_background": "",
                "business_case": {},
                "financial_summary": {},
                "competitive_position": "",
                "risk_assessment": [],
                "strategic_rationale": "",
                "approval_recommendation": "",
                "required_signoffs": [],
            }


deal_approval_package_generator_service = DealApprovalPackageGeneratorService()
