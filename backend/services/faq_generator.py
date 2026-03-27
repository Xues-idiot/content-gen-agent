"""
Vox FAQ Generator Service 模块

FAQ生成服务
- 常见问题生成
- 解答生成
- 知识库构建
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class FAQGeneratorService:
    """
    FAQ生成服务

    为产品或话题生成常见问题
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_faq(
        self,
        topic: str,
        num: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        生成FAQ

        Args:
            topic: 主题
            num: 数量

        Returns:
            List[Dict]: FAQ列表
        """
        try:
            prompt = f"""请为"{topic}"主题生成{num}个常见问题及解答。

请以JSON格式返回：
{{
    "faqs": [
        {{
            "question": "问题",
            "answer": "解答",
            "category": "分类"
        }}
    ]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return result.get("faqs", [])

        except Exception as e:
            logger.error(f"生成FAQ失败: {e}")
            return []


faq_generator_service = FAQGeneratorService()