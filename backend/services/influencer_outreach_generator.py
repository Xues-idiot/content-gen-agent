"""
Vox Influencer Outreach Generator Service 模块

影响者外联生成服务
- KOL合作
- 外联邮件
- 合作提案
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class InfluencerOutreachGeneratorService:
    """
    影响者外联生成服务

    生成影响者外联内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_influencer_outreach(
        self,
        influencer_name: str,
        platform: str,
        brand_name: str,
    ) -> Dict[str, Any]:
        """
        生成影响者外联

        Args:
            influencer_name: 影响者姓名
            platform: 平台
            brand_name: 品牌名称

        Returns:
            Dict: 影响者外联
        """
        try:
            prompt = f"""请为"{brand_name}"生成与{platform}平台的影响者"{influencer_name}"的外联内容。

请以JSON格式返回：
{{
    "influencer_name": "影响者姓名",
    "platform": "平台",
    "brand_name": "品牌名称",
    "outreach_email": {{
        "subject": "主题",
        "body": "正文"
    }},
    "collaboration_proposal": {{
        "campaign_name": "活动名称",
        "deliverables": ["交付物1"],
        "timeline": "时间线",
        "compensation": "补偿"
    }},
    "partnership_types": ["合作类型1"],
    "brand_fit_reasons": ["品牌契合原因1"],
    "content_ideas": ["内容创意1"],
    "follow_up_strategy": "跟进策略"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "influencer_name": influencer_name,
                "platform": platform,
                "brand_name": brand_name,
                **result,
            }

        except Exception as e:
            logger.error(f"生成影响者外联失败: {e}")
            return {
                "influencer_name": influencer_name,
                "platform": platform,
                "brand_name": brand_name,
                "outreach_email": {},
                "collaboration_proposal": {},
                "partnership_types": [],
                "brand_fit_reasons": [],
                "content_ideas": [],
                "follow_up_strategy": "",
            }


influencer_outreach_generator_service = InfluencerOutreachGeneratorService()