"""
Vox Webinar Abstract Generator Service 模块

网络研讨会摘要生成服务
- 演讲摘要
- 学习目标
- 目标受众
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class WebinarAbstractGeneratorService:
    """
    网络研讨会摘要生成服务

    生成网络研讨会摘要内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_webinar_abstract(
        self,
        webinar_title: str,
        presenter_name: str,
        duration_minutes: int,
    ) -> Dict[str, Any]:
        """
        生成网络研讨会摘要

        Args:
            webinar_title: 研讨会标题
            presenter_name: 演讲者姓名
            duration_minutes: 时长（分钟）

        Returns:
            Dict: 网络研讨会摘要
        """
        try:
            prompt = f"""请为"{webinar_title}"（演讲者：{presenter_name}，时长：{duration_minutes}分钟）生成研讨会摘要。

请以JSON格式返回：
{{
    "webinar_title": "研讨会标题",
    "presenter_name": "演讲者姓名",
    "duration_minutes": {duration_minutes},
    "abstract": "摘要",
    "learning_objectives": ["学习目标1"],
    "target_audience": "目标受众",
    "key_takeaways": ["关键收获1"],
    "presenter_bio": "演讲者简介",
    "relevant_experience": "相关经验",
    "suggested_questions": ["建议问题1"]
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
                "presenter_name": presenter_name,
                "duration_minutes": duration_minutes,
                **result,
            }

        except Exception as e:
            logger.error(f"生成网络研讨会摘要失败: {e}")
            return {
                "webinar_title": webinar_title,
                "presenter_name": presenter_name,
                "duration_minutes": duration_minutes,
                "abstract": "",
                "learning_objectives": [],
                "target_audience": "",
                "key_takeaways": [],
                "presenter_bio": "",
                "relevant_experience": "",
                "suggested_questions": [],
            }


webinar_abstract_generator_service = WebinarAbstractGeneratorService()