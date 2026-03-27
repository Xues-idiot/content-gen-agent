"""
Vox Competitive Positioning Statement Generator Service 模块

竞争定位声明生成服务
- 市场定位
- 差异化因素
- 价值主张
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CompetitivePositioningStatementGeneratorService:
    """
    竞争定位声明生成服务

    生成竞争定位声明内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_competitive_positioning_statement(
        self,
        product_name: str,
        target_market: str,
        main_competitor: str,
    ) -> Dict[str, Any]:
        """
        生成竞争定位声明

        Args:
            product_name: 产品名称
            target_market: 目标市场
            main_competitor: 主要竞争对手

        Returns:
            Dict: 竞争定位声明
        """
        try:
            prompt = f"""请为"{product_name}"生成在{target_market}市场针对"{main_competitor}"的竞争定位声明。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "target_market": "目标市场",
    "main_competitor": "主要竞争对手",
    "positioning_statement": "定位声明",
    "target_audience": "目标受众",
    "our_positioning": "我们的定位",
    "competitor_positioning": "竞争对手定位",
    "key_differentiators": ["关键差异化因素1"],
    "unique_value_proposition": "独特价值主张",
    "proof_points": ["证明要点1"],
    "messaging_framework": "信息框架"
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
                "target_market": target_market,
                "main_competitor": main_competitor,
                **result,
            }

        except Exception as e:
            logger.error(f"生成竞争定位声明失败: {e}")
            return {
                "product_name": product_name,
                "target_market": target_market,
                "main_competitor": main_competitor,
                "positioning_statement": "",
                "target_audience": "",
                "our_positioning": "",
                "competitor_positioning": "",
                "key_differentiators": [],
                "unique_value_proposition": "",
                "proof_points": [],
                "messaging_framework": "",
            }


competitive_positioning_statement_generator_service = CompetitivePositioningStatementGeneratorService()