"""
Vox Podcast Episode Generator Service 模块

播客剧集生成服务
- 剧集大纲
- 节目笔记
- 嘉宾介绍
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PodcastEpisodeGeneratorService:
    """
    播客剧集生成服务

    生成播客剧集内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_podcast_episode(
        self,
        episode_title: str,
        topic: str,
        duration_minutes: int = 30,
        episode_type: str = "solo",
    ) -> Dict[str, Any]:
        """
        生成播客剧集

        Args:
            episode_title: 剧集标题
            topic: 主题
            duration_minutes: 时长（分钟）
            episode_type: 剧集类型

        Returns:
            Dict: 播客剧集
        """
        try:
            prompt = f"""请为播客剧集"{episode_title}"（主题：{topic}，时长：{duration_minutes}分钟，类型：{episode_type}）生成内容。

请以JSON格式返回：
{{
    "episode_title": "剧集标题",
    "topic": "主题",
    "duration_minutes": 时长,
    "episode_type": "剧集类型",
    "episode_description": "剧集描述",
    "key_talking_points": ["讨论要点1"],
    "timestamps": [
        {{
            "time": "0:00",
            "segment": "开场"
        }}
    ],
    "guest_bio": "嘉宾介绍（如果有）",
    "resources_mentioned": ["提到的资源1"],
    "call_to_action": "行动号召",
    "outro_message": "结束语"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "episode_title": episode_title,
                "topic": topic,
                "duration_minutes": duration_minutes,
                "episode_type": episode_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成播客剧集失败: {e}")
            return {
                "episode_title": episode_title,
                "topic": topic,
                "duration_minutes": duration_minutes,
                "episode_type": episode_type,
                "episode_description": "",
                "key_talking_points": [],
                "timestamps": [],
                "guest_bio": "",
                "resources_mentioned": [],
                "call_to_action": "",
                "outro_message": "",
            }


podcast_episode_generator_service = PodcastEpisodeGeneratorService()