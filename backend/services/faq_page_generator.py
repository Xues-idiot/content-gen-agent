"""
Vox FAQ Page Generator Service 模块

常见问题页面生成服务
- 问题分类
- 答案模板
- 搜索优化
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class FAQPageGeneratorService:
    """
    常见问题页面生成服务

    生成常见问题页面内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_faq_page(
        self,
        topic: str,
        num_categories: int = 5,
        num_questions: int = 15,
    ) -> Dict[str, Any]:
        """
        生成常见问题页面

        Args:
            topic: 主题
            num_categories: 类别数量
            num_questions: 问题数量

        Returns:
            Dict: 常见问题页面
        """
        try:
            prompt = f"""请为"{topic}"生成包含{num_categories}个类别共{num_questions}个问题的FAQ页面。

请以JSON格式返回：
{{
    "topic": "主题",
    "num_categories": {num_categories},
    "num_questions": {num_questions},
    "page_title": "页面标题",
    "intro_text": "介绍文本",
    "search_hint": "搜索提示",
    "categories": [
        {{
            "category_name": "类别名称",
            "description": "描述",
            "questions": [
                {{
                    "question": "问题",
                    "answer": "答案",
                    "tags": ["标签1"],
                    "related_questions": ["相关问题1"]
                }}
            ]
        }}
    ],
    "featured_popular": [
        {{
            "question": "问题",
            "answer": "答案",
            "view_count": "浏览次数"
        }}
    ],
    "contact_prompt": "联系提示",
    "feedback_section": "反馈部分",
    "expand_all_option": "是否提供全展开选项",
    "schema_markup_notes": "Schema标记说明"
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
                "num_categories": num_categories,
                "num_questions": num_questions,
                **result,
            }

        except Exception as e:
            logger.error(f"生成FAQ页面失败: {e}")
            return {
                "topic": topic,
                "num_categories": num_categories,
                "num_questions": num_questions,
                "page_title": "",
                "intro_text": "",
                "search_hint": "",
                "categories": [],
                "featured_popular": [],
                "contact_prompt": "",
                "feedback_section": "",
                "expand_all_option": True,
                "schema_markup_notes": "",
            }


faq_page_generator_service = FAQPageGeneratorService()