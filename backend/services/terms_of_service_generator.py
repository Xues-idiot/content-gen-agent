"""
Vox Terms of Service Generator Service 模块

服务条款生成服务
- 使用条件
- 责任限制
- 法律声明
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TermsOfServiceGeneratorService:
    """
    服务条款生成服务

    生成服务条款内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_terms_of_service(
        self,
        company_name: str,
        product_name: str,
        effective_date: str,
    ) -> Dict[str, Any]:
        """
        生成服务条款

        Args:
            company_name: 公司名称
            product_name: 产品名称
            effective_date: 生效日期

        Returns:
            Dict: 服务条款
        """
        try:
            prompt = f"""请为"{company_name}"的"{product_name}"（生效日期：{effective_date}）生成服务条款。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "product_name": "产品名称",
    "effective_date": "生效日期",
    "overview": "概述",
    "acceptance_of_terms": "条款接受",
    "description_of_service": "服务描述",
    "user_obligations": ["用户义务1"],
    "account_terms": "账户条款",
    "payment_terms": "支付条款",
    "intellectual_property": "知识产权",
    "user_content": "用户内容",
    "prohibited_uses": ["禁止使用1"],
    "warranties_and_disclaimers": "保证与免责声明",
    "limitation_of_liability": "责任限制",
    "indemnification": "赔偿",
    "termination": "终止",
    "governing_law": "适用法律",
    "dispute_resolution": "争议解决",
    "amendments": "修订",
    "contact_information": "联系信息",
    "entire_agreement": "完整协议"
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
                "effective_date": effective_date,
                **result,
            }

        except Exception as e:
            logger.error(f"生成服务条款失败: {e}")
            return {
                "company_name": company_name,
                "product_name": product_name,
                "effective_date": effective_date,
                "overview": "",
                "acceptance_of_terms": "",
                "description_of_service": "",
                "user_obligations": [],
                "account_terms": "",
                "payment_terms": "",
                "intellectual_property": "",
                "user_content": "",
                "prohibited_uses": [],
                "warranties_and_disclaimers": "",
                "limitation_of_liability": "",
                "indemnification": "",
                "termination": "",
                "governing_law": "",
                "dispute_resolution": "",
                "amendments": "",
                "contact_information": "",
                "entire_agreement": "",
            }


terms_of_service_generator_service = TermsOfServiceGeneratorService()