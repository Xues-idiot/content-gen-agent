"""
Vox FAQ Document Generator Service 模块

FAQ文档生成服务
- 常见问题
- 解答说明
- 分类整理
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class FAQDocumentGeneratorService:
    """
    FAQ文档生成服务

    生成FAQ文档内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_faq_document(
        self,
        topic: str,
        product_name: str,
        num_questions: int = 10,
    ) -> Dict[str, Any]:
        """
        生成FAQ文档

        Args:
            topic: 主题
            product_name: 产品名称
            num_questions: 问题数量

        Returns:
            Dict: FAQ文档
        """
        try:
            prompt = f"""请为"{product_name}"（主题：{topic}）生成{num_questions}个常见问题及解答。

请以JSON格式返回：
{{
    "topic": "主题",
    "product_name": "产品名称",
    "num_questions": 问题数量,
    "title": "FAQ标题",
    "categories": [
        {{
            "category_name": "分类名称",
            "questions": [
                {{
                    "question": "问题",
                    "answer": "回答",
                    "related_links": ["相关链接1"]
                }}
            ]
        }}
    ],
    "contact_support": "联系支持",
    "additional_resources": ["额外资源1"]
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
                "product_name": product_name,
                "num_questions": num_questions,
                **result,
            }

        except Exception as e:
            logger.error(f"生成FAQ文档失败: {e}")
            return {
                "topic": topic,
                "product_name": product_name,
                "num_questions": num_questions,
                "title": "",
                "categories": [],
                "contact_support": "",
                "additional_resources": [],
            }


faq_document_generator_service = FAQDocumentGeneratorService()