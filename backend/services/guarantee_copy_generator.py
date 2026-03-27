"""
Vox Guarantee Copy Generator Service 模块

保证声明生成服务
- 退款政策
- 质量保证
- 服务承诺
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class GuaranteeCopyGeneratorService:
    """
    保证声明生成服务

    生成保证声明内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_guarantee_copy(
        self,
        product_service: str,
        guarantee_type: str = "satisfaction",
        duration_days: int = 30,
    ) -> Dict[str, Any]:
        """
        生成保证声明

        Args:
            product_service: 产品/服务
            guarantee_type: 保证类型
            duration_days: 期限（天）

        Returns:
            Dict: 保证声明
        """
        try:
            prompt = f"""请为"{product_service}"生成{duration_days}天的{guarantee_type}类型的保证声明。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "guarantee_type": "保证类型",
    "duration_days": {duration_days},
    "headline": "标题",
    "guarantee_statement": "保证声明",
    "key_terms": ["关键条款1"],
    "coverage_details": {{
        "what_is_covered": ["承保范围1"],
        "what_is_not_covered": ["不保范围1"]
    }},
    "claim_process": [
        {{
            "step": "步骤",
            "action": "行动",
            "timeline": "时间线"
        }}
    ],
    "customer_commitments": ["客户承诺1"],
    "company_commitments": ["公司承诺1"],
    "limitations_exceptions": ["限制/例外1"],
    "legal_disclaimer": "法律免责声明",
    "comparison_to_competitors": "与竞争对手比较",
    "promotional_angle": "促销角度",
    "faq": [
        {{
            "question": "问题",
            "answer": "答案"
        }}
    ],
    "visuals_suggestions": ["视觉建议1"],
    "placement_recommendations": ["放置建议1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_service": product_service,
                "guarantee_type": guarantee_type,
                "duration_days": duration_days,
                **result,
            }

        except Exception as e:
            logger.error(f"生成保证声明失败: {e}")
            return {
                "product_service": product_service,
                "guarantee_type": guarantee_type,
                "duration_days": duration_days,
                "headline": "",
                "guarantee_statement": "",
                "key_terms": [],
                "coverage_details": {},
                "claim_process": [],
                "customer_commitments": [],
                "company_commitments": [],
                "limitations_exceptions": [],
                "legal_disclaimer": "",
                "comparison_to_competitors": "",
                "promotional_angle": "",
                "faq": [],
                "visuals_suggestions": [],
                "placement_recommendations": [],
            }


guarantee_copy_generator_service = GuaranteeCopyGeneratorService()