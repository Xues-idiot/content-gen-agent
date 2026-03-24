"""
Vox Reporting 模块 - 报告生成

生成内容生成报告、统计报表等功能
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class ReportConfig:
    """报告配置"""
    title: str
    include_sections: List[str]
    date_range: Optional[tuple] = None
    platforms: Optional[List[str]] = None


@dataclass
class ContentReport:
    """内容报告"""
    success: bool
    report: Dict[str, Any]
    generated_at: str


class ContentReporter:
    """
    内容报告生成器

    功能：
    - 生成综合内容报告
    - 生成平台对比报告
    - 生成质量趋势报告
    - 生成违规词报告
    """

    def __init__(self):
        self._report_history: List[Dict[str, Any]] = []

    def generate_summary_report(
        self,
        content_data: List[Dict[str, Any]],
        config: ReportConfig,
    ) -> ContentReport:
        """
        生成综合报告

        Args:
            content_data: 内容数据列表
            config: 报告配置

        Returns:
            ContentReport: 综合报告
        """
        report = {
            "title": config.title,
            "date_range": config.date_range,
            "platforms": config.platforms or [],
            "sections": {},
        }

        # 生成各部分内容
        if "overview" in config.include_sections:
            report["sections"]["overview"] = self._generate_overview(content_data)

        if "platform_breakdown" in config.include_sections:
            report["sections"]["platform_breakdown"] = self._generate_platform_breakdown(content_data)

        if "quality_analysis" in config.include_sections:
            report["sections"]["quality_analysis"] = self._generate_quality_analysis(content_data)

        if "violation_report" in config.include_sections:
            report["sections"]["violation_report"] = self._generate_violation_report(content_data)

        return ContentReport(
            success=True,
            report=report,
            generated_at=datetime.now().isoformat(),
        )

    def _generate_overview(self, content_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成概览部分"""
        total = len(content_data)
        passed = len([c for c in content_data if c.get("passed", False)])
        failed = total - passed

        return {
            "total_contents": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / total * 100, 1) if total > 0 else 0,
        }

    def _generate_platform_breakdown(self, content_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成平台分布部分"""
        platform_counts = defaultdict(int)

        for content in content_data:
            platform = content.get("platform", "unknown")
            platform_counts[platform] += 1

        return {
            "platforms": dict(platform_counts),
            "top_platform": max(platform_counts.items(), key=lambda x: x[1])[0] if platform_counts else None,
        }

    def _generate_quality_analysis(self, content_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成质量分析部分"""
        scores = [c.get("quality_score", 0) for c in content_data]

        if not scores:
            return {"avg_score": 0, "min_score": 0, "max_score": 0}

        return {
            "avg_score": round(sum(scores) / len(scores), 2),
            "min_score": min(scores),
            "max_score": max(scores),
            "score_distribution": {
                "A (8+)": len([s for s in scores if s >= 8]),
                "B (6-8)": len([s for s in scores if 6 <= s < 8]),
                "C (4-6)": len([s for s in scores if 4 <= s < 6]),
                "D (<4)": len([s for s in scores if s < 4]),
            },
        }

    def _generate_violation_report(self, content_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成违规词报告部分"""
        all_violations = []

        for content in content_data:
            violations = content.get("violations", [])
            all_violations.extend([
                {"word": v.get("word"), "severity": v.get("severity")}
                for v in violations
            ])

        # 统计违规词频率
        violation_counts = defaultdict(int)
        severity_counts = defaultdict(int)

        for v in all_violations:
            violation_counts[v["word"]] += 1
            severity_counts[v["severity"]] += 1

        # Top 违规词
        top_violations = sorted(
            violation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            "total_violations": len(all_violations),
            "by_severity": dict(severity_counts),
            "top_violations": [{"word": w, "count": c} for w, c in top_violations],
        }

    def generate_comparison_report(
        self,
        content1: Dict[str, Any],
        content2: Dict[str, Any],
    ) -> ContentReport:
        """
        生成内容对比报告

        Args:
            content1: 第一个内容
            content2: 第二个内容

        Returns:
            ContentReport: 对比报告
        """
        report = {
            "title": "内容对比报告",
            "content1_overview": {
                "platform": content1.get("platform", "unknown"),
                "quality_score": content1.get("quality_score", 0),
                "passed": content1.get("passed", False),
            },
            "content2_overview": {
                "platform": content2.get("platform", "unknown"),
                "quality_score": content2.get("quality_score", 0),
                "passed": content2.get("passed", False),
            },
            "comparison": {
                "score_diff": content2.get("quality_score", 0) - content1.get("quality_score", 0),
                "winner": "content2" if content2.get("quality_score", 0) > content1.get("quality_score", 0) else "content1",
            },
        }

        return ContentReport(
            success=True,
            report=report,
            generated_at=datetime.now().isoformat(),
        )

    def generate_trend_report(
        self,
        daily_data: List[Dict[str, Any]],
        days: int = 7,
    ) -> ContentReport:
        """
        生成趋势报告

        Args:
            daily_data: 每日数据
            days: 统计天数

        Returns:
            ContentReport: 趋势报告
        """
        # 计算趋势
        scores = [d.get("avg_score", 0) for d in daily_data]

        trend = "stable"
        if len(scores) >= 2:
            if scores[-1] > scores[0] * 1.1:
                trend = "improving"
            elif scores[-1] < scores[0] * 0.9:
                trend = "declining"

        report = {
            "title": f"内容质量趋势报告 ({days}天)",
            "period": {
                "start": (datetime.now() - timedelta(days=days)).isoformat(),
                "end": datetime.now().isoformat(),
            },
            "daily_data": daily_data,
            "trend": {
                "direction": trend,
                "avg_score_change": scores[-1] - scores[0] if len(scores) >= 2 else 0,
            },
        }

        return ContentReport(
            success=True,
            report=report,
            generated_at=datetime.now().isoformat(),
        )

    def get_report_history(self) -> List[Dict[str, Any]]:
        """获取报告历史"""
        return self._report_history[-50:]  # 返回最近50条


# 全局报告器实例
content_reporter = ContentReporter()


if __name__ == "__main__":
    # 测试
    reporter = ContentReporter()

    test_data = [
        {"platform": "xiaohongshu", "quality_score": 8.5, "passed": True, "violations": []},
        {"platform": "xiaohongshu", "quality_score": 7.5, "passed": True, "violations": [{"word": "最好", "severity": "error"}]},
        {"platform": "tiktok", "quality_score": 9.0, "passed": True, "violations": []},
    ]

    config = ReportConfig(
        title="测试报告",
        include_sections=["overview", "platform_breakdown", "quality_analysis", "violation_report"],
    )

    report = reporter.generate_summary_report(test_data, config)
    print(f"Success: {report.success}")
    print(f"Report sections: {list(report.report['sections'].keys())}")
    print(f"Generated at: {report.generated_at}")