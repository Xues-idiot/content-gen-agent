"""
Vox Crisis Communication Generator Service 模块

危机公关生成服务
- 声明草稿
- 应对策略
- 媒体回复
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CrisisCommunicationGeneratorService:
    """
    危机公关生成服务

    生成危机公关内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_crisis_communication(
        self,
        company_name: str,
        crisis_type: str,
        severity: str = "medium",
    ) -> Dict[str, Any]:
        """
        生成危机公关

        Args:
            company_name: 公司名称
            crisis_type: 危机类型
            severity: 严重程度

        Returns:
            Dict: 危机公关
        """
        try:
            prompt = f"""请为"{company_name}"生成{crisis_type}危机的公关应对方案（严重程度：{severity}）。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "crisis_type": "危机类型",
    "severity": "严重程度",
    "initial_statement": "初步声明",
    "key_messages": ["关键信息1"],
    "response_timeline": "响应时间线",
    "media_response": "媒体回复模板",
    "social_media_response": "社交媒体回复",
    "internal_communication": "内部沟通",
    "corrective_actions": "纠正措施",
    "monitoring_plan": "监测计划",
    "recovery_strategy": "恢复策略"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "company_name": company_name,
                "crisis_type": crisis_type,
                "severity": severity,
                **result,
            }

        except Exception as e:
            logger.error(f"生成危机公关失败: {e}")
            return {
                "company_name": company_name,
                "crisis_type": crisis_type,
                "severity": severity,
                "initial_statement": "",
                "key_messages": [],
                "response_timeline": "",
                "media_response": "",
                "social_media_response": "",
                "internal_communication": "",
                "corrective_actions": [],
                "monitoring_plan": "",
                "recovery_strategy": "",
            }


crisis_communication_generator_service = CrisisCommunicationGeneratorService()