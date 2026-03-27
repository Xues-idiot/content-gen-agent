"""
Vox Trending Topics Analyzer 模块

热门话题分析服务
- 分析当前热门话题
- 提供话题趋势预测
- 话题热度对比
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class TrendingTopic:
    """热门话题"""
    topic: str
    platform: str
    heat_score: int  # 0-100
    category: str  # 娱乐/科技/美食/旅游/时尚/等
    description: str
    related_hashtags: List[str]
    best_posting_time: str  # 最佳发布时间
    growth_trend: str  #上升/平稳/下降


class TrendingAnalyzerService:
    """
    热门话题分析服务

    分析和预测热门话题
    """

    CATEGORIES = [
        "娱乐", "科技", "美食", "旅游", "时尚",
        "教育", "健身", "职场", "情感", "家居",
        "美妆", "母婴", "宠物", "游戏", "影视"
    ]

    PLATFORM_TRENDING_FEATURES = {
        "xiaohongshu": {
            "name": "小红书",
            "trending_types": ["种草", "测评", "教程", "好物推荐", "日常分享"],
            "update_frequency": "每小时",
        },
        "tiktok": {
            "name": "抖音",
            "trending_types": ["短视频", "挑战赛", "热门BGM", "达人合作"],
            "update_frequency": "实时",
        },
        "weibo": {
            "name": "微博",
            "trending_types": ["热搜话题", "明星八卦", "社会热点", "段子"],
            "update_frequency": "分钟级",
        },
        "weixin": {
            "name": "微信",
            "trending_types": ["公众号爆文", "视频号", "朋友圈热点"],
            "update_frequency": "每天",
        },
    }

    def __init__(self):
        self.llm = llm_service

    async def analyze_trending_topics(
        self,
        platform: str = "xiaohongshu",
        category: str = "",
        num_topics: int = 10,
    ) -> List[TrendingTopic]:
        """
        分析热门话题

        Args:
            platform: 目标平台
            category: 话题分类
            num_topics: 返回数量

        Returns:
            List[TrendingTopic]: 热门话题列表
        """
        try:
            platform_info = self.PLATFORM_TRENDING_FEATURES.get(platform, {})
            platform_name = platform_info.get("name", platform)

            category_hint = f"，聚焦{category}类话题" if category else ""

            prompt = f"""请分析当前{platform_name}平台上的热门话题趋势。

目标平台：{platform_name}{category_hint}
返回数量：{num_topics}个

请列出当前最热的{num_topics}个话题，包括：
1. 话题名称
2. 热度指数（0-100）
3. 话题分类
4. 简短描述
5. 相关Hashtag（3-5个）
6. 最佳发布时间建议
7. 趋势预测（上升/平稳/下降）

请以JSON格式返回：
{{
    "topics": [
        {{
            "topic": "话题名称",
            "heat_score": 85,
            "category": "分类",
            "description": "话题描述",
            "related_hashtags": ["#标签1", "#标签2"],
            "best_posting_time": "时间建议",
            "growth_trend": "上升"
        }}
    ]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
                topics_data = result.get("topics", [])
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                if match:
                    try:
                        result = json.loads(match.group())
                        topics_data = result.get("topics", [])
                    except:
                        topics_data = self._get_fallback_topics(platform, num_topics)
                else:
                    topics_data = self._get_fallback_topics(platform, num_topics)

            return [
                TrendingTopic(
                    topic=t.get("topic", ""),
                    platform=platform,
                    heat_score=t.get("heat_score", 50),
                    category=t.get("category", category or "通用"),
                    description=t.get("description", ""),
                    related_hashtags=t.get("related_hashtags", []),
                    best_posting_time=t.get("best_posting_time", ""),
                    growth_trend=t.get("growth_trend", "平稳"),
                )
                for t in topics_data[:num_topics]
            ]

        except Exception as e:
            logger.error(f"分析热门话题失败: {e}")
            return self._get_fallback_topics(platform, num_topics)

    def _get_fallback_topics(self, platform: str, num: int) -> List[Dict]:
        """获取默认话题（当LLM不可用时）"""
        platform_name = self.PLATFORM_TRENDING_FEATURES.get(platform, {}).get("name", platform)

        common_topics = [
            {"topic": f"{platform_name}好物分享", "heat_score": 80, "category": "种草", "description": "分享近期发现的宝藏好物", "related_hashtags": ["#好物分享", "#种草"], "best_posting_time": "晚间8-10点", "growth_trend": "上升"},
            {"topic": "周末生活记录", "heat_score": 75, "category": "日常", "description": "记录周末的悠闲时光", "related_hashtags": ["#周末", "#生活记录"], "best_posting_time": "周末下午", "growth_trend": "平稳"},
            {"topic": "职场干货分享", "heat_score": 70, "category": "职场", "description": "分享工作技巧和经验", "related_hashtags": ["#职场", "#干货"], "best_posting_time": "工作日午休", "growth_trend": "上升"},
            {"topic": "美食探店打卡", "heat_score": 85, "category": "美食", "description": "推荐特色美食店铺", "related_hashtags": ["#美食探店", "#打卡"], "best_posting_time": "饭点前", "growth_trend": "上升"},
            {"topic": "新手入门教程", "heat_score": 72, "category": "教程", "description": "某领域的入门指南", "related_hashtags": ["#教程", "#新手"], "best_posting_time": "晚间7-9点", "growth_trend": "平稳"},
        ]

        return common_topics[:num]

    async def predict_topic_trend(
        self,
        topic: str,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        预测话题趋势

        Args:
            topic: 话题名称
            platform: 平台

        Returns:
            Dict: 趋势预测结果
        """
        try:
            prompt = f"""请分析话题"{topic}"在{platform}平台的未来趋势。

请预测：
1. 未来7天热度趋势（上升/平稳/下降）
2. 热度峰值时间
3. 最佳行动时间窗口
4. 风险提示（如有）

请以JSON格式返回：
{{
    "topic": "话题名",
    "trend_prediction": "上升/平稳/下降",
    "peak_time": "预计峰值时间",
    "best_timing": "最佳行动时间窗口",
    "risk_notes": "风险提示（没有则留空）",
    "confidence": 85
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
                "trend_prediction": result.get("trend_prediction", "平稳"),
                "peak_time": result.get("peak_time", "未来3-5天"),
                "best_timing": result.get("best_timing", "尽快行动"),
                "risk_notes": result.get("risk_notes", ""),
                "confidence": result.get("confidence", 70),
            }

        except Exception as e:
            logger.error(f"预测话题趋势失败: {e}")
            return {
                "topic": topic,
                "trend_prediction": "平稳",
                "peak_time": "未知",
                "best_timing": "尽快行动",
                "risk_notes": "",
                "confidence": 50,
            }

    def compare_topics(
        self,
        topics: List[str],
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        对比多个话题的热度

        Args:
            topics: 话题列表
            platform: 平台

        Returns:
            Dict: 对比分析结果
        """
        if not topics:
            return {"comparison": [], "recommendation": ""}

        # 简单对比逻辑（实际应该调用LLM）
        comparison = []
        for i, topic in enumerate(topics):
            comparison.append({
                "topic": topic,
                "rank": i + 1,
                "estimated_heat": 100 - (i * 10),  # 简单估算
                "competition_level": "高" if i == 0 else ("中" if i == 1 else "低"),
            })

        return {
            "comparison": comparison,
            "recommendation": f"建议优先选择话题「{topics[0] if topics else ''}」，热度高但竞争也较大",
        }


# 全局实例
trending_analyzer_service = TrendingAnalyzerService()


if __name__ == "__main__":
    import asyncio

    service = TrendingAnalyzerService()

    async def test():
        print("=== 热门话题分析 ===")
        topics = await service.analyze_trending_topics(
            platform="xiaohongshu",
            num_topics=5,
        )

        for topic in topics:
            print(f"\n话题: {topic.topic}")
            print(f"  热度: {topic.heat_score}")
            print(f"  分类: {topic.category}")
            print(f"  趋势: {topic.growth_trend}")
            print(f"  标签: {', '.join(topic.related_hashtags)}")
            print(f"  发布时间: {topic.best_posting_time}")

        print("\n=== 话题趋势预测 ===")
        prediction = await service.predict_topic_trend("春季穿搭")
        print(f"话题: {prediction['topic']}")
        print(f"趋势: {prediction['trend_prediction']}")
        print(f"峰值时间: {prediction['peak_time']}")
        print(f"最佳时机: {prediction['best_timing']}")

    asyncio.run(test())
