"""
Vox Speech Generator Service 模块

演讲稿生成服务
- 演讲稿撰写
- 演讲技巧
- PPT备注
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SpeechGeneratorService:
    """
    演讲稿生成服务

    生成演讲稿和PPT备注
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_speech(
        self,
        topic: str,
        duration: int = 10,
        audience: str = "general",
    ) -> Dict[str, Any]:
        """
        生成演讲稿

        Args:
            topic: 主题
            duration: 时长（分钟）
            audience: 听众

        Returns:
            Dict: 演讲稿内容
        """
        try:
            prompt = f"""请为"{topic}"生成一篇{duration}分钟的演讲稿。

听众：{audience}

请以JSON格式返回：
{{
    "title": "演讲标题",
    "introduction": "开场白",
    "main_points": ["要点1", "要点2"],
    "stories": ["故事1"],
    "conclusion": "结语",
    "ppt_notes": ["PPT备注1", "PPT备注2"]
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
                "duration": duration,
                "audience": audience,
                **result,
            }

        except Exception as e:
            logger.error(f"生成演讲稿失败: {e}")
            return {
                "topic": topic,
                "duration": duration,
                "audience": audience,
                "title": "",
                "introduction": "",
                "main_points": [],
                "stories": [],
                "conclusion": "",
                "ppt_notes": [],
            }


speech_generator_service = SpeechGeneratorService()