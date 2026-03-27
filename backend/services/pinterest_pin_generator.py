"""
Vox Pinterest Pin Generator Service 模块

Pinterest图钉生成服务
- Pin设计
- 描述优化
- 板整理
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class PinterestPinGeneratorService:
    """
    Pinterest图钉生成服务

    生成Pinterest图钉内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_pinterest_pin(
        self,
        pin_topic: str,
        pin_type: str = "product",
        num_pins: int = 5,
    ) -> Dict[str, Any]:
        """
        生成Pinterest图钉

        Args:
            pin_topic: 图钉主题
            pin_type: 图钉类型
            num_pins: 图钉数量

        Returns:
            Dict: Pinterest图钉
        """
        try:
            prompt = f"""请为"{pin_topic}"生成{num_pins}个{pin_type}类型的Pinterest图钉。

请以JSON格式返回：
{{
    "pin_topic": "图钉主题",
    "pin_type": "图钉类型",
    "num_pins": {num_pins},
    "pins": [
        {{
            "pin_title": "图钉标题",
            "description": "描述",
            "image_suggestion": "图片建议",
            "board_assignment": "板分配",
            "keywords": ["关键词1"]
        }}
    ],
    "board_organization": "板组织",
    "pinning_schedule": "固定计划",
    "seo_tips": ["SEO提示1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "pin_topic": pin_topic,
                "pin_type": pin_type,
                "num_pins": num_pins,
                **result,
            }

        except Exception as e:
            logger.error(f"生成Pinterest图钉失败: {e}")
            return {
                "pin_topic": pin_topic,
                "pin_type": pin_type,
                "num_pins": num_pins,
                "pins": [],
                "board_organization": "",
                "pinning_schedule": "",
                "seo_tips": [],
            }


pinterest_pin_generator_service = PinterestPinGeneratorService()