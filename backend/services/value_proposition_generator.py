"""
Vox Value Proposition Generator Service 模块

价值主张生成服务
- 核心价值
- 差异化卖点
- 品牌承诺
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ValuePropositionGeneratorService:
    """
    价值主张生成服务

    生成价值主张内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_value_proposition(
        self,
        product_name: str,
        target_audience: str,
        main_benefit: str,
    ) -> Dict[str, Any]:
        """
        生成价值主张

        Args:
            product_name: 产品名称
            target_audience: 目标受众
            main_benefit: 主要利益

        Returns:
            Dict: 价值主张
        """
        try:
            prompt = f"""请为"{product_name}"为"{target_audience}"生成价值主张（核心利益：{main_benefit}）。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "target_audience": "目标受众",
    "main_benefit": "主要利益",
    "headline": "标题",
    "subheadline": "副标题",
    "value_statement": "价值陈述",
    "key_benefits": ["关键利益1"],
    "differentiators": ["差异化因素1"],
    "proof_points": ["证明点1"],
    "emotional_benefits": ["情感利益1"],
    "rational_benefits": ["理性利益1"],
    "brand_promise": "品牌承诺",
    "supporting_evidence": ["支持证据1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_name": product_name,
                "target_audience": target_audience,
                "main_benefit": main_benefit,
                **result,
            }

        except Exception as e:
            logger.error(f"生成价值主张失败: {e}")
            return {
                "product_name": product_name,
                "target_audience": target_audience,
                "main_benefit": main_benefit,
                "headline": "",
                "subheadline": "",
                "value_statement": "",
                "key_benefits": [],
                "differentiators": [],
                "proof_points": [],
                "emotional_benefits": [],
                "rational_benefits": [],
                "brand_promise": "",
                "supporting_evidence": [],
            }


value_proposition_generator_service = ValuePropositionGeneratorService()