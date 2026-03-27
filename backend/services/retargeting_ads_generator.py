"""
Vox Retargeting Ads Generator Service 模块

再营销广告生成服务
- 广告创意
- 受众定位
- 投放策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class RetargetingAdsGeneratorService:
    """
    再营销广告生成服务

    生成再营销广告内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_retargeting_ads(
        self,
        audience_segment: str,
        product_service: str,
        num_ad_variants: int = 5,
    ) -> Dict[str, Any]:
        """
        生成再营销广告

        Args:
            audience_segment: 受众细分
            product_service: 产品/服务
            num_ad_variants: 广告变体数量

        Returns:
            Dict: 再营销广告
        """
        try:
            prompt = f"""请为"{audience_segment}"受众细分生成{num_ad_variants}个{product_service}的再营销广告。

请以JSON格式返回：
{{
    "audience_segment": "受众细分",
    "product_service": "产品/服务",
    "num_ad_variants": {num_ad_variants},
    "ad_variants": [
        {{
            "variant_name": "变体名称",
            "headline": "标题",
            "description": "描述",
            "cta": "CTA",
            "image_suggestions": ["图片建议1"]
        }}
    ],
    "bidding_strategy": "竞价策略",
    "frequency_capping": "频率上限",
    "ad_schedule": "广告排期"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "audience_segment": audience_segment,
                "product_service": product_service,
                "num_ad_variants": num_ad_variants,
                **result,
            }

        except Exception as e:
            logger.error(f"生成再营销广告失败: {e}")
            return {
                "audience_segment": audience_segment,
                "product_service": product_service,
                "num_ad_variants": num_ad_variants,
                "ad_variants": [],
                "bidding_strategy": "",
                "frequency_capping": "",
                "ad_schedule": "",
            }


retargeting_ads_generator_service = RetargetingAdsGeneratorService()