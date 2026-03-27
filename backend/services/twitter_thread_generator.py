"""
Vox Twitter Thread Generator Service 模块

Twitter推文串生成服务
- 推文内容
- 话题标签
- 互动策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class TwitterThreadGeneratorService:
    """
    Twitter推文串生成服务

    生成Twitter推文串内容
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_twitter_thread(
        self,
        topic: str,
        num_tweets: int = 10,
        thread_type: str = "educational",
    ) -> Dict[str, Any]:
        """
        生成Twitter推文串

        Args:
            topic: 主题
            num_tweets: 推文数量
            thread_type: 推文串类型

        Returns:
            Dict: Twitter推文串
        """
        try:
            prompt = f"""请为"{topic}"生成{num_tweets}条{thread_type}类型的Twitter推文串。

请以JSON格式返回：
{{
    "topic": "主题",
    "num_tweets": {num_tweets},
    "thread_type": "推文串类型",
    "thread_hook": "推文串钩子",
    "tweets": [
        {{
            "tweet_number": 1,
            "text": "推文文本",
            "hashtags": ["话题标签1"],
            "media_suggestion": "媒体建议"
        }}
    ],
    "engagement_tips": ["互动提示1"],
    "best_posting_times": "最佳发布时间",
    "follow_up_strategies": ["跟进策略1"]
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
                "num_tweets": num_tweets,
                "thread_type": thread_type,
                **result,
            }

        except Exception as e:
            logger.error(f"生成Twitter推文串失败: {e}")
            return {
                "topic": topic,
                "num_tweets": num_tweets,
                "thread_type": thread_type,
                "thread_hook": "",
                "tweets": [],
                "engagement_tips": [],
                "best_posting_times": "",
                "follow_up_strategies": [],
            }


twitter_thread_generator_service = TwitterThreadGeneratorService()