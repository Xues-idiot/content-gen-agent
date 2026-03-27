"""
Vox Investor Deck Generator Service 模块

投资人演示文稿生成服务
- 路演展示
- 投资亮点
- 财务数据
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class InvestorDeckGeneratorService:
    """
    投资人演示文稿生成服务

    生成投资人演示文稿内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_investor_deck(
        self,
        company_name: str,
        industry: str,
        funding_round: str = "Series A",
        amount_raising: str = "¥10M",
    ) -> Dict[str, Any]:
        """
        生成投资人演示文稿

        Args:
            company_name: 公司名称
            industry: 行业
            funding_round: 融资轮次
            amount_raising: 融资金额

        Returns:
            Dict: 投资人演示文稿
        """
        try:
            prompt = f"""请为"{company_name}"（{industry}行业，{funding_round}，融资{amount_raising}）生成投资人演示文稿。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "industry": "行业",
    "funding_round": "融资轮次",
    "amount_raising": "融资金额",
    "pitch_title": "演示标题",
    "problem": "问题陈述",
    "solution": "解决方案",
    "market_opportunity": "市场机会",
    "product_description": "产品描述",
    "business_model": "商业模式",
    "traction": "进展与成绩",
    "competition_analysis": "竞争分析",
    "team": "团队介绍",
    "financials": "财务数据",
    "use_of_funds": "资金用途",
    "contact_information": "联系方式"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "company_name": company_name,
                "industry": industry,
                "funding_round": funding_round,
                "amount_raising": amount_raising,
                **result,
            }

        except Exception as e:
            logger.error(f"生成投资人演示文稿失败: {e}")
            return {
                "company_name": company_name,
                "industry": industry,
                "funding_round": funding_round,
                "amount_raising": amount_raising,
                "pitch_title": "",
                "problem": "",
                "solution": "",
                "market_opportunity": "",
                "product_description": "",
                "business_model": "",
                "traction": "",
                "competition_analysis": "",
                "team": "",
                "financials": "",
                "use_of_funds": "",
                "contact_information": "",
            }


investor_deck_generator_service = InvestorDeckGeneratorService()