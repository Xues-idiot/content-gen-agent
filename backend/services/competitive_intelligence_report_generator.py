"""
Vox Competitive Intelligence Report Generator Service 模块

竞争情报报告生成服务
- 竞争对手分析
- 市场定位
- 战略建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CompetitiveIntelligenceReportGeneratorService:
    """
    竞争情报报告生成服务

    生成竞争情报报告内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_competitive_intelligence_report(
        self,
        main_competitor: str,
        industry: str,
        num_areas: int = 6,
    ) -> Dict[str, Any]:
        """
        生成竞争情报报告

        Args:
            main_competitor: 主要竞争对手
            industry: 行业
            num_areas: 分析领域数量

        Returns:
            Dict: 竞争情报报告
        """
        try:
            prompt = f"""请为{main_competitor}生成{industry}行业的竞争情报报告，包含{num_areas}个分析领域。

请以JSON格式返回：
{{
    "main_competitor": "主要竞争对手",
    "industry": "行业",
    "num_areas": {num_areas},
    "executive_summary": "执行摘要",
    "company_overview": {{
        "founded": "成立时间",
        "headquarters": "总部",
        "leadership": "领导层",
        "funding": "融资情况"
    }},
    "product_analysis": {{
        "key_products": ["主要产品1"],
        "pricing_strategy": "定价策略",
        "differentiation": "差异化"
    }},
    "market_position": {{
        "market_share": "市场份额",
        "target_segments": ["目标细分1"],
        "geographic_presence": "地域存在"
    }},
    "swot_analysis": {{
        "strengths": ["优势1"],
        "weaknesses": ["弱点1"],
        "opportunities": ["机会1"],
        "threats": ["威胁1"]
    }},
    "recent_moves": ["近期动向1"],
    "threat_assessment": "威胁评估",
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
                "main_competitor": main_competitor,
                "industry": industry,
                "num_areas": num_areas,
                **result,
            }

        except Exception as e:
            logger.error(f"生成竞争情报报告失败: {e}")
            return {
                "main_competitor": main_competitor,
                "industry": industry,
                "num_areas": num_areas,
                "executive_summary": "",
                "company_overview": {},
                "product_analysis": {},
                "market_position": {},
                "swot_analysis": {},
                "recent_moves": [],
                "threat_assessment": "",
                "strategic_recommendations": [],
            }


competitive_intelligence_report_generator_service = CompetitiveIntelligenceReportGeneratorService()
