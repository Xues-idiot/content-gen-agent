"""
Vox Industry News Generator Service 模块

行业资讯生成服务
- 行业动态
- 新闻摘要
- 趋势解读
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class IndustryNewsGeneratorService:
    """
    行业资讯生成服务

    生成行业资讯内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_news_summary(
        self,
        industry: str,
        topic: str,
    ) -> Dict[str, Any]:
        """
        生成行业资讯摘要

        Args:
            industry: 行业
            topic: 话题

        Returns:
            Dict: 资讯摘要
        """
        try:
            prompt = f"""请为{industry}行业生成一个关于"{topic}"的资讯摘要。

请以JSON格式返回：
{{
    "title": "资讯标题",
    "summary": "资讯摘要",
    "key_points": ["要点1", "要点2"],
    "impact": "影响分析",
    "source_suggestion": "信息来源"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "industry": industry,
                "topic": topic,
                **result,
            }

        except Exception as e:
            logger.error(f"生成行业资讯失败: {e}")
            return {
                "industry": industry,
                "topic": topic,
                "title": "",
                "summary": "",
                "key_points": [],
                "impact": "",
                "source_suggestion": "",
            }


industry_news_generator_service = IndustryNewsGeneratorService()