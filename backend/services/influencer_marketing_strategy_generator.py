"""
Vox Influencer Marketing Strategy Generator Service 模块

网红营销策略生成服务
- 网红筛选
- 合作模式
- 内容计划
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class InfluencerMarketingStrategyGeneratorService:
    """
    网红营销策略生成服务

    生成网红营销策略内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_influencer_marketing_strategy(
        self,
        brand_name: str,
        target_audience: str,
        num_influencers: int = 5,
    ) -> Dict[str, Any]:
        """
        生成网红营销策略

        Args:
            brand_name: 品牌名称
            target_audience: 目标受众
            num_influencers: 网红数量

        Returns:
            Dict: 网红营销策略
        """
        try:
            prompt = f"""请为"{brand_name}"生成针对{target_audience}的{num_influencers}位网红的营销策略。

请以JSON格式返回：
{{
    "brand_name": "品牌名称",
    "target_audience": "目标受众",
    "num_influencers": {num_influencers},
    "campaign_objectives": ["活动目标1"],
    "influencer_criteria": ["网红标准1"],
    "influencer_tiers": [
        {{
            "tier_name": "层级名称",
            "follower_range": "粉丝范围",
            "collaboration_model": "合作模式",
            "budget_range": "预算范围"
        }}
    ],
    "content_guidelines": ["内容指南1"],
    "campaign_timeline": "活动时间线",
    "platform_strategy": "平台策略",
    "kpis": ["KPI1"],
    "compliance_requirements": "合规要求",
    "measurement_approach": "测量方法"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "brand_name": brand_name,
                "target_audience": target_audience,
                "num_influencers": num_influencers,
                **result,
            }

        except Exception as e:
            logger.error(f"生成网红营销策略失败: {e}")
            return {
                "brand_name": brand_name,
                "target_audience": target_audience,
                "num_influencers": num_influencers,
                "campaign_objectives": [],
                "influencer_criteria": [],
                "influencer_tiers": [],
                "content_guidelines": [],
                "campaign_timeline": "",
                "platform_strategy": "",
                "kpis": [],
                "compliance_requirements": "",
                "measurement_approach": "",
            }


influencer_marketing_strategy_generator_service = InfluencerMarketingStrategyGeneratorService()
