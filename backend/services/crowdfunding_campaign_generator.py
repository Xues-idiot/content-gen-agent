"""
Vox Crowdfunding Campaign Generator Service 模块

众筹活动生成服务
- 活动故事
- 回报设计
- 更新内容
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CrowdfundingCampaignGeneratorService:
    """
    众筹活动生成服务

    生成众筹活动内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_crowdfunding_campaign(
        self,
        project_name: str,
        platform: str,
        funding_goal: float,
    ) -> Dict[str, Any]:
        """
        生成众筹活动

        Args:
            project_name: 项目名称
            platform: 平台
            funding_goal: 融资目标

        Returns:
            Dict: 众筹活动
        """
        try:
            prompt = f"""请为"{project_name}"生成在{platform}平台的众筹活动（目标：${funding_goal}）。

请以JSON格式返回：
{{
    "project_name": "项目名称",
    "platform": "平台",
    "funding_goal": {funding_goal},
    "campaign_headline": "活动标题",
    "tagline": "标语",
    "elevator_pitch": "电梯演讲",
    "story_sections": [
        {{
            "section": "章节",
            "content": "内容",
            "media_suggestions": ["媒体建议1"]
        }}
    ],
    "problem_solution": {{
        "the_problem": "问题",
        "our_solution": "我们的解决方案",
        "how_it_works": "工作原理"
    }},
    "reward_tiers": [
        {{
            "tier_number": 1,
            "title": "标题",
            "pledge_amount": "承诺金额",
            "estimated_delivery": "预计交付",
            "items_included": ["包含物品1"],
            "limited_quantity": 数量
        }}
    ],
    "stretch_goals": [
        {{
            "amount": "金额",
            "description": "描述"
        }}
    ],
    "risks_challenges": "风险与挑战",
    "team_introduction": "团队介绍",
    "timeline_milestones": [
        {{
            "milestone": "里程碑",
            "date": "日期"
        }}
    ],
    "faq": [
        {{
            "question": "问题",
            "answer": "答案"
        }}
    ],
    "update_templates": ["更新模板1"],
    "social_media_plan": "社交媒体计划",
    "backer_rewards_ideas": ["支持者回报创意1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "project_name": project_name,
                "platform": platform,
                "funding_goal": funding_goal,
                **result,
            }

        except Exception as e:
            logger.error(f"生成众筹活动失败: {e}")
            return {
                "project_name": project_name,
                "platform": platform,
                "funding_goal": funding_goal,
                "campaign_headline": "",
                "tagline": "",
                "elevator_pitch": "",
                "story_sections": [],
                "problem_solution": {},
                "reward_tiers": [],
                "stretch_goals": [],
                "risks_challenges": "",
                "team_introduction": "",
                "timeline_milestones": [],
                "faq": [],
                "update_templates": [],
                "social_media_plan": "",
                "backer_rewards_ideas": [],
            }


crowdfunding_campaign_generator_service = CrowdfundingCampaignGeneratorService()