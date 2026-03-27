"""
Vox Product Launch Checklist Generator Service 模块

产品发布清单生成服务
- 发布前检查
- 准备事项
- 风险确认
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductLaunchChecklistGeneratorService:
    """
    产品发布清单生成服务

    生成产品发布清单内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_launch_checklist(
        self,
        product_name: str,
        launch_date: str,
        launch_type: str = "new product",
    ) -> Dict[str, Any]:
        """
        生成产品发布清单

        Args:
            product_name: 产品名称
            launch_date: 发布日期
            launch_type: 发布类型

        Returns:
            Dict: 产品发布清单
        """
        try:
            prompt = f"""请为"{product_name}"（发布日期：{launch_date}，类型：{launch_type}）生成发布清单。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "launch_date": "发布日期",
    "launch_type": "发布类型",
    "overview": "概述",
    "pre_launch_checklist": [
        {{
            "category": "类别",
            "items": [
                {{
                    "item": "事项",
                    "status": "状态",
                    "owner": "负责人",
                    "due_date": "截止日期",
                    "notes": "备注"
                }}
            ]
        }}
    ],
    "launch_day_checklist": ["发布日检查事项1"],
    "post_launch_checklist": ["发布后检查事项1"],
    "risk_items": ["风险项1"],
    "escalation_plan": "升级计划",
    "success_criteria": "成功标准"
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
                "launch_type": launch_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品发布清单失败: {e}")
            return {
                "product_name": product_name,
                "launch_date": launch_date,
                "launch_type": launch_type,
                "overview": "",
                "pre_launch_checklist": [],
                "launch_day_checklist": [],
                "post_launch_checklist": [],
                "risk_items": [],
                "escalation_plan": "",
                "success_criteria": "",
            }


product_launch_checklist_generator_service = ProductLaunchChecklistGeneratorService()