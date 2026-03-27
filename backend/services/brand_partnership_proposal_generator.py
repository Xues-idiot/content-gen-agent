"""
Vox Brand Partnership Proposal Generator Service 模块

品牌合作关系提案生成服务
- 合作模式
- 互利条款
- 实施方案
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BrandPartnershipProposalGeneratorService:
    """
    品牌合作关系提案生成服务

    生成品牌合作关系提案内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_brand_partnership_proposal(
        self,
        your_brand: str,
        partner_brand: str,
        partnership_model: str,
    ) -> Dict[str, Any]:
        """
        生成品牌合作关系提案

        Args:
            your_brand: 你的品牌
            partner_brand: 合作方品牌
            partnership_model: 合作模式

        Returns:
            Dict: 品牌合作关系提案
        """
        try:
            prompt = f"""请为"{your_brand}"与"{partner_brand}"生成{partnership_model}模式的品牌合作关系提案。

请以JSON格式返回：
{{
    "your_brand": "你的品牌",
    "partner_brand": "合作方品牌",
    "partnership_model": "合作模式",
    "proposal_title": "提案标题",
    "executive_summary": "执行摘要",
    "partnership_objectives": ["合作目标1"],
    "collaboration_areas": ["合作领域1"],
    "mutual_benefits": {{
        "for_your_brand": ["对你的品牌的好处1"],
        "for_partner_brand": ["对合作方品牌的好处1"]
    }},
    "proposed_activities": ["提议的活动1"],
    "resource_contributions": {{
        "your_brand": ["你的品牌的贡献1"],
        "partner_brand": ["合作方品牌的贡献1"]
    }},
    "timeline": "时间线",
    "success_metrics": ["成功指标1"],
    "terms_and_conditions": ["条款和条件1"],
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
                "partner_brand": partner_brand,
                "partnership_model": partnership_model,
                **result,
            }

        except Exception as e:
            logger.error(f"生成品牌合作关系提案失败: {e}")
            return {
                "your_brand": your_brand,
                "partner_brand": partner_brand,
                "partnership_model": partnership_model,
                "proposal_title": "",
                "executive_summary": "",
                "partnership_objectives": [],
                "collaboration_areas": [],
                "mutual_benefits": {},
                "proposed_activities": [],
                "resource_contributions": {},
                "timeline": "",
                "success_metrics": [],
                "terms_and_conditions": [],
                "next_steps": [],
            }


brand_partnership_proposal_generator_service = BrandPartnershipProposalGeneratorService()