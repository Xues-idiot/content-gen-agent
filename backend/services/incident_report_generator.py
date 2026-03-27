"""
Vox Incident Report Generator Service 模块

事件报告生成服务
- 故障分析
- 根本原因
- 改进措施
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class IncidentReportGeneratorService:
    """
    事件报告生成服务

    生成事件报告内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_incident_report(
        self,
        incident_title: str,
        severity: str = "medium",
        system_name: str = "",
    ) -> Dict[str, Any]:
        """
        生成事件报告

        Args:
            incident_title: 事件标题
            severity: 严重程度
            system_name: 系统名称

        Returns:
            Dict: 事件报告
        """
        try:
            system_context = f"系统：{system_name}" if system_name else "系统：未指定"
            prompt = f"""请为"{incident_title}"（严重程度：{severity}，{system_context}）生成事件报告。

请以JSON格式返回：
{{
    "incident_title": "事件标题",
    "severity": "严重程度",
    "system_name": "系统名称",
    "incident_id": "事件ID",
    "detected_time": "发现时间",
    "resolved_time": "解决时间",
    "duration": "持续时间",
    "summary": "摘要",
    "impact": "影响",
    "timeline": [
        {{
            "time": "时间",
            "event": "事件",
            "action_taken": "采取的行动"
        }}
    ],
    "root_cause": "根本原因",
    "contributing_factors": ["促成因素1"],
    "resolution_steps": ["解决步骤1"],
    "lessons_learned": ["经验教训1"],
    "preventive_measures": ["预防措施1"],
    "action_items": [
        {{
            "item": "行动项",
            "owner": "负责人",
            "due_date": "截止日期",
            "status": "状态"
        }}
    ],
    "resources_affected": ["受影响的资源1"],
    "customer_impact": "客户影响"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "incident_title": incident_title,
                "severity": severity,
                "system_name": system_name,
                **result,
            }

        except Exception as e:
            logger.error(f"生成事件报告失败: {e}")
            return {
                "incident_title": incident_title,
                "severity": severity,
                "system_name": system_name,
                "incident_id": "",
                "detected_time": "",
                "resolved_time": "",
                "duration": "",
                "summary": "",
                "impact": "",
                "timeline": [],
                "root_cause": "",
                "contributing_factors": [],
                "resolution_steps": [],
                "lessons_learned": [],
                "preventive_measures": [],
                "action_items": [],
                "resources_affected": [],
                "customer_impact": "",
            }


incident_report_generator_service = IncidentReportGeneratorService()