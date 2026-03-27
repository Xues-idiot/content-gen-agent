"""
Vox Cookie Policy Generator Service 模块

Cookie政策生成服务
- Cookie使用
- 数据收集
- 用户选择
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CookiePolicyGeneratorService:
    """
    Cookie政策生成服务

    生成Cookie政策内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_cookie_policy(
        self,
        website_name: str,
        company_name: str,
    ) -> Dict[str, Any]:
        """
        生成Cookie政策

        Args:
            website_name: 网站名称
            company_name: 公司名称

        Returns:
            Dict: Cookie政策
        """
        try:
            prompt = f"""请为"{website_name}"（公司：{company_name}）生成Cookie政策。

请以JSON格式返回：
{{
    "website_name": "网站名称",
    "company_name": "公司名称",
    "effective_date": "生效日期",
    "overview": "概述",
    "what_are_cookies": "什么是Cookie",
    "how_we_use_cookies": ["我们如何使用Cookie1"],
    "types_of_cookies": [
        {{
            "cookie_type": "Cookie类型",
            "purpose": "目的",
            "duration": "持续时间"
        }}
    ],
    "third_party_cookies": ["第三方Cookie1"],
    "cookie_purposes": ["Cookie用途1"],
    "managing_cookies": "管理Cookie",
    "browser_settings": "浏览器设置",
    "impact_of_disabling": "禁用影响",
    "updates_to_policy": "政策更新",
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
                "website_name": website_name,
                "company_name": company_name,
                **result,
            }

        except Exception as e:
            logger.error(f"生成Cookie政策失败: {e}")
            return {
                "website_name": website_name,
                "company_name": company_name,
                "effective_date": "",
                "overview": "",
                "what_are_cookies": "",
                "how_we_use_cookies": [],
                "types_of_cookies": [],
                "third_party_cookies": [],
                "cookie_purposes": [],
                "managing_cookies": "",
                "browser_settings": "",
                "impact_of_disabling": "",
                "updates_to_policy": "",
                "contact_information": "",
            }


cookie_policy_generator_service = CookiePolicyGeneratorService()