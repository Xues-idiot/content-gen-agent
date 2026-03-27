"""
Vox Seasonal Campaign Generator Service 模块

季节性活动生成服务
- 节日主题
- 促销策略
- 内容日历
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SeasonalCampaignGeneratorService:
    """
    季节性活动生成服务

    生成季节性活动内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_seasonal_campaign(
        self,
        season_event: str,
        brand_name: str,
        campaign_goal: str,
    ) -> Dict[str, Any]:
        """
        生成季节性活动

        Args:
            season_event: 季节/节日
            brand_name: 品牌名称
            campaign_goal: 活动目标

        Returns:
            Dict: 季节性活动
        """
        try:
            prompt = f"""请为"{brand_name}"的{season_event}生成以{campaign_goal}为目标的季节性活动内容。

请以JSON格式返回：
{{
    "season_event": "季节/节日",
    "brand_name": "品牌名称",
    "campaign_goal": "活动目标",
    "campaign_name": "活动名称",
    "campaign_theme": "活动主题",
    "key_messages": ["关键信息1"],
    "promotional_offer": "促销优惠",
    "content_calendar": [
        {{
            "date": "日期",
            "content_type": "内容类型",
            "channel": "渠道",
            "content_idea": "内容创意"
        }}
    ],
    "email_sequence": [
        {{
            "email_type": "邮件类型",
            "subject": "主题",
            "timing": "时机",
            "content_summary": "内容摘要"
        }}
    ],
    "social_media_posts": [
        {{
            "platform": "平台",
            "post_idea": "帖子创意",
            "hashtags": ["标签1"]
        }}
    ],
    "creative_assets_needed": ["需要的创意素材1"],
    "limited_edition_ideas": ["限量版创意1"],
    "collaboration_opportunities": ["合作机会1"],
    "post_campaign_analysis": "活动后分析"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "season_event": season_event,
                "brand_name": brand_name,
                "campaign_goal": campaign_goal,
                **result,
            }

        except Exception as e:
            logger.error(f"生成季节性活动失败: {e}")
            return {
                "season_event": season_event,
                "brand_name": brand_name,
                "campaign_goal": campaign_goal,
                "campaign_name": "",
                "campaign_theme": "",
                "key_messages": [],
                "promotional_offer": "",
                "content_calendar": [],
                "email_sequence": [],
                "social_media_posts": [],
                "creative_assets_needed": [],
                "limited_edition_ideas": [],
                "collaboration_opportunities": [],
                "post_campaign_analysis": "",
            }


seasonal_campaign_generator_service = SeasonalCampaignGeneratorService()