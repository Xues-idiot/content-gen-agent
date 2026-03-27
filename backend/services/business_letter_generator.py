"""
Vox Business Letter Generator Service 模块

商业信函生成服务
- 信函格式
- 专业用语
- 签署信息
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BusinessLetterGeneratorService:
    """
    商业信函生成服务

    生成商业信函内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_business_letter(
        self,
        letter_type: str,
        recipient_name: str,
        sender_name: str,
        subject: str,
    ) -> Dict[str, Any]:
        """
        生成商业信函

        Args:
            letter_type: 信函类型
            recipient_name: 收件人姓名
            sender_name: 发件人姓名
            subject: 主题

        Returns:
            Dict: 商业信函
        """
        try:
            prompt = f"""请生成{letter_type}类型的商业信函（收件人：{recipient_name}，发件人：{sender_name}，主题：{subject}）。

请以JSON格式返回：
{{
    "letter_type": "信函类型",
    "date": "日期",
    "recipient": {{
        "name": "姓名",
        "title": "职位",
        "company": "公司",
        "address": "地址"
    }},
    "sender": {{
        "name": "姓名",
        "title": "职位",
        "company": "公司",
        "address": "地址"
    }},
    "subject": "主题",
    "salutation": "称呼",
    "body": {{
        "opening": "开头",
        "main_content": "主要内容",
        "closing": "结尾"
    }},
    "enclosures": ["附件1"],
    "cc": ["抄送1"],
    "signature_block": "签名栏",
    "formatting_notes": "格式说明"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "letter_type": letter_type,
                "recipient_name": recipient_name,
                "sender_name": sender_name,
                "subject": subject,
                **result,
            }

        except Exception as e:
            logger.error(f"生成商业信函失败: {e}")
            return {
                "letter_type": letter_type,
                "recipient_name": recipient_name,
                "sender_name": sender_name,
                "subject": subject,
                "date": "",
                "recipient": {},
                "sender": {},
                "salutation": "",
                "body": {},
                "enclosures": [],
                "cc": [],
                "signature_block": "",
                "formatting_notes": "",
            }


business_letter_generator_service = BusinessLetterGeneratorService()