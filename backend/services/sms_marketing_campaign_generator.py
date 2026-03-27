"""
Vox SMS Marketing Campaign Generator Service 模块

短信营销活动生成服务
- 短信文案
- 发送时机
- 合规要求
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SMSMarketingCampaignGeneratorService:
    """
    短信营销活动生成服务

    生成短信营销活动内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_sms_marketing_campaign(
        self,
        offer_type: str,
        target_action: str,
        num_messages: int = 5,
    ) -> Dict[str, Any]:
        """
        生成短信营销活动

        Args:
            offer_type: 优惠类型
            target_action: 目标行动
            num_messages: 消息数量

        Returns:
            Dict: 短信营销活动
        """
        try:
            prompt = f"""请为"{offer_type}"（目标行动：{target_action}）生成{num_messages}条短信营销活动消息。

请以JSON格式返回：
{{
    "offer_type": "优惠类型",
    "target_action": "目标行动",
    "num_messages": {num_messages},
    "messages": [
        {{
            "message_number": 1,
            "timing": "时机",
            "message_text": "消息文本",
            "cta": "CTA",
            "link": "链接"
        }}
    ],
    "sending_schedule": "发送计划",
    "opt_in_strategy": "选择加入策略",
    "compliance_notes": "合规注意事项",
    "character_count_warning": "字符数警告"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "offer_type": offer_type,
                "target_action": target_action,
                "num_messages": num_messages,
                **result,
            }

        except Exception as e:
            logger.error(f"生成短信营销活动失败: {e}")
            return {
                "offer_type": offer_type,
                "target_action": target_action,
                "num_messages": num_messages,
                "messages": [],
                "sending_schedule": "",
                "opt_in_strategy": "",
                "compliance_notes": "",
                "character_count_warning": "",
            }


sms_marketing_campaign_generator_service = SMSMarketingCampaignGeneratorService()