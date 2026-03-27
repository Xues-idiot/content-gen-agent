"""
Vox Service Proposal Generator Service 模块

服务提案生成服务
- 项目方案
- 报价明细
- 实施计划
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ServiceProposalGeneratorService:
    """
    服务提案生成服务

    生成服务提案内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_service_proposal(
        self,
        client_name: str,
        service_type: str,
        project_scope: str,
    ) -> Dict[str, Any]:
        """
        生成服务提案

        Args:
            client_name: 客户名称
            service_type: 服务类型
            project_scope: 项目范围

        Returns:
            Dict: 服务提案
        """
        try:
            prompt = f"""请为"{client_name}"生成{service_type}服务提案（范围：{project_scope}）。

请以JSON格式返回：
{{
    "proposal_title": "提案标题",
    "client_name": "客户名称",
    "service_type": "服务类型",
    "project_scope": "项目范围",
    "executive_summary": "执行摘要",
    "client_background": "客户背景",
    "problem_statement": "问题陈述",
    "proposed_solution": {{
        "approach": "方法",
        "methodology": "方法论",
        "key_components": ["关键组件1"]
    }},
    "deliverables": [
        {{
            "deliverable": "交付物",
            "description": "描述",
            "timeline": "时间线"
        }}
    ],
    "timeline": {{
        "total_duration": "总时长",
        "phases": [
            {{
                "phase": "阶段",
                "duration": "时长",
                "start_date": "开始日期",
                "end_date": "结束日期"
            }}
        ]
    }},
    "pricing": {{
        "total_cost": "总成本",
        "currency": "货币",
        "breakdown": [
            {{
                "item": "项目",
                "cost": "成本",
                "notes": "备注"
            }}
        ],
        "payment_terms": "付款条款"
    }},
    "team": [
        {{
            "name": "姓名",
            "role": "角色",
            "bio": "简介"
        }}
    ],
    "case_studies": ["案例研究1"],
    "client_testimonials": ["客户推荐1"],
    "terms_and_conditions": ["条款和条件1"],
    "next_steps": "下一步",
    "validity_period": "有效期",
    "signature_block": "签名栏"
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
                "project_scope": project_scope,
                **result,
            }

        except Exception as e:
            logger.error(f"生成服务提案失败: {e}")
            return {
                "client_name": client_name,
                "service_type": service_type,
                "project_scope": project_scope,
                "proposal_title": "",
                "executive_summary": "",
                "client_background": "",
                "problem_statement": "",
                "proposed_solution": {},
                "deliverables": [],
                "timeline": {},
                "pricing": {},
                "team": [],
                "case_studies": [],
                "client_testimonials": [],
                "terms_and_conditions": [],
                "next_steps": "",
                "validity_period": "",
                "signature_block": "",
            }


service_proposal_generator_service = ServiceProposalGeneratorService()