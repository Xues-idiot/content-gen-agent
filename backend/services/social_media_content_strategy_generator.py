"""
Vox Social Media Content Strategy Generator Service 模块

社交媒体内容策略生成服务
- 内容主题
- 发布计划
- 参与策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SocialMediaContentStrategyGeneratorService:
    """
    社交媒体内容策略生成服务

    生成社交媒体内容策略内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_social_media_content_strategy(
        self,
        brand_name: str,
        platforms: List[str],
        num_topics: int = 8,
    ) -> Dict[str, Any]:
        """
        生成社交媒体内容策略

        Args:
            brand_name: 品牌名称
            platforms: 平台列表
            num_topics: 主题数量

        Returns:
            Dict: 社交媒体内容策略
        """
        platforms_str = ", ".join(platforms[:3])

        try:
            prompt = f"""请为"{brand_name}"在{platforms_str}平台生成{num_topics}个主题的社交媒体内容策略。

请以JSON格式返回：
{{
    "brand_name": "品牌名称",
    "platforms": {platforms},
    "num_topics": {num_topics},
    "content_themes": ["内容主题1"],
    "posting_schedule": "发布计划",
    "platform_strategies": [
        {{
            "platform": "平台",
            "content_types": ["内容类型1"],
            "posting_frequency": "发布频率",
            "best_times": "最佳时间"
        }}
    ],
    "engagement_tactics": ["参与策略1"],
    "hashtag_strategy": "话题标签策略",
    "content_calendar_sample": ["内容日历示例1"],
    "kpis": ["KPI1"],
    "influencer_strategy": "网红策略"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "brand_name": brand_name,
                "platforms": platforms,
                "num_topics": num_topics,
                **result,
            }

        except Exception as e:
            logger.error(f"生成社交媒体内容策略失败: {e}")
            return {
                "brand_name": brand_name,
                "platforms": platforms,
                "num_topics": num_topics,
                "content_themes": [],
                "posting_schedule": "",
                "platform_strategies": [],
                "engagement_tactics": [],
                "hashtag_strategy": "",
                "content_calendar_sample": [],
                "kpis": [],
                "influencer_strategy": "",
            }


social_media_content_strategy_generator_service = SocialMediaContentStrategyGeneratorService()
