"""
Vox Email Newsletter Series Generator Service 模块

邮件通讯系列生成服务
- 系列主题
- 发送节奏
- 内容规划
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class EmailNewsletterSeriesGeneratorService:
    """
    邮件通讯系列生成服务

    生成邮件通讯系列内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_email_newsletter_series(
        self,
        series_theme: str,
        num_emails: int,
        audience: str,
    ) -> Dict[str, Any]:
        """
        生成邮件通讯系列

        Args:
            series_theme: 系列主题
            num_emails: 邮件数量
            audience: 受众

        Returns:
            Dict: 邮件通讯系列
        """
        try:
            prompt = f"""请为"{series_theme}"主题生成针对{audience}受众的{num_emails}封邮件通讯系列。

请以JSON格式返回：
{{
    "series_theme": "系列主题",
    "num_emails": {num_emails},
    "audience": "受众",
    "series_overview": "系列概述",
    "emails": [
        {{
            "email_number": 1,
            "subject": "主题",
            "preview_text": "预览文本",
            "content_focus": "内容焦点",
            "key_message": "关键信息",
            "cta": "CTA"
        }}
    ],
    "sending_schedule": "发送节奏",
    "engagement_tracking": "参与度追踪"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "series_theme": series_theme,
                "num_emails": num_emails,
                "audience": audience,
                **result,
            }

        except Exception as e:
            logger.error(f"生成邮件通讯系列失败: {e}")
            return {
                "series_theme": series_theme,
                "num_emails": num_emails,
                "audience": audience,
                "series_overview": "",
                "emails": [],
                "sending_schedule": "",
                "engagement_tracking": "",
            }


email_newsletter_series_generator_service = EmailNewsletterSeriesGeneratorService()