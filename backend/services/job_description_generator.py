"""
Vox Job Description Generator Service 模块

职位描述生成服务
- 职位概要
- 职责要求
- 任职资格
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class JobDescriptionGeneratorService:
    """
    职位描述生成服务

    生成职位描述内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_job_description(
        self,
        job_title: str,
        department: str,
        location: str,
        employment_type: str = "full-time",
    ) -> Dict[str, Any]:
        """
        生成职位描述

        Args:
            job_title: 职位名称
            department: 部门
            location: 工作地点
            employment_type: 雇佣类型

        Returns:
            Dict: 职位描述
        """
        try:
            prompt = f"""请为"{job_title}"（部门：{department}，地点：{location}，类型：{employment_type}）生成职位描述。

请以JSON格式返回：
{{
    "job_title": "职位名称",
    "department": "部门",
    "location": "工作地点",
    "employment_type": "雇佣类型",
    "job_summary": "职位概要",
    "about_company": "公司介绍",
    "key_responsibilities": ["主要职责1"],
    "daily_activities": ["日常工作1"],
    "qualifications": {{
        "education": "教育要求",
        "experience": "经验要求",
        "skills": ["技能要求1"]
    }},
    "required_experience": ["必需经验1"],
    "preferred_qualifications": ["优先资格1"],
    "technical_requirements": ["技术要求1"],
    "soft_skills": ["软技能1"],
    "language_requirements": ["语言要求1"],
    "certifications": ["证书1"],
    "compensation_benefits": ["薪酬福利1"],
    "career_growth": "职业发展",
    "work_environment": "工作环境",
    "diversity_statement": "多样性声明"
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
            logger.error(f"生成职位描述失败: {e}")
            return {
                "job_title": job_title,
                "department": department,
                "location": location,
                "employment_type": employment_type,
                "job_summary": "",
                "about_company": "",
                "key_responsibilities": [],
                "daily_activities": [],
                "qualifications": {},
                "required_experience": [],
                "preferred_qualifications": [],
                "technical_requirements": [],
                "soft_skills": [],
                "language_requirements": [],
                "certifications": [],
                "compensation_benefits": [],
                "career_growth": "",
                "work_environment": "",
                "diversity_statement": "",
            }


job_description_generator_service = JobDescriptionGeneratorService()