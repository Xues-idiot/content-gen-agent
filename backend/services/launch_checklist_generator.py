"""
Vox Launch Checklist Generator Service 模块

产品发布检查清单生成服务
- 发布前检查
- 跨部门协调
- 风险预案
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class LaunchChecklistGeneratorService:
    """
    产品发布检查清单生成服务

    生成产品发布检查清单内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_launch_checklist(
        self,
        product_name: str,
        launch_type: str = "new product",
        team_size: str = "small",
    ) -> Dict[str, Any]:
        """
        生成产品发布检查清单

        Args:
            product_name: 产品名称
            launch_type: 发布类型
            team_size: 团队规模

        Returns:
            Dict: 产品发布检查清单
        """
        try:
            prompt = f"""请为"{product_name}"生成{launch_type}类型的发布检查清单（团队规模：{team_size}）。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "launch_type": "发布类型",
    "team_size": "团队规模",
    "launch_date": "发布日期",
    "pre_launch_checklist": [
        {{
            "category": "类别",
            "item": "项目",
            "responsible": "负责人",
            "due_date": "截止日期",
            "status": "状态"
        }}
    ],
    "marketing_preparation": ["营销准备1"],
    "sales_enablement": ["销售赋能1"],
    "customer_support_setup": ["客户支持设置1"],
    "technical_requirements": ["技术要求1"],
    "legal_compliance": ["法律合规1"],
    "internal_announcements": ["内部公告1"],
    "launch_day_checklist": ["发布日检查清单1"],
    "post_launch_followup": ["发布后跟进1"],
    "risk_contingencies": ["风险应急预案1"]
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
                "launch_type": launch_type,
                "team_size": team_size,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品发布检查清单失败: {e}")
            return {
                "product_name": product_name,
                "launch_type": launch_type,
                "team_size": team_size,
                "launch_date": "",
                "pre_launch_checklist": [],
                "marketing_preparation": [],
                "sales_enablement": [],
                "customer_support_setup": [],
                "technical_requirements": [],
                "legal_compliance": [],
                "internal_announcements": [],
                "launch_day_checklist": [],
                "post_launch_followup": [],
                "risk_contingencies": [],
            }


launch_checklist_generator_service = LaunchChecklistGeneratorService()