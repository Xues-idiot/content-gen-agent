"""
Vox Content Distribution Strategy Generator Service 模块

内容分发策略生成服务
- 分发渠道
- 内容适配
- 推广计划
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ContentDistributionStrategyGeneratorService:
    """
    内容分发策略生成服务

    生成内容分发策略内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_content_distribution_strategy(
        self,
        content_type: str,
        target_audience: str,
        num_channels: int = 6,
    ) -> Dict[str, Any]:
        """
        生成内容分发策略

        Args:
            content_type: 内容类型
            target_audience: 目标受众
            num_channels: 渠道数量

        Returns:
            Dict: 内容分发策略
        """
        try:
            prompt = f"""请为"{content_type}"类型内容生成针对{target_audience}的{num_channels}个渠道的分发策略。

请以JSON格式返回：
{{
    "content_type": "内容类型",
    "target_audience": "目标受众",
    "num_channels": {num_channels},
    "distribution_objectives": ["分发目标1"],
    "channel_strategy": [
        {{
            "channel": "渠道",
            "content_adaptation": "内容适配",
            "promotion_tactics": ["推广策略1"],
            "optimal_timing": "最佳时机"
        }}
    ],
    "repurposing_plan": "再利用计划",
    "seo_considerations": "SEO考虑",
    "paid_promotion": "付费推广",
    "success_metrics": ["成功指标1"],
    "budget_recommendations": "预算建议"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "content_type": content_type,
                "target_audience": target_audience,
                "num_channels": num_channels,
                **result,
            }

        except Exception as e:
            logger.error(f"生成内容分发策略失败: {e}")
            return {
                "content_type": content_type,
                "target_audience": target_audience,
                "num_channels": num_channels,
                "distribution_objectives": [],
                "channel_strategy": [],
                "repurposing_plan": "",
                "seo_considerations": "",
                "paid_promotion": "",
                "success_metrics": [],
                "budget_recommendations": "",
            }


content_distribution_strategy_generator_service = ContentDistributionStrategyGeneratorService()
