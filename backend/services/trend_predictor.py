"""
Vox Trend Predictor Service 模块

趋势预测服务
- 预测内容趋势
- 话题热度预测
- 病毒式传播预测
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class TrendPrediction:
    """趋势预测"""
    topic: str
    trend_direction: str  # rising/falling/stable
    peak_time: str  # 预计峰值时间
    duration_days: int  # 持续天数
    confidence: int  # 置信度 0-100
    viral_potential: str  # 病毒潜力: low/medium/high


class TrendPredictorService:
    """
    趋势预测服务

    预测话题和内容的趋势
    """

    def __init__(self):
        self.llm = llm_service

    async def predict_topic_trend(
        self,
        topic: str,
        platform: str = "xiaohongshu",
    ) -> TrendPrediction:
        """
        预测话题趋势

        Args:
            topic: 话题
            platform: 平台

        Returns:
            TrendPrediction: 趋势预测
        """
        try:
            prompt = f"""请预测话题"{topic}"在{platform}平台的趋势。

请分析：
1. 趋势方向（上升/下降/平稳）
2. 预计峰值时间
3. 预计持续天数
4. 预测置信度（0-100）
5. 病毒式传播潜力（低/中/高）

请以JSON格式返回：
{{
    "topic": "{topic}",
    "trend_direction": "上升/下降/平稳",
    "peak_time": "预计时间",
    "duration_days": 7,
    "confidence": 75,
    "viral_potential": "中"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return TrendPrediction(
                topic=result.get("topic", topic),
                trend_direction=result.get("trend_direction", "平稳"),
                peak_time=result.get("peak_time", "未来几天"),
                duration_days=result.get("duration_days", 7),
                confidence=result.get("confidence", 60),
                viral_potential=result.get("viral_potential", "中"),
            )

        except Exception as e:
            logger.error(f"预测话题趋势失败: {e}")
            return TrendPrediction(
                topic=topic,
                trend_direction="平稳",
                peak_time="未知",
                duration_days=7,
                confidence=50,
                viral_potential="中",
            )

    async def predict_viral_potential(
        self,
        content: str,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        预测内容病毒潜力

        Args:
            content: 内容
            platform: 平台

        Returns:
            Dict: 病毒潜力分析
        """
        try:
            prompt = f"""请分析以下内容的病毒式传播潜力。

平台：{platform}
内容：{content[:500]}

请分析：
1. 病毒潜力等级（低/中/高）
2. 可能火的原因
3. 需要注意的风险
4. 提高病毒潜力的建议

请以JSON格式返回：
{{
    "viral_potential": "中",
    "reasons": ["原因1", "原因2"],
    "risks": ["风险1"],
    "improvement_suggestions": ["建议1", "建议2"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "content_preview": content[:100],
                "platform": platform,
                "viral_potential": result.get("viral_potential", "中"),
                "reasons": result.get("reasons", []),
                "risks": result.get("risks", []),
                "improvement_suggestions": result.get("improvement_suggestions", []),
            }

        except Exception as e:
            logger.error(f"预测病毒潜力失败: {e}")
            return {
                "content_preview": content[:100],
                "platform": platform,
                "viral_potential": "中",
                "reasons": [],
                "risks": [],
                "improvement_suggestions": [],
            }

    async def get_trending_window(
        self,
        topic: str,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        获取最佳发布窗口

        Args:
            topic: 话题
            platform: 平台

        Returns:
            Dict: 最佳发布窗口
        """
        try:
            prompt = f"""请为话题"{topic}"在{platform}平台确定最佳发布窗口。

请分析：
1. 现在是否是最佳时机
2. 如果不是，什么时候是
3. 窗口持续多久
4. 错过窗口的影响

请以JSON格式返回：
{{
    "topic": "{topic}",
    "is_optimal_now": true,
    "best_window_start": "时间",
    "best_window_end": "时间",
    "window_duration_hours": 24,
    "urgency": "高/中/低",
    "missed_impact": "影响说明"
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
                "platform": platform,
                "is_optimal_now": result.get("is_optimal_now", False),
                "best_window_start": result.get("best_window_start", ""),
                "best_window_end": result.get("best_window_end", ""),
                "window_duration_hours": result.get("window_duration_hours", 24),
                "urgency": result.get("urgency", "中"),
                "missed_impact": result.get("missed_impact", ""),
            }

        except Exception as e:
            logger.error(f"获取发布窗口失败: {e}")
            return {
                "topic": topic,
                "platform": platform,
                "is_optimal_now": False,
                "best_window_start": "",
                "best_window_end": "",
                "window_duration_hours": 24,
                "urgency": "中",
                "missed_impact": "",
            }

    def analyze_seasonal_trends(
        self,
        topic: str,
    ) -> Dict[str, Any]:
        """
        分析季节性趋势

        Args:
            topic: 话题

        Returns:
            Dict: 季节性分析
        """
        # 简单实现
        current_month = datetime.now().month

        seasonal_keywords = {
            "春季": ["踏青", "春游", "换季", "春季穿搭"],
            "夏季": ["防晒", "游泳", "夏季护肤", "清凉"],
            "秋季": ["换季", "秋游", "秋季护肤", "养生"],
            "冬季": ["保暖", "冬季护肤", "圣诞", "新年"],
        }

        season = ""
        if current_month in [3, 4, 5]:
            season = "春季"
        elif current_month in [6, 7, 8]:
            season = "夏季"
        elif current_month in [9, 10, 11]:
            season = "秋季"
        else:
            season = "冬季"

        return {
            "topic": topic,
            "current_season": season,
            "is_seasonal": any(kw in topic for kw in seasonal_keywords.get(season, [])),
            "seasonal_keywords": seasonal_keywords.get(season, []),
            "recommendation": f"当前{season}，可结合季节性关键词",
        }


# 全局实例
trend_predictor_service = TrendPredictorService()


if __name__ == "__main__":
    import asyncio

    service = TrendPredictorService()

    async def test():
        print("=== 话题趋势预测 ===")
        pred = await service.predict_topic_trend("春季穿搭")
        print(f"话题: {pred.topic}")
        print(f"趋势: {pred.trend_direction}")
        print(f"峰值: {pred.peak_time}")
        print(f"持续: {pred.duration_days}天")
        print(f"病毒潜力: {pred.viral_potential}")

        print("\n=== 病毒潜力分析 ===")
        viral = await service.predict_viral_potential("这款面霜太好用了！")
        print(f"潜力: {viral['viral_potential']}")
        print(f"原因: {', '.join(viral['reasons'][:2])}")

        print("\n=== 发布窗口 ===")
        window = await service.get_trending_window("端午节粽子")
        print(f"现在是最佳时机: {window['is_optimal_now']}")
        print(f"窗口时间: {window['best_window_start']}")
        print(f"紧急程度: {window['urgency']}")

    asyncio.run(test())
