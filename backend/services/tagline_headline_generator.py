"""
Vox Tagline Headline Generator Service 模块

标语标题生成服务
- 品牌标语
- 广告标题
- 价值主张
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TaglineHeadlineGeneratorService:
    """
    标语标题生成服务

    生成标语和标题内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_tagline_headline(
        self,
        brand_product: str,
        num_options: int = 10,
        tone: str = "professional",
    ) -> Dict[str, Any]:
        """
        生成标语和标题

        Args:
            brand_product: 品牌/产品
            num_options: 选项数量
            tone: 语气

        Returns:
            Dict: 标语和标题
        """
        try:
            prompt = f"""请为"{brand_product}"生成{num_options}个{tone}语气的标语和标题选项。

请以JSON格式返回：
{{
    "brand_product": "品牌/产品",
    "num_options": {num_options},
    "tone": "语气",
    "taglines": [
        {{
            "tagline": "标语",
            "category": "类别",
            "description": "描述",
            "use_cases": ["使用场景1"]
        }}
    ],
    "headlines": [
        {{
            "headline": "标题",
            "type": "类型",
            "platform_recommendation": "平台推荐"
        }}
    ],
    "value_propositions": [
        {{
            "proposition": "价值主张",
            "emphasis": "强调点"
        }}
    ],
    "brand_catchphrases": ["品牌流行语1"],
    "campaign_taglines": [
        {{
            "campaign": "活动",
            "tagline": "标语"
        }}
    ],
    "social_media_handles": ["社交媒体 handle1"],
    "domain_name_suggestions": ["域名建议1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "brand_product": brand_product,
                "num_options": num_options,
                "tone": tone,
                **result,
            }

        except Exception as e:
            logger.error(f"生成标语标题失败: {e}")
            return {
                "brand_product": brand_product,
                "num_options": num_options,
                "tone": tone,
                "taglines": [],
                "headlines": [],
                "value_propositions": [],
                "brand_catchphrases": [],
                "campaign_taglines": [],
                "social_media_handles": [],
                "domain_name_suggestions": [],
            }


tagline_headline_generator_service = TaglineHeadlineGeneratorService()