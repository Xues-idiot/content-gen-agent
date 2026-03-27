"""
Vox Internal Memo Generator Service 模块

内部备忘录生成服务
- 通知内容
- 政策更新
- 决策沟通
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class InternalMemoGeneratorService:
    """
    内部备忘录生成服务

    生成内部备忘录内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_internal_memo(
        self,
        memo_subject: str,
        department: str,
        urgency: str = "normal",
    ) -> Dict[str, Any]:
        """
        生成内部备忘录

        Args:
            memo_subject: 备忘录主题
            department: 部门
            urgency: 紧急程度

        Returns:
            Dict: 内部备忘录
        """
        try:
            prompt = f"""请生成关于"{memo_subject}"的内部备忘录（部门：{department}，紧急程度：{urgency}）。

请以JSON格式返回：
{{
    "to": ["收件人1"],
    "from": "发件人",
    "date": "日期",
    "subject": "主题",
    "department": "部门",
    "urgency": "紧急程度",
    "summary": "摘要",
    "background": "背景",
    "details": "详情",
    "action_required": [
        {{
            "action": "行动",
            "owner": "负责人",
            "deadline": "截止日期"
        }}
    ],
    "attachments": ["附件1"],
    "distribution_list": ["分发列表1"],
    "response_required_by": "需要回复日期",
    "confidentiality_note": "保密说明"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "memo_subject": memo_subject,
                "department": department,
                "urgency": urgency,
                **result,
            }

        except Exception as e:
            logger.error(f"生成内部备忘录失败: {e}")
            return {
                "memo_subject": memo_subject,
                "department": department,
                "urgency": urgency,
                "to": [],
                "from": "",
                "date": "",
                "subject": "",
                "summary": "",
                "background": "",
                "details": "",
                "action_required": [],
                "attachments": [],
                "distribution_list": [],
                "response_required_by": "",
                "confidentiality_note": "",
            }


internal_memo_generator_service = InternalMemoGeneratorService()