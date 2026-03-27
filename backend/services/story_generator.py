"""
Vox Story Generator Service 模块

故事生成服务
- 个人故事
- 品牌故事
- 场景故事
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class StoryGeneratorService:
    """
    故事生成服务

    生成故事内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_story(
        self,
        topic: str,
        story_type: str = "personal",
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        生成故事

        Args:
            topic: 主题
            story_type: 故事类型（personal/brand/scenario）
            platform: 平台

        Returns:
            Dict: 故事内容
        """
        try:
            prompt = f"""请为"{topic}"生成一个{story_type}类型的故事。

平台：{platform}

请以JSON格式返回：
{{
    "title": "故事标题",
    "setting": "背景设定",
    "characters": ["角色1", "角色2"],
    "plot_points": ["情节点1", "情节点2"],
    "emotional_takeaway": "情感收获"
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
                "story_type": story_type,
                "platform": platform,
                **result,
            }

        except Exception as e:
            logger.error(f"生成故事失败: {e}")
            return {
                "topic": topic,
                "story_type": story_type,
                "platform": platform,
                "title": "",
                "setting": "",
                "characters": [],
                "plot_points": [],
                "emotional_takeaway": "",
            }


story_generator_service = StoryGeneratorService()