"""
Vox Newsletter Generator Service 模块

 newsletter内容生成服务
- newsletter主题生成
- 内容策划
- 订阅者互动
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class NewsletterGeneratorService:
    """
    Newsletter生成服务

    生成Newsletter内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_newsletter(
        self,
        topic: str,
        num_sections: int = 3,
        style: str = "professional",
    ) -> Dict[str, Any]:
        """
        生成Newsletter

        Args:
            topic: 主题
            num_sections: 版块数量
            style: 风格

        Returns:
            Dict: Newsletter内容
        """
        try:
            prompt = f"""请为"{topic}"生成一个{num_sections}个版块的Newsletter。

风格：{style}

请以JSON格式返回：
{{
    "subject": "邮件主题",
    "sections": [
        {{
            "title": "版块标题",
            "content": "版块内容",
            "cta": "行动号召"
        }}
    ],
    "closing": "结束语"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "topic": topic,
                "num_sections": num_sections,
                "style": style,
                **result,
            }

        except Exception as e:
            logger.error(f"生成Newsletter失败: {e}")
            return {
                "topic": topic,
                "num_sections": num_sections,
                "style": style,
                "subject": "",
                "sections": [],
                "closing": "",
            }


newsletter_generator_service = NewsletterGeneratorService()