"""
Vox Comparison Page Generator Service 模块

比较页面生成服务
- 功能对比
- 定价对比
- 优劣势分析
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ComparisonPageGeneratorService:
    """
    比较页面生成服务

    生成比较页面内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_comparison_page(
        self,
        product_name: str,
        competitors: List[str],
        comparison_type: str = "features",
    ) -> Dict[str, Any]:
        """
        生成比较页面

        Args:
            product_name: 产品名称
            competitors: 竞争对手列表
            comparison_type: 比较类型

        Returns:
            Dict: 比较页面
        """
        competitors_str = ", ".join(competitors)
        try:
            prompt = f"""请为"{product_name}"与{competitors_str}生成{comparison_type}类型的比较页面。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "competitors": {competitors},
    "comparison_type": "比较类型",
    "page_headline": "页面标题",
    "our_product_summary": "我们的产品摘要",
    "comparison_matrix": {{
        "features": ["功能1"],
        "products": ["产品1"]
    }},
    "strengths_weaknesses": {{
        "our_product": {{
            "strengths": ["优势1"],
            "weaknesses": ["劣势1"]
        }},
        "competitors": [
            {{
                "name": "名称",
                "strengths": ["优势1"],
                "weaknesses": ["劣势1"]
            }}
        ]
    }},
    "detailed_comparisons": [
        {{
            "category": "类别",
            "items": [
                {{
                    "feature": "功能",
                    "our_product": "我们的产品",
                    "competitor_a": "竞品A",
                    "competitor_b": "竞品B"
                }}
            ]
        }}
    ],
    "pricing_comparison": {{
        "our_product": "我们的产品定价",
        "competitors": "竞争对手定价"
    }},
    "use_case_recommendations": [
        {{
            "scenario": "场景",
            "recommended": "推荐"
        }}
    ],
    "migration_support": "迁移支持",
    "conversion_cta": "转化CTA"
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
                "competitors": competitors,
                "comparison_type": comparison_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成比较页面失败: {e}")
            return {
                "product_name": product_name,
                "competitors": competitors,
                "comparison_type": comparison_type,
                "page_headline": "",
                "our_product_summary": "",
                "comparison_matrix": {},
                "strengths_weaknesses": {},
                "detailed_comparisons": [],
                "pricing_comparison": {},
                "use_case_recommendations": [],
                "migration_support": "",
                "conversion_cta": "",
            }


comparison_page_generator_service = ComparisonPageGeneratorService()