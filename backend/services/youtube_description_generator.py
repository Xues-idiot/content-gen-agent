"""
Vox YouTube Description Generator Service 模块

YouTube描述生成服务
- 视频描述
- 标签建议
- 行动号召
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class YouTubeDescriptionGeneratorService:
    """
    YouTube描述生成服务

    生成YouTube描述内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_youtube_description(
        self,
        video_title: str,
        video_type: str,
        duration_seconds: int,
    ) -> Dict[str, Any]:
        """
        生成YouTube描述

        Args:
            video_title: 视频标题
            video_type: 视频类型
            duration_seconds: 时长（秒）

        Returns:
            Dict: YouTube描述
        """
        try:
            prompt = f"""请为"{video_title}"（{video_type}，{duration_seconds}秒）生成YouTube视频描述。

请以JSON格式返回：
{{
    "video_title": "视频标题",
    "video_type": "视频类型",
    "duration_seconds": {duration_seconds},
    "description": "描述",
    "timestamps": [
        {{
            "time": "时间戳",
            "label": "标签"
        }}
    ],
    "tags": ["标签1"],
    "links": [
        {{
            "text": "文本",
            "url": "URL"
        }}
    ],
    "cta": "CTA",
    "hashtags": ["#话题标签1"]
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
                "video_type": video_type,
                "duration_seconds": duration_seconds,
                **result,
            }

        except Exception as e:
            logger.error(f"生成YouTube描述失败: {e}")
            return {
                "video_title": video_title,
                "video_type": video_type,
                "duration_seconds": duration_seconds,
                "description": "",
                "timestamps": [],
                "tags": [],
                "links": [],
                "cta": "",
                "hashtags": [],
            }


youtube_description_generator_service = YouTubeDescriptionGeneratorService()