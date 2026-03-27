"""
Vox Seasonal Content Generator Service 模块

季节性内容生成服务
- 节日内容
- 季节主题
- 时效性内容
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class SeasonalContentGeneratorService:
    """
    季节性内容生成服务

    生成节日和季节性内容
    """

    def __init__(self):
        self.llm = llm_service

    # 节日列表
    FESTIVALS = [
        "春节", "元宵节", "情人节", "妇女节", "清明节",
        "劳动节", "端午节", "中秋节", "国庆节", "万圣节",
        "感恩节", "圣诞节", "元旦", "618", "双11",
    ]

    async def generate_festival_content(
        self,
        festival: str,
        product_info: Dict[str, Any],
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        生成节日内容

        Args:
            festival: 节日
            product_info: 产品信息
            platform: 平台

        Returns:
            Dict: 节日内容
        """
        try:
            prompt = f"""请为"{festival}"生成一个{product_info.get('name', '')}的节日内容创意。

平台：{platform}

请以JSON格式返回：
{{
    "festival": "{festival}",
    "content_idea": "内容创意",
    "title": "标题",
    "key_points": ["要点1", "要点2"],
    "hashtag_suggestions": ["#标签1", "#标签2"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "festival": festival,
                "product_name": product_info.get("name", ""),
                "platform": platform,
                **result,
            }

        except Exception as e:
            logger.error(f"生成节日内容失败: {e}")
            return {
                "festival": festival,
                "product_name": product_info.get("name", ""),
                "platform": platform,
                "content_idea": "",
                "title": "",
                "key_points": [],
                "hashtag_suggestions": [],
            }

    def get_festivals(self) -> List[str]:
        """获取节日列表"""
        return self.FESTIVALS


seasonal_content_generator_service = SeasonalContentGeneratorService()