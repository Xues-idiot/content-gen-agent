"""
Vox Customer Retention Plan Generator Service 模块

客户保留计划生成服务
- 忠诚度计划
- 参与策略
- 流失预防
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CustomerRetentionPlanGeneratorService:
    """
    客户保留计划生成服务

    生成客户保留计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_customer_retention_plan(
        self,
        business_name: str,
        customer_segment: str,
        plan_type: str = "loyalty",
    ) -> Dict[str, Any]:
        """
        生成客户保留计划

        Args:
            business_name: 业务名称
            customer_segment: 客户细分
            plan_type: 计划类型

        Returns:
            Dict: 客户保留计划
        """
        try:
            prompt = f"""请为"{business_name}"的{customer_segment}客户生成{plan_type}类型的客户保留计划。

请以JSON格式返回：
{{
    "business_name": "业务名称",
    "customer_segment": "客户细分",
    "plan_type": "计划类型",
    "plan_overview": "计划概述",
    "loyalty_tiers": [
        {{
            "tier_name": "层级名称",
            "requirements": "要求",
            "benefits": ["好处1"]
        }}
    ],
    "reward_structure": {{
        "points_system": "积分系统",
        "redemption_options": ["兑换选项1"],
        "expiration_policy": "过期政策"
    }},
    "engagement_activities": ["参与活动1"],
    "churn_prevention": {{
        "early_warning_signs": ["早期预警信号1"],
        "intervention_tactics": ["干预策略1"],
        "win_back_offers": ["赢回优惠1"]
    }},
    "communication_plan": "沟通计划",
    "success_metrics": ["成功指标1"],
    "implementation_timeline": "实施时间线"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "business_name": business_name,
                "customer_segment": customer_segment,
                "plan_type": plan_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户保留计划失败: {e}")
            return {
                "business_name": business_name,
                "customer_segment": customer_segment,
                "plan_type": plan_type,
                "plan_overview": "",
                "loyalty_tiers": [],
                "reward_structure": {},
                "engagement_activities": [],
                "churn_prevention": {},
                "communication_plan": "",
                "success_metrics": [],
                "implementation_timeline": "",
            }


customer_retention_plan_generator_service = CustomerRetentionPlanGeneratorService()