"""
Vox Career Opportunity Generator Service 模块

职位招聘生成服务
- 职位描述
- 任职要求
- 福利待遇
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CareerOpportunityGeneratorService:
    """
    职位招聘生成服务

    生成招聘职位内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_career_opportunity(
        self,
        job_title: str,
        department: str,
        location: str,
        employment_type: str = "full-time",
    ) -> Dict[str, Any]:
        """
        生成职位招聘

        Args:
            job_title: 职位名称
            department: 部门
            location: 工作地点
            employment_type: 雇佣类型

        Returns:
            Dict: 职位招聘
        """
        try:
            prompt = f"""请为"{job_title}"职位（部门：{department}，地点：{location}，类型：{employment_type}）生成招聘内容。

请以JSON格式返回：
{{
    "job_title": "职位名称",
    "department": "部门",
    "location": "工作地点",
    "employment_type": "雇佣类型",
    "job_summary": "职位摘要",
    "responsibilities": ["职责1", "职责2"],
    "requirements": ["要求1", "要求2"],
    "nice_to_have": ["加分项1"],
    "benefits": ["福利1"],
    "growth_opportunities": "发展机会"
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
                "location": location,
                "employment_type": employment_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成职位招聘失败: {e}")
            return {
                "job_title": job_title,
                "department": department,
                "location": location,
                "employment_type": employment_type,
                "job_summary": "",
                "responsibilities": [],
                "requirements": [],
                "nice_to_have": [],
                "benefits": [],
                "growth_opportunities": "",
            }


career_opportunity_generator_service = CareerOpportunityGeneratorService()