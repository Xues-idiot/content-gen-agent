"""
Vox Market Entry Analysis Generator Service 模块

市场进入分析生成服务
- 市场吸引力
- 进入壁垒
- 战略选择
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class MarketEntryAnalysisGeneratorService:
    """
    市场进入分析生成服务

    生成市场进入分析内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_market_entry_analysis(
        self,
        target_market: str,
        product_category: str,
        num_factors: int = 8,
    ) -> Dict[str, Any]:
        """
        生成市场进入分析

        Args:
            target_market: 目标市场
            product_category: 产品类别
            num_factors: 因素数量

        Returns:
            Dict: 市场进入分析
        """
        try:
            prompt = f"""请为{target_market}市场的{product_category}产品类别生成{num_factors}个因素的市场进入分析。

请以JSON格式返回：
{{
    "target_market": "目标市场",
    "product_category": "产品类别",
    "num_factors": {num_factors},
    "executive_summary": "执行摘要",
    "market_attractiveness": {{
        "market_size": "市场规模",
        "growth_rate": "增长率",
        "profitability": "盈利能力",
        "trend": "趋势"
    }},
    "entry_barriers": ["进入壁垒1"],
    "competitive_intensity": "竞争强度",
    "regulatory_environment": "监管环境",
    "customer_accessibility": "客户可达性",
    "entry_strategy_options": ["进入战略选项1"],
    "recommended_entry_mode": "推荐的进入模式",
    "risk_assessment": ["风险评估1"],
    "success_requirements": ["成功要求1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "target_market": target_market,
                "product_category": product_category,
                "num_factors": num_factors,
                **result,
            }

        except Exception as e:
            logger.error(f"生成市场进入分析失败: {e}")
            return {
                "target_market": target_market,
                "product_category": product_category,
                "num_factors": num_factors,
                "executive_summary": "",
                "market_attractiveness": {},
                "entry_barriers": [],
                "competitive_intensity": "",
                "regulatory_environment": "",
                "customer_accessibility": "",
                "entry_strategy_options": [],
                "recommended_entry_mode": "",
                "risk_assessment": [],
                "success_requirements": [],
            }


market_entry_analysis_generator_service = MarketEntryAnalysisGeneratorService()
