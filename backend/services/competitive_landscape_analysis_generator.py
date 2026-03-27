"""
Vox Competitive Landscape Analysis Generator Service 模块

竞争格局分析生成服务
- 竞争对手地图
- 市场份额
- 战略建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CompetitiveLandscapeAnalysisGeneratorService:
    """
    竞争格局分析生成服务

    生成竞争格局分析内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_competitive_landscape_analysis(
        self,
        industry: str,
        product_category: str,
        num_players: int = 8,
    ) -> Dict[str, Any]:
        """
        生成竞争格局分析

        Args:
            industry: 行业
            product_category: 产品类别
            num_players: 参与者数量

        Returns:
            Dict: 竞争格局分析
        """
        try:
            prompt = f"""请为{industry}行业的{product_category}产品类别生成{num_players}个参与者的竞争格局分析。

请以JSON格式返回：
{{
    "industry": "行业",
    "product_category": "产品类别",
    "num_players": {num_players},
    "market_overview": "市场概述",
    "competitive_map": [
        {{
            "company_name": "公司名称",
            "market_position": "市场地位",
            "strengths": ["优势1"],
            "weaknesses": ["弱点1"],
            "market_share": "市场份额"
        }}
    ],
    "market_share_breakdown": "市场份额明细",
    "competitive_trends": ["竞争趋势1"],
    "emerging_competitors": ["新兴竞争对手1"],
    "strategic_gaps": ["战略差距1"],
    "opportunities": ["机会1"],
    "threats": ["威胁1"],
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
                "industry": industry,
                "product_category": product_category,
                "num_players": num_players,
                **result,
            }

        except Exception as e:
            logger.error(f"生成竞争格局分析失败: {e}")
            return {
                "industry": industry,
                "product_category": product_category,
                "num_players": num_players,
                "market_overview": "",
                "competitive_map": [],
                "market_share_breakdown": "",
                "competitive_trends": [],
                "emerging_competitors": [],
                "strategic_gaps": [],
                "opportunities": [],
                "threats": [],
                "strategic_recommendations": [],
            }


competitive_landscape_analysis_generator_service = CompetitiveLandscapeAnalysisGeneratorService()
