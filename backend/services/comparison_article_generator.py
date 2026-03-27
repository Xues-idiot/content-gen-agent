"""
Vox Comparison Article Generator Service 模块

对比文章生成服务
- 产品对比
- 方案比较
- 优劣势分析
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ComparisonArticleGeneratorService:
    """
    对比文章生成服务

    生成对比文章内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_comparison_article(
        self,
        item_a: str,
        item_b: str,
        comparison_criteria: List[str] = None,
    ) -> Dict[str, Any]:
        """
        生成对比文章

        Args:
            item_a: 对比项A
            item_b: 对比项B
            comparison_criteria: 对比标准

        Returns:
            Dict: 对比文章
        """
        if comparison_criteria is None:
            comparison_criteria = ["功能", "价格", "易用性", "支持"]

        try:
            criteria_str = ", ".join(comparison_criteria)
            prompt = f"""请为"{item_a}"和"{item_b}"生成对比文章（对比标准：{criteria_str}）。

请以JSON格式返回：
{{
    "item_a": "对比项A",
    "item_b": "对比项B",
    "comparison_criteria": ["对比标准1"],
    "title": "文章标题",
    "introduction": "引言",
    "summary_table": [
        {{
            "criteria": "标准",
            "item_a_rating": "A评分",
            "item_b_rating": "B评分"
        }}
    ],
    "pros_cons": {{
        "item_a": {{
            "pros": ["优点1"],
            "cons": ["缺点1"]
        }},
        "item_b": {{
            "pros": ["优点1"],
            "cons": ["缺点1"]
        }}
    }},
    "detailed_analysis": "详细分析",
    "recommendation": "推荐建议",
    "conclusion": "结论"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "item_a": item_a,
                "item_b": item_b,
                "comparison_criteria": comparison_criteria,
                **result,
            }

        except Exception as e:
            logger.error(f"生成对比文章失败: {e}")
            return {
                "item_a": item_a,
                "item_b": item_b,
                "comparison_criteria": comparison_criteria,
                "title": "",
                "introduction": "",
                "summary_table": [],
                "pros_cons": {},
                "detailed_analysis": "",
                "recommendation": "",
                "conclusion": "",
            }


comparison_article_generator_service = ComparisonArticleGeneratorService()