"""
Vox Testimonial Highlight Generator Service 模块

证言亮点生成服务
- 精选引言
- 场景标签
- 展示优化
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TestimonialHighlightGeneratorService:
    """
    证言亮点生成服务

    生成证言亮点内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_testimonial_highlight(
        self,
        product_service: str,
        num_highlights: int = 5,
        focus_area: str = "benefits",
    ) -> Dict[str, Any]:
        """
        生成证言亮点

        Args:
            product_service: 产品/服务
            num_highlights: 亮点数量
            focus_area: 聚焦领域

        Returns:
            Dict: 证言亮点
        """
        try:
            prompt = f"""请为"{product_service}"生成{num_highlights}个聚焦{focus_area}的证言亮点。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "num_highlights": {num_highlights},
    "focus_area": "聚焦领域",
    "highlights": [
        {{
            "headline": "标题",
            "quote_excerpt": "引言摘要",
            "full_story_link": "完整故事链接",
            "author": "作者",
            "role": "角色",
            "company": "公司",
            "use_case": "用例",
            "metrics_results": "指标/结果",
            "tags": ["标签1"]
        }}
    ],
    "highlight_categories": [
        {{
            "category": "类别",
            "count": 数量,
            "examples": ["示例1"]
        }}
    ],
    "cta_for_more_testimonials": "更多证言CTA",
    "display_suggestions": ["展示建议1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_service": product_service,
                "num_highlights": num_highlights,
                "focus_area": focus_area,
                **result,
            }

        except Exception as e:
            logger.error(f"生成证言亮点失败: {e}")
            return {
                "product_service": product_service,
                "num_highlights": num_highlights,
                "focus_area": focus_area,
                "highlights": [],
                "highlight_categories": [],
                "cta_for_more_testimonials": "",
                "display_suggestions": [],
            }


testimonial_highlight_generator_service = TestimonialHighlightGeneratorService()