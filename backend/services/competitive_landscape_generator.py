"""
Vox Competitive Landscape Generator Service 模块

竞争格局分析生成服务
- 竞争对手
- 市场定位
- 差异化策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CompetitiveLandscapeGeneratorService:
    """
    竞争格局分析生成服务

    生成竞争格局分析内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_competitive_landscape(
        self,
        company_name: str,
        industry: str,
        main_competitors: List[str] = None,
    ) -> Dict[str, Any]:
        """
        生成竞争格局分析

        Args:
            company_name: 公司名称
            industry: 行业
            main_competitors: 主要竞争对手

        Returns:
            Dict: 竞争格局分析
        """
        if main_competitors is None:
            main_competitors = ["竞争对手A", "竞争对手B"]

        try:
            competitors_str = ", ".join(main_competitors)
            prompt = f"""请为"{company_name}"（{industry}行业）生成竞争格局分析。

主要竞争对手：{competitors_str}

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "industry": "行业",
    "main_competitors": ["竞争对手1"],
    "market_overview": "市场概述",
    "competitor_analysis": [
        {{
            "competitor_name": "竞争对手名称",
            "market_share": "市场份额",
            "strengths": ["优势1"],
            "weaknesses": ["劣势1"],
            "key_products": ["主要产品1"],
            "pricing_strategy": "定价策略",
            "market_position": "市场定位"
        }}
    ],
    "competitive_advantages": ["竞争优势1"],
    "market_gaps": ["市场空白1"],
    "threats": ["威胁1"],
    "recommendations": ["建议1"]
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
                "industry": industry,
                "main_competitors": main_competitors,
                **result,
            }

        except Exception as e:
            logger.error(f"生成竞争格局分析失败: {e}")
            return {
                "company_name": company_name,
                "industry": industry,
                "main_competitors": main_competitors,
                "market_overview": "",
                "competitor_analysis": [],
                "competitive_advantages": [],
                "market_gaps": [],
                "threats": [],
                "recommendations": [],
            }


competitive_landscape_generator_service = CompetitiveLandscapeGeneratorService()