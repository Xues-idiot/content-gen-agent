"""
Vox Training Materials Generator Service 模块

培训材料生成服务
- 培训大纲
- 课程内容
- 评估材料
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TrainingMaterialsGeneratorService:
    """
    培训材料生成服务

    生成培训材料内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_training_materials(
        self,
        training_topic: str,
        audience_level: str,
        num_modules: int = 5,
    ) -> Dict[str, Any]:
        """
        生成培训材料

        Args:
            training_topic: 培训主题
            audience_level: 受众级别
            num_modules: 模块数量

        Returns:
            Dict: 培训材料
        """
        try:
            prompt = f"""请为"{training_topic}"培训生成{average_level}级别的{num_modules}模块培训材料。

请以JSON格式返回：
{{
    "training_topic": "培训主题",
    "audience_level": "受众级别",
    "num_modules": {num_modules},
    "course_title": "课程标题",
    "course_duration": "课程时长",
    "learning_objectives": ["学习目标1"],
    "modules": [
        {{
            "module_title": "模块标题",
            "module_duration": "模块时长",
            "learning_outcomes": ["学习成果1"],
            "content_ outline": "内容大纲",
            "activities": ["活动1"],
            "resources": ["资源1"]
        }}
    ],
    "teaching_methods": ["教学方法1"],
    "assessment_methods": ["评估方法1"],
    "materials_provided": ["提供的材料1"],
    "prerequisites": ["先决条件1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "training_topic": training_topic,
                "audience_level": audience_level,
                "num_modules": num_modules,
                **result,
            }

        except Exception as e:
            logger.error(f"生成培训材料失败: {e}")
            return {
                "training_topic": training_topic,
                "audience_level": audience_level,
                "num_modules": num_modules,
                "course_title": "",
                "course_duration": "",
                "learning_objectives": [],
                "modules": [],
                "teaching_methods": [],
                "assessment_methods": [],
                "materials_provided": [],
                "prerequisites": [],
            }


training_materials_generator_service = TrainingMaterialsGeneratorService()
