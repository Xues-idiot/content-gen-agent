"""
Vox Whitepaper Generator Service 模块

白皮书生成服务
- 行业白皮书
- 技术白皮书
- 产品白皮书
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class WhitepaperGeneratorService:
    """
    白皮书生成服务

    生成行业/技术白皮书内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_whitepaper_outline(
        self,
        topic: str,
        whitepaper_type: str = "industry",
    ) -> Dict[str, Any]:
        """
        生成白皮书大纲

        Args:
            topic: 主题
            whitepaper_type: 白皮书类型

        Returns:
            Dict: 白皮书大纲
        """
        try:
            prompt = f"""请为"{topic}"生成{whitepaper_type}类型白皮书大纲。

请以JSON格式返回：
{{
    "title": "白皮书标题",
    "executive_summary": "执行摘要",
    "sections": [
        {{
            "title": "章节标题",
            "key_points": ["要点1", "要点2"]
        }}
    ],
    "conclusion": "结论"
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
                "whitepaper_type": whitepaper_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成白皮书大纲失败: {e}")
            return {
                "topic": topic,
                "whitepaper_type": whitepaper_type,
                "title": "",
                "executive_summary": "",
                "sections": [],
                "conclusion": "",
            }


whitepaper_generator_service = WhitepaperGeneratorService()