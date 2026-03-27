"""
Vox Contact Page Generator Service 模块

联系我们页面生成服务
- 联系表单
- 办公地址
- 社交链接
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ContactPageGeneratorService:
    """
    联系我们页面生成服务

    生成联系我们页面内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_contact_page(
        self,
        company_name: str,
        num_offices: int = 1,
        primary_contact_method: str = "email",
    ) -> Dict[str, Any]:
        """
        生成联系我们页面

        Args:
            company_name: 公司名称
            num_offices: 办公室数量
            primary_contact_method: 主要联系方法

        Returns:
            Dict: 联系我们页面
        """
        try:
            prompt = f"""请为"{company_name}"生成联系我们页面（{num_offices}个办公室，主要联系方法：{primary_contact_method}）。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "num_offices": {num_offices},
    "primary_contact_method": "主要联系方法",
    "page_headline": "页面标题",
    "intro_text": "介绍文本",
    "contact_form": {{
        "fields": ["字段1"],
        "required_fields": ["必填字段1"],
        "submission_note": "提交说明"
    }},
    "offices": [
        {{
            "office_name": "办公室名称",
            "address": "地址",
            "phone": "电话",
            "email": "电子邮件",
            "hours": "营业时间",
            "map_embed_instructions": "地图嵌入说明"
        }}
    ],
    "social_media_links": [
        {{
            "platform": "平台",
            "url": "URL",
            "handle": "handle"
        }}
    ],
    "general_inquiries": "一般咨询",
    "customer_support": "客户支持",
    "partnership_opportunities": "合作机会",
    "media_press": "媒体/新闻",
    "response_time_expectations": "响应时间预期",
    "faq_section": ["FAQ部分1"],
    "emergency_contact": "紧急联系",
    "live_chat_offer": "是否提供在线聊天"
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
                "num_offices": num_offices,
                "primary_contact_method": primary_contact_method,
                **result,
            }

        except Exception as e:
            logger.error(f"生成联系我们页面失败: {e}")
            return {
                "company_name": company_name,
                "num_offices": num_offices,
                "primary_contact_method": primary_contact_method,
                "page_headline": "",
                "intro_text": "",
                "contact_form": {},
                "offices": [],
                "social_media_links": [],
                "general_inquiries": "",
                "customer_support": "",
                "partnership_opportunities": "",
                "media_press": "",
                "response_time_expectations": "",
                "faq_section": [],
                "emergency_contact": "",
                "live_chat_offer": "",
            }


contact_page_generator_service = ContactPageGeneratorService()