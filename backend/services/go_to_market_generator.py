"""
Vox Go-To-Market Generator Service 模块

市场推广计划生成服务
- 上市策略
- 推广计划
- 渠道布局
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class GoToMarketGeneratorService:
    """
    市场推广计划生成服务

    生成市场推广计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_go_to_market(
        self,
        product_name: str,
        launch_date: str,
        target_market: str,
    ) -> Dict[str, Any]:
        """
        生成市场推广计划

        Args:
            product_name: 产品名称
            launch_date: 发布日期
            target_market: 目标市场

        Returns:
            Dict: 市场推广计划
        """
        try:
            prompt = f"""请为"{product_name}"生成上市计划（发布日期：{launch_date}，目标市场：{target_market}）。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "launch_date": "发布日期",
    "target_market": "目标市场",
    "executive_summary": "执行摘要",
    "market_analysis": "市场分析",
    "target_customer": "目标客户",
    "competitive_positioning": "竞争定位",
    "pricing_strategy": "定价策略",
    "launch_phases": [
        {{
            "phase": "阶段",
            "timeline": "时间线",
            "activities": ["活动1"],
            "success_metrics": "成功指标"
        }}
    ],
    "marketing_channels": ["营销渠道1"],
    "promotional_tactics": ["推广策略1"],
    "sales_enablement": "销售支持",
    "budget_allocation": "预算分配",
    "risk_assessment": "风险评估",
    "success_metrics": "成功指标"
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
                "launch_date": launch_date,
                "target_market": target_market,
                **result,
            }

        except Exception as e:
            logger.error(f"生成市场推广计划失败: {e}")
            return {
                "product_name": product_name,
                "launch_date": launch_date,
                "target_market": target_market,
                "executive_summary": "",
                "market_analysis": "",
                "target_customer": "",
                "competitive_positioning": "",
                "pricing_strategy": "",
                "launch_phases": [],
                "marketing_channels": [],
                "promotional_tactics": [],
                "sales_enablement": "",
                "budget_allocation": "",
                "risk_assessment": "",
                "success_metrics": "",
            }


go_to_market_generator_service = GoToMarketGeneratorService()