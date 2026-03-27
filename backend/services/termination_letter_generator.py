"""
Vox Termination Letter Generator Service 模块

终止函生成服务
- 离职原因
- 权益说明
- 交接程序
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TerminationLetterGeneratorService:
    """
    终止函生成服务

    生成终止函内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_termination_letter(
        self,
        employee_name: str,
        termination_date: str,
        reason: str,
    ) -> Dict[str, Any]:
        """
        生成终止函

        Args:
            employee_name: 员工姓名
            termination_date: 终止日期
            reason: 原因

        Returns:
            Dict: 终止函
        """
        try:
            prompt = f"""请为"{employee_name}"生成终止函（终止日期：{termination_date}，原因：{reason}）。

请以JSON格式返回：
{{
    "employee_name": "员工姓名",
    "termination_date": "终止日期",
    "reason": "原因",
    "company_name": "公司名称",
    "letter_date": "函件日期",
    "salutation": "称呼",
    "body": "正文",
    "final_pay": {{
        "accrued_vacation": " accrued vacation",
        "severance": "遣散费",
        "other_payments": "其他付款"
    }},
    "benefits_continuation": "福利继续",
    "company_property": "公司财产",
    "reference_policy": "推荐政策",
    "non_disparagement": " non-disparagement",
    "legal_notes": "法律备注",
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
                "termination_date": termination_date,
                "reason": reason,
                **result,
            }

        except Exception as e:
            logger.error(f"生成终止函失败: {e}")
            return {
                "employee_name": employee_name,
                "termination_date": termination_date,
                "reason": reason,
                "company_name": "",
                "letter_date": "",
                "salutation": "",
                "body": "",
                "final_pay": {},
                "benefits_continuation": "",
                "company_property": "",
                "reference_policy": "",
                "non_disparagement": "",
                "legal_notes": "",
                "signature": "",
            }


termination_letter_generator_service = TerminationLetterGeneratorService()