"""
Vox Listicle Generator Service 模块

清单生成服务
- 列表形式内容
- 排名清单
- 推荐清单
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ListicleGeneratorService:
    """
    清单生成服务

    生成清单形式的内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_listicle(
        self,
        topic: str,
        num_items: int = 5,
        list_type: str = "ranking",
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        生成清单

        Args:
            topic: 主题
            num_items: 条目数量
            list_type: 清单类型（ranking/recommended/tips）
            platform: 平台

        Returns:
            Dict: 清单内容
        """
        try:
            prompt = f"""请为"{topic}"生成一个{num_items}条的清单。

类型：{list_type}
平台：{platform}

请以JSON格式返回：
{{
    "title": "清单标题",
    "intro": "引言",
    "items": [
        {{
            "rank": 1,
            "title": "条目标题",
            "description": "条目描述",
            "highlight": "亮点"
        }}
    ],
    "conclusion": "结语"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "topic": topic,
                "num_items": num_items,
                "list_type": list_type,
                "platform": platform,
                **result,
            }

        except Exception as e:
            logger.error(f"生成清单失败: {e}")
            return {
                "topic": topic,
                "num_items": num_items,
                "list_type": list_type,
                "platform": platform,
                "title": "",
                "intro": "",
                "items": [],
                "conclusion": "",
            }


listicle_generator_service = ListicleGeneratorService()