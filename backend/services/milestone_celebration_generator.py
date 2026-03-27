"""
Vox Milestone Celebration Generator Service 模块

里程碑庆祝生成服务
- 成就庆祝
- 团队认可
- 庆祝信息
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class MilestoneCelebrationGeneratorService:
    """
    里程碑庆祝生成服务

    生成里程碑庆祝内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_milestone_celebration(
        self,
        milestone: str,
        team_name: str = "团队",
        achievement_type: str = "performance",
    ) -> Dict[str, Any]:
        """
        生成里程碑庆祝

        Args:
            milestone: 里程碑
            team_name: 团队名称
            achievement_type: 成就类型

        Returns:
            Dict: 里程碑庆祝
        """
        try:
            prompt = f"""请为"{team_name}"达成"{milestone}"（类型：{achievement_type}）生成庆祝内容。

请以JSON格式返回：
{{
    "milestone": "里程碑",
    "team_name": "团队名称",
    "achievement_type": "成就类型",
    "celebration_title": "庆祝标题",
    "achievement_highlights": ["成就亮点1"],
    "team_shoutouts": ["团队表扬1"],
    "key_contributors": ["关键贡献者1"],
    "memorable_moments": ["难忘时刻1"],
    "social_media_post": "社交媒体帖子",
    "internal_communication": "内部沟通",
    "next_goals": ["下一个目标1"],
    "celebration_ideas": ["庆祝建议1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "milestone": milestone,
                "team_name": team_name,
                "achievement_type": achievement_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成里程碑庆祝失败: {e}")
            return {
                "milestone": milestone,
                "team_name": team_name,
                "achievement_type": achievement_type,
                "celebration_title": "",
                "achievement_highlights": [],
                "team_shoutouts": [],
                "key_contributors": [],
                "memorable_moments": [],
                "social_media_post": "",
                "internal_communication": "",
                "next_goals": [],
                "celebration_ideas": [],
            }


milestone_celebration_generator_service = MilestoneCelebrationGeneratorService()