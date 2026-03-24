"""
Vox Analytics 模块 - 内容分析统计

提供内容质量追踪、平台表现分析、趋势预测等功能
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import uuid


@dataclass
class ContentMetrics:
    """内容指标"""
    content_id: str
    platform: str
    quality_score: float
    word_count: int
    char_count: int
    violation_count: int
    emoji_count: int
    hashtag_count: int
    created_at: str


@dataclass
class PlatformAnalytics:
    """平台分析"""
    platform: str
    total_contents: int
    avg_quality_score: float
    avg_word_count: float
    total_violations: int
    top_keywords: List[str]
    trend_direction: str  # "up", "down", "stable"


@dataclass
class QualityTrend:
    """质量趋势"""
    date: str
    avg_score: float
    content_count: int
    violation_rate: float


class ContentAnalytics:
    """
    内容分析服务

    功能：
    - 内容质量追踪
    - 平台表现分析
    - 关键词频率统计
    - 质量趋势预测
    """

    def __init__(self):
        self._metrics_store: List[ContentMetrics] = []
        self._content_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def record_content(self, content_data: Dict[str, Any]) -> str:
        """
        记录内容指标

        Args:
            content_data: 内容数据字典

        Returns:
            str: 内容ID
        """
        content_id = str(uuid.uuid4())[:8]
        metrics = ContentMetrics(
            content_id=content_id,
            platform=content_data.get("platform", "unknown"),
            quality_score=content_data.get("quality_score", 0.0),
            word_count=content_data.get("word_count", 0),
            char_count=content_data.get("char_count", 0),
            violation_count=content_data.get("violation_count", 0),
            emoji_count=content_data.get("emoji_count", 0),
            hashtag_count=content_data.get("hashtag_count", 0),
            created_at=datetime.now().isoformat(),
        )
        self._metrics_store.append(metrics)
        return content_id

    def get_platform_analytics(self, platform: Optional[str] = None) -> Dict[str, Any]:
        """
        获取平台分析

        Args:
            platform: 可选的平台过滤

        Returns:
            dict: 平台分析结果
        """
        metrics_list = (
            [m for m in self._metrics_store if m.platform == platform]
            if platform
            else self._metrics_store
        )

        if not metrics_list:
            return {
                "platform": platform or "all",
                "total_contents": 0,
                "message": "No data available",
            }

        # 按平台分组
        platform_groups: Dict[str, List[ContentMetrics]] = defaultdict(list)
        for m in metrics_list:
            platform_groups[m.platform].append(m)

        # 计算每个平台的统计
        platform_stats = {}
        for plat, metrics in platform_groups.items():
            scores = [m.quality_score for m in metrics]
            word_counts = [m.word_count for m in metrics]
            violations = sum(m.violation_count for m in metrics)

            # 提取高频关键词
            all_keywords = []
            for m in metrics:
                all_keywords.extend([f"word_{m.word_count}", f"emoji_{m.emoji_count}"])

            platform_stats[plat] = {
                "total_contents": len(metrics),
                "avg_quality_score": sum(scores) / len(scores) if scores else 0,
                "avg_word_count": sum(word_counts) / len(word_counts) if word_counts else 0,
                "total_violations": violations,
                "violation_rate": violations / len(metrics) if metrics else 0,
            }

        # 总体统计
        all_scores = [m.quality_score for m in metrics_list]
        all_words = [m.word_count for m in metrics_list]
        total_violations = sum(m.violation_count for m in metrics_list)

        return {
            "platform": platform or "all",
            "total_contents": len(metrics_list),
            "avg_quality_score": sum(all_scores) / len(all_scores) if all_scores else 0,
            "avg_word_count": sum(all_words) / len(all_words) if all_words else 0,
            "total_violations": total_violations,
            "violation_rate": total_violations / len(metrics_list) if metrics_list else 0,
            "by_platform": platform_stats,
        }

    def get_quality_trends(self, days: int = 7) -> List[QualityTrend]:
        """
        获取质量趋势

        Args:
            days: 统计天数

        Returns:
            List[QualityTrend]: 每日质量趋势
        """
        trends = []
        now = datetime.now()

        for i in range(days):
            date = now - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")

            day_metrics = [
                m for m in self._metrics_store
                if m.created_at.startswith(date_str)
            ]

            if day_metrics:
                scores = [m.quality_score for m in day_metrics]
                violations = sum(m.violation_count for m in day_metrics)
                trends.append(QualityTrend(
                    date=date_str,
                    avg_score=sum(scores) / len(scores),
                    content_count=len(day_metrics),
                    violation_rate=violations / len(day_metrics),
                ))
            else:
                trends.append(QualityTrend(
                    date=date_str,
                    avg_score=0.0,
                    content_count=0,
                    violation_rate=0.0,
                ))

        return trends

    def compare_platforms(self) -> Dict[str, Any]:
        """
        对比各平台表现

        Returns:
            dict: 平台对比结果
        """
        platform_groups: Dict[str, List[ContentMetrics]] = defaultdict(list)
        for m in self._metrics_store:
            platform_groups[m.platform].append(m)

        comparison = {}
        for platform, metrics in platform_groups.items():
            scores = [m.quality_score for m in metrics]
            comparison[platform] = {
                "total_contents": len(metrics),
                "avg_quality": sum(scores) / len(scores) if scores else 0,
                "min_quality": min(scores) if scores else 0,
                "max_quality": max(scores) if scores else 0,
                "total_violations": sum(m.violation_count for m in metrics),
            }

        # 计算最佳平台
        if comparison:
            best_platform = max(
                comparison.items(),
                key=lambda x: x[1]["avg_quality"]
            )[0]
            comparison["best_platform"] = best_platform

        return comparison

    def get_content_health_score(self, content_id: str) -> Dict[str, Any]:
        """
        获取内容健康分

        Args:
            content_id: 内容ID

        Returns:
            dict: 健康分详情
        """
        content_metrics = [m for m in self._metrics_store if m.content_id == content_id]

        if not content_metrics:
            return {"error": "Content not found", "health_score": 0}

        m = content_metrics[0]

        # 计算健康分 (0-100)
        quality_weight = 0.4
        length_weight = 0.2
        violation_weight = 0.3
        engagement_weight = 0.1

        # 质量分 (直接使用)
        quality_score = m.quality_score * 10  # 转换为0-100

        # 长度分 (理想长度300-800字)
        if 300 <= m.word_count <= 800:
            length_score = 100
        elif m.word_count < 300:
            length_score = (m.word_count / 300) * 100
        else:
            length_score = max(0, 100 - (m.word_count - 800) / 10)

        # 违规分 (越低越好)
        violation_score = max(0, 100 - m.violation_count * 20)

        # 互动分 (emoji + hashtag)
        engagement_score = min(100, (m.emoji_count + m.hashtag_count) * 10)

        health_score = (
            quality_score * quality_weight +
            length_score * length_weight +
            violation_score * violation_weight +
            engagement_score * engagement_weight
        )

        return {
            "content_id": content_id,
            "health_score": round(health_score, 1),
            "breakdown": {
                "quality": round(quality_score, 1),
                "length": round(length_score, 1),
                "violation": round(violation_score, 1),
                "engagement": round(engagement_score, 1),
            },
            "suggestions": self._generate_health_suggestions(m),
        }

    def _generate_health_suggestions(self, metrics: ContentMetrics) -> List[str]:
        """生成健康改进建议"""
        suggestions = []

        if metrics.quality_score < 7:
            suggestions.append("质量分数偏低，建议优化文案结构和表达")
        if metrics.word_count < 300:
            suggestions.append("内容偏短，建议增加详细信息或案例")
        if metrics.word_count > 1000:
            suggestions.append("内容偏长，建议精简要点")
        if metrics.violation_count > 0:
            suggestions.append(f"发现{metrics.violation_count}处违规词，请修改")
        if metrics.emoji_count == 0:
            suggestions.append("建议添加emoji提升可读性")
        if metrics.hashtag_count < 3:
            suggestions.append("建议增加相关标签提升曝光")

        return suggestions


# 全局实例
content_analytics = ContentAnalytics()


if __name__ == "__main__":
    # 测试
    analytics = ContentAnalytics()

    # 添加测试数据
    test_data = [
        {"platform": "xiaohongshu", "quality_score": 8.5, "word_count": 500, "char_count": 2500, "violation_count": 0, "emoji_count": 5, "hashtag_count": 4},
        {"platform": "xiaohongshu", "quality_score": 7.5, "word_count": 400, "char_count": 2000, "violation_count": 1, "emoji_count": 3, "hashtag_count": 3},
        {"platform": "tiktok", "quality_score": 9.0, "word_count": 150, "char_count": 750, "violation_count": 0, "emoji_count": 2, "hashtag_count": 5},
    ]

    for data in test_data:
        analytics.record_content(data)

    # 测试分析
    print("Platform Analytics:", analytics.get_platform_analytics())
    print("\nQuality Trends:", analytics.get_quality_trends())
    print("\nPlatform Comparison:", analytics.compare_platforms())