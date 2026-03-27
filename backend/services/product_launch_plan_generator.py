"""
Vox Product Launch Plan Generator Service 模块

产品发布计划生成服务
- 发布时间线
- 营销策略
- 成功指标
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductLaunchPlanGeneratorService:
    """
    产品发布计划生成服务

    生成产品发布计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_product_launch_plan(
        self,
        product_name: str,
        launch_date: str,
        num_phases: int = 4,
    ) -> Dict[str, Any]:
        """
        生成产品发布计划

        Args:
            product_name: 产品名称
            launch_date: 发布日期
            num_phases: 阶段数量

        Returns:
            Dict: 产品发布计划
        """
        try:
            prompt = f"""请为"{product_name}"生成发布日期为{launch_date}的{num_phases}阶段产品发布计划。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "launch_date": "发布日期",
    "num_phases": {num_phases},
    "launch_strategy": "发布策略",
    "phases": [
        {{
            "phase_name": "阶段名称",
            "start_date": "开始日期",
            "end_date": "结束日期",
            "objectives": ["目标1"],
            "activities": ["活动1"],
            "deliverables": ["可交付成果1"]
        }}
    ],
    "marketing_activities": [
        {{
            "activity_type": "活动类型",
            "channel": "渠道",
            "timeline": "时间线"
        }}
    ],
    "budget_allocation": "预算分配",
    "success_metrics": ["成功指标1"],
    "risk_assessment": "风险评估",
    "contingency_plans": ["应急计划1"]
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
                "num_phases": num_phases,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品发布计划失败: {e}")
            return {
                "product_name": product_name,
                "launch_date": launch_date,
                "num_phases": num_phases,
                "launch_strategy": "",
                "phases": [],
                "marketing_activities": [],
                "budget_allocation": "",
                "success_metrics": [],
                "risk_assessment": "",
                "contingency_plans": [],
            }


product_launch_plan_generator_service = ProductLaunchPlanGeneratorService()
