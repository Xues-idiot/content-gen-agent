"""
Vox Onboarding Checklist Generator Service 模块

入职清单生成服务
- 新员工入职
- 流程检查
- 培训计划
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class OnboardingChecklistGeneratorService:
    """
    入职清单生成服务

    生成入职清单内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_onboarding_checklist(
        self,
        job_title: str,
        department: str,
        employment_type: str = "full-time",
    ) -> Dict[str, Any]:
        """
        生成入职清单

        Args:
            job_title: 职位名称
            department: 部门
            employment_type: 雇佣类型

        Returns:
            Dict: 入职清单
        """
        try:
            prompt = f"""请为"{job_title}"（部门：{department}，类型：{employment_type}）生成入职清单。

请以JSON格式返回：
{{
    "job_title": "职位名称",
    "department": "部门",
    "employment_type": "雇佣类型",
    "overview": "概述",
    "pre_day_one": [
        {{
            "task": "任务",
            "owner": "负责人",
            "due_date": "截止日期",
            "status": "状态"
        }}
    ],
    "day_one": ["第一天任务1"],
    "first_week": [
        {{
            "task": "任务",
            "day": "日期",
            "owner": "负责人"
        }}
    ],
    "first_month": [
        {{
            "task": "任务",
            "week": "周",
            "owner": "负责人"
        }}
    ],
    "training_requirements": ["培训要求1"],
    "required_documents": ["所需文件1"],
    "equipment_and_access": ["设备和访问权限1"],
    "key_contacts": ["关键联系人1"],
    "team_introductions": ["团队介绍1"],
    "goals_for_first_30_days": ["30天目标1"],
    "success_metrics": "成功指标"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "job_title": job_title,
                "department": department,
                "employment_type": employment_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成入职清单失败: {e}")
            return {
                "job_title": job_title,
                "department": department,
                "employment_type": employment_type,
                "overview": "",
                "pre_day_one": [],
                "day_one": [],
                "first_week": [],
                "first_month": [],
                "training_requirements": [],
                "required_documents": [],
                "equipment_and_access": [],
                "key_contacts": [],
                "team_introductions": [],
                "goals_for_first_30_days": [],
                "success_metrics": "",
            }


onboarding_checklist_generator_service = OnboardingChecklistGeneratorService()