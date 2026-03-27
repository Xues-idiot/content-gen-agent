"""
Vox Press Release Angles Generator Service 模块

新闻稿角度生成服务
- 新闻由头
- 媒体钩子
- 故事角度
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PressReleaseAnglesGeneratorService:
    """
    新闻稿角度生成服务

    生成新闻稿角度内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_press_release_angles(
        self,
        company_name: str,
        news_type: str,
        num_angles: int = 5,
    ) -> Dict[str, Any]:
        """
        生成新闻稿角度

        Args:
            company_name: 公司名称
            news_type: 新闻类型
            num_angles: 角度数量

        Returns:
            Dict: 新闻稿角度
        """
        try:
            prompt = f"""请为"{company_name}"生成{num_angles}个{news_type}类型的新闻稿角度。

请以JSON格式返回：
{{
    "company_name": "公司名称",
    "news_type": "新闻类型",
    "num_angles": {num_angles},
    "angles": [
        {{
            "angle_title": "角度标题",
            "news_hook": "新闻钩子",
            "story_angle": "故事角度",
            "target_media": "目标媒体",
            "potential_headline": "潜在标题"
        }}
    ],
    "timing_recommendations": "时机建议",
    " multimedia_assets_needed": "需要的多媒体素材"
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
                "news_type": news_type,
                "num_angles": num_angles,
                **result,
            }

        except Exception as e:
            logger.error(f"生成新闻稿角度失败: {e}")
            return {
                "company_name": company_name,
                "news_type": news_type,
                "num_angles": num_angles,
                "angles": [],
                "timing_recommendations": "",
                "multimedia_assets_needed": "",
            }


press_release_angles_generator_service = PressReleaseAnglesGeneratorService()