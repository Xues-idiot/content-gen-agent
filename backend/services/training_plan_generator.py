"""
Vox Training Plan Generator Service 模块

培训计划生成服务
- 培训内容
- 时间安排
- 效果评估
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TrainingPlanGeneratorService:
    """
    培训计划生成服务

    生成培训计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_training_plan(
        self,
        training_title: str,
        target_audience: str,
        duration_hours: int = 8,
        num_sessions: int = 4,
    ) -> Dict[str, Any]:
        """
        生成培训计划

        Args:
            training_title: 培训标题
            target_audience: 目标受众
            duration_hours: 培训时长
            num_sessions: 场次数量

        Returns:
            Dict: 培训计划
        """
        try:
            prompt = f"""请为"{training_title}"（受众：{target_audience}，时长：{duration_hours}小时，共{num_sessions}场）生成培训计划。

请以JSON格式返回：
{{
    "training_title": "培训标题",
    "target_audience": "目标受众",
    "duration_hours": 时长,
    "num_sessions": 场数,
    "overview": "概述",
    "objectives": ["培训目标1"],
    "prerequisites": ["前提条件1"],
    "sessions": [
        {{
            "session_number": 1,
            "session_title": "场次标题",
            "duration_minutes": 分钟数,
            "topics": ["主题1"],
            "activities": ["活动1"],
            "materials": ["材料1"],
            "trainer": "培训师"
        }}
    ],
    "methodology": "培训方法",
    "assessment_methods": ["评估方法1"],
    "resources_required": ["所需资源1"],
    "post_training_support": "培训后支持",
    "evaluation_criteria": "评估标准",
    "certification": "证书",
    "follow_up_plan": "跟进计划"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "training_title": training_title,
                "target_audience": target_audience,
                "duration_hours": duration_hours,
                "num_sessions": num_sessions,
                **result,
            }

        except Exception as e:
            logger.error(f"生成培训计划失败: {e}")
            return {
                "training_title": training_title,
                "target_audience": target_audience,
                "duration_hours": duration_hours,
                "num_sessions": num_sessions,
                "overview": "",
                "objectives": [],
                "prerequisites": [],
                "sessions": [],
                "methodology": "",
                "assessment_methods": [],
                "resources_required": [],
                "post_training_support": "",
                "evaluation_criteria": "",
                "certification": "",
                "follow_up_plan": "",
            }


training_plan_generator_service = TrainingPlanGeneratorService()