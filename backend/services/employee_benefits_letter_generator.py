"""
Vox Employee Benefits Letter Generator Service 模块

员工福利函生成服务
- 福利详情
-  enrollment 信息
- 变更通知
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class EmployeeBenefitsLetterGeneratorService:
    """
    员工福利函生成服务

    生成员工福利函内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_employee_benefits_letter(
        self,
        employee_name: str,
        benefits_type: str,
        effective_date: str,
    ) -> Dict[str, Any]:
        """
        生成员工福利函

        Args:
            employee_name: 员工姓名
            benefits_type: 福利类型
            effective_date: 生效日期

        Returns:
            Dict: 员工福利函
        """
        try:
            prompt = f"""请为"{employee_name}"生成{benefits_type}福利类型的员工福利函（生效日期：{effective_date}）。

请以JSON格式返回：
{{
    "employee_name": "员工姓名",
    "benefits_type": "福利类型",
    "effective_date": "生效日期",
    "company_name": "公司名称",
    "letter_date": "函件日期",
    "salutation": "称呼",
    "benefits_summary": "福利摘要",
    "health_insurance": {{
        "plan_name": "计划名称",
        "coverage_level": "保障级别",
        "premium": "保费",
        "deductible": "免赔额"
    }},
    "retirement_benefits": {{
        "plan_type": "计划类型",
        "contribution_match": "缴款匹配",
        "vesting_schedule": "归属时间表"
    }},
    "paid_time_off": {{
        "vacation_days": "休假天数",
        "sick_days": "病假天数",
        "holidays": "节假日"
    }},
    "additional_benefits": ["额外福利1"],
    "enrollment_instructions": "注册说明",
    "next_steps": "下一步",
    "contact_information": "联系信息",
    "closing": "结束语",
    "signature": "签名"
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
                "benefits_type": benefits_type,
                "effective_date": effective_date,
                **result,
            }

        except Exception as e:
            logger.error(f"生成员工福利函失败: {e}")
            return {
                "employee_name": employee_name,
                "benefits_type": benefits_type,
                "effective_date": effective_date,
                "company_name": "",
                "letter_date": "",
                "salutation": "",
                "benefits_summary": "",
                "health_insurance": {},
                "retirement_benefits": {},
                "paid_time_off": {},
                "additional_benefits": [],
                "enrollment_instructions": "",
                "next_steps": "",
                "contact_information": "",
                "closing": "",
                "signature": "",
            }


employee_benefits_letter_generator_service = EmployeeBenefitsLetterGeneratorService()