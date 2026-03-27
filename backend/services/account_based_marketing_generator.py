"""
Vox Account Based Marketing Generator Service 模块

账户营销生成服务
- 目标账户
- 个性化内容
- 多渠道策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class AccountBasedMarketingGeneratorService:
    """
    账户营销生成服务

    生成账户营销内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_account_based_marketing(
        self,
        target_company: str,
        industry: str,
        num_channels: int = 3,
    ) -> Dict[str, Any]:
        """
        生成账户营销

        Args:
            target_company: 目标公司
            industry: 行业
            num_channels: 渠道数量

        Returns:
            Dict: 账户营销
        """
        try:
            prompt = f"""请为"{target_company}"（{industry}行业）生成基于账户的营销内容（{num_channels}个渠道）。

请以JSON格式返回：
{{
    "target_company": "目标公司",
    "industry": "行业",
    "num_channels": {num_channels},
    "company_research": {{
        "company_size": "公司规模",
        "key_decision_makers": ["关键决策者1"],
        "recent_news": ["最新消息1"],
        "pain_points": ["痛点1"]
    }},
    "personalized_content": [
        {{
            "content_type": "内容类型",
            "headline": "标题",
            "key_message": "关键信息",
            "relevance_to_target": "与目标的相关性"
        }}
    ],
    "channel_strategy": [
        {{
            "channel": "渠道",
            "tactic": "策略",
            "content_piece": "内容片段",
            "timing": "时机"
        }}
    ],
    "outreach_sequence": [
        {{
            "step": "步骤",
            "channel": "渠道",
            "message": "消息",
            "goal": "目标"
        }}
    ],
    "roi_projections": "ROI预测",
    "success_metrics": ["成功指标1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "target_company": target_company,
                "industry": industry,
                "num_channels": num_channels,
                **result,
            }

        except Exception as e:
            logger.error(f"生成账户营销失败: {e}")
            return {
                "target_company": target_company,
                "industry": industry,
                "num_channels": num_channels,
                "company_research": {},
                "personalized_content": [],
                "channel_strategy": [],
                "outreach_sequence": [],
                "roi_projections": "",
                "success_metrics": [],
            }


account_based_marketing_generator_service = AccountBasedMarketingGeneratorService()