"""
Vox Customer Onboarding Checklist Generator Service 模块

客户入职检查清单生成服务
- 入职步骤
- 资源链接
- 成功标准
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CustomerOnboardingChecklistGeneratorService:
    """
    客户入职检查清单生成服务

    生成客户入职检查清单内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_customer_onboarding_checklist(
        self,
        product_name: str,
        customer_type: str,
        onboarding_duration: str = "7 days",
    ) -> Dict[str, Any]:
        """
        生成客户入职检查清单

        Args:
            product_name: 产品名称
            customer_type: 客户类型
            onboarding_duration: 入职持续时间

        Returns:
            Dict: 客户入职检查清单
        """
        try:
            prompt = f"""请为"{product_name}"生成{customer_type}客户的{onboarding_duration}入职检查清单。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "customer_type": "客户类型",
    "onboarding_duration": "入职持续时间",
    "overview": "概述",
    "checklist_items": [
        {{
            "day": "天",
            "task": "任务",
            "description": "描述",
            "resources": ["资源1"],
            "completed": false
        }}
    ],
    "key_milestones": ["关键里程碑1"],
    "required_training": ["必需培训1"],
    "optional_resources": ["可选资源1"],
    "success_criteria": "成功标准",
    "support_contacts": "支持联系人"
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
                "customer_type": customer_type,
                "onboarding_duration": onboarding_duration,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户入职检查清单失败: {e}")
            return {
                "product_name": product_name,
                "customer_type": customer_type,
                "onboarding_duration": onboarding_duration,
                "overview": "",
                "checklist_items": [],
                "key_milestones": [],
                "required_training": [],
                "optional_resources": [],
                "success_criteria": "",
                "support_contacts": "",
            }


customer_onboarding_checklist_generator_service = CustomerOnboardingChecklistGeneratorService()