"""
Vox Client Intake Form Generator Service 模块

客户 intake 表单生成服务
- 信息收集
- 需求问卷
- 协议确认
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ClientIntakeFormGeneratorService:
    """
    客户intake表单生成服务

    生成客户intake表单内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_client_intake_form(
        self,
        business_type: str,
        form_length: str = "standard",
        num_sections: int = 5,
    ) -> Dict[str, Any]:
        """
        生成客户intake表单

        Args:
            business_type: 业务类型
            form_length: 表单长度
            num_sections: 部分数量

        Returns:
            Dict: 客户intake表单
        """
        try:
            prompt = f"""请为{business_type}业务生成{num_sections}部分的{form_length}长度客户intake表单。

请以JSON格式返回：
{{
    "business_type": "业务类型",
    "form_length": "表单长度",
    "num_sections": {num_sections},
    "form_title": "表单标题",
    "intro_text": "介绍文本",
    "sections": [
        {{
            "section_name": "部分名称",
            "fields": [
                {{
                    "field_name": "字段名称",
                    "field_type": "字段类型",
                    "required": true,
                    "placeholder": "占位符"
                }}
            ]
        }}
    ],
    "consent_checkboxes": ["同意复选框1"],
    "submission_instructions": "提交说明",
    "follow_up_process": "跟进流程"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "business_type": business_type,
                "form_length": form_length,
                "num_sections": num_sections,
                **result,
            }

        except Exception as e:
            logger.error(f"生成客户intake表单失败: {e}")
            return {
                "business_type": business_type,
                "form_length": form_length,
                "num_sections": num_sections,
                "form_title": "",
                "intro_text": "",
                "sections": [],
                "consent_checkboxes": [],
                "submission_instructions": "",
                "follow_up_process": "",
            }


client_intake_form_generator_service = ClientIntakeFormGeneratorService()