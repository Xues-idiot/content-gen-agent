"""
Vox Vendor Risk Assessment Generator Service 模块

供应商风险评估生成服务
- 风险因素
- 合规性
- 缓解策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class VendorRiskAssessmentGeneratorService:
    """
    供应商风险评估生成服务

    生成供应商风险评估内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_vendor_risk_assessment(
        self,
        vendor_name: str,
        vendor_category: str,
        num_factors: int = 10,
    ) -> Dict[str, Any]:
        """
        生成供应商风险评估

        Args:
            vendor_name: 供应商名称
            vendor_category: 供应商类别
            num_factors: 因素数量

        Returns:
            Dict: 供应商风险评估
        """
        try:
            prompt = f"""请为"{vendor_name}"（{vendor_category}类别）生成{num_factors}个因素的供应商风险评估。

请以JSON格式返回：
{{
    "vendor_name": "供应商名称",
    "vendor_category": "供应商类别",
    "num_factors": {num_factors},
    "executive_summary": "执行摘要",
    "vendor_overview": {{
        "company_background": "公司背景",
        "years_in_business": "营业年限",
        "client_base": "客户群",
        "financial_stability": "财务稳定性"
    }},
    "risk_factors": [
        {{
            "risk_factor": "风险因素",
            "risk_level": "风险级别",
            "assessment": "评估",
            "mitigation_strategy": "缓解策略"
        }}
    ],
    "compliance_checklist": ["合规检查清单1"],
    "data_security_practices": "数据安全实践",
    "business_continuity_plan": "业务连续性计划",
    "reference_checks": ["参考检查1"],
    "overall_risk_rating": "总体风险评级",
    "recommendations": ["建议1"],
    "ongoing_monitoring_requirements": "持续监控要求"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "vendor_name": vendor_name,
                "vendor_category": vendor_category,
                "num_factors": num_factors,
                **result,
            }

        except Exception as e:
            logger.error(f"生成供应商风险评估失败: {e}")
            return {
                "vendor_name": vendor_name,
                "vendor_category": vendor_category,
                "num_factors": num_factors,
                "executive_summary": "",
                "vendor_overview": {},
                "risk_factors": [],
                "compliance_checklist": [],
                "data_security_practices": "",
                "business_continuity_plan": "",
                "reference_checks": [],
                "overall_risk_rating": "",
                "recommendations": [],
                "ongoing_monitoring_requirements": "",
            }


vendor_risk_assessment_generator_service = VendorRiskAssessmentGeneratorService()
