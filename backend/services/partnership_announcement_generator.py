"""
Vox Partnership Announcement Generator Service 模块

合作公告生成服务
- 合作发布
- 联合声明
- 合作亮点
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PartnershipAnnouncementGeneratorService:
    """
    合作公告生成服务

    生成合作公告内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_partnership_announcement(
        self,
        company_a: str,
        company_b: str,
        partnership_type: str,
    ) -> Dict[str, Any]:
        """
        生成合作公告

        Args:
            company_a: 公司A
            company_b: 公司B
            partnership_type: 合作类型

        Returns:
            Dict: 合作公告
        """
        try:
            prompt = f"""请为"{company_a}"和"{company_b}"生成{partnership_type}合作公告。

请以JSON格式返回：
{{
    "company_a": "公司A",
    "company_b": "公司B",
    "partnership_type": "合作类型",
    "headline": "标题",
    "subheadline": "副标题",
    "announcement_body": "公告正文",
    "partnership_details": "合作详情",
    "mutual_benefits": [" mutual benefit 1"],
    "joint_initiatives": ["联合举措1"],
    "quote_company_a": "A公司高管引言",
    "quote_company_b": "B公司高管引言",
    "timeline": "时间线",
    "contact_information": "联系方式"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "company_a": company_a,
                "company_b": company_b,
                "partnership_type": partnership_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成合作公告失败: {e}")
            return {
                "company_a": company_a,
                "company_b": company_b,
                "partnership_type": partnership_type,
                "headline": "",
                "subheadline": "",
                "announcement_body": "",
                "partnership_details": "",
                "mutual_benefits": [],
                "joint_initiatives": [],
                "quote_company_a": "",
                "quote_company_b": "",
                "timeline": "",
                "contact_information": "",
            }


partnership_announcement_generator_service = PartnershipAnnouncementGeneratorService()