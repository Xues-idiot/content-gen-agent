"""
Vox Social Media Policy Generator Service 模块

社交媒体政策生成服务
- 发布准则
- 品牌声音
- 风险管理
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SocialMediaPolicyGeneratorService:
    """
    社交媒体政策生成服务

    生成社交媒体政策内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_social_media_policy(
        self,
        company_name: str,
        num_sections: int = 8,
    ) -> Dict[str, Any]:
        """
        生成社交媒体政策

        Args:
            company_name: 公司名称
            num_sections: 章节数量

        Returns:
            Dict: 社交媒体政策
        """
        try:
            prompt = f"""请为"{company_name}"生成包含{num_sections}章的社交媒体政策。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "num_sections": 章节数,
    "effective_date": "生效日期",
    "purpose": "目的",
    "scope": "范围",
    "sections": [
        {{
            "section_title": "章节标题",
            "content": "内容",
            "guidelines": ["指南1"]
        }}
    ],
    "brand_voice_guidelines": "品牌声音指南",
    "content_guidelines": "内容指南",
    "dos_and_donts": {{
        "do": ["可以做1"],
        "dont": ["不要做1"]
    }},
    "disclosure_requirements": "披露要求",
    "confidentiality": "保密性",
    "legal_compliance": "法律合规",
    "crisis_management": "危机管理",
    "employee_guidelines": "员工指南",
    "approval_process": "审批流程",
    "monitoring": "监控",
    "enforcement": "执行",
    "training_requirements": "培训要求",
    "contact_information": "联系信息"
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
                "num_sections": num_sections,
                **result,
            }

        except Exception as e:
            logger.error(f"生成社交媒体政策失败: {e}")
            return {
                "company_name": company_name,
                "num_sections": num_sections,
                "effective_date": "",
                "purpose": "",
                "scope": "",
                "sections": [],
                "brand_voice_guidelines": "",
                "content_guidelines": "",
                "dos_and_donts": {"do": [], "dont": []},
                "disclosure_requirements": "",
                "confidentiality": "",
                "legal_compliance": "",
                "crisis_management": "",
                "employee_guidelines": "",
                "approval_process": "",
                "monitoring": "",
                "enforcement": "",
                "training_requirements": "",
                "contact_information": "",
            }


social_media_policy_generator_service = SocialMediaPolicyGeneratorService()