"""
Vox Email Drip Campaign Generator Service 模块

邮件滴灌活动生成服务
- 滴灌序列
- 触发器
- 内容规划
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class EmailDripCampaignGeneratorService:
    """
    邮件滴灌活动生成服务

    生成邮件滴灌活动内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_email_drip_campaign(
        self,
        campaign_goal: str,
        trigger_type: str,
        num_emails: int = 10,
    ) -> Dict[str, Any]:
        """
        生成邮件滴灌活动

        Args:
            campaign_goal: 活动目标
            trigger_type: 触发器类型
            num_emails: 邮件数量

        Returns:
            Dict: 邮件滴灌活动
        """
        try:
            prompt = f"""请为"{campaign_goal}"目标生成{num_emails}封触发器类型为{trigger_type}的邮件滴灌活动。

请以JSON格式返回：
{{
    "campaign_goal": "活动目标",
    "trigger_type": "触发器类型",
    "num_emails": {num_emails},
    "campaign_overview": "活动概述",
    "trigger_definition": "触发器定义",
    "emails": [
        {{
            "email_number": 1,
            "day_offset": "天数偏移",
            "subject": "主题",
            "preview_text": "预览文本",
            "content_purpose": "内容目的",
            "body_summary": "正文摘要",
            "cta": "CTA"
        }}
    ],
    "drip_timing": "滴灌时机",
    "segmentation_criteria": "细分标准",
    "stop_conditions": "停止条件"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "campaign_goal": campaign_goal,
                "trigger_type": trigger_type,
                "num_emails": num_emails,
                **result,
            }

        except Exception as e:
            logger.error(f"生成邮件滴灌活动失败: {e}")
            return {
                "campaign_goal": campaign_goal,
                "trigger_type": trigger_type,
                "num_emails": num_emails,
                "campaign_overview": "",
                "trigger_definition": "",
                "emails": [],
                "drip_timing": "",
                "segmentation_criteria": "",
                "stop_conditions": "",
            }


email_drip_campaign_generator_service = EmailDripCampaignGeneratorService()