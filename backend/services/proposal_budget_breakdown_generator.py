"""
Vox Proposal Budget Breakdown Generator Service 模块

提案预算明细生成服务
- 成本分类
- 定价明细
- ROI分析
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProposalBudgetBreakdownGeneratorService:
    """
    提案预算明细生成服务

    生成提案预算明细内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_proposal_budget_breakdown(
        self,
        project_name: str,
        total_budget: str,
        num_line_items: int = 10,
    ) -> Dict[str, Any]:
        """
        生成提案预算明细

        Args:
            project_name: 项目名称
            total_budget: 总预算
            num_line_items: 明细项目数量

        Returns:
            Dict: 提案预算明细
        """
        try:
            prompt = f"""请为"{project_name}"生成{total_budget}总预算的{num_line_items}项提案预算明细。

请以JSON格式返回：
{{
    "project_name": "项目名称",
    "total_budget": "总预算",
    "num_line_items": {num_line_items},
    "budget_summary": "预算摘要",
    "line_items": [
        {{
            "item_number": 1,
            "item_name": "项目名称",
            "description": "描述",
            "quantity": "数量",
            "unit_price": "单价",
            "total": "总计"
        }}
    ],
    "cost_categories": ["成本类别1"],
    "payment_schedule": "付款计划",
    "roi_analysis": "ROI分析",
    "cost_savings": "成本节省",
    "terms_conditions": "条款条件"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "project_name": project_name,
                "total_budget": total_budget,
                "num_line_items": num_line_items,
                **result,
            }

        except Exception as e:
            logger.error(f"生成提案预算明细失败: {e}")
            return {
                "project_name": project_name,
                "total_budget": total_budget,
                "num_line_items": num_line_items,
                "budget_summary": "",
                "line_items": [],
                "cost_categories": [],
                "payment_schedule": "",
                "roi_analysis": "",
                "cost_savings": "",
                "terms_conditions": "",
            }


proposal_budget_breakdown_generator_service = ProposalBudgetBreakdownGeneratorService()