"""
Vox Loyalty Program Launch Generator Service 模块

忠诚度计划启动生成服务
- 会员权益
- 积分规则
- 沟通策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class LoyaltyProgramLaunchGeneratorService:
    """
    忠诚度计划启动生成服务

    生成忠诚度计划启动内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_loyalty_program_launch(
        self,
        brand_name: str,
        program_name: str,
        member_tiers: int = 3,
    ) -> Dict[str, Any]:
        """
        生成忠诚度计划启动

        Args:
            brand_name: 品牌名称
            program_name: 计划名称
            member_tiers: 会员层级

        Returns:
            Dict: 忠诚度计划启动
        """
        try:
            prompt = f"""请为"{brand_name}"生成"{program_name}"忠诚度计划（{member_tiers}个会员层级）。

请以JSON格式返回：
{{
    "brand_name": "品牌名称",
    "program_name": "计划名称",
    "member_tiers": {member_tiers},
    "program_overview": "计划概述",
    "membership_tiers": [
        {{
            "tier_name": "层级名称",
            "requirements": "要求",
            "benefits": ["权益1"]
        }}
    ],
    "points_system": {{
        "earning_rules": "赚取规则",
        "redemption_options": ["兑换选项1"],
        "point_expiration": "积分过期"
    }},
    "launch_messaging": {{
        "announcement": "公告",
        "member_invitation": "会员邀请"
    }},
    "communication_plan": "沟通计划",
    "promotional_offer": "促销优惠"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "brand_name": brand_name,
                "program_name": program_name,
                "member_tiers": member_tiers,
                **result,
            }

        except Exception as e:
            logger.error(f"生成忠诚度计划启动失败: {e}")
            return {
                "brand_name": brand_name,
                "program_name": program_name,
                "member_tiers": member_tiers,
                "program_overview": "",
                "membership_tiers": [],
                "points_system": {},
                "launch_messaging": {},
                "communication_plan": "",
                "promotional_offer": "",
            }


loyalty_program_launch_generator_service = LoyaltyProgramLaunchGeneratorService()