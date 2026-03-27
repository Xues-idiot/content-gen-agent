"""
Vox Video Tutorial Generator Service 模块

视频教程生成服务
- 教程大纲
- 步骤说明
- 常见问题
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class VideoTutorialGeneratorService:
    """
    视频教程生成服务

    生成视频教程内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_video_tutorial(
        self,
        tutorial_topic: str,
        skill_level: str = "beginner",
        estimated_duration: int = 10,
        platform: str = "youtube",
    ) -> Dict[str, Any]:
        """
        生成视频教程

        Args:
            tutorial_topic: 教程主题
            skill_level: 技能级别
            estimated_duration: 预计时长（分钟）
            platform: 平台

        Returns:
            Dict: 视频教程
        """
        try:
            prompt = f"""请为"{tutorial_topic}"视频教程（级别：{skill_level}，时长：{estimated_duration}分钟，平台：{platform}）生成内容。

请以JSON格式返回：
{{
    "tutorial_topic": "教程主题",
    "skill_level": "技能级别",
    "estimated_duration": 时长,
    "platform": "平台",
    "tutorial_title": "教程标题",
    "video_description": "视频描述",
    "key_steps": [
        {{
            "step_number": 1,
            "title": "步骤标题",
            "description": "步骤描述",
            "timestamp": "0:00"
        }}
    ],
    "required_materials": ["所需材料1"],
    "tips_and_warnings": ["技巧1", "警告1"],
    "related_tutorials": ["相关教程1"],
    "chapters": ["章节1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "tutorial_topic": tutorial_topic,
                "skill_level": skill_level,
                "estimated_duration": estimated_duration,
                "platform": platform,
                **result,
            }

        except Exception as e:
            logger.error(f"生成视频教程失败: {e}")
            return {
                "tutorial_topic": tutorial_topic,
                "skill_level": skill_level,
                "estimated_duration": estimated_duration,
                "platform": platform,
                "tutorial_title": "",
                "video_description": "",
                "key_steps": [],
                "required_materials": [],
                "tips_and_warnings": [],
                "related_tutorials": [],
                "chapters": [],
            }


video_tutorial_generator_service = VideoTutorialGeneratorService()