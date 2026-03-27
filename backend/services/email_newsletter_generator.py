"""
Vox Email Newsletter Generator Service 模块

电子邮件通讯生成服务
- 邮件主题
- 邮件正文
- 订阅者管理
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class EmailNewsletterGeneratorService:
    """
    电子邮件通讯生成服务

    生成邮件通讯内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_email_newsletter(
        self,
        newsletter_title: str,
        subscriber_segment: str = "general",
        frequency: str = "weekly",
    ) -> Dict[str, Any]:
        """
        生成电子邮件通讯

        Args:
            newsletter_title: 通讯标题
            subscriber_segment: 订阅者细分
            frequency: 发送频率

        Returns:
            Dict: 邮件通讯
        """
        try:
            prompt = f"""请为"{newsletter_title}"（细分：{subscriber_segment}，频率：{frequency}）生成邮件通讯。

请以JSON格式返回：
{{
    "subject_line": "邮件主题",
    "preview_text": "预览文本",
    "from_name": "发件人姓名",
    "from_email": "发件人邮箱",
    "subscriber_segment": "订阅者细分",
    "frequency": "发送频率",
    "header": "头部",
    "greeting": "问候语",
    "featured_article": {{
        "title": "标题",
        "summary": "摘要",
        "image_url": "图片URL",
        "cta_text": "CTA文本",
        "cta_link": "CTA链接"
    }},
    "sections": [
        {{
            "section_title": "章节标题",
            "content": "内容",
            "image_url": "图片URL",
            "link_text": "链接文本",
            "link_url": "链接URL"
        }}
    ],
    "footer": {{
        "unsubscribe_link": "退订链接",
        "address": "地址",
        "privacy_policy_link": "隐私政策链接",
        "social_media_links": ["社交媒体链接1"]
    }},
    "primary_cta": "主要CTA",
    "secondary_cta": "次要CTA",
    "personalization_tokens": ["个性化令牌1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "newsletter_title": newsletter_title,
                "subscriber_segment": subscriber_segment,
                "frequency": frequency,
                **result,
            }

        except Exception as e:
            logger.error(f"生成邮件通讯失败: {e}")
            return {
                "newsletter_title": newsletter_title,
                "subscriber_segment": subscriber_segment,
                "frequency": frequency,
                "subject_line": "",
                "preview_text": "",
                "from_name": "",
                "from_email": "",
                "header": "",
                "greeting": "",
                "featured_article": {},
                "sections": [],
                "footer": {},
                "primary_cta": "",
                "secondary_cta": "",
                "personalization_tokens": [],
            }


email_newsletter_generator_service = EmailNewsletterGeneratorService()