"""
Vox Course Syllabus Generator Service 模块

课程大纲生成服务
- 课程结构
- 教学计划
- 评估方式
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CourseSyllabusGeneratorService:
    """
    课程大纲生成服务

    生成课程大纲内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_course_syllabus(
        self,
        course_title: str,
        subject: str,
        duration_weeks: int = 8,
        level: str = "beginner",
    ) -> Dict[str, Any]:
        """
        生成课程大纲

        Args:
            course_title: 课程标题
            subject: 科目
            duration_weeks: 课程周期（周）
            level: 难度级别

        Returns:
            Dict: 课程大纲
        """
        try:
            prompt = f"""请为"{course_title}"课程（科目：{subject}，周期：{duration_weeks}周，级别：{level}）生成大纲。

请以JSON格式返回：
{{
    "course_title": "课程标题",
    "subject": "科目",
    "duration_weeks": 周数,
    "level": "级别",
    "course_description": "课程描述",
    "learning_outcomes": ["学习成果1"],
    "weekly_topics": ["第1周：主题1", "第2周：主题2"],
    "required_materials": ["教材1"],
    "grading_policy": "评估政策",
    "prerequisites": "先修条件",
    "office_hours": "答疑时间"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "course_title": course_title,
                "subject": subject,
                "duration_weeks": duration_weeks,
                "level": level,
                **result,
            }

        except Exception as e:
            logger.error(f"生成课程大纲失败: {e}")
            return {
                "course_title": course_title,
                "subject": subject,
                "duration_weeks": duration_weeks,
                "level": level,
                "course_description": "",
                "learning_outcomes": [],
                "weekly_topics": [],
                "required_materials": [],
                "grading_policy": "",
                "prerequisites": "",
                "office_hours": "",
            }


course_syllabus_generator_service = CourseSyllabusGeneratorService()