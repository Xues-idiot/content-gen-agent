"""
Vox Referral Program Messaging Generator Service 模块

推荐计划消息生成服务
- 推荐话术
- 奖励机制
- 进度追踪
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ReferralProgramMessagingGeneratorService:
    """
    推荐计划消息生成服务

    生成推荐计划消息内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_referral_program_messaging(
        self,
        product_name: str,
        reward_type: str,
        num_referrals: int = 3,
    ) -> Dict[str, Any]:
        """
        生成推荐计划消息

        Args:
            product_name: 产品名称
            reward_type: 奖励类型
            num_referrals: 推荐数量

        Returns:
            Dict: 推荐计划消息
        """
        try:
            prompt = f"""请为"{product_name}"生成{reward_type}奖励类型的{num_referrals}次推荐计划消息内容。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "reward_type": "奖励类型",
    "num_referrals": {num_referrals},
    "referral_headline": "推荐标题",
    "referral_value_proposition": "推荐价值主张",
    "messaging_templates": [
        {{
            "touchpoint": "接触点",
            "message": "消息",
            "cta": "CTA"
        }}
    ],
    "reward_tiers": [
        {{
            "referrals_needed": "需要的推荐数",
            "reward": "奖励"
        }}
    ],
    "progress_notification": "进度通知",
    "reminder_messages": ["提醒消息1"],
    "celebration_messages": ["庆祝消息1"],
    "social_share_options": ["社交分享选项1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_name": product_name,
                "reward_type": reward_type,
                "num_referrals": num_referrals,
                **result,
            }

        except Exception as e:
            logger.error(f"生成推荐计划消息失败: {e}")
            return {
                "product_name": product_name,
                "reward_type": reward_type,
                "num_referrals": num_referrals,
                "referral_headline": "",
                "referral_value_proposition": "",
                "messaging_templates": [],
                "reward_tiers": [],
                "progress_notification": "",
                "reminder_messages": [],
                "celebration_messages": [],
                "social_share_options": [],
            }


referral_program_messaging_generator_service = ReferralProgramMessagingGeneratorService()