"""
Vox Human Resources Policy Generator Service 模块

人力资源政策生成服务
- 员工政策
- 福利说明
- 行为准则
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class HumanResourcesPolicyGeneratorService:
    """
    人力资源政策生成服务

    生成人力资源政策内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_hr_policy(
        self,
        company_name: str,
        policy_type: str,
        num_sections: int = 8,
    ) -> Dict[str, Any]:
        """
        生成人力资源政策

        Args:
            company_name: 公司名称
            policy_type: 政策类型
            num_sections: 章节数量

        Returns:
            Dict: 人力资源政策
        """
        try:
            prompt = f"""请为"{company_name}"生成{policy_type}人力资源政策（共{num_sections}章节）。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "policy_type": "政策类型",
    "num_sections": 章节数,
    "effective_date": "生效日期",
    "purpose": "目的",
    "scope": "范围",
    "policy_statements": [
        {{
            "section": "章节",
            "content": "内容",
            "key_points": ["要点1"]
        }}
    ],
    "procedures": ["程序1"],
    "employee_responsibilities": ["员工责任1"],
    "management_responsibilities": "管理责任",
    "compliance_requirements": ["合规要求1"],
    "violation_consequences": "违规后果",
    "review_process": "审查流程",
    "contact_information": "联系信息"
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
                "policy_type": policy_type,
                "num_sections": num_sections,
                **result,
            }

        except Exception as e:
            logger.error(f"生成人力资源政策失败: {e}")
            return {
                "company_name": company_name,
                "policy_type": policy_type,
                "num_sections": num_sections,
                "effective_date": "",
                "purpose": "",
                "scope": "",
                "policy_statements": [],
                "procedures": [],
                "employee_responsibilities": [],
                "management_responsibilities": "",
                "compliance_requirements": [],
                "violation_consequences": "",
                "review_process": "",
                "contact_information": "",
            }


human_resources_policy_generator_service = HumanResourcesPolicyGeneratorService()