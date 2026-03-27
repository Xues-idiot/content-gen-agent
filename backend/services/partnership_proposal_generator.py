"""
Vox Partnership Proposal Generator Service 模块

合作关系提案生成服务
- 合作方案
- 互利共赢
- 实施计划
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PartnershipProposalGeneratorService:
    """
    合作关系提案生成服务

    生成合作关系提案内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_partnership_proposal(
        self,
        your_brand: str,
        potential_partner: str,
        partnership_type: str = "cross-promotion",
    ) -> Dict[str, Any]:
        """
        生成合作关系提案

        Args:
            your_brand: 你的品牌
            potential_partner: 潜在合作伙伴
            partnership_type: 合作类型

        Returns:
            Dict: 合作关系提案
        """
        try:
            prompt = f"""请为"{your_brand}"与"{potential_partner}"生成{partnership_type}合作提案。

请以JSON格式返回：
{{
    "your_brand": "你的品牌",
    "potential_partner": "潜在合作伙伴",
    "partnership_type": "合作类型",
    "proposal_title": "提案标题",
    "partnership_summary": "合作概要",
    "mutual_benefits": [" mutual benefit 1"],
    "collaboration_areas": ["合作领域1"],
    "proposed_activities": ["建议活动1"],
    "timeline": "时间线",
    "resource_commitment": "资源投入",
    "expected_outcomes": ["预期成果1"],
    "success_metrics": ["成功指标1"],
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
                "your_brand": your_brand,
                "potential_partner": potential_partner,
                "partnership_type": partnership_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成合作关系提案失败: {e}")
            return {
                "your_brand": your_brand,
                "potential_partner": potential_partner,
                "partnership_type": partnership_type,
                "proposal_title": "",
                "partnership_summary": "",
                "mutual_benefits": [],
                "collaboration_areas": [],
                "proposed_activities": [],
                "timeline": "",
                "resource_commitment": "",
                "expected_outcomes": [],
                "success_metrics": [],
                "terms_and_conditions": [],
                "next_steps": [],
            }


partnership_proposal_generator_service = PartnershipProposalGeneratorService()