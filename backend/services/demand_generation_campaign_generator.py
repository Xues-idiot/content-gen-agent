"""
Vox Demand Generation Campaign Generator Service 模块

需求生成活动生成服务
- 活动策略
- 内容计划
- 渠道组合
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class DemandGenerationCampaignGeneratorService:
    """
    需求生成活动生成服务

    生成需求生成活动内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_demand_generation_campaign(
        self,
        campaign_name: str,
        target_audience: str,
        num_channels: int = 5,
    ) -> Dict[str, Any]:
        """
        生成需求生成活动

        Args:
            campaign_name: 活动名称
            target_audience: 目标受众
            num_channels: 渠道数量

        Returns:
            Dict: 需求生成活动
        """
        try:
            prompt = f"""请为"{campaign_name}"生成针对{target_audience}的{num_channels}个渠道的需求生成活动。

请以JSON格式返回：
{{
    "campaign_name": "活动名称",
    "target_audience": "目标受众",
    "num_channels": {num_channels},
    "campaign_objectives": ["活动目标1"],
    "channel_strategy": [
        {{
            "channel": "渠道",
            "tactics": ["策略1"],
            "content_types": ["内容类型1"],
            "budget_allocation": "预算分配"
        }}
    ],
    "content_calendar": ["内容日历1"],
    "lead_targets": "潜在客户目标",
    "timeline": "时间线",
    "kpis": ["KPI1"],
    "measurement_framework": "测量框架"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "campaign_name": campaign_name,
                "target_audience": target_audience,
                "num_channels": num_channels,
                **result,
            }

        except Exception as e:
            logger.error(f"生成需求生成活动失败: {e}")
            return {
                "campaign_name": campaign_name,
                "target_audience": target_audience,
                "num_channels": num_channels,
                "campaign_objectives": [],
                "channel_strategy": [],
                "content_calendar": [],
                "lead_targets": "",
                "timeline": "",
                "kpis": [],
                "measurement_framework": "",
            }


demand_generation_campaign_generator_service = DemandGenerationCampaignGeneratorService()
