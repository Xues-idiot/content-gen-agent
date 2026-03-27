"""
Vox Enterprise Software Selection Generator Service 模块

企业软件选型生成服务
- 需求定义
- 供应商评估
- 决策建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class EnterpriseSoftwareSelectionGeneratorService:
    """
    企业软件选型生成服务

    生成企业软件选型内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_enterprise_software_selection(
        self,
        software_category: str,
        organization_size: str,
        num_requirements: int = 10,
    ) -> Dict[str, Any]:
        """
        生成企业软件选型

        Args:
            software_category: 软件类别
            organization_size: 组织规模
            num_requirements: 需求数量

        Returns:
            Dict: 企业软件选型
        """
        try:
            prompt = f"""请为{software_category}软件在{organization_size}规模组织中生成{num_requirements}个需求的企业软件选型。

请以JSON格式返回：
{{
    "software_category": "软件类别",
    "organization_size": "组织规模",
    "num_requirements": {num_requirements},
    "executive_summary": "执行摘要",
    "business_requirements": ["业务需求1"],
    "technical_requirements": ["技术需求1"],
    "vendor_evaluation_criteria": ["供应商评估标准1"],
    "recommended_vendors": [
        {{
            "vendor_name": "供应商名称",
            "strengths": ["优势1"],
            "weaknesses": ["弱点1"],
            "estimated_cost": "估计成本",
            "implementation_complexity": "实施复杂性"
        }}
    ],
    "decision_framework": "决策框架",
    "risk_assessment": ["风险评估1"],
    "implementation_recommendations": "实施建议"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "software_category": software_category,
                "organization_size": organization_size,
                "num_requirements": num_requirements,
                **result,
            }

        except Exception as e:
            logger.error(f"生成企业软件选型失败: {e}")
            return {
                "software_category": software_category,
                "organization_size": organization_size,
                "num_requirements": num_requirements,
                "executive_summary": "",
                "business_requirements": [],
                "technical_requirements": [],
                "vendor_evaluation_criteria": [],
                "recommended_vendors": [],
                "decision_framework": "",
                "risk_assessment": [],
                "implementation_recommendations": "",
            }


enterprise_software_selection_generator_service = EnterpriseSoftwareSelectionGeneratorService()
