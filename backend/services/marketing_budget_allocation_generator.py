"""
Vox Marketing Budget Allocation Generator Service 模块

营销预算分配生成服务
- 渠道分配
- 季度计划
- ROI预期
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class MarketingBudgetAllocationGeneratorService:
    """
    营销预算分配生成服务

    生成营销预算分配内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_marketing_budget_allocation(
        self,
        total_budget: str,
        planning_period: str,
        num_channels: int = 6,
    ) -> Dict[str, Any]:
        """
        生成营销预算分配

        Args:
            total_budget: 总预算
            planning_period: 计划周期
            num_channels: 渠道数量

        Returns:
            Dict: 营销预算分配
        """
        try:
            prompt = f"""请为{total_budget}总预算生成{planning_period}的{num_channels}个渠道的营销预算分配。

请以JSON格式返回：
{{
    "total_budget": "总预算",
    "planning_period": "计划周期",
    "num_channels": {num_channels},
    "allocation_summary": "分配摘要",
    "channel_allocations": [
        {{
            "channel": "渠道",
            "budget_percentage": "预算百分比",
            "budget_amount": "预算金额",
            "expected_roi": "预期ROI",
            "strategic_rationale": "战略理由"
        }}
    ],
    "quarterly_breakdown": [
        {{
            "quarter": "季度",
            "total_spend": "总支出",
            "key_activities": ["关键活动1"]
        }}
    ],
    "contingency_fund": "应急资金",
    "performance_benchmarks": ["性能基准1"],
    "optimization_strategy": "优化策略"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "total_budget": total_budget,
                "planning_period": planning_period,
                "num_channels": num_channels,
                **result,
            }

        except Exception as e:
            logger.error(f"生成营销预算分配失败: {e}")
            return {
                "total_budget": total_budget,
                "planning_period": planning_period,
                "num_channels": num_channels,
                "allocation_summary": "",
                "channel_allocations": [],
                "quarterly_breakdown": [],
                "contingency_fund": "",
                "performance_benchmarks": [],
                "optimization_strategy": "",
            }


marketing_budget_allocation_generator_service = MarketingBudgetAllocationGeneratorService()
