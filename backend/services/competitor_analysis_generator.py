"""
Vox Competitor Analysis Generator Service 模块

竞争对手分析生成服务
- 竞品对比
- 市场份额
- 策略分析
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CompetitorAnalysisGeneratorService:
    """
    竞争对手分析生成服务

    生成竞争对手分析内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_competitor_analysis(
        self,
        your_product: str,
        competitor_name: str,
        industry: str,
    ) -> Dict[str, Any]:
        """
        生成竞争对手分析

        Args:
            your_product: 你的产品
            competitor_name: 竞争对手名称
            industry: 行业

        Returns:
            Dict: 竞争对手分析
        """
        try:
            prompt = f"""请为"{your_product}"与"{competitor_name}"（{industry}行业）进行竞争对手分析。

请以JSON格式返回：
{{
    "your_product": "你的产品",
    "competitor_name": "竞争对手",
    "industry": "行业",
    "overview": "概述",
    "competitor_profile": {{
        "company_size": "公司规模",
        "market_position": "市场地位",
        "founded_year": "成立年份",
        "headquarters": "总部"
    }},
    "product_comparison": [
        {{
            "feature": "功能",
            "your_product": "你的产品",
            "competitor": "竞品",
            "advantage": "优势方"
        }}
    ],
    "pricing_comparison": "定价对比",
    "strengths": ["竞争对手优势1"],
    "weaknesses": ["竞争对手劣势1"],
    "market_share": "市场份额",
    "customer_reviews_summary": "客户评价摘要",
    "marketing_strategies": ["营销策略1"],
    "distribution_channels": ["分销渠道1"],
    "swot_analysis": {{
        "strengths": ["优势1"],
        "weaknesses": ["劣势1"],
        "opportunities": ["机会1"],
        "threats": ["威胁1"]
    }},
    "competitive_advantages_to_emphasize": ["需强调的竞争优势1"],
    "potential_threats": ["潜在威胁1"],
    "strategic_recommendations": ["战略建议1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "your_product": your_product,
                "competitor_name": competitor_name,
                "industry": industry,
                **result,
            }

        except Exception as e:
            logger.error(f"生成竞争对手分析失败: {e}")
            return {
                "your_product": your_product,
                "competitor_name": competitor_name,
                "industry": industry,
                "overview": "",
                "competitor_profile": {},
                "product_comparison": [],
                "pricing_comparison": "",
                "strengths": [],
                "weaknesses": [],
                "market_share": "",
                "customer_reviews_summary": "",
                "marketing_strategies": [],
                "distribution_channels": [],
                "swot_analysis": {},
                "competitive_advantages_to_emphasize": [],
                "potential_threats": [],
                "strategic_recommendations": [],
            }


competitor_analysis_generator_service = CompetitorAnalysisGeneratorService()