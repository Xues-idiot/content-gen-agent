"""
Vox Sales RFP Response Generator Service 模块

销售RFP回复生成服务
- 提案内容
- 能力展示
- 评分标准
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SalesRFPResponseGeneratorService:
    """
    销售RFP回复生成服务

    生成销售RFP回复内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_sales_rfp_response(
        self,
        rfp_title: str,
        client_name: str,
        solution_type: str,
    ) -> Dict[str, Any]:
        """
        生成销售RFP回复

        Args:
            rfp_title: RFP标题
            client_name: 客户名称
            solution_type: 解决方案类型

        Returns:
            Dict: 销售RFP回复
        """
        try:
            prompt = f"""请为"{client_name}"的"{rfp_title}"生成{solution_type}解决方案的RFP回复。

请以JSON格式返回：
{{
    "rfp_title": "RFP标题",
    "client_name": "客户名称",
    "solution_type": "解决方案类型",
    "executive_summary": "执行摘要",
    "understanding_of_needs": "对需求的理解",
    "proposed_solution": {{
        "approach": "方法",
        "methodology": "方法论",
        "scope": "范围",
        "timeline": "时间线"
    }},
    "company_credentials": {{
        "company_overview": "公司概述",
        "relevant_experience": "相关经验",
        "client_testimonials": ["客户推荐1"]
    }},
    "team_qualifications": [
        {{
            "role": "角色",
            "qualifications": "资格"
        }}
    ],
    "case_studies": ["案例研究1"],
    "pricing_structure": "定价结构",
    "implementation_plan": "实施计划",
    "support_maintenance": "支持与维护",
    "terms_conditions": "条款与条件",
    "references": "参考",
    "next_steps": "下一步"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "rfp_title": rfp_title,
                "client_name": client_name,
                "solution_type": solution_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成销售RFP回复失败: {e}")
            return {
                "rfp_title": rfp_title,
                "client_name": client_name,
                "solution_type": solution_type,
                "executive_summary": "",
                "understanding_of_needs": "",
                "proposed_solution": {},
                "company_credentials": {},
                "team_qualifications": [],
                "case_studies": [],
                "pricing_structure": "",
                "implementation_plan": "",
                "support_maintenance": "",
                "terms_conditions": "",
                "references": "",
                "next_steps": "",
            }


sales_rfp_response_generator_service = SalesRFPResponseGeneratorService()