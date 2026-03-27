"""
Vox Video Marketing Campaign Generator Service 模块

视频营销活动生成服务
- 视频概念
- 制作计划
- 分发策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class VideoMarketingCampaignGeneratorService:
    """
    视频营销活动生成服务

    生成视频营销活动内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_video_marketing_campaign(
        self,
        campaign_name: str,
        product_service: str,
        num_videos: int = 4,
    ) -> Dict[str, Any]:
        """
        生成视频营销活动

        Args:
            campaign_name: 活动名称
            product_service: 产品/服务
            num_videos: 视频数量

        Returns:
            Dict: 视频营销活动
        """
        try:
            prompt = f"""请为"{campaign_name}"活动生成{product_service}的{num_videos}个视频的营销活动。

请以JSON格式返回：
{{
    "campaign_name": "活动名称",
    "product_service": "产品/服务",
    "num_videos": {num_videos},
    "video_concepts": [
        {{
            "video_title": "视频标题",
            "video_type": "视频类型",
            "duration": "时长",
            "key_message": "关键信息",
            "target_platform": "目标平台"
        }}
    ],
    "production_timeline": "制作时间线",
    "script_overview": "脚本概述",
    "distribution_plan": "分发计划",
    "budget_breakdown": "预算明细",
    "success_metrics": ["成功指标1"],
    "call_to_action": "行动号召"
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
                "product_service": product_service,
                "num_videos": num_videos,
                **result,
            }

        except Exception as e:
            logger.error(f"生成视频营销活动失败: {e}")
            return {
                "campaign_name": campaign_name,
                "product_service": product_service,
                "num_videos": num_videos,
                "video_concepts": [],
                "production_timeline": "",
                "script_overview": "",
                "distribution_plan": "",
                "budget_breakdown": "",
                "success_metrics": [],
                "call_to_action": "",
            }


video_marketing_campaign_generator_service = VideoMarketingCampaignGeneratorService()
