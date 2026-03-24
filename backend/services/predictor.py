"""
Vox Performance Predictor - 内容表现预测

基于历史数据和内容特征预测内容表现
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime
import random


@dataclass
class PerformancePrediction:
    """表现预测结果"""
    predicted_views: int
    predicted_likes: int
    predicted_comments: int
    predicted_shares: int
    engagement_rate: float
    reach_score: float
    confidence: str
    factors: Dict[str, Any]
    recommendations: List[str]


@dataclass
class PlatformBenchmarks:
    """平台基准数据"""
    platform: str
    avg_views: int
    avg_engagement_rate: float
    best_performing_categories: List[str]
    optimal_posting_times: List[str]


PLATFORM_BENCHMARKS = {
    "xiaohongshu": PlatformBenchmarks(
        platform="xiaohongshu",
        avg_views=5000,
        avg_engagement_rate=0.05,
        best_performing_categories=["美妆", "穿搭", "护肤", "母婴", "家居"],
        optimal_posting_times=["12:00-13:00", "18:00-20:00", "21:00-22:00"],
    ),
    "tiktok": PlatformBenchmarks(
        platform="tiktok",
        avg_views=10000,
        avg_engagement_rate=0.03,
        best_performing_categories=["美食", "搞笑", "生活", "知识", "宠物"],
        optimal_posting_times=["12:00-14:00", "18:00-20:00", "21:00-23:00"],
    ),
    "official": PlatformBenchmarks(
        platform="official",
        avg_views=2000,
        avg_engagement_rate=0.02,
        best_performing_categories=["科技", "财经", "职场", "健康", "教育"],
        optimal_posting_times=["08:00-09:00", "12:00-13:00", "20:00-21:00"],
    ),
    "friend_circle": PlatformBenchmarks(
        platform="friend_circle",
        avg_views=500,
        avg_engagement_rate=0.08,
        best_performing_categories=["生活", "美食", "旅行", "亲子", "日常"],
        optimal_posting_times=["08:00-09:00", "12:00-13:00", "17:30-18:30", "21:00-22:00"],
    ),
}


class PerformancePredictor:
    """
    内容表现预测器

    基于内容特征和平台数据预测内容表现
    """

    def __init__(self):
        self.benchmarks = PLATFORM_BENCHMARKS

    def predict(
        self,
        content: str,
        platform: str,
        title: str = "",
        tags: Optional[List[str]] = None,
        posting_time: Optional[str] = None,
        category: Optional[str] = None,
    ) -> PerformancePrediction:
        """
        预测内容表现

        Args:
            content: 内容正文
            platform: 目标平台
            title: 标题
            tags: 标签列表
            posting_time: 发布时间
            category: 内容类别

        Returns:
            PerformancePrediction: 预测结果
        """
        benchmark = self.benchmarks.get(platform, self.benchmarks["xiaohongshu"])

        # 计算各项得分
        content_score = self._calculate_content_score(content, title, tags)
        timing_score = self._calculate_timing_score(posting_time, benchmark)
        category_score = self._calculate_category_score(category, benchmark)
        engagement_score = self._calculate_engagement_factors(content, tags)

        # 综合得分 (0-100)
        combined_score = (
            content_score * 0.4 +
            timing_score * 0.2 +
            category_score * 0.2 +
            engagement_score * 0.2
        )

        # 预测数值
        base_multiplier = combined_score / 100

        predicted_views = int(benchmark.avg_views * base_multiplier * random.uniform(0.8, 1.2))
        engagement_rate = benchmark.avg_engagement_rate * (1 + (combined_score - 50) / 100)

        predicted_likes = int(predicted_views * engagement_rate)
        predicted_comments = int(predicted_views * engagement_rate * 0.1)
        predicted_shares = int(predicted_views * engagement_rate * 0.05)

        # 置信度
        confidence = self._get_confidence(content_score, timing_score)

        # 影响因素
        factors = {
            "content_score": content_score,
            "timing_score": timing_score,
            "category_score": category_score,
            "engagement_score": engagement_score,
            "combined_score": combined_score,
        }

        # 建议
        recommendations = self._generate_recommendations(
            content_score, timing_score, category_score, platform
        )

        return PerformancePrediction(
            predicted_views=predicted_views,
            predicted_likes=predicted_likes,
            predicted_comments=predicted_comments,
            predicted_shares=predicted_shares,
            engagement_rate=engagement_rate,
            reach_score=combined_score,
            confidence=confidence,
            factors=factors,
            recommendations=recommendations,
        )

    def _calculate_content_score(
        self,
        content: str,
        title: str,
        tags: Optional[List[str]],
    ) -> float:
        """计算内容得分"""
        score = 50.0

        # 长度因素
        length = len(content)
        if 300 <= length <= 800:
            score += 15
        elif length < 300:
            score += (length / 300) * 10
        elif length > 1000:
            score -= 5

        # 标题因素
        if title:
            if len(title) <= 20:
                score += 5
            if any(char in title for char in ["！", "?", "？", "..."]):
                score += 5

        # 标签因素
        if tags:
            if 3 <= len(tags) <= 8:
                score += 10
            elif len(tags) > 8:
                score += 5

        # Emoji因素
        emoji_count = content.count("[") + content.count("!")
        if 3 <= emoji_count <= 10:
            score += 5

        return min(100, max(0, score))

    def _calculate_timing_score(
        self,
        posting_time: Optional[str],
        benchmark: PlatformBenchmarks,
    ) -> float:
        """计算时间得分"""
        if not posting_time:
            return 50.0

        # 简化逻辑：检查是否在最佳时间
        for best_time in benchmark.optimal_posting_times:
            if posting_time >= best_time.split("-")[0]:
                return 80.0

        return 50.0

    def _calculate_category_score(
        self,
        category: Optional[str],
        benchmark: PlatformBenchmarks,
    ) -> float:
        """计算类别得分"""
        if not category:
            return 50.0

        if category in benchmark.best_performing_categories:
            return 80.0

        return 50.0

    def _calculate_engagement_factors(
        self,
        content: str,
        tags: Optional[List[str]],
    ) -> float:
        """计算互动因素得分"""
        score = 50.0

        # 问题引导
        if "？" in content or "?" in content:
            score += 10

        # 数字使用
        has_numbers = any(char.isdigit() for char in content)
        if has_numbers:
            score += 5

        # CTA
        cta_keywords = ["评论", "点赞", "关注", "收藏", "分享"]
        if any(keyword in content for keyword in cta_keywords):
            score += 10

        # 热门标签
        hot_tags = ["好物推荐", "种草", "测评", "教程", "分享"]
        if tags and any(tag in hot_tags for tag in tags):
            score += 5

        return min(100, max(0, score))

    def _get_confidence(self, content_score: float, timing_score: float) -> str:
        """获取预测置信度"""
        variance = abs(content_score - timing_score)

        if variance < 15:
            return "high"
        elif variance < 30:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(
        self,
        content_score: float,
        timing_score: float,
        category_score: float,
        platform: str,
    ) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if content_score < 60:
            recommendations.append("内容质量有提升空间，建议优化文案结构和表达")
        if timing_score < 60:
            recommendations.append("发布时间可能不是最佳时段，建议调整")
        if category_score < 60:
            recommendations.append("内容类别可能不适合该平台，建议调整方向")

        if not recommendations:
            recommendations.append("内容和发布策略良好，保持当前做法")

        return recommendations

    def compare_predictions(
        self,
        prediction1: PerformancePrediction,
        prediction2: PerformancePrediction,
    ) -> Dict[str, Any]:
        """
        对比两个预测结果

        Args:
            prediction1: 第一个预测
            prediction2: 第二个预测

        Returns:
            dict: 对比分析
        """
        views_diff = prediction2.predicted_views - prediction1.predicted_views
        engagement_diff = prediction2.engagement_rate - prediction1.engagement_rate

        return {
            "winner": "prediction2" if prediction2.reach_score > prediction1.reach_score else "prediction1",
            "views_diff": views_diff,
            "views_diff_pct": round(views_diff / max(prediction1.predicted_views, 1) * 100, 1),
            "engagement_diff": round(engagement_diff * 100, 2),
            "score_diff": round(prediction2.reach_score - prediction1.reach_score, 1),
        }

    def get_platform_recommendations(self, platform: str) -> Dict[str, Any]:
        """
        获取平台发布建议

        Args:
            platform: 平台名称

        Returns:
            dict: 平台建议
        """
        benchmark = self.benchmarks.get(platform, self.benchmarks["xiaohongshu"])

        return {
            "platform": platform,
            "avg_views": benchmark.avg_views,
            "avg_engagement_rate": benchmark.avg_engagement_rate,
            "best_categories": benchmark.best_performing_categories,
            "optimal_times": benchmark.optimal_posting_times,
            "tips": [
                f"该平台平均浏览量约{benchmark.avg_views}",
                f"平均互动率约{benchmark.avg_engagement_rate * 100}%",
                f"最佳发布时段: {', '.join(benchmark.optimal_posting_times)}",
                f"热门类别: {', '.join(benchmark.best_performing_categories[:3])}",
            ],
        }


# 全局预测器实例
performance_predictor = PerformancePredictor()


if __name__ == "__main__":
    predictor = PerformancePredictor()

    # 测试预测
    result = predictor.predict(
        content="今天要跟大家分享一款超好用的产品！用了之后效果真的太惊艳了...",
        platform="xiaohongshu",
        title="这款产品真的绝了！强烈推荐",
        tags=["#好物推荐", "#种草", "#测评"],
        posting_time="19:00",
        category="美妆",
    )

    print(f"Predicted Views: {result.predicted_views}")
    print(f"Engagement Rate: {result.engagement_rate:.2%}")
    print(f"Reach Score: {result.reach_score:.1f}")
    print(f"Confidence: {result.confidence}")
    print(f"Recommendations: {result.recommendations}")