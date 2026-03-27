"""
Vox Sales Training Module Generator Service 模块

销售培训模块生成服务
- 培训内容
- 学习目标
- 评估标准
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SalesTrainingModuleGeneratorService:
    """
    销售培训模块生成服务

    生成销售培训模块内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_sales_training_module(
        self,
        module_topic: str,
        audience_level: str,
        num_lessons: int = 5,
    ) -> Dict[str, Any]:
        """
        生成销售培训模块

        Args:
            module_topic: 模块主题
            audience_level: 受众级别
            num_lessons: 课程数量

        Returns:
            Dict: 销售培训模块
        """
        try:
            prompt = f"""请为"{module_topic}"主题生成{num_lessons}个课程的{average_level}级别销售培训模块。

请以JSON格式返回：
{{
    "module_topic": "模块主题",
    "audience_level": "受众级别",
    "num_lessons": {num_lessons},
    "module_title": "模块标题",
    "learning_objectives": ["学习目标1"],
    "lessons": [
        {{
            "lesson_title": "课程标题",
            "duration": "时长",
            "content_outline": "内容大纲",
            "activities": ["活动1"],
            "deliverables": ["可交付成果1"]
        }}
    ],
    "teaching_methods": ["教学方法1"],
    "assessment_methods": ["评估方法1"],
    "prerequisites": ["先决条件1"],
    "resources_provided": ["提供的资源1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "module_topic": module_topic,
                "audience_level": audience_level,
                "num_lessons": num_lessons,
                **result,
            }

        except Exception as e:
            logger.error(f"生成销售培训模块失败: {e}")
            return {
                "module_topic": module_topic,
                "audience_level": audience_level,
                "num_lessons": num_lessons,
                "module_title": "",
                "learning_objectives": [],
                "lessons": [],
                "teaching_methods": [],
                "assessment_methods": [],
                "prerequisites": [],
                "resources_provided": [],
            }


sales_training_module_generator_service = SalesTrainingModuleGeneratorService()
