"""
Vox Content Performance Report Service 模块

内容表现报告服务
- 生成内容表现报告
- 分析内容表现数据
- 提供改进建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class PerformanceReport:
    """内容表现报告"""
    content_title: str
    platform: str
    report_date: str
    metrics: Dict[str, Any]  # 关键指标
    analysis: str  # 分析文字
    highlights: List[str]  # 亮点
    issues: List[str]  # 问题
    suggestions: List[str]  # 改进建议
    overall_score: int  # 综合评分 0-100


class PerformanceReportService:
    """
    内容表现报告服务

    基于内容数据生成表现报告和改进建议
    """

    METRIC_NAMES = {
        "views": "浏览量",
        "likes": "点赞数",
        "comments": "评论数",
        "shares": "分享数",
        "saves": "收藏数",
        "followers": "新增粉丝",
        "engagement_rate": "互动率",
        "click_through_rate": "点击率",
        "completion_rate": "完播率",
    }

    def __init__(self):
        self.llm = llm_service

    async def generate_report(
        self,
        content_data: Dict[str, Any],
        platform: str = "xiaohongshu",
    ) -> PerformanceReport:
        """
        生成内容表现报告

        Args:
            content_data: 内容数据，包含各种指标
                - title: 内容标题
                - views: 浏览量
                - likes: 点赞数
                - comments: 评论数
                - shares: 分享数
                - saves: 收藏数
                - followers: 新增粉丝（可选）
                - engagement_rate: 互动率（可选）
            platform: 平台

        Returns:
            PerformanceReport: 表现报告
        """
        try:
            title = content_data.get("title", "未知内容")
            views = content_data.get("views", 0)
            likes = content_data.get("likes", 0)
            comments = content_data.get("comments", 0)
            shares = content_data.get("shares", 0)
            saves = content_data.get("saves", 0)

            # 计算互动率
            engagement_rate = (likes + comments + shares + saves) / views * 100 if views > 0 else 0

            prompt = f"""请分析以下内容的表现数据，并生成详细报告。

平台：{platform}
内容标题：{title}

表现数据：
- 浏览量：{views:,}
- 点赞数：{likes:,}
- 评论数：{comments:,}
- 分享数：{shares:,}
- 收藏数：{saves:,}
- 互动率：{engagement_rate:.2f}%

请生成包含以下内容的报告：
1. **关键指标分析** - 各指标的评价
2. **亮点** - 表现好的方面（2-3个）
3. **问题** - 表现不足的方面（2-3个）
4. **改进建议** - 具体可操作的改进建议（3-5个）
5. **综合评分** - 0-100分的评分

请以JSON格式返回：
{{
    "metrics": {{
        "views": {{"value": {views}, "evaluation": "评价", "score": 0-100}},
        "likes": {{"value": {likes}, "evaluation": "评价", "score": 0-100}},
        "comments": {{"value": {comments}, "evaluation": "评价", "score": 0-100}},
        "shares": {{"value": {shares}, "evaluation": "评价", "score": 0-100}},
        "saves": {{"value": {saves}, "evaluation": "评价", "score": 0-100}},
        "engagement_rate": {{"value": {engagement_rate:.2f}, "evaluation": "评价", "score": 0-100}}
    }},
    "analysis": "整体分析文字",
    "highlights": ["亮点1", "亮点2"],
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2", "建议3"],
    "overall_score": 75
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                if match:
                    result = json.loads(match.group())
                else:
                    result = self._get_default_report(title, platform, content_data)

            metrics = result.get("metrics", {})
            highlights = result.get("highlights", [])
            issues = result.get("issues", [])
            suggestions = result.get("suggestions", [])

            return PerformanceReport(
                content_title=title,
                platform=platform,
                report_date=datetime.now().strftime("%Y-%m-%d"),
                metrics=metrics,
                analysis=result.get("analysis", ""),
                highlights=highlights,
                issues=issues,
                suggestions=suggestions,
                overall_score=result.get("overall_score", 60),
            )

        except Exception as e:
            logger.error(f"生成表现报告失败: {e}")
            return self._get_default_report(
                content_data.get("title", "未知"),
                platform,
                content_data
            )

    def _get_default_report(
        self,
        title: str,
        platform: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """获取默认报告"""
        views = data.get("views", 0)
        engagement_rate = 0
        if views > 0:
            likes = data.get("likes", 0)
            comments = data.get("comments", 0)
            shares = data.get("shares", 0)
            saves = data.get("saves", 0)
            engagement_rate = (likes + comments + shares + saves) / views * 100

        return {
            "metrics": {
                "views": {"value": views, "evaluation": "中等", "score": 60},
                "likes": {"value": data.get("likes", 0), "evaluation": "中等", "score": 60},
                "comments": {"value": data.get("comments", 0), "evaluation": "中等", "score": 60},
                "shares": {"value": data.get("shares", 0), "evaluation": "中等", "score": 60},
                "saves": {"value": data.get("saves", 0), "evaluation": "中等", "score": 60},
                "engagement_rate": {"value": engagement_rate, "evaluation": "中等", "score": 60},
            },
            "analysis": "内容表现中等，建议持续优化",
            "highlights": ["基础数据正常"],
            "issues": ["缺乏爆款因素"],
            "suggestions": ["优化标题", "增加互动引导", "提高内容质量"],
            "overall_score": 60,
        }

    async def compare_content_report(
        self,
        content_list: List[Dict[str, Any]],
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        生成内容对比报告

        Args:
            content_list: 内容列表
            platform: 平台

        Returns:
            Dict: 对比分析结果
        """
        try:
            prompt = f"""请对比分析以下多个内容的表现数据。

平台：{platform}

内容列表：
{json.dumps(content_list, ensure_ascii=False, indent=2)}

请分析：
1. 表现最好的内容及原因
2. 表现最差的内容及原因
3. 共同的成功因素
4. 共同的不足之处
5. 差异化分析

请以JSON格式返回：
{{
    "best_performer": {{
        "title": "最佳内容标题",
        "reasons": ["原因1", "原因2"]
    }},
    "worst_performer": {{
        "title": "最差内容标题",
        "reasons": ["原因1", "原因2"]
    }},
    "common_success_factors": ["因素1", "因素2"],
    "common_weaknesses": ["不足1", "不足2"],
    "differentiation_tips": ["技巧1", "技巧2"]
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
            logger.error(f"生成对比报告失败: {e}")
            return {
                "best_performer": {"title": content_list[0].get("title", "") if content_list else "", "reasons": ["数据不足"]},
                "worst_performer": {"title": "", "reasons": ["数据不足"]},
                "common_success_factors": [],
                "common_weaknesses": [],
                "differentiation_tips": [],
            }

    def generate_summary_dashboard(
        self,
        content_data_list: List[Dict[str, Any]],
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        生成汇总数据看板

        Args:
            content_data_list: 内容数据列表
            platform: 平台

        Returns:
            Dict: 看板数据
        """
        if not content_data_list:
            return self._empty_dashboard(platform)

        # 计算汇总指标
        total_views = sum(c.get("views", 0) for c in content_data_list)
        total_likes = sum(c.get("likes", 0) for c in content_data_list)
        total_comments = sum(c.get("comments", 0) for c in content_data_list)
        total_shares = sum(c.get("shares", 0) for c in content_data_list)
        total_saves = sum(c.get("saves", 0) for c in content_data_list)

        avg_engagement = 0
        if total_views > 0:
            avg_engagement = (total_likes + total_comments + total_shares + total_saves) / total_views * 100

        # 找出最佳和最差
        sorted_by_views = sorted(content_data_list, key=lambda x: x.get("views", 0), reverse=True)
        best = sorted_by_views[0] if sorted_by_views else {}
        worst = sorted_by_views[-1] if len(sorted_by_views) > 1 else best

        return {
            "platform": platform,
            "period": "最近N天",
            "total_contents": len(content_data_list),
            "total_metrics": {
                "views": total_views,
                "likes": total_likes,
                "comments": total_comments,
                "shares": total_shares,
                "saves": total_saves,
            },
            "averages": {
                "views": total_views // len(content_data_list),
                "likes": total_likes // len(content_data_list),
                "engagement_rate": avg_engagement,
            },
            "best_content": {
                "title": best.get("title", ""),
                "views": best.get("views", 0),
            },
            "worst_content": {
                "title": worst.get("title", ""),
                "views": worst.get("views", 0),
            },
            "performance_distribution": {
                "excellent": len([c for c in content_data_list if c.get("views", 0) > total_views // len(content_data_list) * 1.5]),
                "good": len([c for c in content_data_list if total_views // len(content_data_list) * 0.5 < c.get("views", 0) <= total_views // len(content_data_list) * 1.5]),
                "poor": len([c for c in content_data_list if c.get("views", 0) <= total_views // len(content_data_list) * 0.5]),
            },
        }

    def _empty_dashboard(self, platform: str) -> Dict[str, Any]:
        """空看板数据"""
        return {
            "platform": platform,
            "period": "最近N天",
            "total_contents": 0,
            "total_metrics": {"views": 0, "likes": 0, "comments": 0, "shares": 0, "saves": 0},
            "averages": {"views": 0, "likes": 0, "engagement_rate": 0},
            "best_content": {"title": "", "views": 0},
            "worst_content": {"title": "", "views": 0},
            "performance_distribution": {"excellent": 0, "good": 0, "poor": 0},
        }


# 全局实例
performance_report_service = PerformanceReportService()


if __name__ == "__main__":
    import asyncio

    service = PerformanceReportService()

    async def test():
        # 测试单个报告
        print("=== 内容表现报告 ===")
        content_data = {
            "title": "这款面霜真的太好用了！",
            "views": 10000,
            "likes": 500,
            "comments": 80,
            "shares": 30,
            "saves": 100,
        }

        report = await service.generate_report(content_data, "xiaohongshu")
        print(f"标题: {report.content_title}")
        print(f"综合评分: {report.overall_score}/100")
        print(f"分析: {report.analysis}")
        print(f"亮点: {', '.join(report.highlights)}")
        print(f"建议: {', '.join(report.suggestions)}")

        # 测试汇总看板
        print("\n=== 汇总看板 ===")
        dashboard = service.generate_summary_dashboard([content_data], "xiaohongshu")
        print(f"总内容数: {dashboard['total_contents']}")
        print(f"总浏览量: {dashboard['total_metrics']['views']:,}")
        print(f"平均互动率: {dashboard['averages']['engagement_rate']:.2f}%")

    asyncio.run(test())
