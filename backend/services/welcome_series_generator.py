"""
Vox Welcome Series Generator Service 模块

欢迎序列生成服务
- 新用户引导
- 产品介绍
- 价值展示
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class WelcomeSeriesGeneratorService:
    """
    欢迎序列生成服务

    生成欢迎序列内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_welcome_series(
        self,
        brand_name: str,
        product_name: str,
        num_emails: int = 5,
    ) -> Dict[str, Any]:
        """
        生成欢迎序列

        Args:
            brand_name: 品牌名称
            product_name: 产品名称
            num_emails: 邮件数量

        Returns:
            Dict: 欢迎序列
        """
        try:
            prompt = f"""请为"{brand_name}"的{product_name}生成{num_emails}封欢迎序列邮件。

请以JSON格式返回：
{{
    "brand_name": "品牌名称",
    "product_name": "产品名称",
    "num_emails": {num_emails},
    "sequence_overview": "序列概述",
    "emails": [
        {{
            "email_number": 1,
            "day": "第几天",
            "subject": "主题",
            "goal": "目标",
            "content_summary": "内容摘要",
            "key_takeaway": "关键收获",
            "cta": "CTA"
        }}
    ],
    "getting_started_checklist": ["入门检查清单1"],
    "tip_tricks": ["技巧窍门1"],
    "success_stories": ["成功故事1"],
    "next_steps_cta": "下一步CTA"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "brand_name": brand_name,
                "product_name": product_name,
                "num_emails": num_emails,
                **result,
            }

        except Exception as e:
            logger.error(f"生成欢迎序列失败: {e}")
            return {
                "brand_name": brand_name,
                "product_name": product_name,
                "num_emails": num_emails,
                "sequence_overview": "",
                "emails": [],
                "getting_started_checklist": [],
                "tip_tricks": [],
                "success_stories": [],
                "next_steps_cta": "",
            }


welcome_series_generator_service = WelcomeSeriesGeneratorService()