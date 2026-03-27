"""
Vox Website Copy Generator Service 模块

网站文案生成服务
- 页面文案
- 标题副标题
- 行动号召
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class WebsiteCopyGeneratorService:
    """
    网站文案生成服务

    生成网站文案内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_website_copy(
        self,
        page_name: str,
        business_type: str,
        target_audience: str,
    ) -> Dict[str, Any]:
        """
        生成网站文案

        Args:
            page_name: 页面名称
            business_type: 业务类型
            target_audience: 目标受众

        Returns:
            Dict: 网站文案
        """
        try:
            prompt = f"""请为"{page_name}"页面生成针对{target_audience}的{business_type}类型网站文案。

请以JSON格式返回：
{{
    "page_name": "页面名称",
    "business_type": "业务类型",
    "target_audience": "目标受众",
    "headline": "标题",
    "subheadline": "副标题",
    "hero_text": "英雄区文本",
    "section_copies": [
        {{
            "section_name": "章节名称",
            "heading": "标题",
            "copy": "文案"
        }}
    ],
    "cta_buttons": [
        {{
            "text": "文本",
            "placement": "位置"
        }}
    ],
    "footer_copy": "页脚文案",
    "meta_description": "元描述"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "page_name": page_name,
                "business_type": business_type,
                "target_audience": target_audience,
                **result,
            }

        except Exception as e:
            logger.error(f"生成网站文案失败: {e}")
            return {
                "page_name": page_name,
                "business_type": business_type,
                "target_audience": target_audience,
                "headline": "",
                "subheadline": "",
                "hero_text": "",
                "section_copies": [],
                "cta_buttons": [],
                "footer_copy": "",
                "meta_description": "",
            }


website_copy_generator_service = WebsiteCopyGeneratorService()