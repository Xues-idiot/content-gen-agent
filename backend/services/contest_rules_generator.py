"""
Vox Contest Rules Generator Service 模块

抽奖活动规则生成服务
- 活动规则
- 参与条款
- 奖品说明
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ContestRulesGeneratorService:
    """
    抽奖活动规则生成服务

    生成活动规则和条款
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_contest_rules(
        self,
        contest_name: str,
        prize: str,
    ) -> Dict[str, Any]:
        """
        生成活动规则

        Args:
            contest_name: 活动名称
            prize: 奖品

        Returns:
            Dict: 活动规则
        """
        try:
            prompt = f"""请为"{contest_name}"（奖品：{prize}）生成活动规则。

请以JSON格式返回：
{{
    "title": "规则标题",
    "eligibility": "参与资格",
    "how_to_participate": "参与方式",
    "prize_description": "奖品描述",
    "selection_criteria": "评选标准",
    "terms_and_conditions": ["条款1", "条款2"],
    "timeline": "时间安排"
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
                "prize": prize,
                **result,
            }

        except Exception as e:
            logger.error(f"生成活动规则失败: {e}")
            return {
                "contest_name": contest_name,
                "prize": prize,
                "title": "",
                "eligibility": "",
                "how_to_participate": "",
                "prize_description": "",
                "selection_criteria": "",
                "terms_and_conditions": [],
                "timeline": "",
            }


contest_rules_generator_service = ContestRulesGeneratorService()