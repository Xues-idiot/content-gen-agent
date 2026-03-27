"""
Vox Testimonial Generator Service 模块

用户评价生成服务
- 真实感评价
- 多角度评价
- 场景化评价
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TestimonialGeneratorService:
    """
    用户评价生成服务

    生成真实的用户评价
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_testimonials(
        self,
        product_name: str,
        num: int = 5,
        platform: str = "xiaohongshu",
    ) -> List[Dict[str, Any]]:
        """
        生成用户评价

        Args:
            product_name: 产品名称
            num: 数量
            platform: 平台

        Returns:
            List[Dict]: 评价列表
        """
        try:
            prompt = f"""请为"{product_name}"生成{num}条真实用户评价。

平台：{platform}

要求：
1. 不同用户画像（年龄、职业、使用场景）
2. 多样化的评价角度
3. 真实的语言风格

请以JSON格式返回：
{{
    "testimonials": [
        {{
            "user_profile": "用户画像",
            "rating": 5,
            "content": "评价内容",
            "pros": ["优点1", "优点2"],
            "cons": ["缺点1"]
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

            return result.get("testimonials", [])

        except Exception as e:
            logger.error(f"生成用户评价失败: {e}")
            return []


testimonial_generator_service = TestimonialGeneratorService()