"""
Vox Exit Interview Template Generator Service 模块

离职面谈模板生成服务
- 离职原因
- 反馈收集
- 改进建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ExitInterviewTemplateGeneratorService:
    """
    离职面谈模板生成服务

    生成离职面谈模板内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_exit_interview_template(
        self,
        employee_name: str,
        department: str,
        tenure: str,
    ) -> Dict[str, Any]:
        """
        生成离职面谈模板

        Args:
            employee_name: 员工姓名
            department: 部门
            tenure: 任职时间

        Returns:
            Dict: 离职面谈模板
        """
        try:
            prompt = f"""请为"{employee_name}"（部门：{department}，任职：{tenure}）生成离职面谈模板。

请以JSON格式返回：
{{
    "employee_name": "员工姓名",
    "department": "部门",
    "tenure": "任职时间",
    "interview_date": "面谈日期",
    "interviewer": "面谈人",
    "sections": [
        {{
            "section_title": "章节标题",
            "questions": ["问题1"],
            "notes_section": "备注区"
        }}
    ],
    "opening_questions": ["开场问题1"],
    "reason_for_leaving_questions": ["离职原因问题1"],
    "job_satisfaction_questions": ["工作满意度问题1"],
    "management_feedback_questions": ["管理反馈问题1"],
    "work_environment_questions": ["工作环境问题1"],
    "compensation_benefits_questions": ["薪酬福利问题1"],
    "career_development_questions": ["职业发展问题1"],
    "training_questions": ["培训问题1"],
    "recommendations_questions": ["建议问题1"],
    "closing_questions": ["结束问题1"],
    "confidentiality_statement": "保密声明",
    "next_steps": "后续步骤"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "employee_name": employee_name,
                "department": department,
                "tenure": tenure,
                **result,
            }

        except Exception as e:
            logger.error(f"生成离职面谈模板失败: {e}")
            return {
                "employee_name": employee_name,
                "department": department,
                "tenure": tenure,
                "interview_date": "",
                "interviewer": "",
                "sections": [],
                "opening_questions": [],
                "reason_for_leaving_questions": [],
                "job_satisfaction_questions": [],
                "management_feedback_questions": [],
                "work_environment_questions": [],
                "compensation_benefits_questions": [],
                "career_development_questions": [],
                "training_questions": [],
                "recommendations_questions": [],
                "closing_questions": [],
                "confidentiality_statement": "",
                "next_steps": "",
            }


exit_interview_template_generator_service = ExitInterviewTemplateGeneratorService()