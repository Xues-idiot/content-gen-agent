"""
Vox Content Calendar Generator Service 模块

内容日历生成服务
- 发布计划
- 内容主题
- 渠道分配
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ContentCalendarGeneratorService:
    """
    内容日历生成服务

    生成内容日历内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_content_calendar(
        self,
        month: str,
        channels: List[str],
        content_pillars: List[str],
    ) -> Dict[str, Any]:
        """
        生成内容日历

        Args:
            month: 月份
            channels: 渠道列表
            content_pillars: 内容支柱

        Returns:
            Dict: 内容日历
        """
        channels_str = ", ".join(channels)
        pillars_str = ", ".join(content_pillars)

        try:
            prompt = f"""请为{month}生成内容日历（渠道：{channels_str}，内容支柱：{pillars_str}）。

请以JSON格式返回：
{{
    "month": "月份",
    "channels": {channels},
    "content_pillars": {content_pillars},
    "overview_summary": "概述摘要",
    "posting_frequency": {{
        "channel": {{
            "posts_per_week": 数量,
            "best_days": ["最佳日期1"],
            "best_times": ["最佳时间1"]
        }}
    }},
    "weekly_themes": [
        {{
            "week": "周次",
            "theme": "主题",
            "goals": ["目标1"]
        }}
    ],
    "content_calendar": [
        {{
            "date": "日期",
            "day_of_week": "星期",
            "channel": "渠道",
            "content_type": "内容类型",
            "content_pillar": "内容支柱",
            "topic_title": "主题标题",
            "brief_description": "简要描述",
            "key_message": "关键信息",
            "cta": "CTA",
            "hashtags": ["标签1"],
            "media_type": "媒体类型",
            "status": "状态"
        }}
    ],
    "campaigns_during_month": [
        {{
            "name": "活动名称",
            "dates": "日期",
            "description": "描述"
        }}
    ],
    "seasonal_observations": ["季节性观察1"],
    "team_responsibilities": {{
        "creation": "创建",
        "approval": "审批",
        "posting": "发布"
    }},
    "performance_benchmarks": "绩效基准"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "month": month,
                "channels": channels,
                "content_pillars": content_pillars,
                **result,
            }

        except Exception as e:
            logger.error(f"生成内容日历失败: {e}")
            return {
                "month": month,
                "channels": channels,
                "content_pillars": content_pillars,
                "overview_summary": "",
                "posting_frequency": {},
                "weekly_themes": [],
                "content_calendar": [],
                "campaigns_during_month": [],
                "seasonal_observations": [],
                "team_responsibilities": {},
                "performance_benchmarks": "",
            }


content_calendar_generator_service = ContentCalendarGeneratorService()