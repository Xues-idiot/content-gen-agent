"""
Vox Status Report Template Generator Service 模块

状态报告模板生成服务
- 项目状态
- 进度追踪
- 风险报告
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class StatusReportTemplateGeneratorService:
    """
    状态报告模板生成服务

    生成状态报告模板内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_status_report_template(
        self,
        project_name: str,
        report_type: str = "project status",
        reporting_period: str = "weekly",
    ) -> Dict[str, Any]:
        """
        生成状态报告模板

        Args:
            project_name: 项目名称
            report_type: 报告类型
            reporting_period: 报告周期

        Returns:
            Dict: 状态报告模板
        """
        try:
            prompt = f"""请为"{project_name}"生成{report_type}类型（周期：{reporting_period}）的状态报告模板。

请以JSON格式返回：
{{
    "project_name": "项目名称",
    "report_type": "报告类型",
    "reporting_period": "报告周期",
    "report_date": "报告日期",
    "prepared_by": "编制人",
    "executive_summary": "执行摘要",
    "overall_status": "总体状态",
    "progress_summary": "进度摘要",
    "accomplishments_this_period": ["本期成就1"],
    "planned_for_next_period": ["下期计划1"],
    "metrics": [
        {{
            "metric": "指标",
            "target": "目标",
            "actual": "实际",
            "variance": "差异",
            "status": "状态"
        }}
    ],
    "budget_status": "预算状态",
    "timeline_status": "时间线状态",
    "resource_status": "资源状态",
    "issues_and_blockers": ["问题和阻碍1"],
    "risks": [
        {{
            "risk": "风险",
            "likelihood": "可能性",
            "impact": "影响",
            "mitigation": "缓解措施"
        }}
    ],
    "changes": ["变更1"],
    "stakeholder_engagement": "利益相关方参与",
    "quality_metrics": "质量指标",
    "next_steps": "下一步",
    "attachments": ["附件1"]
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
                "report_type": report_type,
                "reporting_period": reporting_period,
                **result,
            }

        except Exception as e:
            logger.error(f"生成状态报告模板失败: {e}")
            return {
                "project_name": project_name,
                "report_type": report_type,
                "reporting_period": reporting_period,
                "report_date": "",
                "prepared_by": "",
                "executive_summary": "",
                "overall_status": "",
                "progress_summary": "",
                "accomplishments_this_period": [],
                "planned_for_next_period": [],
                "metrics": [],
                "budget_status": "",
                "timeline_status": "",
                "resource_status": "",
                "issues_and_blockers": [],
                "risks": [],
                "changes": [],
                "stakeholder_engagement": "",
                "quality_metrics": "",
                "next_steps": "",
                "attachments": [],
            }


status_report_template_generator_service = StatusReportTemplateGeneratorService()