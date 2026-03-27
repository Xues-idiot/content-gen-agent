"""
Vox About Us Generator Service 模块

关于我们页面生成服务
- 品牌故事
- 团队介绍
- 使命愿景
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class AboutUsGeneratorService:
    """
    About Us页面生成服务

    生成品牌介绍内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_about_us(
        self,
        brand_name: str,
        brand_type: str = "business",
    ) -> Dict[str, Any]:
        """
        生成About Us内容

        Args:
            brand_name: 品牌名称
            brand_type: 品牌类型

        Returns:
            Dict: About Us内容
        """
        try:
            prompt = f"""请为"{brand_name}"生成About Us页面内容。

类型：{brand_type}

请以JSON格式返回：
{{
    "story": "品牌故事",
    "mission": "使命",
    "vision": "愿景",
    "values": ["价值1", "价值2"],
    "team_highlight": "团队亮点"
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
                "brand_type": brand_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成About Us失败: {e}")
            return {
                "brand_name": brand_name,
                "brand_type": brand_type,
                "story": "",
                "mission": "",
                "vision": "",
                "values": [],
                "team_highlight": "",
            }


about_us_generator_service = AboutUsGeneratorService()