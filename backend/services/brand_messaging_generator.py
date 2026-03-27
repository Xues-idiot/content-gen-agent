"""
Vox Brand Messaging Generator Service 模块

品牌话术生成服务
- 品牌语调
- 沟通风格
- 话术模板
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class BrandMessagingGeneratorService:
    """
    品牌话术生成服务

    生成品牌话术内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_brand_messaging(
        self,
        brand_name: str,
        industry: str,
        communication_context: str = "general",
    ) -> Dict[str, Any]:
        """
        生成品牌话术

        Args:
            brand_name: 品牌名称
            industry: 行业
            communication_context: 沟通场景

        Returns:
            Dict: 品牌话术
        """
        try:
            prompt = f"""请为"{brand_name}"（{industry}行业）生成{communication_context}场景的品牌话术。

请以JSON格式返回：
{{
    "brand_name": "品牌名称",
    "industry": "行业",
    "communication_context": "沟通场景",
    "tone_of_voice": "语调",
    "messaging_framework": "话术框架",
    "key_messages": ["关键信息1"],
    "sample_copy": {{
        "headline": "标题文案",
        "tagline": "标语",
        "description": "描述文案",
        "cta": "行动号召"
    }},
    "do_and_donts": {{
        "do": ["可以做1"],
        "donts": ["不要做1"]
    }},
    "platform_specific_messaging": ["平台特定话术1"],
    "industry_terms": ["行业术语1"],
    "forbidden_words": ["禁用词1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "brand_name": brand_name,
                "industry": industry,
                "communication_context": communication_context,
                **result,
            }

        except Exception as e:
            logger.error(f"生成品牌话术失败: {e}")
            return {
                "brand_name": brand_name,
                "industry": industry,
                "communication_context": communication_context,
                "tone_of_voice": "",
                "messaging_framework": "",
                "key_messages": [],
                "sample_copy": {},
                "do_and_donts": {"do": [], "donts": []},
                "platform_specific_messaging": [],
                "industry_terms": [],
                "forbidden_words": [],
            }


brand_messaging_generator_service = BrandMessagingGeneratorService()