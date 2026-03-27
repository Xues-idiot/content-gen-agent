"""
Vox Account Discovery Report Generator Service 模块

账户发现报告生成服务
- 潜在客户
- 决策链
- 机会评估
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class AccountDiscoveryReportGeneratorService:
    """
    账户发现报告生成服务

    生成账户发现报告内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_account_discovery_report(
        self,
        account_name: str,
        industry: str,
        num_stakeholders: int = 6,
    ) -> Dict[str, Any]:
        """
        生成账户发现报告

        Args:
            account_name: 账户名称
            industry: 行业
            num_stakeholders: 利益相关者数量

        Returns:
            Dict: 账户发现报告
        """
        try:
            prompt = f"""请为"{account_name}"（{industry}行业）生成{num_stakeholders}个利益相关者的账户发现报告。

请以JSON格式返回：
{{
    "account_name": "账户名称",
    "industry": "行业",
    "num_stakeholders": {num_stakeholders},
    "company_overview": "公司概述",
    "business_challenges": ["业务挑战1"],
    "stakeholders": [
        {{
            "name": "姓名",
            "title": "职位",
            "influence_level": "影响力级别",
            "pain_points": ["痛点1"],
            "communication_preference": "沟通偏好"
        }}
    ],
    "buying_process": "购买流程",
    "competitive_landscape": "竞争格局",
    "opportunity_assessment": "机会评估",
    "recommended_approach": "推荐方法",
    "risk_factors": ["风险因素1"]
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
                "industry": industry,
                "num_stakeholders": num_stakeholders,
                **result,
            }

        except Exception as e:
            logger.error(f"生成账户发现报告失败: {e}")
            return {
                "account_name": account_name,
                "industry": industry,
                "num_stakeholders": num_stakeholders,
                "company_overview": "",
                "business_challenges": [],
                "stakeholders": [],
                "buying_process": "",
                "competitive_landscape": "",
                "opportunity_assessment": "",
                "recommended_approach": "",
                "risk_factors": [],
            }


account_discovery_report_generator_service = AccountDiscoveryReportGeneratorService()
