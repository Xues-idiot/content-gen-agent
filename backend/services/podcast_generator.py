"""
Vox Podcast Show Notes Generator Service 模块

播客节目笔记生成服务
- 节目描述
- 章节标记
- shownotes生成
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PodcastShowNotesGeneratorService:
    """
    播客笔记生成服务

    生成播客节目的shownotes
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_show_notes(
        self,
        episode_title: str,
        duration: int,
        topics: List[str],
    ) -> Dict[str, Any]:
        """
        生成播客笔记

        Args:
            episode_title: 节目标题
            duration: 时长（分钟）
            topics: 讨论话题

        Returns:
            Dict: 笔记内容
        """
        try:
            prompt = f"""请为"{episode_title}"生成播客shownotes。

时长：{duration}分钟
话题：{', '.join(topics)}

请以JSON格式返回：
{{
    "episode_title": "节目标题",
    "description": "节目简介",
    "chapters": [
        {{
            "start_time": "00:00",
            "title": "章节标题",
            "description": "章节描述"
        }}
    ],
    "key_takeaways": ["要点1", "要点2"],
    "links": ["相关链接1"]
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
                "duration": duration,
                "topics": topics,
                **result,
            }

        except Exception as e:
            logger.error(f"生成播客笔记失败: {e}")
            return {
                "episode_title": episode_title,
                "duration": duration,
                "topics": topics,
                "description": "",
                "chapters": [],
                "key_takeaways": [],
                "links": [],
            }


podcast_show_notes_generator_service = PodcastShowNotesGeneratorService()