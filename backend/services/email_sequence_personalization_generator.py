"""
Vox Email Sequence Personalization Generator Service 模块

邮件序列个性化生成服务
- 行为触发
- 个性化元素
- 动态内容
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class EmailSequencePersonalizationGeneratorService:
    """
    邮件序列个性化生成服务

    生成邮件序列个性化内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_email_sequence_personalization(
        self,
        sequence_name: str,
        trigger_event: str,
        num_emails: int = 5,
    ) -> Dict[str, Any]:
        """
        生成邮件序列个性化

        Args:
            sequence_name: 序列名称
            trigger_event: 触发事件
            num_emails: 邮件数量

        Returns:
            Dict: 邮件序列个性化
        """
        try:
            prompt = f"""请为"{sequence_name}"（触发事件：{trigger_event}）生成{num_emails}封个性化邮件序列。

请以JSON格式返回：
{{
    "sequence_name": "序列名称",
    "trigger_event": "触发事件",
    "num_emails": {num_emails},
    "personalization_tokens": ["个性化令牌1"],
    "dynamic_content_blocks": ["动态内容块1"],
    "emails": [
        {{
            "email_number": 1,
            "subject_line": "主题行",
            "preview_text": "预览文本",
            "body_template": "正文模板",
            "personalization_by_trigger": "按触发器的个性化"
        }}
    ],
    "segment_criteria": "细分标准",
    "a_b_test_ideas": ["A/B测试创意1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "sequence_name": sequence_name,
                "trigger_event": trigger_event,
                "num_emails": num_emails,
                **result,
            }

        except Exception as e:
            logger.error(f"生成邮件序列个性化失败: {e}")
            return {
                "sequence_name": sequence_name,
                "trigger_event": trigger_event,
                "num_emails": num_emails,
                "personalization_tokens": [],
                "dynamic_content_blocks": [],
                "emails": [],
                "segment_criteria": "",
                "a_b_test_ideas": [],
            }


email_sequence_personalization_generator_service = EmailSequencePersonalizationGeneratorService()