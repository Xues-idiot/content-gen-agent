"""
Vox Strategic Partnership Assessment Generator Service 模块

战略合作伙伴评估生成服务
- 合作伙伴契合度
- 价值创造潜力
- 风险评估
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class StrategicPartnershipAssessmentGeneratorService:
    """
    战略合作伙伴评估生成服务

    生成战略合作伙伴评估内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_strategic_partnership_assessment(
        self,
        partner_name: str,
        partnership_type: str,
    ) -> Dict[str, Any]:
        """
        生成战略合作伙伴评估

        Args:
            partner_name: 合作伙伴名称
            partnership_type: 合作关系类型

        Returns:
            Dict: 战略合作伙伴评估
        """
        try:
            prompt = f"""请为"{partner_name}"（{partnership_type}合作关系）生成战略合作伙伴评估。

请以JSON格式返回：
{{
    "partner_name": "合作伙伴名称",
    "partnership_type": "合作关系类型",
    "partner_overview": {{
        "company_background": "公司背景",
        "market_position": "市场地位",
        "financial_health": "财务状况"
    }},
    "strategic_fit": {{
        "alignment_goals": "目标一致性",
        "alignment_culture": "文化一致性",
        "complementary_capabilities": "互补能力"
    }},
    "value_creation_potential": ["价值创造潜力1"],
    "collaboration_risks": ["合作风险1"],
    "mutual_commitment": "相互承诺",
    "alternative_options": ["替代选项1"],
    "success_probability": "成功概率",
    "recommendation": "建议",
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
                "partner_name": partner_name,
                "partnership_type": partnership_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成战略合作伙伴评估失败: {e}")
            return {
                "partner_name": partner_name,
                "partnership_type": partnership_type,
                "partner_overview": {},
                "strategic_fit": {},
                "value_creation_potential": [],
                "collaboration_risks": [],
                "mutual_commitment": "",
                "alternative_options": [],
                "success_probability": "",
                "recommendation": "",
                "next_steps": [],
            }


strategic_partnership_assessment_generator_service = StrategicPartnershipAssessmentGeneratorService()
