"""
Vox Impact Report Generator Service 模块

影响报告生成服务
- 项目成效
- 社会价值
- 数据展示
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ImpactReportGeneratorService:
    """
    影响报告生成服务

    生成影响报告内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_impact_report(
        self,
        organization_name: str,
        project_name: str,
        report_period: str = "2025",
    ) -> Dict[str, Any]:
        """
        生成影响报告

        Args:
            organization_name: 组织名称
            project_name: 项目名称
            report_period: 报告周期

        Returns:
            Dict: 影响报告
        """
        try:
            prompt = f"""请为"{organization_name}"的"{project_name}"项目生成{report_period}年影响报告。

请以JSON格式返回：
{{
    "organization_name": "组织名称",
    "project_name": "项目名称",
    "report_period": "报告周期",
    "executive_summary": "执行摘要",
    "key_achievements": ["关键成就1"],
    "impact_metrics": [
        {{
            "metric": "指标",
            "value": "数值",
            "change": "变化"
        }}
    ],
    "beneficiary_stories": ["受益者故事1"],
    "challenges_faced": ["面临的挑战1"],
    "lessons_learned": ["经验教训1"],
    "partnerships": ["合作伙伴1"],
    "financial_summary": "财务摘要",
    "future_plans": "未来计划",
    "testimonials": ["推荐信1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "organization_name": organization_name,
                "project_name": project_name,
                "report_period": report_period,
                **result,
            }

        except Exception as e:
            logger.error(f"生成影响报告失败: {e}")
            return {
                "organization_name": organization_name,
                "project_name": project_name,
                "report_period": report_period,
                "executive_summary": "",
                "key_achievements": [],
                "impact_metrics": [],
                "beneficiary_stories": [],
                "challenges_faced": [],
                "lessons_learned": [],
                "partnerships": [],
                "financial_summary": "",
                "future_plans": "",
                "testimonials": [],
            }


impact_report_generator_service = ImpactReportGeneratorService()