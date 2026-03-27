"""
Vox Sales Deck Generator Service 模块

销售演示文稿生成服务
- 公司介绍
- 产品展示
- 成功案例
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SalesDeckGeneratorService:
    """
    销售演示文稿生成服务

    生成销售演示文稿内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_sales_deck(
        self,
        company_name: str,
        product_service: str,
        target_audience: str,
    ) -> Dict[str, Any]:
        """
        生成销售演示文稿

        Args:
            company_name: 公司名称
            product_service: 产品/服务
            target_audience: 目标受众

        Returns:
            Dict: 销售演示文稿
        """
        try:
            prompt = f"""请为"{company_name}"生成针对{target_audience}的{product_service}销售演示文稿。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "product_service": "产品/服务",
    "target_audience": "目标受众",
    "presentation_title": "演示标题",
    "opening_hook": "开场吸引点",
    "slides": [
        {{
            "slide_number": 1,
            "title": "幻灯片标题",
            "subtitle": "副标题",
            "bullets": ["要点1"],
            "visuals_notes": "视觉说明",
            "speaker_notes": "演讲者备注",
            "time_allocation": "时间分配"
        }}
    ],
    "problem_agitation": {{
        "pain_points": ["痛点1"],
        "current_challenges": ["当前挑战1"]
    }},
    "solution_presentation": {{
        "key_benefits": ["关键好处1"],
        "how_it_works": "工作原理",
        "unique_value_proposition": "独特价值主张"
    }},
    "product_demo_highlights": ["产品演示亮点1"],
    "case_study_snippets": ["案例研究片段1"],
    "social_proof": ["社会证明1"],
    "pricing_overview": "定价概述",
    "objection_handling": [
        {{
            "objection": "异议",
            "response": "回应"
        }}
    ],
    "faq": ["常见问题1"],
    "cta_next_steps": "CTA下一步",
    "closing_slide": "结束幻灯片",
    "appendix_resources": ["附录资源1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "company_name": company_name,
                "product_service": product_service,
                "target_audience": target_audience,
                **result,
            }

        except Exception as e:
            logger.error(f"生成销售演示文稿失败: {e}")
            return {
                "company_name": company_name,
                "product_service": product_service,
                "target_audience": target_audience,
                "presentation_title": "",
                "opening_hook": "",
                "slides": [],
                "problem_agitation": {},
                "solution_presentation": {},
                "product_demo_highlights": [],
                "case_study_snippets": [],
                "social_proof": [],
                "pricing_overview": "",
                "objection_handling": [],
                "faq": [],
                "cta_next_steps": "",
                "closing_slide": "",
                "appendix_resources": [],
            }


sales_deck_generator_service = SalesDeckGeneratorService()