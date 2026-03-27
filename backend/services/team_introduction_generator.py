"""
Vox Team Introduction Generator Service 模块

团队介绍生成服务
- 团队成员介绍
- 团队简介
- 成员分工
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TeamIntroductionGeneratorService:
    """
    团队介绍生成服务

    生成团队介绍内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_team_introduction(
        self,
        team_name: str,
        company_name: str,
        team_size: int = 5,
    ) -> Dict[str, Any]:
        """
        生成团队介绍

        Args:
            team_name: 团队名称
            company_name: 公司名称
            team_size: 团队规模

        Returns:
            Dict: 团队介绍
        """
        try:
            prompt = f"""请为"{team_name}"团队（属于{company_name}，共{team_size}人）生成团队介绍。

请以JSON格式返回：
{{
    "team_name": "团队名称",
    "tagline": "团队口号",
    "description": "团队描述",
    "core_values": ["价值观1", "价值观2"],
    "key_strengths": ["优势1"],
    "fun_facts": ["趣事1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "team_name": team_name,
                "company_name": company_name,
                "team_size": team_size,
                **result,
            }

        except Exception as e:
            logger.error(f"生成团队介绍失败: {e}")
            return {
                "team_name": team_name,
                "company_name": company_name,
                "team_size": team_size,
                "tagline": "",
                "description": "",
                "core_values": [],
                "key_strengths": [],
                "fun_facts": [],
            }


team_introduction_generator_service = TeamIntroductionGeneratorService()