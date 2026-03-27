"""
Vox Product Launch Generator Service 模块

产品发布生成服务
- 发布公告
- 发布预告
- 媒体包
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ProductLaunchGeneratorService:
    """
    产品发布生成服务

    生成产品发布相关内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_launch_content(
        self,
        product_name: str,
        launch_date: str,
    ) -> Dict[str, Any]:
        """
        生成产品发布内容

        Args:
            product_name: 产品名称
            launch_date: 发布日期

        Returns:
            Dict: 发布内容
        """
        try:
            prompt = f"""请为"{product_name}"（发布日期：{launch_date}）生成产品发布内容。

请以JSON格式返回：
{{
    "teaser": "预告文案",
    "announcement": "发布公告",
    "press_kit_intro": "媒体包介绍",
    "social_posts": ["社交帖子1", "社交帖子2"],
    "hashtags": ["#标签1"]
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
                "launch_date": launch_date,
                **result,
            }

        except Exception as e:
            logger.error(f"生成产品发布内容失败: {e}")
            return {
                "product_name": product_name,
                "launch_date": launch_date,
                "teaser": "",
                "announcement": "",
                "press_kit_intro": "",
                "social_posts": [],
                "hashtags": [],
            }


product_launch_generator_service = ProductLaunchGeneratorService()