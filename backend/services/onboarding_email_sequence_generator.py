"""
Vox Onboarding Email Sequence Generator Service 模块

入职邮件序列生成服务
- 欢迎邮件
- 产品培训
- 成功提示
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class OnboardingEmailSequenceGeneratorService:
    """
    入职邮件序列生成服务

    生成入职邮件序列内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_onboarding_email_sequence(
        self,
        product_name: str,
        num_emails: int = 7,
        user_type: str = "new customer",
    ) -> Dict[str, Any]:
        """
        生成入职邮件序列

        Args:
            product_name: 产品名称
            num_emails: 邮件数量
            user_type: 用户类型

        Returns:
            Dict: 入职邮件序列
        """
        try:
            prompt = f"""请为"{product_name}"生成{num_emails}封{user_type}入职邮件序列。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "num_emails": {num_emails},
    "user_type": "用户类型",
    "sequence_overview": "序列概述",
    "total_duration": "总持续时间",
    "emails": [
        {{
            "email_number": 1,
            "day_number": "第几天",
            "subject": "主题",
            "goal": "目标",
            "content_summary": "内容摘要",
            "key_takeaway": "关键收获",
            "cta": "CTA"
        }}
    ],
    "engagement_milestones": ["参与里程碑1"],
    "success_metrics": ["成功指标1"],
    "optional_upsells": ["可选追加销售1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_name": product_name,
                "num_emails": num_emails,
                "user_type": user_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成入职邮件序列失败: {e}")
            return {
                "product_name": product_name,
                "num_emails": num_emails,
                "user_type": user_type,
                "sequence_overview": "",
                "total_duration": "",
                "emails": [],
                "engagement_milestones": [],
                "success_metrics": [],
                "optional_upsells": [],
            }


onboarding_email_sequence_generator_service = OnboardingEmailSequenceGeneratorService()