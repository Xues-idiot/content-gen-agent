"""
Vox Company Profile Generator Service 模块

公司介绍生成服务
- 公司概况
- 发展历程
- 企业文化
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CompanyProfileGeneratorService:
    """
    公司介绍生成服务

    生成公司介绍内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_company_profile(
        self,
        company_name: str,
        industry: str,
        company_size: str,
    ) -> Dict[str, Any]:
        """
        生成公司介绍

        Args:
            company_name: 公司名称
            industry: 行业
            company_size: 公司规模

        Returns:
            Dict: 公司介绍
        """
        try:
            prompt = f"""请为"{company_name}"（{industry}行业，{company_size}规模）生成公司介绍。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "industry": "行业",
    "company_size": "公司规模",
    "tagline": "标语",
    "executive_summary": "执行摘要",
    "company_overview": "公司概况",
    "history_milestones": [
        {{
            "year": "年份",
            "milestone": "里程碑"
        }}
    ],
    "mission": "使命",
    "vision": "愿景",
    "values": ["价值观1"],
    "leadership_team": [
        {{
            "name": "姓名",
            "title": "职位"
        }}
    ],
    "products_services": ["产品/服务1"],
    "market_position": "市场地位",
    "geographic_presence": "地理分布",
    "partnerships": ["合作伙伴1"],
    "awards_recognition": ["奖项/认可1"],
    "corporate_social_responsibility": "企业社会责任",
    "newsroom_url": "新闻室URL",
    "contact_information": {{
        "address": "地址",
        "phone": "电话",
        "email": "电子邮件",
        "website": "网站"
    }}
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
                "company_size": company_size,
                **result,
            }

        except Exception as e:
            logger.error(f"生成公司介绍失败: {e}")
            return {
                "company_name": company_name,
                "industry": industry,
                "company_size": company_size,
                "tagline": "",
                "executive_summary": "",
                "company_overview": "",
                "history_milestones": [],
                "mission": "",
                "vision": "",
                "values": [],
                "leadership_team": [],
                "products_services": [],
                "market_position": "",
                "geographic_presence": "",
                "partnerships": [],
                "awards_recognition": [],
                "corporate_social_responsibility": "",
                "newsroom_url": "",
                "contact_information": {},
            }


company_profile_generator_service = CompanyProfileGeneratorService()