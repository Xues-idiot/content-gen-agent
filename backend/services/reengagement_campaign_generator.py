"""
Vox Reengagement Campaign Generator Service 模块

重新参与活动生成服务
- 唤醒邮件
- 激励措施
- 赢回策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ReengagementCampaignGeneratorService:
    """
    重新参与活动生成服务

    生成重新参与活动内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_reengagement_campaign(
        self,
        brand_name: str,
        inactive_period: str,
        offer_type: str = "discount",
    ) -> Dict[str, Any]:
        """
        生成重新参与活动

        Args:
            brand_name: 品牌名称
            inactive_period: 非活跃期
            offer_type: 优惠类型

        Returns:
            Dict: 重新参与活动
        """
        try:
            prompt = f"""请为"{brand_name}"生成为期{inactive_period}的非活跃用户重新参与活动（优惠类型：{offer_type}）。

请以JSON格式返回：
{{
    "brand_name": "品牌名称",
    "inactive_period": "非活跃期",
    "offer_type": "优惠类型",
    "campaign_headline": "活动标题",
    "email_sequence": [
        {{
            "email_number": 1,
            "timing": "时机",
            "subject": "主题",
            "headline": "标题",
            "content": "内容",
            "cta": "CTA"
        }}
    ],
    "subject_line_options": ["主题行选项1"],
    "win_back_offers": [
        {{
            "offer": "优惠",
            "eligibility": "资格",
            "expiry": "过期时间"
        }}
    ],
    "update_preferences_cta": "更新偏好CTA",
    "content_ideas": ["内容创意1"],
    "survey_questions": ["调查问题1"],
    "success_metrics": ["成功指标1"]
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
                "inactive_period": inactive_period,
                "offer_type": offer_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成重新参与活动失败: {e}")
            return {
                "brand_name": brand_name,
                "inactive_period": inactive_period,
                "offer_type": offer_type,
                "campaign_headline": "",
                "email_sequence": [],
                "subject_line_options": [],
                "win_back_offers": [],
                "update_preferences_cta": "",
                "content_ideas": [],
                "survey_questions": [],
                "success_metrics": [],
            }


reengagement_campaign_generator_service = ReengagementCampaignGeneratorService()