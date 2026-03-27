"""
Vox Webinar Followup Sequence Generator Service 模块

网络研讨会跟进序列生成服务
- 感谢邮件
- 内容资源
- 后续线索培养
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class WebinarFollowupSequenceGeneratorService:
    """
    网络研讨会跟进序列生成服务

    生成网络研讨会跟进序列内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_webinar_followup_sequence(
        self,
        webinar_title: str,
        num_emails: int = 5,
        attendee_type: str = "registered",
    ) -> Dict[str, Any]:
        """
        生成网络研讨会跟进序列

        Args:
            webinar_title: 研讨会标题
            num_emails: 邮件数量
            attendee_type: 参会者类型

        Returns:
            Dict: 网络研讨会跟进序列
        """
        try:
            prompt = f"""请为"{webinar_title}"生成{attendee_type}参会者的{num_emails}封网络研讨会跟进序列邮件。

请以JSON格式返回：
{{
    "webinar_title": "研讨会标题",
    "num_emails": {num_emails},
    "attendee_type": "参会者类型",
    "emails": [
        {{
            "email_number": 1,
            "timing": "时机",
            "subject": "主题",
            "content_purpose": "内容目的",
            "body_summary": "正文摘要",
            "cta": "CTA"
        }}
    ],
    "content_upgrades": ["内容升级1"],
    "survey_feedback_request": "调查反馈请求",
    "on_demand_offer": "点播优惠",
    "next_webinar_promo": "下一个研讨会推广"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "webinar_title": webinar_title,
                "num_emails": num_emails,
                "attendee_type": attendee_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成网络研讨会跟进序列失败: {e}")
            return {
                "webinar_title": webinar_title,
                "num_emails": num_emails,
                "attendee_type": attendee_type,
                "emails": [],
                "content_upgrades": [],
                "survey_feedback_request": "",
                "on_demand_offer": "",
                "next_webinar_promo": "",
            }


webinar_followup_sequence_generator_service = WebinarFollowupSequenceGeneratorService()