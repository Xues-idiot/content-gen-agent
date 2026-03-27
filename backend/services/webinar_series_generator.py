"""
Vox Webinar Series Generator Service 模块

网络研讨会系列生成服务
- 系列主题
- 剧集规划
- 参与策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class WebinarSeriesGeneratorService:
    """
    网络研讨会系列生成服务

    生成网络研讨会系列内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_webinar_series(
        self,
        series_name: str,
        num_episodes: int = 5,
        target_audience: str = "general",
    ) -> Dict[str, Any]:
        """
        生成网络研讨会系列

        Args:
            series_name: 系列名称
            num_episodes: 剧集数量
            target_audience: 目标受众

        Returns:
            Dict: 网络研讨会系列
        """
        try:
            prompt = f"""请为"{series_name}"生成{num_episodes}集的网络研讨会系列（目标受众：{target_audience}）。

请以JSON格式返回：
{{
    "series_name": "系列名称",
    "num_episodes": {num_episodes},
    "target_audience": "目标受众",
    "series_overview": "系列概述",
    "series_theme": "系列主题",
    "episodes": [
        {{
            "episode_number": 1,
            "episode_title": "剧集标题",
            "episode_theme": "剧集主题",
            "description": "描述",
            "duration_minutes": 分钟,
            "key_takeaways": ["关键收获1"]
        }}
    ],
    "speaker_assignments": ["演讲者分配1"],
    "series_promotion_plan": "系列推广计划",
    "engagement_strategy": "参与策略"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "series_name": series_name,
                "num_episodes": num_episodes,
                "target_audience": target_audience,
                **result,
            }

        except Exception as e:
            logger.error(f"生成网络研讨会系列失败: {e}")
            return {
                "series_name": series_name,
                "num_episodes": num_episodes,
                "target_audience": target_audience,
                "series_overview": "",
                "series_theme": "",
                "episodes": [],
                "speaker_assignments": [],
                "series_promotion_plan": "",
                "engagement_strategy": "",
            }


webinar_series_generator_service = WebinarSeriesGeneratorService()