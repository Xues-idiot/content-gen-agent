"""
Vox Client Proposal Generator Service 模块

客户提案生成服务
- 方案概述
- 报价明细
- 实施计划
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ClientProposalGeneratorService:
    """
    客户提案生成服务

    生成客户提案内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_client_proposal(
        self,
        client_name: str,
        service_type: str,
        project_scale: str = "medium",
    ) -> Dict[str, Any]:
        """
        生成客户提案

        Args:
            client_name: 客户名称
            service_type: 服务类型
            project_scale: 项目规模

        Returns:
            Dict: 客户提案
        """
        try:
            prompt = f"""请为"{client_name}"生成{service_type}服务提案（规模：{project_scale}）。

请以JSON格式返回：
{{
    "client_name": "客户名称",
    "service_type": "服务类型",
    "project_scale": "项目规模",
    "proposal_title": "提案标题",
    "executive_summary": "执行摘要",
    "proposed_solution": "建议方案",
    "scope_of_work": ["工作范围1"],
    "timeline": "时间线",
    "pricing_breakdown": [
        {{
            "item": "项目",
            "amount": 金额
        }}
    ],
    "payment_terms": "付款条款",
    "terms_and_conditions": ["条款1"],
    "next_steps": ["下一步1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "client_name": client_name,
                "service_type": service_type,
                "project_scale": project_scale,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户提案失败: {e}")
            return {
                "client_name": client_name,
                "service_type": service_type,
                "project_scale": project_scale,
                "proposal_title": "",
                "executive_summary": "",
                "proposed_solution": "",
                "scope_of_work": [],
                "timeline": "",
                "pricing_breakdown": [],
                "payment_terms": "",
                "terms_and_conditions": [],
                "next_steps": [],
            }


client_proposal_generator_service = ClientProposalGeneratorService()