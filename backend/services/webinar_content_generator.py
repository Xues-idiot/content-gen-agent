"""
Vox Webinar Content Generator Service 模块

网络研讨会内容生成服务
- 主题设计
- 演示幻灯片
- 观众参与
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class WebinarContentGeneratorService:
    """
    网络研讨会内容生成服务

    生成网络研讨会内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_webinar_content(
        self,
        topic: str,
        target_audience: str,
        duration_minutes: int = 60,
    ) -> Dict[str, Any]:
        """
        生成网络研讨会内容

        Args:
            topic: 主题
            target_audience: 目标受众
            duration_minutes: 时长（分钟）

        Returns:
            Dict: 网络研讨会内容
        """
        try:
            prompt = f"""请为"{topic}"生成针对{target_audience}的网络研讨会内容（时长：{duration_minutes}分钟）。

请以JSON格式返回：
{{
    "title": "标题",
    "topic": "主题",
    "target_audience": "目标受众",
    "duration_minutes": {duration_minutes},
    "description": "描述",
    "learning_objectives": ["学习目标1"],
    "agenda": [
        {{
            "time_slot": "时间段",
            "topic": "主题",
            "speaker": "演讲者",
            "format": "格式",
            "duration_minutes": 分钟数
        }}
    ],
    "slides": [
        {{
            "slide_number": 1,
            "title": "幻灯片标题",
            "bullets": ["要点1"],
            "speaker_notes": "演讲者备注",
            "visuals_suggested": "建议视觉元素"
        }}
    ],
    "polls": [
        {{
            "question": "问题",
            "options": ["选项1"],
            "timing": "时机",
            "purpose": "目的"
        }}
    ],
    "qa_questions": ["Q&A问题1"],
    "resources": [
        {{
            "title": "资源标题",
            "type": "类型",
            "url": "URL",
            "when_to_share": "何时分享"
        }}
    ],
    "follow_up_email": "跟进邮件内容",
    "promotional_copy": "推广文案",
    "technical_requirements": ["技术要求1"],
    "speaker_briefing": "演讲者简报"
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
                "target_audience": target_audience,
                "duration_minutes": duration_minutes,
                **result,
            }

        except Exception as e:
            logger.error(f"生成网络研讨会内容失败: {e}")
            return {
                "topic": topic,
                "target_audience": target_audience,
                "duration_minutes": duration_minutes,
                "title": "",
                "description": "",
                "learning_objectives": [],
                "agenda": [],
                "slides": [],
                "polls": [],
                "qa_questions": [],
                "resources": [],
                "follow_up_email": "",
                "promotional_copy": "",
                "technical_requirements": [],
                "speaker_briefing": "",
            }


webinar_content_generator_service = WebinarContentGeneratorService()