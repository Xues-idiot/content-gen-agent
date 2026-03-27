"""
Vox Book Summary Generator Service 模块

书籍摘要生成服务
- 核心要点
- 章节总结
- 阅读建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BookSummaryGeneratorService:
    """
    书籍摘要生成服务

    生成书籍摘要内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_book_summary(
        self,
        book_title: str,
        author: str,
        genre: str = "non-fiction",
    ) -> Dict[str, Any]:
        """
        生成书籍摘要

        Args:
            book_title: 书名
            author: 作者
            genre: 类型

        Returns:
            Dict: 书籍摘要
        """
        try:
            prompt = f"""请为《{book_title}》（作者：{author}，类型：{genre}）生成书籍摘要。

请以JSON格式返回：
{{
    "book_title": "书名",
    "author": "作者",
    "genre": "类型",
    "book_overview": "书籍概述",
    "key_themes": ["核心主题1", "核心主题2"],
    "chapter_summaries": [
        {{
            "chapter": "章节名",
            "summary": "章节摘要"
        }}
    ],
    "main_takeaways": ["主要收获1"],
    "notable_quotes": ["名言1"],
    "reading_recommendations": "阅读建议",
    "who_should_read": "适合人群"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "book_title": book_title,
                "author": author,
                "genre": genre,
                **result,
            }

        except Exception as e:
            logger.error(f"生成书籍摘要失败: {e}")
            return {
                "book_title": book_title,
                "author": author,
                "genre": genre,
                "book_overview": "",
                "key_themes": [],
                "chapter_summaries": [],
                "main_takeaways": [],
                "notable_quotes": [],
                "reading_recommendations": "",
                "who_should_read": "",
            }


book_summary_generator_service = BookSummaryGeneratorService()