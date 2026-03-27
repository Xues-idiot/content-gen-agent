"""
Vox Competitor Tracker Service 模块

竞品追踪服务
- 追踪竞品内容动态
- 分析竞品策略
- 提供竞品对比
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class CompetitorInfo:
    """竞品信息"""
    name: str
    platform: str
    followers: int
    avg_views: int
    avg_engagement: float
    content_frequency: str  # 发布频率
    top_content_types: List[str]  # 热门内容类型
    strengths: List[str]  # 优势


class CompetitorTrackerService:
    """
    竞品追踪服务

    帮助追踪和分析竞品
    """

    def __init__(self):
        self.llm = llm_service

    async def track_competitor(
        self,
        competitor_name: str,
        platform: str = "xiaohongshu",
    ) -> CompetitorInfo:
        """
        追踪竞品

        Args:
            competitor_name: 竞品名称/账号
            platform: 平台

        Returns:
            CompetitorInfo: 竞品信息
        """
        try:
            prompt = f"""请分析{platform}平台上的竞品账号"{competitor_name}"。

请提供以下信息：
1. 粉丝数（预估）
2. 平均浏览量（预估）
3. 平均互动率（%）
4. 发布频率
5. 热门内容类型
6. 主要优势

请以JSON格式返回：
{{
    "name": "{competitor_name}",
    "platform": "{platform}",
    "followers": 50000,
    "avg_views": 10000,
    "avg_engagement": 5.5,
    "content_frequency": "每天1-2篇",
    "top_content_types": ["种草", "测评", "教程"],
    "strengths": ["内容质量高", "更新频繁", "互动好"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return CompetitorInfo(
                name=result.get("name", competitor_name),
                platform=result.get("platform", platform),
                followers=result.get("followers", 0),
                avg_views=result.get("avg_views", 0),
                avg_engagement=result.get("avg_engagement", 0.0),
                content_frequency=result.get("content_frequency", "未知"),
                top_content_types=result.get("top_content_types", []),
                strengths=result.get("strengths", []),
            )

        except Exception as e:
            logger.error(f"追踪竞品失败: {e}")
            return CompetitorInfo(
                name=competitor_name,
                platform=platform,
                followers=0,
                avg_views=0,
                avg_engagement=0.0,
                content_frequency="未知",
                top_content_types=[],
                strengths=[],
            )

    async def analyze_competitor_content(
        self,
        competitor_name: str,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        分析竞品内容策略

        Args:
            competitor_name: 竞品名称
            platform: 平台

        Returns:
            Dict: 内容策略分析
        """
        try:
            prompt = f"""请分析{platform}平台上竞品"{competitor_name}"的内容策略。

请分析：
1. 内容主题倾向
2. 标题风格特点
3. 发布时间规律
4. Hashtag使用策略
5. 互动策略
6. 可借鉴之处

请以JSON格式返回：
{{
    "topic_tendencies": ["主题1", "主题2"],
    "title_styles": ["风格1", "风格2"],
    "posting_schedule": "发布时间规律",
    "hashtag_strategy": "标签策略",
    "engagement_strategy": "互动策略",
    "takeaways": ["借鉴1", "借鉴2"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "competitor": competitor_name,
                "platform": platform,
                "topic_tendencies": result.get("topic_tendencies", []),
                "title_styles": result.get("title_styles", []),
                "posting_schedule": result.get("posting_schedule", ""),
                "hashtag_strategy": result.get("hashtag_strategy", ""),
                "engagement_strategy": result.get("engagement_strategy", ""),
                "takeaways": result.get("takeaways", []),
            }

        except Exception as e:
            logger.error(f"分析竞品内容失败: {e}")
            return {
                "competitor": competitor_name,
                "platform": platform,
                "topic_tendencies": [],
                "title_styles": [],
                "posting_schedule": "",
                "hashtag_strategy": "",
                "engagement_strategy": "",
                "takeaways": [],
            }

    async def compare_with_competitor(
        self,
        my_content: str,
        competitor_name: str,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        与竞品对比

        Args:
            my_content: 自己的内容
            competitor_name: 竞品名称
            platform: 平台

        Returns:
            Dict: 对比结果
        """
        try:
            prompt = f"""请对比分析以下内容与竞品"{competitor_name}"的差异。

自己的内容：
{my_content[:500]}

平台：{platform}

请分析：
1. 主要差距
2. 竞争优势
3. 劣势分析
4. 改进建议

请以JSON格式返回：
{{
    "main_gaps": ["差距1", "差距2"],
    "advantages": ["优势1", "优势2"],
    "disadvantages": ["劣势1", "劣势2"],
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
                "competitor": competitor_name,
                "platform": platform,
                "main_gaps": result.get("main_gaps", []),
                "advantages": result.get("advantages", []),
                "disadvantages": result.get("disadvantages", []),
                "improvement_suggestions": result.get("improvement_suggestions", []),
            }

        except Exception as e:
            logger.error(f"竞品对比失败: {e}")
            return {
                "competitor": competitor_name,
                "platform": platform,
                "main_gaps": [],
                "advantages": [],
                "disadvantages": [],
                "improvement_suggestions": [],
            }

    def get_benchmark_metrics(
        self,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        获取平台基准指标

        Args:
            platform: 平台

        Returns:
            Dict: 基准指标
        """
        benchmarks = {
            "xiaohongshu": {
                "avg_like_rate": 3.5,  # %
                "avg_comment_rate": 0.8,
                "avg_share_rate": 0.5,
                "avg_save_rate": 1.2,
                "good_engagement_rate": 5.0,
                "excellent_engagement_rate": 10.0,
            },
            "tiktok": {
                "avg_like_rate": 5.0,
                "avg_comment_rate": 0.4,
                "avg_share_rate": 0.8,
                "avg_save_rate": 0.3,
                "good_engagement_rate": 8.0,
                "excellent_engagement_rate": 15.0,
            },
            "weibo": {
                "avg_like_rate": 2.0,
                "avg_comment_rate": 0.5,
                "avg_share_rate": 1.0,
                "avg_save_rate": 0.2,
                "good_engagement_rate": 4.0,
                "excellent_engagement_rate": 8.0,
            },
        }

        return benchmarks.get(platform, benchmarks["xiaohongshu"])


# 全局实例
competitor_tracker_service = CompetitorTrackerService()


if __name__ == "__main__":
    import asyncio

    service = CompetitorTrackerService()

    async def test():
        print("=== 竞品追踪 ===")
        competitor = await service.track_competitor("某知名账号")
        print(f"竞品: {competitor.name}")
        print(f"粉丝: {competitor.followers:,}")
        print(f"平均浏览: {competitor.avg_views:,}")
        print(f"互动率: {competitor.avg_engagement}%")
        print(f"热门类型: {', '.join(competitor.top_content_types)}")
        print(f"优势: {', '.join(competitor.strengths)}")

        print("\n=== 竞品内容分析 ===")
        analysis = await service.analyze_competitor_content("某知名账号")
        print(f"主题倾向: {', '.join(analysis['topic_tendencies'][:3])}")
        print(f"标题风格: {', '.join(analysis['title_styles'][:2])}")
        print(f"借鉴之处: {', '.join(analysis['takeaways'][:2])}")

        print("\n=== 平台基准 ===")
        benchmarks = service.get_benchmark_metrics("xiaohongshu")
        print(f"平均点赞率: {benchmarks['avg_like_rate']}%")
        print(f"优秀互动率: {benchmarks['excellent_engagement_rate']}%")

    asyncio.run(test())
