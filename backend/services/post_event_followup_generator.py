"""
Vox Post Event Followup Generator Service 模块

活动后续生成服务
- 感谢信
- 活动总结
- 后续行动
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PostEventFollowupGeneratorService:
    """
    活动后续生成服务

    生成活动后续内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_post_event_followup(
        self,
        event_name: str,
        event_date: str,
        followup_type: str = "thank you",
    ) -> Dict[str, Any]:
        """
        生成活动后续

        Args:
            event_name: 活动名称
            event_date: 活动日期
            followup_type: 后续类型

        Returns:
            Dict: 活动后续
        """
        try:
            prompt = f"""请为"{event_name}"（{event_date}）生成{followup_type}类型的活动后续内容。

请以JSON格式返回：
{{
    "event_name": "活动名称",
    "event_date": "活动日期",
    "followup_type": "后续类型",
    "thank_you_email": {{
        "subject": "主题",
        "body": "正文",
        "cta": "CTA"
    }},
    "event_summary": {{
        "highlights": ["亮点1"],
        "attendance_numbers": "出席人数",
        "key_takeaways": ["关键收获1"]
    }},
    "photos_media": ["照片/媒体1"],
    "surveys_feedback": ["调查/反馈1"],
    "next_steps_actions": [
        {{
            "action": "行动",
            "owner": "负责人",
            "due_date": "截止日期"
        }}
    ],
    "attendee_followup_templates": [
        {{
            "segment": "细分",
            "subject": "主题",
            "message": "消息"
        }}
    ],
    "speaker_thank_you": "演讲者感谢",
    "sponsor_thank_you": "赞助商感谢",
    "social_media_posts": ["社交媒体帖子1"],
    "content_sharing_plan": "内容分享计划",
    "lead_follow_up_sequence": ["潜在客户跟进序列1"],
    "roi_metrics": "ROI指标"
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
                "event_date": event_date,
                "followup_type": followup_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成活动后续失败: {e}")
            return {
                "event_name": event_name,
                "event_date": event_date,
                "followup_type": followup_type,
                "thank_you_email": {},
                "event_summary": {},
                "photos_media": [],
                "surveys_feedback": [],
                "next_steps_actions": [],
                "attendee_followup_templates": [],
                "speaker_thank_you": "",
                "sponsor_thank_you": "",
                "social_media_posts": [],
                "content_sharing_plan": "",
                "lead_follow_up_sequence": [],
                "roi_metrics": "",
            }


post_event_followup_generator_service = PostEventFollowupGeneratorService()