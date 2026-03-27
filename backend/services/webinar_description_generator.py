"""
Vox Webinar Description Generator Service 模块

网络研讨会描述生成服务
- 研讨会介绍
- 议程安排
- 注册页面
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class WebinarDescriptionGeneratorService:
    """
    网络研讨会描述生成服务

    生成网络研讨会描述内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_webinar_description(
        self,
        webinar_title: str,
        topic: str,
        duration_minutes: int = 60,
        speaker_info: str = "",
    ) -> Dict[str, Any]:
        """
        生成网络研讨会描述

        Args:
            webinar_title: 研讨会标题
            topic: 主题
            duration_minutes: 时长（分钟）
            speaker_info: 演讲者信息

        Returns:
            Dict: 网络研讨会描述
        """
        try:
            prompt = f"""请为"{webinar_title}"（主题：{topic}，时长：{duration_minutes}分钟）生成描述。

请以JSON格式返回：
{{
    "webinar_title": "研讨会标题",
    "topic": "主题",
    "duration_minutes": 时长,
    "event_description": "活动描述",
    "key_learning_points": ["关键学习点1"],
    "agenda": [
        {{
            "time": "时间",
            "session": "环节",
            "speaker": "演讲者"
        }}
    ],
    "speaker_profiles": ["演讲者简介1"],
    "target_audience": "目标受众",
    "benefits": ["参会好处1"],
    "registration_cta": "注册行动号召",
    "faq": ["常见问题1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "webinar_title": webinar_title,
                "topic": topic,
                "duration_minutes": duration_minutes,
                "speaker_info": speaker_info,
                **result,
            }

        except Exception as e:
            logger.error(f"生成网络研讨会描述失败: {e}")
            return {
                "webinar_title": webinar_title,
                "topic": topic,
                "duration_minutes": duration_minutes,
                "speaker_info": speaker_info,
                "event_description": "",
                "key_learning_points": [],
                "agenda": [],
                "speaker_profiles": [],
                "target_audience": "",
                "benefits": [],
                "registration_cta": "",
                "faq": [],
            }


webinar_description_generator_service = WebinarDescriptionGeneratorService()