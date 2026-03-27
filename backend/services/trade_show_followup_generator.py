"""
Vox Trade Show Followup Generator Service 模块

展会跟进生成服务
- 后续邮件
- 潜在客户管理
- 社交连接
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TradeShowFollowupGeneratorService:
    """
    展会跟进生成服务

    生成展会跟进内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_trade_show_followup(
        self,
        event_name: str,
        lead_type: str,
        num_followups: int = 3,
    ) -> Dict[str, Any]:
        """
        生成展会跟进

        Args:
            event_name: 活动名称
            lead_type: 潜在客户类型
            num_followups: 跟进数量

        Returns:
            Dict: 展会跟进
        """
        try:
            prompt = f"""请为"{event_name}"（潜在客户类型：{lead_type}）生成{num_followups}封展会跟进邮件。

请以JSON格式返回：
{{
    "event_name": "活动名称",
    "lead_type": "潜在客户类型",
    "num_followups": {num_followups},
    "emails": [
        {{
            "email_number": 1,
            "timing": "时机",
            "subject": "主题",
            "body": "正文",
            "cta": "CTA"
        }}
    ],
    "linkedin_connection_message": "LinkedIn连接消息",
    "lead_scoring_criteria": "潜在客户评分标准",
    "follow_up_schedule": "跟进计划"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "event_name": event_name,
                "lead_type": lead_type,
                "num_followups": num_followups,
                **result,
            }

        except Exception as e:
            logger.error(f"生成展会跟进失败: {e}")
            return {
                "event_name": event_name,
                "lead_type": lead_type,
                "num_followups": num_followups,
                "emails": [],
                "linkedin_connection_message": "",
                "lead_scoring_criteria": "",
                "follow_up_schedule": "",
            }


trade_show_followup_generator_service = TradeShowFollowupGeneratorService()