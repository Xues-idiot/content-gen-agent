"""
Vox Team Announcement Generator Service 模块

团队公告生成服务
- 组织变更
- 新成员
- 团队新闻
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TeamAnnouncementGeneratorService:
    """
    团队公告生成服务

    生成团队公告内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_team_announcement(
        self,
        announcement_type: str,
        audience: str,
        urgency: str = "normal",
    ) -> Dict[str, Any]:
        """
        生成团队公告

        Args:
            announcement_type: 公告类型
            audience: 受众
            urgency: 紧急程度

        Returns:
            Dict: 团队公告
        """
        try:
            prompt = f"""请生成{announcement_type}类型的团队公告（受众：{audience}，紧急程度：{urgency}）。

请以JSON格式返回：
{{
    "announcement_type": "公告类型",
    "audience": "受众",
    "urgency": "紧急程度",
    "subject": "主题",
    "headline": "标题",
    "body": "正文",
    "key_points": ["关键点1"],
    "action_required": [
        {{
            "action": "行动",
            "responsible": "负责人",
            "deadline": "截止日期"
        }}
    ],
    "attachments": ["附件1"],
    "contact_info": "联系信息",
    "response_deadline": "回复截止日期",
    "follow_up_date": "跟进日期"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "announcement_type": announcement_type,
                "audience": audience,
                "urgency": urgency,
                **result,
            }

        except Exception as e:
            logger.error(f"生成团队公告失败: {e}")
            return {
                "announcement_type": announcement_type,
                "audience": audience,
                "urgency": urgency,
                "subject": "",
                "headline": "",
                "body": "",
                "key_points": [],
                "action_required": [],
                "attachments": [],
                "contact_info": "",
                "response_deadline": "",
                "follow_up_date": "",
            }


team_announcement_generator_service = TeamAnnouncementGeneratorService()