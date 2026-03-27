"""
Vox Email Sequence Generator Service 模块

邮件序列生成服务
- 欢迎序列
- 培育序列
- 跟进序列
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class EmailSequenceGeneratorService:
    """
    邮件序列生成服务

    生成邮件序列内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_email_sequence(
        self,
        sequence_type: str,
        product_name: str,
        num_emails: int = 5,
        target_audience: str = "new leads",
    ) -> Dict[str, Any]:
        """
        生成邮件序列

        Args:
            sequence_type: 序列类型
            product_name: 产品名称
            num_emails: 邮件数量
            target_audience: 目标受众

        Returns:
            Dict: 邮件序列
        """
        try:
            prompt = f"""请为"{product_name}"生成{sequence_type}邮件序列（{num_emails}封，目标受众：{target_audience}）。

请以JSON格式返回：
{{
    "sequence_type": "序列类型",
    "product_name": "产品名称",
    "num_emails": 邮件数量,
    "target_audience": "目标受众",
    "sequence_overview": "序列概述",
    "emails": [
        {{
            "email_number": 1,
            "subject": "邮件主题",
            "preheader": "预header",
            "body": "邮件正文",
            "timing": "发送时间",
            "goal": "目标"
        }}
    ],
    "conversion_goals": ["转化目标1"],
    "performance_metrics": "性能指标"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "sequence_type": sequence_type,
                "product_name": product_name,
                "num_emails": num_emails,
                "target_audience": target_audience,
                **result,
            }

        except Exception as e:
            logger.error(f"生成邮件序列失败: {e}")
            return {
                "sequence_type": sequence_type,
                "product_name": product_name,
                "num_emails": num_emails,
                "target_audience": target_audience,
                "sequence_overview": "",
                "emails": [],
                "conversion_goals": [],
                "performance_metrics": "",
            }


email_sequence_generator_service = EmailSequenceGeneratorService()