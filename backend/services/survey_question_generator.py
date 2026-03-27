"""
Vox Survey Question Generator Service 模块

调查问卷生成服务
- 问卷设计
- 问题选项
- 调研脚本
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SurveyQuestionGeneratorService:
    """
    调查问卷生成服务

    生成用户调研问卷
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_survey(
        self,
        survey_topic: str,
        num_questions: int = 10,
        survey_type: str = "feedback",
    ) -> Dict[str, Any]:
        """
        生成调查问卷

        Args:
            survey_topic: 问卷主题
            num_questions: 问题数量
            survey_type: 问卷类型

        Returns:
            Dict: 问卷内容
        """
        try:
            prompt = f"""请为"{survey_topic}"生成{num_questions}道{survey_type}类型的问卷题目。

请以JSON格式返回：
{{
    "title": "问卷标题",
    "questions": [
        {{
            "question": "问题",
            "type": "选择题/填空题/量表题",
            "options": ["选项1", "选项2"]
        }}
    ],
    "thank_you_message": "感谢语"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "survey_topic": survey_topic,
                "num_questions": num_questions,
                "survey_type": survey_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成调查问卷失败: {e}")
            return {
                "survey_topic": survey_topic,
                "num_questions": num_questions,
                "survey_type": survey_type,
                "title": "",
                "questions": [],
                "thank_you_message": "",
            }


survey_question_generator_service = SurveyQuestionGeneratorService()