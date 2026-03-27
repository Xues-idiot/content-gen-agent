"""
Vox Disclaimer Generator Service 模块

免责声明生成服务
- 责任限制
- 风险提示
- 法律声明
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class DisclaimerGeneratorService:
    """
    免责声明生成服务

    生成免责声明内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_disclaimer(
        self,
        content_type: str,
        company_name: str,
        product_name: str,
    ) -> Dict[str, Any]:
        """
        生成免责声明

        Args:
            content_type: 内容类型
            company_name: 公司名称
            product_name: 产品名称

        Returns:
            Dict: 免责声明
        """
        try:
            prompt = f"""请为"{product_name}"（公司：{company_name}，内容类型：{content_type}）生成免责声明。

请以JSON格式返回：
{{
    "content_type": "内容类型",
    "company_name": "公司名称",
    "product_name": "产品名称",
    "effective_date": "生效日期",
    "general_disclaimer": "一般免责声明",
    "accuracy_disclaimer": "准确性免责声明",
    "medical_disclaimer": "医疗免责声明",
    "financial_disclaimer": "财务免责声明",
    "legal_disclaimer": "法律免责声明",
    "professional_advice_disclaimer": "专业建议免责声明",
    "third_party_links": "第三方链接",
    "user_responsibility": "用户责任",
    "limitation_of_liability": "责任限制",
    "indemnification": "赔偿",
    "changes_to_disclaimer": "免责声明变更",
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
                "content_type": content_type,
                "company_name": company_name,
                "product_name": product_name,
                **result,
            }

        except Exception as e:
            logger.error(f"生成免责声明失败: {e}")
            return {
                "content_type": content_type,
                "company_name": company_name,
                "product_name": product_name,
                "effective_date": "",
                "general_disclaimer": "",
                "accuracy_disclaimer": "",
                "medical_disclaimer": "",
                "financial_disclaimer": "",
                "legal_disclaimer": "",
                "professional_advice_disclaimer": "",
                "third_party_links": "",
                "user_responsibility": "",
                "limitation_of_liability": "",
                "indemnification": "",
                "changes_to_disclaimer": "",
                "contact_information": "",
            }


disclaimer_generator_service = DisclaimerGeneratorService()