"""
Vox Crisis Communication Plan Generator Service 模块

危机沟通计划生成服务
- 危机响应
- 消息模板
- 利益相关方沟通
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CrisisCommunicationPlanGeneratorService:
    """
    危机沟通计划生成服务

    生成危机沟通计划内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_crisis_communication_plan(
        self,
        organization_name: str,
        crisis_type: str,
        severity: str = "moderate",
    ) -> Dict[str, Any]:
        """
        生成危机沟通计划

        Args:
            organization_name: 组织名称
            crisis_type: 危机类型
            severity: 严重程度

        Returns:
            Dict: 危机沟通计划
        """
        try:
            prompt = f"""请为"{organization_name}"生成{crisis_type}类型（严重程度：{severity}）的危机沟通计划。

请以JSON格式返回：
{{
    "organization_name": "组织名称",
    "crisis_type": "危机类型",
    "severity": "严重程度",
    "plan_created_date": "计划创建日期",
    "executive_summary": "执行摘要",
    "crisis_assessment": {{
        "potential_impact": "潜在影响",
        "stakeholders_affected": ["受影响的利益相关方1"],
        "reputational_risk": "声誉风险"
    }},
    "response_team": [
        {{
            "role": "角色",
            "name": "姓名",
            "responsibilities": ["职责1"]
        }}
    ],
    "communication_channels": ["沟通渠道1"],
    "key_messages": {{
        "internal": ["内部信息1"],
        "external": ["外部信息1"]
    }},
    "statement_templates": [
        {{
            "audience": "受众",
            "situation": "情况",
            "template": "模板"
        }}
    ],
    "media_response": {{
        "press_contact": "媒体联系人",
        "holding_statement": "暂定声明",
        "faq": ["常见问题1"]
    }},
    "social_media_response": {{
        "monitoring_channels": ["监控渠道1"],
        "response_templates": ["响应模板1"]
    }},
    "stakeholder_communication": [
        {{
            "stakeholder": "利益相关方",
            "message": "消息",
            "timing": "时机"
        }}
    ],
    "timeline_actions": [
        {{
            "time": "时间",
            "action": "行动",
            "responsible": "负责人"
        }}
    ],
    "post_crisis_plan": "危机后计划",
    "training_requirements": "培训要求",
    "review_frequency": "审查频率"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "organization_name": organization_name,
                "crisis_type": crisis_type,
                "severity": severity,
                **result,
            }

        except Exception as e:
            logger.error(f"生成危机沟通计划失败: {e}")
            return {
                "organization_name": organization_name,
                "crisis_type": crisis_type,
                "severity": severity,
                "plan_created_date": "",
                "executive_summary": "",
                "crisis_assessment": {},
                "response_team": [],
                "communication_channels": [],
                "key_messages": {},
                "statement_templates": [],
                "media_response": {},
                "social_media_response": {},
                "stakeholder_communication": [],
                "timeline_actions": [],
                "post_crisis_plan": "",
                "training_requirements": "",
                "review_frequency": "",
            }


crisis_communication_plan_generator_service = CrisisCommunicationPlanGeneratorService()