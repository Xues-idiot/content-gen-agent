"""
Vox Newsletter Content Generator Service 模块

新闻通讯内容生成服务
- 时事通讯
- 行业新闻
- 精选内容
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class NewsletterContentGeneratorService:
    """
    新闻通讯内容生成服务

    生成新闻通讯内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_newsletter_content(
        self,
        newsletter_name: str,
        issue_number: int,
        theme: str = "monthly update",
    ) -> Dict[str, Any]:
        """
        生成新闻通讯内容

        Args:
            newsletter_name: 新闻通讯名称
            issue_number: 期号
            theme: 主题

        Returns:
            Dict: 新闻通讯内容
        """
        try:
            prompt = f"""请为"{newsletter_name}"第{issue_number}期（主题：{theme}）生成内容。

请以JSON格式返回：
{{
    "newsletter_name": "新闻通讯名称",
    "issue_number": 期号,
    "theme": "主题",
    "subject_line": "邮件主题",
    "header_title": "标题",
    "opening_message": "开场语",
    "featured_articles": [
        {{
            "title": "文章标题",
            "summary": "摘要",
            "link": "链接",
            "image_suggestion": "配图建议"
        }}
    ],
    "quick_tips": ["小贴士1"],
    "upcoming_events": ["即将到来活动1"],
    "reader_poll": "读者投票",
    "closing_message": "结束语",
    "footer": "页脚",
    "social_share_text": "社交分享文字"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "newsletter_name": newsletter_name,
                "issue_number": issue_number,
                "theme": theme,
                **result,
            }

        except Exception as e:
            logger.error(f"生成新闻通讯内容失败: {e}")
            return {
                "newsletter_name": newsletter_name,
                "issue_number": issue_number,
                "theme": theme,
                "subject_line": "",
                "header_title": "",
                "opening_message": "",
                "featured_articles": [],
                "quick_tips": [],
                "upcoming_events": [],
                "reader_poll": "",
                "closing_message": "",
                "footer": "",
                "social_share_text": "",
            }


newsletter_content_generator_service = NewsletterContentGeneratorService()