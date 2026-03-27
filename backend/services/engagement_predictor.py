"""
Vox Engagement Predictor Service 模块

互动预测服务
- 预测内容互动率
- 互动优化建议
- 平台对比分析
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class EngagementPrediction:
    """互动预测结果"""
    predicted_likes: int
    predicted_comments: int
    predicted_shares: int
    engagement_rate: float  # 百分比
    confidence: str  # high/medium/low
    factors: List[str]


class EngagementPredictorService:
    """
    互动预测服务

    预测内容的互动表现
    """

    def __init__(self):
        self.llm = llm_service

    # 平台平均互动率参考
    PLATFORM_BENCHMARKS = {
        "xiaohongshu": {
            "avg_engagement_rate": 3.5,  # %
            "likes_ratio": 0.85,
            "comments_ratio": 0.10,
            "shares_ratio": 0.05,
        },
        "tiktok": {
            "avg_engagement_rate": 5.0,
            "likes_ratio": 0.90,
            "comments_ratio": 0.05,
            "shares_ratio": 0.05,
        },
        "weibo": {
            "avg_engagement_rate": 1.5,
            "likes_ratio": 0.70,
            "comments_ratio": 0.20,
            "shares_ratio": 0.10,
        },
        "official": {
            "avg_engagement_rate": 2.0,
            "likes_ratio": 0.60,
            "comments_ratio": 0.25,
            "shares_ratio": 0.15,
        },
    }

    async def predict_engagement(
        self,
        content: str,
        title: str = "",
        platform: str = "xiaohongshu",
        follower_count: int = 10000,
    ) -> EngagementPrediction:
        """
        预测互动

        Args:
            content: 内容
            title: 标题
            platform: 平台
            follower_count: 粉丝数

        Returns:
            EngagementPrediction: 预测结果
        """
        try:
            prompt = f"""请预测以下内容的互动表现。

平台：{platform}
粉丝数：{follower_count}
标题：{title}
内容：{content[:500]}

请预测：
1. 预计点赞数
2. 预计评论数
3. 预计分享数
4. 预计互动率
5. 预测置信度（高/中/低）
6. 影响互动的主要因素

请以JSON格式返回：
{{
    "predicted_likes": 1000,
    "predicted_comments": 100,
    "predicted_shares": 50,
    "engagement_rate": 3.5,
    "confidence": "高",
    "factors": ["因素1", "因素2"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return EngagementPrediction(
                predicted_likes=result.get("predicted_likes", 0),
                predicted_comments=result.get("predicted_comments", 0),
                predicted_shares=result.get("predicted_shares", 0),
                engagement_rate=result.get("engagement_rate", 0.0),
                confidence=result.get("confidence", "中"),
                factors=result.get("factors", []),
            )

        except Exception as e:
            logger.error(f"预测互动失败: {e}")
            return EngagementPrediction(
                predicted_likes=0,
                predicted_comments=0,
                predicted_shares=0,
                engagement_rate=0.0,
                confidence="低",
                factors=[],
            )

    async def get_optimization_suggestions(
        self,
        content: str,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        获取互动优化建议

        Args:
            content: 内容
            platform: 平台

        Returns:
            Dict: 优化建议
        """
        try:
            prompt = f"""请分析以下内容并提供提高互动的建议。

平台：{platform}
内容：{content[:500]}

请分析：
1. 当前互动潜力
2. 互动障碍
3. 优化建议（标题、内容结构、CTA等）

请以JSON格式返回：
{{
    "current_potential": "当前潜力评估",
    "barriers": ["障碍1", "障碍2"],
    "suggestions": ["建议1", "建议2"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return result

        except Exception as e:
            logger.error(f"获取优化建议失败: {e}")
            return {
                "current_potential": "",
                "barriers": [],
                "suggestions": [],
            }

    def get_platform_benchmark(self, platform: str) -> Dict[str, Any]:
        """
        获取平台基准

        Args:
            platform: 平台

        Returns:
            Dict: 平台基准数据
        """
        return self.PLATFORM_BENCHMARKS.get(
            platform, self.PLATFORM_BENCHMARKS["xiaohongshu"]
        )


# 全局实例
engagement_predictor_service = EngagementPredictorService()


if __name__ == "__main__":
    import asyncio

    service = EngagementPredictorService()

    async def test():
        print("=== 互动预测 ===")
        result = await service.predict_engagement(
            "这款面霜太好用了！",
            "面霜推荐",
            "xiaohongshu",
            10000
        )
        print(f"点赞: {result.predicted_likes}")
        print(f"评论: {result.predicted_comments}")
        print(f"互动率: {result.engagement_rate}%")
        print(f"置信度: {result.confidence}")

        print("\n=== 平台基准 ===")
        bench = service.get_platform_benchmark("xiaohongshu")
        print(f"平均互动率: {bench['avg_engagement_rate']}%")

    asyncio.run(test())