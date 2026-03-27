"""
Vox Client Welcome Package Generator Service 模块

客户欢迎包生成服务
- 欢迎材料
- 资源导航
- 快速入门
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ClientWelcomePackageGeneratorService:
    """
    客户欢迎包生成服务

    生成客户欢迎包内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_client_welcome_package(
        self,
        company_name: str,
        package_type: str = "standard",
        client_segment: str = "new business",
    ) -> Dict[str, Any]:
        """
        生成客户欢迎包

        Args:
            company_name: 公司名称
            package_type: 包类型
            client_segment: 客户细分

        Returns:
            Dict: 客户欢迎包
        """
        try:
            prompt = f"""请为"{company_name}"生成{package_type}类型的{client_segment}客户欢迎包。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "package_type": "包类型",
    "client_segment": "客户细分",
    "welcome_letter": "欢迎信",
    "quick_start_guide": "快速入门指南",
    "resources": [
        {{
            "resource_name": "资源名称",
            "resource_type": "资源类型",
            "description": "描述",
            "link": "链接"
        }}
    ],
    "contact_information": {{
        "account_manager": "客户经理",
        "support_email": "支持邮箱",
        "support_phone": "支持电话"
    }},
    "next_steps": ["下一步1"],
    "helpful_tips": ["有用提示1"]
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
                "package_type": package_type,
                "client_segment": client_segment,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户欢迎包失败: {e}")
            return {
                "company_name": company_name,
                "package_type": package_type,
                "client_segment": client_segment,
                "welcome_letter": "",
                "quick_start_guide": "",
                "resources": [],
                "contact_information": {},
                "next_steps": [],
                "helpful_tips": [],
            }


client_welcome_package_generator_service = ClientWelcomePackageGeneratorService()