"""
Vox Comparison Generator Service 模块

对比生成服务
- 产品对比
- 方案对比
- 优缺点分析
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ComparisonGeneratorService:
    """
    对比生成服务

    生成对比内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_comparison(
        self,
        item_a: str,
        item_b: str,
        comparison_dimensions: List[str],
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        生成对比

        Args:
            item_a: 对比项A
            item_b: 对比项B
            comparison_dimensions: 对比维度
            platform: 平台

        Returns:
            Dict: 对比内容
        """
        try:
            prompt = f"""请对比"{item_a}"和"{item_b}"。

平台：{platform}
对比维度：{', '.join(comparison_dimensions)}

请以JSON格式返回：
{{
    "item_a": "{item_a}",
    "item_b": "{item_b}",
    "comparison_table": [
        {{
            "dimension": "维度",
            "item_a_score": "A评分",
            "item_b_score": "B评分",
            "winner": "A/B/平手"
        }}
    ],
    "summary": "总结",
    "recommendation": "推荐建议"
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
                "platform": platform,
                **result,
            }

        except Exception as e:
            logger.error(f"生成对比失败: {e}")
            return {
                "item_a": item_a,
                "item_b": item_b,
                "platform": platform,
                "comparison_table": [],
                "summary": "",
                "recommendation": "",
            }


comparison_generator_service = ComparisonGeneratorService()