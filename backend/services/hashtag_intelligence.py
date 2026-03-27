"""
Vox Hashtag Intelligence Service 模块

Hashtag智能分析服务
- hashtag效果分析
- hashtag组合优化
- hashtag趋势追踪
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class HashtagAnalysis:
    """Hashtag分析结果"""
    hashtag: str
    popularity: str  # hot/warm/cold
    competition: str  # high/medium/low
    relevance_score: int  # 0-100
    best_posting_time: str


class HashtagIntelligenceService:
    """
    Hashtag智能分析服务

    提供hashtag相关的智能分析
    """

    def __init__(self):
        self.llm = llm_service

    async def analyze_hashtag(
        self,
        hashtag: str,
        platform: str = "xiaohongshu",
    ) -> HashtagAnalysis:
        """
        分析单个hashtag

        Args:
            hashtag: hashtag
            platform: 平台

        Returns:
            HashtagAnalysis: 分析结果
        """
        try:
            prompt = f"""请分析{platform}平台上的hashtag "#{hashtag}"。

请评估：
1. 热度（热门/温/冷）
2. 竞争程度（高/中/低）
3. 相关性评分（0-100）
4. 最佳发布时间

请以JSON格式返回：
{{
    "hashtag": "{hashtag}",
    "popularity": "热门",
    "competition": "中",
    "relevance_score": 75,
    "best_posting_time": "晚间8-10点"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return HashtagAnalysis(
                hashtag=result.get("hashtag", hashtag),
                popularity=result.get("popularity", "温"),
                competition=result.get("competition", "中"),
                relevance_score=result.get("relevance_score", 60),
                best_posting_time=result.get("best_posting_time", ""),
            )

        except Exception as e:
            logger.error(f"分析hashtag失败: {e}")
            return HashtagAnalysis(
                hashtag=hashtag,
                popularity="温",
                competition="中",
                relevance_score=60,
                best_posting_time="",
            )

    async def optimize_hashtag_set(
        self,
        hashtags: List[str],
        platform: str = "xiaohongshu",
        target_count: int = 10,
    ) -> Dict[str, Any]:
        """
        优化hashtag组合

        Args:
            hashtags: 原始hashtag列表
            platform: 平台
            target_count: 目标数量

        Returns:
            Dict: 优化建议
        """
        try:
            prompt = f"""请优化以下hashtag组合，使其达到最佳效果。

平台：{platform}
目标数量：{target_count}个
原始hashtag：{', '.join(['#'+h for h in hashtags])}

请分析并提供：
1. 当前组合的问题
2. 推荐的hashtag（保留/新增/移除）
3. 最佳组合策略

请以JSON格式返回：
{{
    "current_issues": ["问题1"],
    "recommended": ["#hashtag1", "#hashtag2"],
    "removed": ["#hashtag3"],
    "strategy": "优化策略说明"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "original_count": len(hashtags),
                "target_count": target_count,
                "current_issues": result.get("current_issues", []),
                "recommended": result.get("recommended", []),
                "removed": result.get("removed", []),
                "strategy": result.get("strategy", ""),
            }

        except Exception as e:
            logger.error(f"优化hashtag组合失败: {e}")
            return {
                "original_count": len(hashtags),
                "target_count": target_count,
                "current_issues": [],
                "recommended": [f"#{h}" for h in hashtags[:target_count]],
                "removed": [],
                "strategy": "优化失败",
            }

    async def generate_hashtag_mix(
        self,
        content_topic: str,
        platform: str = "xiaohongshu",
        num: int = 10,
    ) -> Dict[str, Any]:
        """
        生成hashtag组合

        根据内容主题生成最佳hashtag组合

        Args:
            content_topic: 内容主题
            platform: 平台
            num: 数量

        Returns:
            Dict: 生成的组合
        """
        try:
            prompt = f"""请为"{content_topic}"主题生成{num}个最佳hashtag组合。

平台：{platform}

请提供：
1. 核心hashtag（1-2个，高热度高相关）
2. 精准hashtag（2-3个，中等热度）
3. 长尾hashtag（2-3个，低热度但精准）
4. 趋势hashtag（1-2个，当前热门）

请以JSON格式返回：
{{
    "core": ["#核心1", "#核心2"],
    "targeted": ["#精准1", "#精准2"],
    "long_tail": ["#长尾1"],
    "trending": ["#趋势1"],
    "mix_recommendation": "组合建议"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            all_hashtags = (
                result.get("core", []) +
                result.get("targeted", []) +
                result.get("long_tail", []) +
                result.get("trending", [])
            )

            return {
                "topic": content_topic,
                "platform": platform,
                "total_count": len(all_hashtags),
                "core": result.get("core", []),
                "targeted": result.get("targeted", []),
                "long_tail": result.get("long_tail", []),
                "trending": result.get("trending", []),
                "mix_recommendation": result.get("mix_recommendation", ""),
            }

        except Exception as e:
            logger.error(f"生成hashtag组合失败: {e}")
            return {
                "topic": content_topic,
                "platform": platform,
                "total_count": 0,
                "core": [],
                "targeted": [],
                "long_tail": [],
                "trending": [],
                "mix_recommendation": "",
            }

    def calculate_hashtag_score(
        self,
        hashtag: str,
        post_time: str = "evening",
    ) -> int:
        """
        计算hashtag分数

        简单的分数计算

        Args:
            hashtag: hashtag
            post_time: 发布时间

        Returns:
            int: 分数 0-100
        """
        score = 60

        # 长度影响
        if len(hashtag) <= 5:
            score += 10
        elif len(hashtag) > 10:
            score -= 10

        # 热门词汇加分
        hot_words = ["测评", "推荐", "分享", "干货", "教程", "种草"]
        if any(w in hashtag for w in hot_words):
            score += 15

        # 避免符号
        if "#" in hashtag:
            score -= 5

        return max(0, min(100, score))


# 全局实例
hashtag_intelligence_service = HashtagIntelligenceService()


if __name__ == "__main__":
    import asyncio

    service = HashtagIntelligenceService()

    async def test():
        print("=== Hashtag分析 ===")
        analysis = await service.analyze_hashtag("面霜推荐")
        print(f"Hashtag: {analysis.hashtag}")
        print(f"热度: {analysis.popularity}")
        print(f"竞争: {analysis.competition}")
        print(f"相关性: {analysis.relevance_score}")

        print("\n=== Hashtag组合生成 ===")
        mix = await service.generate_hashtag_mix("春季护肤", num=10)
        print(f"主题: {mix['topic']}")
        print(f"总数: {mix['total_count']}")
        print(f"核心: {', '.join(mix['core'])}")
        print(f"精准: {', '.join(mix['targeted'])}")

        print("\n=== Hashtag分数 ===")
        score = service.calculate_hashtag_score("面霜测评")
        print(f"分数: {score}")

    asyncio.run(test())
