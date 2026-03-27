"""
Vox Video Description Generator Service 模块

视频描述生成服务
- 视频简介
- SEO优化
- 标签建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class VideoDescriptionGeneratorService:
    """
    视频描述生成服务

    生成YouTube/视频平台描述
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_description(
        self,
        video_title: str,
        duration: int,
        topics: List[str],
    ) -> Dict[str, Any]:
        """
        生成视频描述

        Args:
            video_title: 视频标题
            duration: 时长
            topics: 话题

        Returns:
            Dict: 描述内容
        """
        try:
            prompt = f"""请为"{video_title}"生成YouTube视频描述。

时长：{duration}分钟
话题：{', '.join(topics)}

请以JSON格式返回：
{{
    "description": "视频描述",
    "tags": ["标签1", "标签2"],
    "hashtags": ["#标签1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "video_title": video_title,
                "duration": duration,
                "topics": topics,
                **result,
            }

        except Exception as e:
            logger.error(f"生成视频描述失败: {e}")
            return {
                "video_title": video_title,
                "duration": duration,
                "topics": topics,
                "description": "",
                "tags": [],
                "hashtags": [],
            }


video_description_generator_service = VideoDescriptionGeneratorService()