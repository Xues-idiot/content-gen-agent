"""
Vox Survey Questionnaire Generator Service 模块

调查问卷生成服务
- 问卷标题
- 问题设计
- 评分标准
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SurveyQuestionnaireGeneratorService:
    """
    调查问卷生成服务

    生成调查问卷内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_survey_questionnaire(
        self,
        survey_title: str,
        num_questions: int = 10,
        target_audience: str = "general",
    ) -> Dict[str, Any]:
        """
        生成调查问卷

        Args:
            survey_title: 问卷标题
            num_questions: 问题数量
            target_audience: 目标受众

        Returns:
            Dict: 调查问卷
        """
        try:
            prompt = f"""请为"{survey_title}"生成包含{num_questions}个问题的调查问卷（目标受众：{target_audience}）。

请以JSON格式返回：
{{
    "survey_title": "问卷标题",
    "description": "问卷描述",
    "target_audience": "目标受众",
    "estimated_completion_time": "预计完成时间",
    "intro_message": "开场白",
    "outro_message": "结束语",
    "questions": [
        {{
            "question_number": 1,
            "question_text": "问题文本",
            "question_type": "问题类型",
            "required": true,
            "options": ["选项1"],
            "scale_min": 1,
            "scale_max": 5,
            "scale_labels": {{"low": "低", "high": "高"}},
            "help_text": "帮助文本"
        }}
    ],
    "question_order": ["问题类型顺序1"],
    "skip_logic": [
        {{
            "if_answer": "如果答案",
            "then_skip_to": "则跳转到"
        }}
    ],
    "response_anonymity": "响应匿名性",
    "thank_you_screen": "感谢页面内容",
    "share_options": ["分享选项1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "survey_title": survey_title,
                "num_questions": num_questions,
                "target_audience": target_audience,
                **result,
            }

        except Exception as e:
            logger.error(f"生成调查问卷失败: {e}")
            return {
                "survey_title": survey_title,
                "num_questions": num_questions,
                "target_audience": target_audience,
                "description": "",
                "estimated_completion_time": "",
                "intro_message": "",
                "outro_message": "",
                "questions": [],
                "question_order": [],
                "skip_logic": [],
                "response_anonymity": "",
                "thank_you_screen": "",
                "share_options": [],
            }


survey_questionnaire_generator_service = SurveyQuestionnaireGeneratorService()