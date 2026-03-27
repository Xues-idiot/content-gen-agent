"""
Vox Value Proposition Canvas Generator Service 模块

价值主张画布生成服务
- 客户工作
- 痛点
- 解决方案
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ValuePropositionCanvasGeneratorService:
    """
    价值主张画布生成服务

    生成价值主张画布内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_value_proposition_canvas(
        self,
        product_service: str,
        target_customer: str,
    ) -> Dict[str, Any]:
        """
        生成价值主张画布

        Args:
            product_service: 产品/服务
            target_customer: 目标客户

        Returns:
            Dict: 价值主张画布
        """
        try:
            prompt = f"""请为"{product_service}"生成目标客户"{target_customer}"的价值主张画布。

请以JSON格式返回：
{{
    "product_service": "产品/服务",
    "target_customer": "目标客户",
    "customer_profile": {{
        "customer_jobs": ["客户工作1"],
        "pains": ["痛苦1"],
        "gains": ["收益1"]
    }},
    "value_map": {{
        "products_services": ["产品/服务1"],
        "pain_relievers": ["减痛器1"],
        "gain_creators": ["收益创造者1"]
    }},
    "fit_score": "匹配度评分",
    "alignment_issues": ["对齐问题1"],
    "recommendations": ["建议1"],
    "priority_actions": ["优先行动1"]
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
                "target_customer": target_customer,
                **result,
            }

        except Exception as e:
            logger.error(f"生成价值主张画布失败: {e}")
            return {
                "product_service": product_service,
                "target_customer": target_customer,
                "customer_profile": {},
                "value_map": {},
                "fit_score": "",
                "alignment_issues": [],
                "recommendations": [],
                "priority_actions": [],
            }


value_proposition_canvas_generator_service = ValuePropositionCanvasGeneratorService()
