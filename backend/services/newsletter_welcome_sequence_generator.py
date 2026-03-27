"""
Vox Newsletter Welcome Sequence Generator Service 模块

通讯欢迎序列生成服务
- 欢迎邮件
- 内容序列
- 参与策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class NewsletterWelcomeSequenceGeneratorService:
    """
    通讯欢迎序列生成服务

    生成通讯欢迎序列内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_newsletter_welcome_sequence(
        self,
        brand_name: str,
        num_emails: int = 5,
        subscriber_type: str = "new subscriber",
    ) -> Dict[str, Any]:
        """
        生成通讯欢迎序列

        Args:
            brand_name: 品牌名称
            num_emails: 邮件数量
            subscriber_type: 订阅者类型

        Returns:
            Dict: 通讯欢迎序列
        """
        try:
            prompt = f"""请为"{brand_name}"生成{num_emails}封欢迎{subscriber_type}的邮件序列。

请以JSON格式返回：
{{
    "brand_name": "品牌名称",
    "num_emails": {num_emails},
    "subscriber_type": "订阅者类型",
    "sequence_overview": "序列概述",
    "emails": [
        {{
            "email_number": 1,
            "subject": "主题",
            "preview_text": "预览文本",
            "delay_days": 延迟天数,
            "content_goal": "内容目标",
            "body": "正文",
            "cta": "CTA",
            "secondary_goal": "次要目标"
        }}
    ],
    "content_themes": ["内容主题1"],
    "engagement_triggers": ["参与触发器1"],
    "unsubscribe_options": "取消订阅选项",
    "total_sequence_duration": "总序列持续时间",
    "metrics_to_track": ["要追踪的指标1"]
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
                "num_emails": num_emails,
                "subscriber_type": subscriber_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成通讯欢迎序列失败: {e}")
            return {
                "brand_name": brand_name,
                "num_emails": num_emails,
                "subscriber_type": subscriber_type,
                "sequence_overview": "",
                "emails": [],
                "content_themes": [],
                "engagement_triggers": [],
                "unsubscribe_options": "",
                "total_sequence_duration": "",
                "metrics_to_track": [],
            }


newsletter_welcome_sequence_generator_service = NewsletterWelcomeSequenceGeneratorService()