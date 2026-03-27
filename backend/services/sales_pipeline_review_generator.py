"""
Vox Sales Pipeline Review Generator Service 模块

销售管道审查生成服务
- 管道健康
- 预测准确性
- 改进建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SalesPipelineReviewGeneratorService:
    """
    销售管道审查生成服务

    生成销售管道审查内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_sales_pipeline_review(
        self,
        review_period: str,
        sales_team: str,
        num_stages: int = 6,
    ) -> Dict[str, Any]:
        """
        生成销售管道审查

        Args:
            review_period: 审查周期
            sales_team: 销售团队
            num_stages: 阶段数量

        Returns:
            Dict: 销售管道审查
        """
        try:
            prompt = f"""请为{sales_team}团队生成{review_period}的{num_stages}个阶段的销售管道审查。

请以JSON格式返回：
{{
    "review_period": "审查周期",
    "sales_team": "销售团队",
    "num_stages": {num_stages},
    "pipeline_overview": {{
        "total_opportunities": "总机会数",
        "total_value": "总价值",
        "weighted_value": "加权价值",
        "average_deal_size": "平均交易规模"
    }},
    "stage_analysis": [
        {{
            "stage_name": "阶段名称",
            "opportunity_count": "机会数",
            "stage_value": "阶段价值",
            "conversion_rate": "转化率",
            "avg_time_in_stage": "平均停留时间"
        }}
    ],
    "forecast_accuracy": "预测准确性",
    "stalled_deals": {{
        "count": "数量",
        "value": "价值",
        "main_reasons": ["主要原因1"]
    }},
    "pipeline_health_indicators": ["管道健康指标1"],
    "risks_opportunities": ["风险/机会1"],
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
                "review_period": review_period,
                "sales_team": sales_team,
                "num_stages": num_stages,
                **result,
            }

        except Exception as e:
            logger.error(f"生成销售管道审查失败: {e}")
            return {
                "review_period": review_period,
                "sales_team": sales_team,
                "num_stages": num_stages,
                "pipeline_overview": {},
                "stage_analysis": [],
                "forecast_accuracy": "",
                "stalled_deals": {},
                "pipeline_health_indicators": [],
                "risks_opportunities": [],
                "recommended_actions": [],
            }


sales_pipeline_review_generator_service = SalesPipelineReviewGeneratorService()
