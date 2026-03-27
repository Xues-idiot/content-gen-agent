"""
Vox Facebook Ad Creative Generator Service 模块

Facebook广告创意生成服务
- 广告文案
- 视觉方向
- 受众定位
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class FacebookAdCreativeGeneratorService:
    """
    Facebook广告创意生成服务

    生成Facebook广告创意内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_facebook_ad_creative(
        self,
        offer: str,
        objective: str,
        num_ad_variations: int = 5,
    ) -> Dict[str, Any]:
        """
        生成Facebook广告创意

        Args:
            offer: 优惠
            objective: 目标
            num_ad_variations: 广告变体数量

        Returns:
            Dict: Facebook广告创意
        """
        try:
            prompt = f"""请为"{offer}"生成{num_ad_variations}个Facebook广告创意（目标：{objective}）。

请以JSON格式返回：
{{
    "offer": "优惠",
    "objective": "目标",
    "num_ad_variations": {num_ad_variations},
    "ad_variations": [
        {{
            "variation_name": "变体名称",
            "ad_format": "广告格式",
            "headline": "标题",
            "primary_text": "主要文案",
            "description": "描述",
            "cta_button": "CTA按钮",
            "image_suggestions": ["图片建议1"]
        }}
    ],
    "audience_targeting": "受众定位",
    "placement_recommendations": "放置建议",
    "video_ad_options": ["视频广告选项1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "offer": offer,
                "objective": objective,
                "num_ad_variations": num_ad_variations,
                **result,
            }

        except Exception as e:
            logger.error(f"生成Facebook广告创意失败: {e}")
            return {
                "offer": offer,
                "objective": objective,
                "num_ad_variations": num_ad_variations,
                "ad_variations": [],
                "audience_targeting": "",
                "placement_recommendations": "",
                "video_ad_options": [],
            }


facebook_ad_creative_generator_service = FacebookAdCreativeGeneratorService()