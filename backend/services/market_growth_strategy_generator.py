"""
Vox Market Growth Strategy Generator Service 模块

市场增长策略生成服务
- 增长机会
- 战略路径
- 资源需求
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class MarketGrowthStrategyGeneratorService:
    """
    市场增长策略生成服务

    生成市场增长策略内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_market_growth_strategy(
        self,
        business_unit: str,
        target_market: str,
        num_initiatives: int = 6,
    ) -> Dict[str, Any]:
        """
        生成市场增长策略

        Args:
            business_unit: 业务单元
            target_market: 目标市场
            num_initiatives: 举措数量

        Returns:
            Dict: 市场增长策略
        """
        try:
            prompt = f"""请为{business_unit}业务单元在{target_market}目标市场生成{num_initiatives}个举措的市场增长策略。

请以JSON格式返回：
{{
    "business_unit": "业务单元",
    "target_market": "目标市场",
    "num_initiatives": {num_initiatives},
    "executive_summary": "执行摘要",
    "market_opportunity": "市场机会",
    "growth_levers": ["增长杠杆1"],
    "strategic_initiatives": [
        {{
            "initiative_name": "举措名称",
            "description": "描述",
            "timeline": "时间线",
            "resource_requirements": "资源需求",
            "expected_impact": "预期影响"
        }}
    ],
    "investment_requirements": "投资需求",
    "risk_assessment": "风险评估",
    "success_metrics": ["成功指标1"],
    "implementation_priorities": ["实施优先级1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "business_unit": business_unit,
                "target_market": target_market,
                "num_initiatives": num_initiatives,
                **result,
            }

        except Exception as e:
            logger.error(f"生成市场增长策略失败: {e}")
            return {
                "business_unit": business_unit,
                "target_market": target_market,
                "num_initiatives": num_initiatives,
                "executive_summary": "",
                "market_opportunity": "",
                "growth_levers": [],
                "strategic_initiatives": [],
                "investment_requirements": "",
                "risk_assessment": "",
                "success_metrics": [],
                "implementation_priorities": [],
            }


market_growth_strategy_generator_service = MarketGrowthStrategyGeneratorService()
