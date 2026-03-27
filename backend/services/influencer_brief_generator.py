"""
Vox Influencer Brief Generator Service 模块

影响者简报生成服务
- 活动要求
- 内容标准
- 交付规范
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class InfluencerBriefGeneratorService:
    """
    影响者简报生成服务

    生成影响者简报内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_influencer_brief(
        self,
        campaign_name: str,
        brand_name: str,
        deliverable_type: str,
    ) -> Dict[str, Any]:
        """
        生成影响者简报

        Args:
            campaign_name: 活动名称
            brand_name: 品牌名称
            deliverable_type: 交付类型

        Returns:
            Dict: 影响者简报
        """
        try:
            prompt = f"""请为"{campaign_name}"（品牌：{brand_name}，交付类型：{deliverable_type}）生成影响者简报。

请以JSON格式返回：
{{
    "campaign_name": "活动名称",
    "brand_name": "品牌名称",
    "deliverable_type": "交付类型",
    "campaign_overview": "活动概述",
    "brand_guidelines": {{
        "tone_of_voice": "语调",
        "key_messages": ["关键信息1"],
        "dos_donts": ["宜/忌1"]
    }},
    "deliverables": [
        {{
            "type": "类型",
            "specifications": "规格",
            "requirements": ["要求1"]
        }}
    ],
    "content_requirements": "内容要求",
    "posting_guidelines": "发布指南",
    "timeline": "时间线",
    "compensation": "补偿",
    "approval_process": "审批流程",
    "usage_rights": "使用权"
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
                "brand_name": brand_name,
                "deliverable_type": deliverable_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成影响者简报失败: {e}")
            return {
                "campaign_name": campaign_name,
                "brand_name": brand_name,
                "deliverable_type": deliverable_type,
                "campaign_overview": "",
                "brand_guidelines": {},
                "deliverables": [],
                "content_requirements": "",
                "posting_guidelines": "",
                "timeline": "",
                "compensation": "",
                "approval_process": "",
                "usage_rights": "",
            }


influencer_brief_generator_service = InfluencerBriefGeneratorService()