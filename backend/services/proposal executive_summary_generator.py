"""
Vox Proposal Executive Summary Generator Service 模块

提案执行摘要生成服务
- 项目概述
- 关键条款
- 预期成果
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProposalExecutiveSummaryGeneratorService:
    """
    提案执行摘要生成服务

    生成提案执行摘要内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_proposal_executive_summary(
        self,
        proposal_title: str,
        client_name: str,
        proposal_value: str,
    ) -> Dict[str, Any]:
        """
        生成提案执行摘要

        Args:
            proposal_title: 提案标题
            client_name: 客户名称
            proposal_value: 提案价值

        Returns:
            Dict: 提案执行摘要
        """
        try:
            prompt = f"""请为"{proposal_title}"（客户：{client_name}，价值：{proposal_value}）生成提案执行摘要。

请以JSON格式返回：
{{
    "proposal_title": "提案标题",
    "client_name": "客户名称",
    "proposal_value": "提案价值",
    "summary": "摘要",
    "objectives": ["目标1"],
    "scope_overview": "范围概述",
    "key_terms": ["关键条款1"],
    "timeline_highlights": "时间线亮点",
    "expected_outcomes": ["预期成果1"],
    "why_choose_us": "为什么选择我们",
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
                "proposal_title": proposal_title,
                "client_name": client_name,
                "proposal_value": proposal_value,
                **result,
            }

        except Exception as e:
            logger.error(f"生成提案执行摘要失败: {e}")
            return {
                "proposal_title": proposal_title,
                "client_name": client_name,
                "proposal_value": proposal_value,
                "summary": "",
                "objectives": [],
                "scope_overview": "",
                "key_terms": [],
                "timeline_highlights": "",
                "expected_outcomes": [],
                "why_choose_us": "",
                "next_steps": [],
            }


proposal_executive_summary_generator_service = ProposalExecutiveSummaryGeneratorService()