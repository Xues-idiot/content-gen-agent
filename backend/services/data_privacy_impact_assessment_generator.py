"""
Vox Data Privacy Impact Assessment Generator Service 模块

数据隐私影响评估生成服务
- 隐私风险
- 影响分析
- 缓解措施
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class DataPrivacyImpactAssessmentGeneratorService:
    """
    数据隐私影响评估生成服务

    生成数据隐私影响评估内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_data_privacy_impact_assessment(
        self,
        project_name: str,
        data_types: List[str],
        num_risks: int = 8,
    ) -> Dict[str, Any]:
        """
        生成数据隐私影响评估

        Args:
            project_name: 项目名称
            data_types: 数据类型列表
            num_risks: 风险数量

        Returns:
            Dict: 数据隐私影响评估
        """
        data_types_str = ", ".join(data_types[:5])

        try:
            prompt = f"""请为"{project_name}"项目（数据类型：{data_types_str}）生成{num_risks}个风险的数据隐私影响评估。

请以JSON格式返回：
{{
    "project_name": "项目名称",
    "data_types": {data_types},
    "num_risks": {num_risks},
    "executive_summary": "执行摘要",
    "project_description": "项目描述",
    "data_flow_description": "数据流描述",
    "privacy_risks": [
        {{
            "risk_name": "风险名称",
            "risk_description": "风险描述",
            "likelihood": "可能性",
            "impact": "影响",
            "risk_level": "风险级别",
            "mitigation_measures": ["缓解措施1"]
        }}
    ],
    "compliance_with_privacy_principles": "隐私原则合规性",
    "data_subject_rights": "数据主体权利",
    "consent_management": "同意管理",
    "data_retention_policy": "数据保留政策",
    "recommended_additional_safeguards": ["推荐的额外保障措施1"],
    "stakeholder_consultation": "利益相关者协商",
    "implementation_timeline": "实施时间线"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "project_name": project_name,
                "data_types": data_types,
                "num_risks": num_risks,
                **result,
            }

        except Exception as e:
            logger.error(f"生成数据隐私影响评估失败: {e}")
            return {
                "project_name": project_name,
                "data_types": data_types,
                "num_risks": num_risks,
                "executive_summary": "",
                "project_description": "",
                "data_flow_description": "",
                "privacy_risks": [],
                "compliance_with_privacy_principles": "",
                "data_subject_rights": "",
                "consent_management": "",
                "data_retention_policy": "",
                "recommended_additional_safeguards": [],
                "stakeholder_consultation": "",
                "implementation_timeline": "",
            }


data_privacy_impact_assessment_generator_service = DataPrivacyImpactAssessmentGeneratorService()
