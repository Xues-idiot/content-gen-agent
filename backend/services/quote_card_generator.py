"""
Vox Quote Card Generator Service 模块

金句生成服务
- 名言金句
- 配文生成
- 视觉建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class QuoteCardGeneratorService:
    """
    金句生成服务

    生成名言金句和配文
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_quote(
        self,
        topic: str,
        num: int = 3,
        platform: str = "xiaohongshu",
    ) -> List[Dict[str, Any]]:
        """
        生成金句

        Args:
            topic: 主题
            num: 数量
            platform: 平台

        Returns:
            List[Dict]: 金句列表
        """
        try:
            prompt = f"""请为"{topic}"生成{num}条金句。

平台：{platform}

请以JSON格式返回：
{{
    "quotes": [
        {{
            "quote": "金句内容",
            "source": "出处/作者",
            "visual_tip": "视觉设计建议"
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

            return result.get("quotes", [])

        except Exception as e:
            logger.error(f"生成金句失败: {e}")
            return []


quote_card_generator_service = QuoteCardGeneratorService()