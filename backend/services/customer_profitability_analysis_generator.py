"""
Vox Customer Profitability Analysis Generator Service 模块

客户盈利能力分析生成服务
- 利润分层
- 成本分析
- 优化策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CustomerProfitabilityAnalysisGeneratorService:
    """
    客户盈利能力分析生成服务

    生成客户盈利能力分析内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_customer_profitability_analysis(
        self,
        analysis_period: str,
        segment_by: str,
        num_segments: int = 4,
    ) -> Dict[str, Any]:
        """
        生成客户盈利能力分析

        Args:
            analysis_period: 分析周期
            segment_by: 细分维度
            num_segments: 细分数量

        Returns:
            Dict: 客户盈利能力分析
        """
        try:
            prompt = f"""请为{analysis_period}期间生成按{segment_by}细分的{num_segments}个客户群体的盈利能力分析。

请以JSON格式返回：
{{
    "analysis_period": "分析周期",
    "segment_by": "细分维度",
    "num_segments": {num_segments},
    "executive_summary": "执行摘要",
    "segment_analysis": [
        {{
            "segment_name": "细分名称",
            "customer_count": "客户数量",
            "total_revenue": "总收入",
            "total_cost": "总成本",
            "profit_margin": "利润率",
            "avg_revenue_per_customer": "每客户平均收入"
        }}
    ],
    "profit_distribution": "利润分布",
    "cost_drivers": ["成本驱动因素1"],
    "high_value_characteristics": ["高价值特征1"],
    "low_value_characteristics": ["低价值特征1"],
    "optimization_strategies": ["优化策略1"],
    "recommended_actions": ["推荐行动1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "analysis_period": analysis_period,
                "segment_by": segment_by,
                "num_segments": num_segments,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户盈利能力分析失败: {e}")
            return {
                "analysis_period": analysis_period,
                "segment_by": segment_by,
                "num_segments": num_segments,
                "executive_summary": "",
                "segment_analysis": [],
                "profit_distribution": "",
                "cost_drivers": [],
                "high_value_characteristics": [],
                "low_value_characteristics": [],
                "optimization_strategies": [],
                "recommended_actions": [],
            }


customer_profitability_analysis_generator_service = CustomerProfitabilityAnalysisGeneratorService()
