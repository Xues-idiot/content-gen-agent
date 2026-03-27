"""
Vox Thought Leadership Generator Service 模块

思想领袖内容生成服务
- 行业洞察
- 专家文章
- 趋势分析
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ThoughtLeadershipGeneratorService:
    """
    思想领袖内容生成服务

    生成思想领袖内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_thought_leadership(
        self,
        author_name: str,
        industry: str,
        topic: str,
        article_type: str = "opinion",
    ) -> Dict[str, Any]:
        """
        生成思想领袖内容

        Args:
            author_name: 作者姓名
            industry: 行业
            topic: 主题
            article_type: 文章类型

        Returns:
            Dict: 思想领袖内容
        """
        try:
            prompt = f"""请为"{author_name}"（{industry}行业专家）生成关于"{topic}"的{article_type}类型思想领袖文章。

请以JSON格式返回：
{{
    "author_name": "作者姓名",
    "industry": "行业",
    "topic": "主题",
    "article_type": "文章类型",
    "title": "文章标题",
    "hook": "开场钩子",
    "main_thesis": "核心论点",
    "key_points": ["关键观点1"],
    "supporting_evidence": ["支持证据1"],
    "counter_arguments": ["反驳观点1"],
    "call_to_action": "行动号召",
    "author_bio": "作者简介",
    "suggested_hashtags": ["建议标签1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "author_name": author_name,
                "industry": industry,
                "topic": topic,
                "article_type": article_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成思想领袖内容失败: {e}")
            return {
                "author_name": author_name,
                "industry": industry,
                "topic": topic,
                "article_type": article_type,
                "title": "",
                "hook": "",
                "main_thesis": "",
                "key_points": [],
                "supporting_evidence": [],
                "counter_arguments": [],
                "call_to_action": "",
                "author_bio": "",
                "suggested_hashtags": [],
            }


thought_leadership_generator_service = ThoughtLeadershipGeneratorService()