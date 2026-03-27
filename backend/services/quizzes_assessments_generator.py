"""
Vox Quizzes Assessments Generator Service 模块

测验评估生成服务
- 知识测验
- 个性化推荐
- 参与互动
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class QuizzesAssessmentsGeneratorService:
    """
    测验评估生成服务

    生成测验评估内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_quizzes_assessments(
        self,
        topic: str,
        num_questions: int = 10,
        quiz_type: str = "knowledge",
    ) -> Dict[str, Any]:
        """
        生成测验评估

        Args:
            topic: 主题
            num_questions: 问题数量
            quiz_type: 测验类型

        Returns:
            Dict: 测验评估
        """
        try:
            prompt = f"""请为"{topic}"生成{quiz_type}类型的{num_questions}题测验评估。

请以JSON格式返回：
{{
    "topic": "主题",
    "num_questions": {num_questions},
    "quiz_type": "测验类型",
    "quiz_title": "测验标题",
    "quiz_description": "测验描述",
    "estimated_time": "预计时间",
    "questions": [
        {{
            "question_number": 1,
            "question_text": "问题文本",
            "question_type": "问题类型",
            "options": ["选项1"],
            "correct_answer": "正确答案",
            "explanation": "解释"
        }}
    ],
    "scoring_logic": "计分逻辑",
    "results_interpretation": [
        {{
            "score_range": "分数范围",
            "result_title": "结果标题",
            "recommendations": ["建议1"]
        }}
    ],
    "lead_capture": "潜在客户捕获",
    "share_results_options": ["分享结果选项1"]
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
                "num_questions": num_questions,
                "quiz_type": quiz_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成测验评估失败: {e}")
            return {
                "topic": topic,
                "num_questions": num_questions,
                "quiz_type": quiz_type,
                "quiz_title": "",
                "quiz_description": "",
                "estimated_time": "",
                "questions": [],
                "scoring_logic": "",
                "results_interpretation": [],
                "lead_capture": "",
                "share_results_options": [],
            }


quizzes_assessments_generator_service = QuizzesAssessmentsGeneratorService()