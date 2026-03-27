"""
Vox Knowledge Base Article Generator Service 模块

知识库文章生成服务
- 文章结构
- 故障排除步骤
- 最佳实践
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class KnowledgeBaseArticleGeneratorService:
    """
    知识库文章生成服务

    生成知识库文章内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_knowledge_base_article(
        self,
        topic: str,
        article_type: str,
    ) -> Dict[str, Any]:
        """
        生成知识库文章

        Args:
            topic: 主题
            article_type: 文章类型

        Returns:
            Dict: 知识库文章
        """
        try:
            prompt = f"""请为"{topic}"生成{article_type}类型的知识库文章。

请以JSON格式返回：
{{
    "topic": "主题",
    "article_type": "文章类型",
    "title": "标题",
    "summary": "摘要",
    "overview": "概述",
    "prerequisites": ["先决条件1"],
    "steps": [
        {{
            "step_number": "步骤编号",
            "step_title": "步骤标题",
            "step_description": "步骤描述",
            "important_notes": ["重要注意事项1"]
        }}
    ],
    "troubleshooting": [
        {{
            "issue": "问题",
            "possible_causes": ["可能原因1"],
            "solutions": ["解决方案1"]
        }}
    ],
    "best_practices": ["最佳实践1"],
    "related_articles": ["相关文章1"],
    "feedback_form_link": "反馈表单链接"
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
                "overview": "",
                "prerequisites": [],
                "steps": [],
                "troubleshooting": [],
                "best_practices": [],
                "related_articles": [],
                "feedback_form_link": "",
            }


knowledge_base_article_generator_service = KnowledgeBaseArticleGeneratorService()
