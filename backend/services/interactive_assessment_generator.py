"""
Vox Interactive Assessment Generator Service 模块

互动评估生成服务
- 评估问题
- 结果计算
- 建议生成
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class InteractiveAssessmentGeneratorService:
    """
    互动评估生成服务

    生成互动评估内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_interactive_assessment(
        self,
        assessment_name: str,
        topic: str,
        num_questions: int = 10,
    ) -> Dict[str, Any]:
        """
        生成互动评估

        Args:
            assessment_name: 评估名称
            topic: 主题
            num_questions: 问题数量

        Returns:
            Dict: 互动评估
        """
        try:
            prompt = f"""请为"{assessment_name}"（主题：{topic}）生成包含{num_questions}个问题的互动评估。

请以JSON格式返回：
{{
    "assessment_name": "评估名称",
    "topic": "主题",
    "num_questions": {num_questions},
    "assessment_headline": "评估标题",
    "intro_text": "介绍文本",
    "estimated_duration": "预计时长",
    "target_audience": "目标受众",
    "questions": [
        {{
            "question_number": 1,
            "question_text": "问题文本",
            "question_type": "问题类型",
            "options": ["选项1"],
            "correct_answer": "正确答案",
            "explanation": "解释",
            "weight": 权重
        }}
    ],
    "scoring_logic": "计分逻辑",
    "result_ranges": [
        {{
            "range": "范围",
            "title": "标题",
            "description": "描述",
            "recommendations": ["建议1"]
        }}
    ],
    "lead_magnet_offer": "潜在客户吸引优惠",
    "share_results_options": "分享结果选项",
    "follow_up_sequence": "跟进序列"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "assessment_name": assessment_name,
                "topic": topic,
                "num_questions": num_questions,
                **result,
            }

        except Exception as e:
            logger.error(f"生成互动评估失败: {e}")
            return {
                "assessment_name": assessment_name,
                "topic": topic,
                "num_questions": num_questions,
                "assessment_headline": "",
                "intro_text": "",
                "estimated_duration": "",
                "target_audience": "",
                "questions": [],
                "scoring_logic": "",
                "result_ranges": [],
                "lead_magnet_offer": "",
                "share_results_options": "",
                "follow_up_sequence": "",
            }


interactive_assessment_generator_service = InteractiveAssessmentGeneratorService()