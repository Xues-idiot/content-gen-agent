"""
Vox Partnership Outreach Generator Service 模块

合作关系外联生成服务
- 合作提案
- 外联邮件
- 跟进序列
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PartnershipOutreachGeneratorService:
    """
    合作关系外联生成服务

    生成合作关系外联内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_partnership_outreach(
        self,
        partner_name: str,
        partnership_type: str,
        your_company: str,
    ) -> Dict[str, Any]:
        """
        生成合作关系外联

        Args:
            partner_name: 合作伙伴名称
            partnership_type: 合作关系类型
            your_company: 你的公司

        Returns:
            Dict: 合作关系外联
        """
        try:
            prompt = f"""请为"{your_company}"生成与"{partner_name}"的{partnership_type}类型合作关系外联内容。

请以JSON格式返回：
{{
    "partner_name": "合作伙伴名称",
    "partnership_type": "合作关系类型",
    "your_company": "你的公司",
    "initial_outreach_email": {{
        "subject": "主题",
        "body": "正文"
    }},
    "follow_up_sequence": [
        {{
            "day": "天",
            "subject": "主题",
            "body": "正文"
        }}
    ],
    "value_proposition": "价值主张",
    "partnership_benefits": {{
        "for_partner": "对合作伙伴",
        "for_you": "对你"
    }},
    "proposed_terms": "提议条款",
    "best_contact_time": "最佳联系时间",
    "linkedin_outreach": "LinkedIn外联",
    "call_script": "电话脚本"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "partner_name": partner_name,
                "partnership_type": partnership_type,
                "your_company": your_company,
                **result,
            }

        except Exception as e:
            logger.error(f"生成合作关系外联失败: {e}")
            return {
                "partner_name": partner_name,
                "partnership_type": partnership_type,
                "your_company": your_company,
                "initial_outreach_email": {},
                "follow_up_sequence": [],
                "value_proposition": "",
                "partnership_benefits": {},
                "proposed_terms": "",
                "best_contact_time": "",
                "linkedin_outreach": "",
                "call_script": "",
            }


partnership_outreach_generator_service = PartnershipOutreachGeneratorService()