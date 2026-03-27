"""
Vox Job Offer Letter Generator Service 模块

工作邀请函生成服务
- 薪酬方案
- 入职详情
- 条款条件
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class JobOfferLetterGeneratorService:
    """
    工作邀请函生成服务

    生成工作邀请函内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_job_offer_letter(
        self,
        candidate_name: str,
        position_title: str,
        start_date: str,
    ) -> Dict[str, Any]:
        """
        生成工作邀请函

        Args:
            candidate_name: 候选人姓名
            position_title: 职位名称
            start_date: 开始日期

        Returns:
            Dict: 工作邀请函
        """
        try:
            prompt = f"""请为"{candidate_name}"生成职位为{position_title}的工作邀请函（开始日期：{start_date}）。

请以JSON格式返回：
{{
    "candidate_name": "候选人姓名",
    "position_title": "职位名称",
    "start_date": "开始日期",
    "company_name": "公司名称",
    "letter_date": "函件日期",
    "salutation": "称呼",
    "position_details": {{
        "title": "职位",
        "department": "部门",
        "reporting_to": "汇报对象",
        "location": "工作地点"
    }},
    "compensation": {{
        "base_salary": "基本工资",
        "bonus": "奖金",
        "equity": "股权",
        "signing_bonus": "签约奖金"
    }},
    "benefits": ["福利1"],
    "start_date_details": "开始日期详情",
    "employment_type": "雇佣类型",
    "probation_period": "试用期",
    "confidentiality_agreement": "保密协议",
    "at_will_employment": "随意雇佣",
    "conditions": ["条件1"],
    "response_deadline": "回复截止日期",
    "acceptance_process": "接受流程",
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
                "candidate_name": candidate_name,
                "position_title": position_title,
                "start_date": start_date,
                **result,
            }

        except Exception as e:
            logger.error(f"生成工作邀请函失败: {e}")
            return {
                "candidate_name": candidate_name,
                "position_title": position_title,
                "start_date": start_date,
                "company_name": "",
                "letter_date": "",
                "salutation": "",
                "position_details": {},
                "compensation": {},
                "benefits": [],
                "start_date_details": "",
                "employment_type": "",
                "probation_period": "",
                "confidentiality_agreement": "",
                "at_will_employment": "",
                "conditions": [],
                "response_deadline": "",
                "acceptance_process": "",
                "next_steps": "",
                "contact_information": "",
                "closing": "",
                "signature": "",
            }


job_offer_letter_generator_service = JobOfferLetterGeneratorService()