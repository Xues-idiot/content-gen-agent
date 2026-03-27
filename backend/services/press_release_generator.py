"""
Vox Press Release Generator Service 模块

新闻稿生成服务
- 产品发布
- 公司新闻
- 媒体发布
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PressReleaseGeneratorService:
    """
    新闻稿生成服务

    生成新闻稿内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_press_release(
        self,
        news_type: str,
        subject: str,
    ) -> Dict[str, Any]:
        """
        生成新闻稿

        Args:
            news_type: 新闻类型
            subject: 主题

        Returns:
            Dict: 新闻稿内容
        """
        try:
            prompt = f"""请生成一篇关于"{subject}"的{news_type}类型新闻稿。

请以JSON格式返回：
{{
    "headline": "标题",
    "subheadline": "副标题",
    "boilerplate": "电头",
    "body": "正文内容",
    "quotes": ["引用1"],
    "contact_info": "联系方式"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "news_type": news_type,
                "subject": subject,
                **result,
            }

        except Exception as e:
            logger.error(f"生成新闻稿失败: {e}")
            return {
                "news_type": news_type,
                "subject": subject,
                "headline": "",
                "subheadline": "",
                "boilerplate": "",
                "body": "",
                "quotes": [],
                "contact_info": "",
            }


press_release_generator_service = PressReleaseGeneratorService()