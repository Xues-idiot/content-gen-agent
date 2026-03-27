"""
Vox Knowledge Base Article Generator Service 模块

知识库文章生成服务
- 帮助文档
- 知识文章
- 操作指南
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class KnowledgeBaseGeneratorService:
    """
    知识库文章生成服务

    生成帮助文档和知识库文章
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_kb_article(
        self,
        topic: str,
        article_type: str = "how_to",
    ) -> Dict[str, Any]:
        """
        生成知识库文章

        Args:
            topic: 主题
            article_type: 文章类型

        Returns:
            Dict: 文章内容
        """
        try:
            prompt = f"""请为"{topic}"生成一篇{article_type}类型的知识库文章。

请以JSON格式返回：
{{
    "title": "文章标题",
    "summary": "摘要",
    "steps": ["步骤1", "步骤2"],
    "troubleshooting": ["问题1:解决方案"],
    "related_articles": ["相关文章1"]
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
                "article_type": article_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成知识库文章失败: {e}")
            return {
                "topic": topic,
                "article_type": article_type,
                "title": "",
                "summary": "",
                "steps": [],
                "troubleshooting": [],
                "related_articles": [],
            }


knowledge_base_generator_service = KnowledgeBaseGeneratorService()