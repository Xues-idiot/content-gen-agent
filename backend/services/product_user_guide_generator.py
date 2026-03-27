"""
Vox Product User Guide Generator Service 模块

产品用户指南生成服务
- 操作说明
- 使用教程
- 故障排除
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductUserGuideGeneratorService:
    """
    产品用户指南生成服务

    生成产品用户指南内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_product_user_guide(
        self,
        product_name: str,
        audience: str = "end users",
        num_sections: int = 8,
    ) -> Dict[str, Any]:
        """
        生成产品用户指南

        Args:
            product_name: 产品名称
            audience: 目标受众
            num_sections: 章节数量

        Returns:
            Dict: 产品用户指南
        """
        try:
            prompt = f"""请为"{product_name}"生成面向"{audience}"的用户指南（共{num_sections}章节）。

请以JSON格式返回：
{{
    "product_name": "产品名称",
    "audience": "目标受众",
    "num_sections": 章节数,
    "title": "标题",
    "introduction": "引言",
    "sections": [
        {{
            "section_title": "章节标题",
            "content": "内容",
            "subsections": ["子章节1"],
            "examples": ["示例1"]
        }}
    ],
    "troubleshooting": [
        {{
            "issue": "问题",
            "solution": "解决方案"
        }}
    ],
    "faqs": ["常见问题1"],
    "glossary": ["术语表1"],
    "contact_support": "联系支持"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "product_name": product_name,
                "audience": audience,
                "num_sections": num_sections,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品用户指南失败: {e}")
            return {
                "product_name": product_name,
                "audience": audience,
                "num_sections": num_sections,
                "title": "",
                "introduction": "",
                "sections": [],
                "troubleshooting": [],
                "faqs": [],
                "glossary": [],
                "contact_support": "",
            }


product_user_guide_generator_service = ProductUserGuideGeneratorService()