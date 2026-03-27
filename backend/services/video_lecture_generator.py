"""
Vox Video Lecture Generator Service 模块

视频课程生成服务
- 课程大纲
- 课时描述
- 学习目标
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class VideoLectureGeneratorService:
    """
    视频课程生成服务

    生成在线课程内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_course_outline(
        self,
        course_name: str,
        num_lessons: int = 5,
    ) -> Dict[str, Any]:
        """
        生成课程大纲

        Args:
            course_name: 课程名称
            num_lessons: 课时数量

        Returns:
            Dict: 课程大纲
        """
        try:
            prompt = f"""请为"{course_name}"生成一个{num_lessons}课时的在线课程大纲。

请以JSON格式返回：
{{
    "course_title": "课程标题",
    "description": "课程描述",
    "lessons": [
        {{
            "title": "课时标题",
            "duration": 10,
            "learning_objectives": ["学习目标1"],
            "key_points": ["要点1"]
        }}
    ],
    "total_duration": 60
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "course_name": course_name,
                "num_lessons": num_lessons,
                **result,
            }

        except Exception as e:
            logger.error(f"生成课程大纲失败: {e}")
            return {
                "course_name": course_name,
                "num_lessons": num_lessons,
                "course_title": "",
                "description": "",
                "lessons": [],
                "total_duration": 0,
            }


video_lecture_generator_service = VideoLectureGeneratorService()