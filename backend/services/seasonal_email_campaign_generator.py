"""
Vox Seasonal Email Campaign Generator Service 模块

季节性邮件活动生成服务
- 节日主题
- 促销内容
- 发送时机
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SeasonalEmailCampaignGeneratorService:
    """
    季节性邮件活动生成服务

    生成季节性邮件活动内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_seasonal_email_campaign(
        self,
        season_event: str,
        brand_name: str,
        num_emails: int = 5,
    ) -> Dict[str, Any]:
        """
        生成季节性邮件活动

        Args:
            season_event: 季节/节日
            brand_name: 品牌名称
            num_emails: 邮件数量

        Returns:
            Dict: 季节性邮件活动
        """
        try:
            prompt = f"""请为"{brand_name}"的{season_event}生成{num_emails}封季节性邮件活动。

请以JSON格式返回：
{{
    "season_event": "季节/节日",
    "brand_name": "品牌名称",
    "num_emails": {num_emails},
    "campaign_theme": "活动主题",
    "emails": [
        {{
            "email_number": 1,
            "send_timing": "发送时机",
            "subject": "主题",
            "preview_text": "预览文本",
            "headline": "标题",
            "body_summary": "正文摘要",
            "cta": "CTA"
        }}
    ],
    "seasonal_offers": ["季节性优惠1"],
    "design_recommendations": "设计建议"
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
                "num_emails": num_emails,
                **result,
            }

        except Exception as e:
            logger.error(f"生成季节性邮件活动失败: {e}")
            return {
                "season_event": season_event,
                "brand_name": brand_name,
                "num_emails": num_emails,
                "campaign_theme": "",
                "emails": [],
                "seasonal_offers": [],
                "design_recommendations": "",
            }


seasonal_email_campaign_generator_service = SeasonalEmailCampaignGeneratorService()