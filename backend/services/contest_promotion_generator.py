"""
Vox Contest Promotion Generator Service 模块

竞赛推广生成服务
- 活动规则
- 参与方式
- 奖品展示
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ContestPromotionGeneratorService:
    """
    竞赛推广生成服务

    生成竞赛推广内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_contest_promotion(
        self,
        contest_name: str,
        prize_value: str,
        entry_method: str,
    ) -> Dict[str, Any]:
        """
        生成竞赛推广

        Args:
            contest_name: 竞赛名称
            prize_value: 奖品价值
            entry_method: 参与方式

        Returns:
            Dict: 竞赛推广
        """
        try:
            prompt = f"""请为"{contest_name}"（奖品价值：{prize_value}，参与方式：{entry_method}）生成竞赛推广内容。

请以JSON格式返回：
{{
    "contest_name": "竞赛名称",
    "prize_value": "奖品价值",
    "entry_method": "参与方式",
    "campaign_headline": "活动标题",
    "campaign_description": "活动描述",
    "eligibility": "资格",
    "entry_period": "参与期限",
    "how_to_enter": "如何参与",
    "judging_criteria": ["评审标准1"],
    "prizes": [
        {{
            "prize_level": "奖品级别",
            "description": "描述",
            "value": "价值"
        }}
    ],
    "terms_and_conditions": ["条款和条件1"],
    "promotional_assets": ["推广素材1"],
    "social_media_copy": [
        {{
            "platform": "平台",
            "post_content": "帖子内容",
            "hashtags": ["标签1"]
        }}
    ],
    "email_sequence": [
        {{
            "email_type": "邮件类型",
            "subject": "主题",
            "content": "内容"
        }}
    ],
    "winner_announcement": "获奖者公告",
    "legal_disclaimer": "法律免责声明"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "contest_name": contest_name,
                "prize_value": prize_value,
                "entry_method": entry_method,
                **result,
            }

        except Exception as e:
            logger.error(f"生成竞赛推广失败: {e}")
            return {
                "contest_name": contest_name,
                "prize_value": prize_value,
                "entry_method": entry_method,
                "campaign_headline": "",
                "campaign_description": "",
                "eligibility": "",
                "entry_period": "",
                "how_to_enter": "",
                "judging_criteria": [],
                "prizes": [],
                "terms_and_conditions": [],
                "promotional_assets": [],
                "social_media_copy": [],
                "email_sequence": [],
                "winner_announcement": "",
                "legal_disclaimer": "",
            }


contest_promotion_generator_service = ContestPromotionGeneratorService()