"""
Vox Business Review Presentation Generator Service 模块

业务审查演示文稿生成服务
- 关键指标
- 趋势分析
- 战略建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BusinessReviewPresentationGeneratorService:
    """
    业务审查演示文稿生成服务

    生成业务审查演示文稿内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_business_review_presentation(
        self,
        review_period: str,
        department: str,
        num_slides: int = 15,
    ) -> Dict[str, Any]:
        """
        生成业务审查演示文稿

        Args:
            review_period: 审查周期
            department: 部门
            num_slides: 幻灯片数量

        Returns:
            Dict: 业务审查演示文稿
        """
        try:
            prompt = f"""请为{department}部门生成{review_period}的{num_slides}页业务审查演示文稿。

请以JSON格式返回：
{{
    "review_period": "审查周期",
    "department": "部门",
    "num_slides": {num_slides},
    "presentation_title": "演示文稿标题",
    "slides": [
        {{
            "slide_number": 1,
            "title": "标题",
            "content_summary": "内容摘要",
            "key_takeaways": ["关键收获1"]
        }}
    ],
    "executive_summary_points": ["执行摘要要点1"],
    "financial_highlights": ["财务亮点1"],
    "achievements": ["成就1"],
    "challenges": ["挑战1"],
    "recommendations": ["建议1"],
    "next_quarter_focus": "下季度重点"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "review_period": review_period,
                "department": department,
                "num_slides": num_slides,
                **result,
            }

        except Exception as e:
            logger.error(f"生成业务审查演示文稿失败: {e}")
            return {
                "review_period": review_period,
                "department": department,
                "num_slides": num_slides,
                "presentation_title": "",
                "slides": [],
                "executive_summary_points": [],
                "financial_highlights": [],
                "achievements": [],
                "challenges": [],
                "recommendations": [],
                "next_quarter_focus": "",
            }


business_review_presentation_generator_service = BusinessReviewPresentationGeneratorService()