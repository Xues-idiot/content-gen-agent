"""
Vox Employee Handbook Generator Service 模块

员工手册生成服务
- 公司政策
- 员工福利
- 行为规范
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class EmployeeHandbookGeneratorService:
    """
    员工手册生成服务

    生成员工手册内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_employee_handbook(
        self,
        company_name: str,
        industry: str,
        num_chapters: int = 10,
    ) -> Dict[str, Any]:
        """
        生成员工手册

        Args:
            company_name: 公司名称
            industry: 行业
            num_chapters: 章节数量

        Returns:
            Dict: 员工手册
        """
        try:
            prompt = f"""请为"{company_name}"（{industry}行业）生成包含{num_chapters}章的员工手册。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "industry": "行业",
    "num_chapters": 章节数,
    "version": "版本",
    "effective_date": "生效日期",
    "introduction": "引言",
    "about_company": "公司简介",
    "chapters": [
        {{
            "chapter_title": "章节标题",
            "content": "内容",
            "key_policies": ["关键政策1"]
        }}
    ],
    "code_of_conduct": "行为准则",
    "benefits_overview": "福利概述",
    "leave_policies": "休假政策",
    "performance_management": "绩效管理",
    "training_development": "培训发展",
    "workplace_safety": "工作场所安全",
    "it_security": "IT安全",
    "emergency_procedures": "紧急程序",
    "contact_directory": "联系人目录",
    "acknowledgment_form": "确认表单"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "company_name": company_name,
                "industry": industry,
                "num_chapters": num_chapters,
                **result,
            }

        except Exception as e:
            logger.error(f"生成员工手册失败: {e}")
            return {
                "company_name": company_name,
                "industry": industry,
                "num_chapters": num_chapters,
                "version": "",
                "effective_date": "",
                "introduction": "",
                "about_company": "",
                "chapters": [],
                "code_of_conduct": "",
                "benefits_overview": "",
                "leave_policies": "",
                "performance_management": "",
                "training_development": "",
                "workplace_safety": "",
                "it_security": "",
                "emergency_procedures": "",
                "contact_directory": "",
                "acknowledgment_form": "",
            }


employee_handbook_generator_service = EmployeeHandbookGeneratorService()