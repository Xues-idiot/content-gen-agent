"""
Vox Crisis Response Plan Generator Service 模块

危机响应计划生成服务
- 响应协议
- 消息模板
- 利益相关方沟通
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CrisisResponsePlanGeneratorService:
    """
    危机响应计划生成服务

    生成危机响应计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_crisis_response_plan(
        self,
        crisis_type: str,
        organization_name: str,
        severity_level: str = "moderate",
    ) -> Dict[str, Any]:
        """
        生成危机响应计划

        Args:
            crisis_type: 危机类型
            organization_name: 组织名称
            severity_level: 严重程度

        Returns:
            Dict: 危机响应计划
        """
        try:
            prompt = f"""请为"{organization_name}"生成{crisis_type}类型（严重程度：{severity_level}）的危机响应计划。

请以JSON格式返回：
{{
    "crisis_type": "危机类型",
    "organization_name": "组织名称",
    "severity_level": "严重程度",
    "response_team": [
        {{
            "role": "角色",
            "name": "姓名",
            "responsibilities": ["职责1"]
        }}
    ],
    "response_protocol": [
        {{
            "step": "步骤",
            "action": "行动",
            "responsible": "负责人",
            "timing": "时机"
        }}
    ],
    "key_messages": {{
        "internal": "内部信息",
        "external": "外部信息"
    }},
    "statement_templates": ["声明模板1"],
    "media_response": "媒体响应",
    "social_media_guidelines": "社交媒体指南",
    "stakeholder_communication": "利益相关方沟通",
    "post_crisis_review": "危机后审查"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "crisis_type": crisis_type,
                "organization_name": organization_name,
                "severity_level": severity_level,
                **result,
            }

        except Exception as e:
            logger.error(f"生成危机响应计划失败: {e}")
            return {
                "crisis_type": crisis_type,
                "organization_name": organization_name,
                "severity_level": severity_level,
                "response_team": [],
                "response_protocol": [],
                "key_messages": {},
                "statement_templates": [],
                "media_response": "",
                "social_media_guidelines": "",
                "stakeholder_communication": "",
                "post_crisis_review": "",
            }


crisis_response_plan_generator_service = CrisisResponsePlanGeneratorService()