"""
Vox Market Trend Report Generator Service 模块

市场趋势报告生成服务
- 行业趋势
- 市场分析
- 预测报告
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class MarketTrendReportGeneratorService:
    """
    市场趋势报告生成服务

    生成市场趋势报告内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_market_trend_report(
        self,
        industry: str,
        region: str = "全球",
        time_horizon: str = "2026",
    ) -> Dict[str, Any]:
        """
        生成市场趋势报告

        Args:
            industry: 行业
            region: 地区
            time_horizon: 时间范围

        Returns:
            Dict: 市场趋势报告
        """
        try:
            prompt = f"""请为"{industry}"行业生成{time_horizon}年{region}市场趋势报告。

请以JSON格式返回：
{{
    "industry": "行业",
    "region": "地区",
    "time_horizon": "时间范围",
    "executive_summary": "执行摘要",
    "market_size": "市场规模",
    "growth_rate": "增长率",
    "key_trends": ["关键趋势1"],
    "driving_factors": ["驱动因素1"],
    "challenges": ["挑战1"],
    "emerging_technologies": ["新兴技术1"],
    "consumer_behavior_changes": ["消费者行为变化1"],
    "competitive_landscape": "竞争格局",
    "investment_opportunities": ["投资机会1"],
    "forecast": "预测",
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
                "industry": industry,
                "region": region,
                "time_horizon": time_horizon,
                **result,
            }

        except Exception as e:
            logger.error(f"生成市场趋势报告失败: {e}")
            return {
                "industry": industry,
                "region": region,
                "time_horizon": time_horizon,
                "executive_summary": "",
                "market_size": "",
                "growth_rate": "",
                "key_trends": [],
                "driving_factors": [],
                "challenges": [],
                "emerging_technologies": [],
                "consumer_behavior_changes": [],
                "competitive_landscape": "",
                "investment_opportunities": [],
                "forecast": "",
                "recommendations": [],
            }


market_trend_report_generator_service = MarketTrendReportGeneratorService()