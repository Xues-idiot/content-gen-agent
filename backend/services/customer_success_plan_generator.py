"""
Vox Customer Success Plan Generator Service 模块

客户成功计划生成服务
- 成功标准
- 参与计划
- 扩展机会
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CustomerSuccessPlanGeneratorService:
    """
    客户成功计划生成服务

    生成客户成功计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_customer_success_plan(
        self,
        customer_name: str,
        product_service: str,
        num_milestones: int = 6,
    ) -> Dict[str, Any]:
        """
        生成客户成功计划

        Args:
            customer_name: 客户名称
            product_service: 产品/服务
            num_milestones: 里程碑数量

        Returns:
            Dict: 客户成功计划
        """
        try:
            prompt = f"""请为"{customer_name}"的{product_service}生成{num_milestones}个里程碑的客户成功计划。

请以JSON格式返回：
{{
    "customer_name": "客户名称",
    "product_service": "产品/服务",
    "num_milestones": {num_milestones},
    "success_definitions": ["成功定义1"],
    "milestones": [
        {{
            "milestone_name": "里程碑名称",
            "target_date": "目标日期",
            "success_criteria": "成功标准",
            "required_actions": ["所需行动1"],
            "owner": "负责人"
        }}
    ],
    "engagement_activities": [
        {{
            "activity_type": "活动类型",
            "frequency": "频率",
            "purpose": "目的"
        }}
    ],
    "health_check_metrics": ["健康检查指标1"],
    "expansion_opportunities": ["扩展机会1"],
    "risk_mitigation": "风险缓解",
    "escalation_process": "升级流程"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "customer_name": customer_name,
                "product_service": product_service,
                "num_milestones": num_milestones,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户成功计划失败: {e}")
            return {
                "customer_name": customer_name,
                "product_service": product_service,
                "num_milestones": num_milestones,
                "success_definitions": [],
                "milestones": [],
                "engagement_activities": [],
                "health_check_metrics": [],
                "expansion_opportunities": [],
                "risk_mitigation": "",
                "escalation_process": "",
            }


customer_success_plan_generator_service = CustomerSuccessPlanGeneratorService()
