"""
Vox Competitor Battlecard Generator Service 模块

竞争对手战斗卡生成服务
- 竞争分析
- 销售对战卡
- 差异化信息
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CompetitorBattlecardGeneratorService:
    """
    竞争对手战斗卡生成服务

    生成竞争对手战斗卡内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_competitor_battlecard(
        self,
        competitor_name: str,
        your_product: str,
        deal_context: str,
    ) -> Dict[str, Any]:
        """
        生成竞争对手战斗卡

        Args:
            competitor_name: 竞争对手名称
            your_product: 你的产品
            deal_context: 交易背景

        Returns:
            Dict: 竞争对手战斗卡
        """
        try:
            prompt = f"""请为"{competitor_name}"与"{your_product}"在"{deal_context}"背景下生成竞争对手战斗卡。

请以JSON格式返回：
{{
    "competitor_name": "竞争对手名称",
    "your_product": "你的产品",
    "deal_context": "交易背景",
    "overview": "概述",
    "competitor_strengths": [
        {{
            "strength": "优势",
            "when_they_win": "他们何时赢"
        }}
    ],
    "competitor_weaknesses": [
        {{
            "weakness": "劣势",
            "how_to_exploit": "如何利用"
        }}
    ],
    "battlecard_scenarios": [
        {{
            "scenario": "场景",
            "our_advantage": "我们的优势",
            "competitor_vulnerability": "竞争对手弱点"
        }}
    ],
    "sales_talk_tracks": [
        {{
            "objection": "异议",
            "response": "回应"
        }}
    ],
    "pricing_positioning": "定价定位",
    "win_loss_analysis": "胜负分析",
    "competitive_moves": ["竞争动作1"],
    "defense_strategy": "防御策略"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "competitor_name": competitor_name,
                "your_product": your_product,
                "deal_context": deal_context,
                **result,
            }

        except Exception as e:
            logger.error(f"生成竞争对手战斗卡失败: {e}")
            return {
                "competitor_name": competitor_name,
                "your_product": your_product,
                "deal_context": deal_context,
                "overview": "",
                "competitor_strengths": [],
                "competitor_weaknesses": [],
                "battlecard_scenarios": [],
                "sales_talk_tracks": [],
                "pricing_positioning": "",
                "win_loss_analysis": "",
                "competitive_moves": [],
                "defense_strategy": "",
            }


competitor_battlecard_generator_service = CompetitorBattlecardGeneratorService()