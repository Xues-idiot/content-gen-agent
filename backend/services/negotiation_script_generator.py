"""
Vox Negotiation Script Generator Service 模块

谈判话术生成服务
- 谈判策略
- 让步模式
- 成交技巧
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class NegotiationScriptGeneratorService:
    """
    谈判话术生成服务

    生成谈判话术内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_negotiation_script(
        self,
        negotiation_type: str,
        counterpart_role: str,
        num_scenarios: int = 6,
    ) -> Dict[str, Any]:
        """
        生成谈判话术

        Args:
            negotiation_type: 谈判类型
            counterpart_role: 对手角色
            num_scenarios: 场景数量

        Returns:
            Dict: 谈判话术
        """
        try:
            prompt = f"""请为{negotiation_type}类型谈判生成与{counterpart_role}对话的{num_scenarios}个场景的谈判话术。

请以JSON格式返回：
{{
    "negotiation_type": "谈判类型",
    "counterpart_role": "对手角色",
    "num_scenarios": {num_scenarios},
    "negotiation_strategy": "谈判策略",
    "preparation_checklist": ["准备清单1"],
    "scenarios": [
        {{
            "scenario": "场景",
            "opening_statement": "开场陈述",
            "key_talking_points": ["关键话题1"],
            "potential_objections": ["潜在异议1"],
            "response_scripts": ["响应话术1"]
        }}
    ],
    "concession_strategy": "让步策略",
    "BATNA_preparation": "BATNA准备",
    "closing_techniques": ["成交技巧1"],
    "walk_away_indicators": ["离开指标1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "negotiation_type": negotiation_type,
                "counterpart_role": counterpart_role,
                "num_scenarios": num_scenarios,
                **result,
            }

        except Exception as e:
            logger.error(f"生成谈判话术失败: {e}")
            return {
                "negotiation_type": negotiation_type,
                "counterpart_role": counterpart_role,
                "num_scenarios": num_scenarios,
                "negotiation_strategy": "",
                "preparation_checklist": [],
                "scenarios": [],
                "concession_strategy": "",
                "BATNA_preparation": "",
                "closing_techniques": [],
                "walk_away_indicators": [],
            }


negotiation_script_generator_service = NegotiationScriptGeneratorService()
