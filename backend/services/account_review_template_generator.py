"""
Vox Account Review Template Generator Service 模块

账户审查模板生成服务
- 审查清单
- 绩效指标
- 行动计划
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class AccountReviewTemplateGeneratorService:
    """
    账户审查模板生成服务

    生成账户审查模板内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_account_review_template(
        self,
        account_name: str,
        review_period: str,
        num_sections: int = 5,
    ) -> Dict[str, Any]:
        """
        生成账户审查模板

        Args:
            account_name: 账户名称
            review_period: 审查周期
            num_sections: 部分数量

        Returns:
            Dict: 账户审查模板
        """
        try:
            prompt = f"""请为"{account_name}"生成{review_period}审查周期的{num_sections}部分账户审查模板。

请以JSON格式返回：
{{
    "account_name": "账户名称",
    "review_period": "审查周期",
    "num_sections": {num_sections},
    "executive_summary": "执行摘要",
    "account_overview": "账户概述",
    "kpi_performance": [
        {{
            "kpi": "KPI",
            "target": "目标",
            "actual": "实际",
            "variance": "差异"
        }}
    ],
    "accomplishments": ["成就1"],
    "challenges": ["挑战1"],
    "customer_feedback": "客户反馈",
    "action_items": [
        {{
            "item": "项目",
            "owner": "负责人",
            "due_date": "截止日期"
        }}
    ],
    "next_period_goals": ["下期目标1"],
    "resources_needed": ["所需资源1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "account_name": account_name,
                "review_period": review_period,
                "num_sections": num_sections,
                **result,
            }

        except Exception as e:
            logger.error(f"生成账户审查模板失败: {e}")
            return {
                "account_name": account_name,
                "review_period": review_period,
                "num_sections": num_sections,
                "executive_summary": "",
                "account_overview": "",
                "kpi_performance": [],
                "accomplishments": [],
                "challenges": [],
                "customer_feedback": "",
                "action_items": [],
                "next_period_goals": [],
                "resources_needed": [],
            }


account_review_template_generator_service = AccountReviewTemplateGeneratorService()