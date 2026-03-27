"""
Vox Affiliate Program Launch Generator Service 模块

联盟计划启动生成服务
- 计划详情
- 佣金结构
- 推广素材
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class AffiliateProgramLaunchGeneratorService:
    """
    联盟计划启动生成服务

    生成联盟计划启动内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_affiliate_program_launch(
        self,
        brand_name: str,
        commission_structure: str,
        program_name: str = "affiliate program",
    ) -> Dict[str, Any]:
        """
        生成联盟计划启动

        Args:
            brand_name: 品牌名称
            commission_structure: 佣金结构
            program_name: 计划名称

        Returns:
            Dict: 联盟计划启动
        """
        try:
            prompt = f"""请为"{brand_name}"的{program_name}（佣金结构：{commission_structure}）生成启动内容。

请以JSON格式返回：
{{
    "brand_name": "品牌名称",
    "commission_structure": "佣金结构",
    "program_name": "计划名称",
    "announcement_headline": "公告标题",
    "program_overview": "计划概述",
    "commission_tiers": [
        {{
            "tier": "层级",
            "commission_rate": "佣金率",
            "requirements": "要求"
        }}
    ],
    "cookie_duration": "Cookie持续时间",
    "payment_methods": ["支付方式1"],
    "payment_schedule": "支付计划",
    "affiliate_benefits": ["联盟伙伴好处1"],
    "getting_started_steps": ["入门步骤1"],
    "approved_traffic_types": ["批准流量类型1"],
    "prohibited_practices": ["禁止做法1"],
    "marketing_assets": ["营销素材1"],
    "affiliate_support": "联盟伙伴支持",
    "faq": [
        {{
            "question": "问题",
            "answer": "答案"
        }}
    ],
    "affiliate_agreement_summary": "联盟协议摘要",
    "signup_cta": "注册CTA"
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
                "commission_structure": commission_structure,
                "program_name": program_name,
                **result,
            }

        except Exception as e:
            logger.error(f"生成联盟计划启动失败: {e}")
            return {
                "brand_name": brand_name,
                "commission_structure": commission_structure,
                "program_name": program_name,
                "announcement_headline": "",
                "program_overview": "",
                "commission_tiers": [],
                "cookie_duration": "",
                "payment_methods": [],
                "payment_schedule": "",
                "affiliate_benefits": [],
                "getting_started_steps": [],
                "approved_traffic_types": [],
                "prohibited_practices": [],
                "marketing_assets": [],
                "affiliate_support": "",
                "faq": [],
                "affiliate_agreement_summary": "",
                "signup_cta": "",
            }


affiliate_program_launch_generator_service = AffiliateProgramLaunchGeneratorService()