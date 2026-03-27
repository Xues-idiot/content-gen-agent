"""
Vox Privacy Policy Generator Service 模块

隐私政策生成服务
- 数据收集
- 使用目的
- 用户权利
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PrivacyPolicyGeneratorService:
    """
    隐私政策生成服务

    生成隐私政策内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_privacy_policy(
        self,
        company_name: str,
        product_name: str,
        jurisdiction: str = "中国",
    ) -> Dict[str, Any]:
        """
        生成隐私政策

        Args:
            company_name: 公司名称
            product_name: 产品名称
            jurisdiction: 管辖区域

        Returns:
            Dict: 隐私政策
        """
        try:
            prompt = f"""请为"{company_name}"的"{product_name}"（管辖区域：{jurisdiction}）生成隐私政策。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "product_name": "产品名称",
    "jurisdiction": "管辖区域",
    "effective_date": "生效日期",
    "last_updated": "最后更新",
    "overview": "概述",
    "information_collected": ["收集的信息1"],
    "how_information_is_used": ["信息使用方式1"],
    "information_sharing": "信息共享",
    "data_protection": "数据保护",
    "cookies_and_tracking": "Cookie和追踪",
    "user_rights": ["用户权利1"],
    "data_retention": "数据保留",
    "children_privacy": "儿童隐私",
    "international_transfers": "国际传输",
    "policy_changes": "政策变更",
    "contact_information": "联系信息",
    "consent_text": "同意文本"
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
                "product_name": product_name,
                "jurisdiction": jurisdiction,
                **result,
            }

        except Exception as e:
            logger.error(f"生成隐私政策失败: {e}")
            return {
                "company_name": company_name,
                "product_name": product_name,
                "jurisdiction": jurisdiction,
                "effective_date": "",
                "last_updated": "",
                "overview": "",
                "information_collected": [],
                "how_information_is_used": [],
                "information_sharing": "",
                "data_protection": "",
                "cookies_and_tracking": "",
                "user_rights": [],
                "data_retention": "",
                "children_privacy": "",
                "international_transfers": "",
                "policy_changes": "",
                "contact_information": "",
                "consent_text": "",
            }


privacy_policy_generator_service = PrivacyPolicyGeneratorService()