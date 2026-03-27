"""
Vox Blog Post Generator Service 模块

博客文章生成服务
- 文章标题
- 文章正文
- SEO优化
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BlogPostGeneratorService:
    """
    博客文章生成服务

    生成博客文章内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_blog_post(
        self,
        topic: str,
        target_audience: str,
        tone: str = "professional",
        word_count: int = 1000,
    ) -> Dict[str, Any]:
        """
        生成博客文章

        Args:
            topic: 文章主题
            target_audience: 目标受众
            tone: 语气
            word_count: 字数

        Returns:
            Dict: 博客文章
        """
        try:
            prompt = f"""请为"{topic}"生成一篇针对{target_audience}的{tone}语气博客文章（约{word_count}字）。

请以JSON格式返回：
{{
    "title": "文章标题",
    "meta_description": "SEO元描述",
    "target_audience": "目标受众",
    "tone": "语气",
    "introduction": "引言",
    "sections": [
        {{
            "heading": "章节标题",
            "content": "章节内容"
        }}
    ],
    "conclusion": "结论",
    "call_to_action": "行动号召",
    "keywords": ["关键词1"],
    "tags": ["标签1"],
    "internal_links": ["内链1"],
    "external_links": ["外链1"],
    "featured_image_suggestion": "配图建议",
    "publishing_checklist": ["发布检查清单1"]
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
                "target_audience": target_audience,
                "tone": tone,
                "word_count": word_count,
                **result,
            }

        except Exception as e:
            logger.error(f"生成博客文章失败: {e}")
            return {
                "topic": topic,
                "target_audience": target_audience,
                "tone": tone,
                "word_count": word_count,
                "title": "",
                "meta_description": "",
                "introduction": "",
                "sections": [],
                "conclusion": "",
                "call_to_action": "",
                "keywords": [],
                "tags": [],
                "internal_links": [],
                "external_links": [],
                "featured_image_suggestion": "",
                "publishing_checklist": [],
            }


blog_post_generator_service = BlogPostGeneratorService()