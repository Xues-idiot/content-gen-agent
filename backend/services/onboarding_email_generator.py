"""
Vox Onboarding Email Generator Service 模块

用户入职邮件生成服务
- 欢迎邮件
- 引导序列
- 激活邮件
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class OnboardingEmailGeneratorService:
    """
    用户入职邮件生成服务

    生成用户入职引导邮件序列
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_onboarding_sequence(
        self,
        product_name: str,
        num_emails: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        生成入职邮件序列

        Args:
            product_name: 产品名称
            num_emails: 邮件数量

        Returns:
            List[Dict]: 邮件序列
        """
        try:
            prompt = f"""请为"{product_name}"生成{num_emails}封用户入职引导邮件。

请以JSON格式返回：
{{
    "emails": [
        {{
            "subject": "邮件主题",
            "preheader": "预览文本",
            "body": "邮件正文",
            "cta": "行动号召"
        }}
    ]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return result.get("emails", [])

        except Exception as e:
            logger.error(f"生成入职邮件序列失败: {e}")
            return []


onboarding_email_generator_service = OnboardingEmailGeneratorService()