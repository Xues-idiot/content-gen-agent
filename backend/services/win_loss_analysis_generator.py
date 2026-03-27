"""
Vox Win Loss Analysis Generator Service 模块

赢单输单分析生成服务
- 赢单因素
- 输单原因
- 竞争洞察
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class WinLossAnalysisGeneratorService:
    """
    赢单输单分析生成服务

    生成赢单输单分析内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_win_loss_analysis(
        self,
        deal_name: str,
        outcome: str,
        competitor: str = "",
        num_factors: int = 8,
    ) -> Dict[str, Any]:
        """
        生成赢单输单分析

        Args:
            deal_name: 交易名称
            outcome: 结果（win/loss）
            competitor: 竞争对手
            num_factors: 因素数量

        Returns:
            Dict: 赢单输单分析
        """
        try:
            prompt = f"""请为交易"{deal_name}"生成{outcome}分析（竞争对手：{competitor}），{num_factors}个因素。

请以JSON格式返回：
{{
    "deal_name": "交易名称",
    "outcome": "结果",
    "competitor": "竞争对手",
    "num_factors": {num_factors},
    "key_factors": ["关键因素1"],
    "winning_losing_reasons": ["赢单/输单原因1"],
    "competitor_strengths": ["竞争对手优势1"],
    "competitor_weaknesses": ["竞争对手弱点1"],
    "lessons_learned": ["经验教训1"],
    "improvement_actions": ["改进行动1"],
    "deal_timeline": "交易时间线",
    "stakeholder_influence": ["利益相关者影响力1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "deal_name": deal_name,
                "outcome": outcome,
                "competitor": competitor,
                "num_factors": num_factors,
                **result,
            }

        except Exception as e:
            logger.error(f"生成赢单输单分析失败: {e}")
            return {
                "deal_name": deal_name,
                "outcome": outcome,
                "competitor": competitor,
                "num_factors": num_factors,
                "key_factors": [],
                "winning_losing_reasons": [],
                "competitor_strengths": [],
                "competitor_weaknesses": [],
                "lessons_learned": [],
                "improvement_actions": [],
                "deal_timeline": "",
                "stakeholder_influence": [],
            }


win_loss_analysis_generator_service = WinLossAnalysisGeneratorService()
