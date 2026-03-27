"""
Vox Email Subject Line Generator Service 模块

邮件主题生成服务
- 邮件主题行
- 预览文本
- 打开率优化
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class EmailSubjectLineGeneratorService:
    """
    邮件主题生成服务

    生成邮件主题行
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_subject_lines(
        self,
        topic: str,
        num: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        生成邮件主题行

        Args:
            topic: 主题
            num: 数量

        Returns:
            List[Dict]: 主题行列表
        """
        try:
            prompt = f"""请为"{topic}"生成{num}个邮件主题行。

请以JSON格式返回：
{{
    "subject_lines": [
        {{
            "subject": "主题行",
            "preview_text": "预览文本",
            "open_rate_prediction": "高/中/低"
        }}
    ]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return result.get("subject_lines", [])

        except Exception as e:
            logger.error(f"生成邮件主题失败: {e}")
            return []


email_subject_line_generator_service = EmailSubjectLineGeneratorService()