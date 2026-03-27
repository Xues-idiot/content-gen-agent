"""
Vox Thread Generator Service 模块

推文串生成服务
- Twitter/微博推文串
- 内容扩展
- 互动引导
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ThreadGeneratorService:
    """
    推文串生成服务

    生成Twitter/微博风格的推文串
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_thread(
        self,
        topic: str,
        num_tweets: int = 5,
        platform: str = "twitter",
    ) -> List[Dict[str, Any]]:
        """
        生成推文串

        Args:
            topic: 主题
            num_tweets: 推文数量
            platform: 平台

        Returns:
            List[Dict]: 推文列表
        """
        try:
            prompt = f"""请为"{topic}"主题生成一个{num_tweets}条的推文串。

平台：{platform}

要求：
1. 每条推文简洁有力
2. 有逻辑递进关系
3. 最后一条有互动引导

请以JSON格式返回：
{{
    "thread": [
        {{
            "order": 1,
            "content": "推文内容",
            "hashtag": "#标签"
        }}
    ]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return result.get("thread", [])

        except Exception as e:
            logger.error(f"生成推文串失败: {e}")
            return []


thread_generator_service = ThreadGeneratorService()