"""
Vox Sentiment Analyzer Service 模块

情感分析服务
- 内容情感分析
- 情感趋势追踪
- 平台情感偏好
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class SentimentResult:
    """情感分析结果"""
    sentiment: str  # positive/negative/neutral
    confidence: int  # 0-100
    emotions: List[str]
    intensity: str  # low/medium/high
    suggestions: List[str]


class SentimentAnalyzerService:
    """
    情感分析服务

    分析内容的情感倾向和情绪
    """

    def __init__(self):
        self.llm = llm_service

    # 平台情感偏好
    PLATFORM_PREFERENCES = {
        "xiaohongshu": {
            "preferred_sentiment": "positive",
            "tone": "温暖、亲切、真实",
            "avoid": "过于负面、消极抱怨",
            "emojis": ["✨", "💖", "😍", "👍", "🌸"],
        },
        "tiktok": {
            "preferred_sentiment": "energetic",
            "tone": "年轻、活力、夸张",
            "avoid": "平淡、无聊",
            "emojis": ["🔥", "💯", "😂", "❤️", "🙄"],
        },
        "weibo": {
            "preferred_sentiment": "expressive",
            "tone": "观点鲜明、有态度",
            "avoid": "模糊不清",
            "emojis": ["[吃瓜]", "[doge]", "[笑哭]"],
        },
        "official": {
            "preferred_sentiment": "professional",
            "tone": "专业、客观、严谨",
            "avoid": "情绪化、主观臆断",
            "emojis": ["📊", "📈", "✅", "💡"],
        },
    }

    async def analyze_sentiment(
        self,
        content: str,
        platform: str = "xiaohongshu",
    ) -> SentimentResult:
        """
        分析内容情感

        Args:
            content: 内容
            platform: 平台

        Returns:
            SentimentResult: 情感分析结果
        """
        try:
            prompt = f"""请分析以下内容的情感倾向和情绪。

平台：{platform}
内容：{content[:500]}

请分析：
1. 情感倾向（积极/消极/中性）
2. 置信度（0-100）
3. 包含的情绪（开心、惊讶、满意、喜爱、思考、无语、悲伤等）
4. 情感强度（低/中/高）
5. 改进建议（如果有）

请以JSON格式返回：
{{
    "sentiment": "积极",
    "confidence": 85,
    "emotions": ["开心", "满意"],
    "intensity": "中",
    "suggestions": ["建议1"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            sentiment_map = {
                "积极": "positive", "positive": "positive",
                "消极": "negative", "negative": "negative",
                "中性": "neutral", "neutral": "neutral",
            }

            return SentimentResult(
                sentiment=sentiment_map.get(result.get("sentiment", "中性"), "neutral"),
                confidence=result.get("confidence", 60),
                emotions=result.get("emotions", []),
                intensity=result.get("intensity", "中"),
                suggestions=result.get("suggestions", []),
            )

        except Exception as e:
            logger.error(f"分析情感失败: {e}")
            return SentimentResult(
                sentiment="neutral",
                confidence=50,
                emotions=[],
                intensity="中",
                suggestions=[],
            )

    async def get_platform_sentiment_tips(
        self,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        获取平台情感建议

        Args:
            platform: 平台

        Returns:
            Dict: 平台情感建议
        """
        pref = self.PLATFORM_PREFERENCES.get(
            platform, self.PLATFORM_PREFERENCES["xiaohongshu"]
        )

        return {
            "platform": platform,
            "preferred_sentiment": pref["preferred_sentiment"],
            "tone": pref["tone"],
            "avoid": pref["avoid"],
            "recommended_emojis": pref["emojis"],
        }

    async def adjust_sentiment(
        self,
        content: str,
        target_sentiment: str = "positive",
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        调整内容情感

        将内容调整为指定情感倾向

        Args:
            content: 原始内容
            target_sentiment: 目标情感 (positive/negative/neutral)
            platform: 平台

        Returns:
            Dict: 调整后的内容和建议
        """
        try:
            prompt = f"""请将以下内容调整为{target_sentiment}的情感倾向。

平台：{platform}
原始内容：{content[:500]}

请提供：
1. 调整后的内容
2. 情感变化说明
3. 保留的核心信息
4. 调整建议

请以JSON格式返回：
{{
    "adjusted_content": "调整后的内容",
    "change_explanation": "变化说明",
    "preserved_core": ["保留的点1", "保留的点2"],
    "adjustment_suggestions": ["建议1", "建议2"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "original_content": content,
                "target_sentiment": target_sentiment,
                "adjusted_content": result.get("adjusted_content", content),
                "change_explanation": result.get("change_explanation", ""),
                "preserved_core": result.get("preserved_core", []),
                "adjustment_suggestions": result.get("adjustment_suggestions", []),
            }

        except Exception as e:
            logger.error(f"调整情感失败: {e}")
            return {
                "original_content": content,
                "target_sentiment": target_sentiment,
                "adjusted_content": content,
                "change_explanation": "调整失败",
                "preserved_core": [],
                "adjustment_suggestions": [],
            }

    def analyze_emotion_distribution(
        self,
        contents: List[str],
    ) -> Dict[str, Any]:
        """
        分析多内容的情绪分布

        Args:
            contents: 内容列表

        Returns:
            Dict: 情绪分布分析
        """
        emotion_counts = {
            "开心": 0,
            "惊讶": 0,
            "满意": 0,
            "喜爱": 0,
            "思考": 0,
            "无语": 0,
            "悲伤": 0,
        }

        # 简单的关键词检测
        emotion_keywords = {
            "开心": ["开心", "高兴", "快乐", "喜欢", "棒", "好", "赞"],
            "惊讶": ["惊讶", "震惊", "没想到", "居然", "竟然"],
            "满意": ["满意", "推荐", "值得", "不错", "good"],
            "喜爱": ["爱", "超爱", "最爱", "心动", "种草"],
            "思考": ["思考", "觉得", "认为", "分析", "觉得"],
            "无语": ["无语", "醉了", "服了", "离谱", "搞笑"],
            "悲伤": ["悲伤", "难过", "伤心", "可惜", "遗憾"],
        }

        for content in contents:
            for emotion, keywords in emotion_keywords.items():
                if any(kw in content for kw in keywords):
                    emotion_counts[emotion] += 1

        total = len(contents) if contents else 1

        return {
            "total_contents": len(contents),
            "emotion_distribution": emotion_counts,
            "emotion_percentages": {
                k: round(v / total * 100, 1) for k, v in emotion_counts.items()
            },
            "dominant_emotion": max(emotion_counts, key=emotion_counts.get) if any(emotion_counts.values()) else "无",
            "recommendations": self._get_emotion_recommendations(emotion_counts),
        }

    def _get_emotion_recommendations(
        self,
        emotion_counts: Dict[str, int],
    ) -> List[str]:
        """根据情绪分布提供建议"""
        recommendations = []

        if emotion_counts["开心"] == 0 and emotion_counts["满意"] == 0:
            recommendations.append("建议增加正面情绪内容，提升用户好感度")

        if emotion_counts["思考"] > emotion_counts["喜爱"]:
            recommendations.append("思考型内容较多，可以增加情感共鸣元素")

        if emotion_counts["无语"] > 3:
            recommendations.append("无语/吐槽内容较多，注意平衡正面内容")

        if emotion_counts["悲伤"] > 2:
            recommendations.append("悲伤情绪内容较多，社交媒体更适合积极内容")

        return recommendations


# 全局实例
sentiment_analyzer_service = SentimentAnalyzerService()


if __name__ == "__main__":
    import asyncio

    service = SentimentAnalyzerService()

    async def test():
        print("=== 情感分析 ===")
        result = await service.analyze_sentiment("这款面霜真的太好用了！皮肤变得超级光滑，推荐给大家！")
        print(f"情感: {result.sentiment}")
        print(f"置信度: {result.confidence}")
        print(f"情绪: {', '.join(result.emotions)}")
        print(f"强度: {result.intensity}")

        print("\n=== 平台情感建议 ===")
        tips = await service.get_platform_sentiment_tips("xiaohongshu")
        print(f"平台: {tips['platform']}")
        print(f"偏好情感: {tips['preferred_sentiment']}")
        print(f"语气: {tips['tone']}")

        print("\n=== 情感调整 ===")
        adjusted = await service.adjust_sentiment(
            "这个产品有点失望，效果不如预期",
            target_sentiment="positive"
        )
        print(f"调整后: {adjusted['adjusted_content'][:50]}...")

        print("\n=== 情绪分布 ===")
        contents = [
            "今天很开心！",
            "这个产品很好用",
            "有点失望",
            "推荐给大家",
            "太棒了！",
        ]
        dist = service.analyze_emotion_distribution(contents)
        print(f"主导情绪: {dist['dominant_emotion']}")
        print(f"分布: {dist['emotion_distribution']}")

    asyncio.run(test())