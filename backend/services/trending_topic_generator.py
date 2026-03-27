"""
Vox Trending Topic Generator Service 模块

趋势话题生成服务
- 热门话题
- 话题分析
- 创作灵感
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TrendingTopicGeneratorService:
    """
    趋势话题生成服务

    生成趋势话题内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_trending_topics(
        self,
        industry: str,
        platform: str = "微博",
        num_topics: int = 10,
    ) -> Dict[str, Any]:
        """
        生成趋势话题

        Args:
            industry: 行业
            platform: 平台
            num_topics: 话题数量

        Returns:
            Dict: 趋势话题
        """
        try:
            prompt = f"""请为{industry}行业在{platform}平台生成{num_topics}个热门趋势话题。

请以JSON格式返回：
{{
    "industry": "行业",
    "platform": "平台",
    "num_topics": 话题数量,
    "generated_at": "生成时间",
    "trending_topics": [
        {{
            "topic": "话题",
            "trend_score": "热度评分",
            "description": "话题描述",
            "content_angles": ["内容角度1"],
            "audience_interest": "受众兴趣",
            "engagement_potential": "互动潜力"
        }}
    ],
    "industry_insights": ["行业洞察1"],
    "content_recommendations": ["内容建议1"]
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
                "platform": platform,
                "num_topics": num_topics,
                **result,
            }

        except Exception as e:
            logger.error(f"生成趋势话题失败: {e}")
            return {
                "industry": industry,
                "platform": platform,
                "num_topics": num_topics,
                "generated_at": "",
                "trending_topics": [],
                "industry_insights": [],
                "content_recommendations": [],
            }


trending_topic_generator_service = TrendingTopicGeneratorService()