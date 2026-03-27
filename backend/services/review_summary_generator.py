"""
Vox Review Summary Generator Service 模块

评测摘要生成服务
- 产品评测总结
- 优缺点汇总
- 购买建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ReviewSummaryGeneratorService:
    """
    评测摘要生成服务

    生成产品评测摘要
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_summary(
        self,
        product_name: str,
        pros: List[str],
        cons: List[str],
    ) -> Dict[str, Any]:
        """
        生成评测摘要

        Args:
            product_name: 产品名称
            pros: 优点列表
            cons: 缺点列表

        Returns:
            Dict: 评测摘要
        """
        try:
            prompt = f"""请为"{product_name}"生成评测摘要。

优点：{', '.join(pros)}
缺点：{', '.join(cons)}

请以JSON格式返回：
{{
    "overall_rating": 8.5,
    "summary": "总体评价",
    "verdict": "最终结论",
    "best_for": "最适合人群",
    "alternatives": ["替代产品1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_name": product_name,
                "pros": pros,
                "cons": cons,
                **result,
            }

        except Exception as e:
            logger.error(f"生成评测摘要失败: {e}")
            return {
                "product_name": product_name,
                "pros": pros,
                "cons": cons,
                "overall_rating": 0,
                "summary": "",
                "verdict": "",
                "best_for": "",
                "alternatives": [],
            }


review_summary_generator_service = ReviewSummaryGeneratorService()