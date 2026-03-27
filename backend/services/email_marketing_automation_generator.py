"""
Vox Email Marketing Automation Generator Service 模块

邮件营销自动化生成服务
- 自动化流程
- 触发条件
- 内容序列
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class EmailMarketingAutomationGeneratorService:
    """
    邮件营销自动化生成服务

    生成邮件营销自动化内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_email_marketing_automation(
        self,
        campaign_name: str,
        trigger_type: str,
        num_emails: int = 5,
    ) -> Dict[str, Any]:
        """
        生成邮件营销自动化

        Args:
            campaign_name: 活动名称
            trigger_type: 触发类型
            num_emails: 邮件数量

        Returns:
            Dict: 邮件营销自动化
        """
        try:
            prompt = f"""请为"{campaign_name}"生成基于{trigger_type}触发的{num_emails}封邮件的营销自动化流程。

请以JSON格式返回：
{{
    "campaign_name": "活动名称",
    "trigger_type": "触发类型",
    "num_emails": {num_emails},
    "automation_flow_name": "自动化流程名称",
    "trigger_conditions": ["触发条件1"],
    "email_sequence": [
        {{
            "email_number": "邮件编号",
            "subject_line": "主题行",
            "send_timing": "发送时间",
            "content_purpose": "内容目的",
            "call_to_action": "行动号召"
        }}
    ],
    "segmentation_criteria": "细分标准",
    "personalization_elements": ["个性化元素1"],
    "success_metrics": ["成功指标1"],
    "optimization_tips": ["优化技巧1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "campaign_name": campaign_name,
                "trigger_type": trigger_type,
                "num_emails": num_emails,
                **result,
            }

        except Exception as e:
            logger.error(f"生成邮件营销自动化失败: {e}")
            return {
                "campaign_name": campaign_name,
                "trigger_type": trigger_type,
                "num_emails": num_emails,
                "automation_flow_name": "",
                "trigger_conditions": [],
                "email_sequence": [],
                "segmentation_criteria": "",
                "personalization_elements": [],
                "success_metrics": [],
                "optimization_tips": [],
            }


email_marketing_automation_generator_service = EmailMarketingAutomationGeneratorService()
