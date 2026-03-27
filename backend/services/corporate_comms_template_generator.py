"""
Vox Corporate Communications Template Generator Service 模块

企业通讯模板生成服务
- 内部通讯
- 新闻稿
- 公告模板
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class CorporateCommsTemplateGeneratorService:
    """
    企业通讯模板生成服务

    生成企业通讯模板内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_corporate_comms_template(
        self,
        comms_type: str,
        company_name: str,
        urgency: str = "normal",
    ) -> Dict[str, Any]:
        """
        生成企业通讯模板

        Args:
            comms_type: 通讯类型
            company_name: 公司名称
            urgency: 紧急程度

        Returns:
            Dict: 企业通讯模板
        """
        try:
            prompt = f"""请为"{company_name}"生成{comms_type}类型（紧急程度：{urgency}）的企业通讯模板。

请以JSON格式返回：
{{
    "comms_type": "通讯类型",
    "company_name": "公司名称",
    "urgency": "紧急程度",
    "template_structure": "模板结构",
    "subject_line": "主题行",
    "header": "头部",
    "body_sections": [
        {{
            "section_title": "章节标题",
            "content": "内容",
            "tone": "语气"
        }}
    ],
    "call_to_action": "行动号召",
    "signature_block": "签名栏",
    "attachments": ["附件1"],
    "distribution_list": "分发列表",
    "timing_recommendations": "时间建议",
    "tone_guidance": "语气指导",
    "branding_guidelines": "品牌指南",
    "legal_disclaimer": "法律免责声明"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "comms_type": comms_type,
                "company_name": company_name,
                "urgency": urgency,
                **result,
            }

        except Exception as e:
            logger.error(f"生成企业通讯模板失败: {e}")
            return {
                "comms_type": comms_type,
                "company_name": company_name,
                "urgency": urgency,
                "template_structure": "",
                "subject_line": "",
                "header": "",
                "body_sections": [],
                "call_to_action": "",
                "signature_block": "",
                "attachments": [],
                "distribution_list": "",
                "timing_recommendations": "",
                "tone_guidance": "",
                "branding_guidelines": "",
                "legal_disclaimer": "",
            }


corporate_comms_template_generator_service = CorporateCommsTemplateGeneratorService()