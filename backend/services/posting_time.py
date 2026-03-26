"""
Vox Posting Time Service 模块

最佳发布时间建议服务
- 基于平台和受众分析推荐发布时间
- 提供每日/每周最佳时段
- 考虑行业特点和时间段效果
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from loguru import logger


@dataclass
class TimeSlot:
    """时间段"""
    time: str  # "09:00"
    day_of_week: str  # "周一" - "周日"
    score: int  # 0-100 推荐分数
    exposure: str  # 低/中/高
    engagement: str  # 低/中/高
    reason: str  # 推荐理由


@dataclass
class PostingTimeSuggestion:
    """发布时间建议"""
    platform: str
    industry: str
    best_times: List[TimeSlot]
    worst_times: List[TimeSlot]
    tips: List[str]


class PostingTimeService:
    """
    最佳发布时间建议服务

    基于平台特性和行业规律提供最佳发布时间建议
    """

    # 平台基础活跃时段数据（小时为单位，24小时制）
    PLATFORM_HOURS = {
        "xiaohongshu": {
            "peak_morning": [8, 9, 10, 11],
            "peak_noon": [12, 13],
            "peak_evening": [18, 19, 20, 21, 22],
            "peak_weekend": [10, 11, 14, 15, 16],
            "low_hours": [0, 1, 2, 3, 4, 5, 6],
        },
        "tiktok": {
            "peak_morning": [7, 8, 9],
            "peak_noon": [12, 13],
            "peak_evening": [18, 19, 20, 21],
            "peak_weekend": [9, 10, 11, 14, 15, 16, 20],
            "low_hours": [0, 1, 2, 3, 4, 5, 6],
        },
        "official": {
            "peak_morning": [8, 9, 10],
            "peak_noon": [12],
            "peak_evening": [20, 21],
            "peak_weekend": [10, 11],
            "low_hours": [0, 1, 2, 3, 4, 5, 6, 22, 23],
        },
        "friend_circle": {
            "peak_morning": [7, 8, 9],
            "peak_noon": [11, 12],
            "peak_evening": [17, 18, 19, 20, 21],
            "peak_weekend": [10, 11, 12, 14, 15, 16, 18],
            "low_hours": [0, 1, 2, 3, 4, 5, 6, 22, 23],
        },
    }

    # 行业特性（工作日 vs 周末偏好）
    INDUSTRY_WEEKEND_PREFERENCE = {
        "美妆": 0.7,  # 周末偏好高
        "时尚": 0.8,  # 强烈周末偏好
        "美食": 0.6,  # 略偏周末
        "旅行": 0.9,  # 强烈周末/假期偏好
        "健身": 0.5,  # 工作日略高
        "母婴": 0.7,  # 周末偏好
        "家居": 0.4,  # 工作日偏好
        "数码": 0.3,  # 工作日偏好
        "宠物": 0.6,  # 略偏周末
        "教育": 0.2,  # 工作日强烈偏好
        "通用": 0.5,  # 中性
    }

    # 时段效果描述
    TIME_EFFECTS = {
        "morning_early": "早起用户刷手机，适合轻松内容",
        "morning_peak": "上班路上，阅读高峰期",
        "noon": "午休时间碎片化浏览",
        "afternoon": "下午工作间隙，可能没那么多注意力",
        "evening_peak": "下班后黄金时段，活跃度最高",
        "night_late": "睡前放松浏览，可能影响睡眠",
    }

    def __init__(self):
        pass

    def _get_day_name(self, day_offset: int) -> str:
        """获取星期几的名称"""
        days = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
        return days[day_offset % 7]

    def _get_time_slot_name(self, hour: int) -> str:
        """获取时段名称"""
        if 5 <= hour < 7:
            return "清晨"
        elif 7 <= hour < 9:
            return "早高峰"
        elif 9 <= hour < 12:
            return "上午"
        elif 12 <= hour < 14:
            return "午休"
        elif 14 <= hour < 17:
            return "下午"
        elif 17 <= hour < 19:
            return "晚高峰"
        elif 19 <= hour < 22:
            return "晚间"
        else:
            return "深夜"

    def _calculate_score(
        self,
        platform: str,
        industry: str,
        day_of_week: int,
        hour: int,
    ) -> int:
        """计算发布时间分数"""
        if platform not in self.PLATFORM_HOURS:
            platform = "xiaohongshu"

        platform_data = self.PLATFORM_HOURS[platform]
        base_score = 30  # 基础分数

        # 平台时段加成
        if hour in platform_data["peak_morning"]:
            base_score += 20
        elif hour in platform_data["peak_noon"]:
            base_score += 15
        elif hour in platform_data["peak_evening"]:
            base_score += 25
        elif hour in platform_data["low_hours"]:
            base_score -= 10

        # 周末加成
        weekend_pref = self.INDUSTRY_WEEKEND_PREFERENCE.get(industry, 0.5)
        is_weekend = day_of_week in [0, 6]  # 周日=0, 周六=6

        if is_weekend:
            # 计算该时段在周末是否是高峰
            if hour in platform_data.get("peak_weekend", []):
                base_score += int(15 * weekend_pref)
            else:
                # 非周末高峰时段在周末可能效果更好
                base_score += int(5 * weekend_pref)
        else:
            # 工作日
            if hour in platform_data["peak_evening"] or hour in platform_data["peak_morning"]:
                base_score += int(10 * (1 - weekend_pref))

        # 确保分数在 0-100 之间
        return max(0, min(100, base_score))

    def _get_exposure_level(self, score: int) -> str:
        """根据分数判断曝光等级"""
        if score >= 70:
            return "高"
        elif score >= 50:
            return "中"
        return "低"

    def _get_engagement_level(self, score: int) -> str:
        """根据分数判断互动等级"""
        if score >= 65:
            return "高"
        elif score >= 45:
            return "中"
        return "低"

    def _generate_reason(self, platform: str, day_of_week: int, hour: int, score: int) -> str:
        """生成推荐理由"""
        reasons = []
        is_weekend = day_of_week in [0, 6]
        day_name = self._get_day_name(day_of_week)
        time_name = self._get_time_slot_name(hour)

        platform_names = {
            "xiaohongshu": "小红书",
            "tiktok": "抖音",
            "official": "公众号",
            "friend_circle": "朋友圈",
        }

        # 基于平台特性
        if platform == "xiaohongshu":
            if 18 <= hour <= 22:
                reasons.append(f"{platform_names.get(platform, platform)}用户晚间活跃度最高")
            elif 8 <= hour <= 11:
                reasons.append(f"职场女性午间浏览高峰")
            elif is_weekend and 14 <= hour <= 16:
                reasons.append(f"周末休闲时光，{platform_names.get(platform, platform)}使用率高")
        elif platform == "tiktok":
            if 12 <= hour <= 13:
                reasons.append(f"午休时间刷短视频放松")
            elif 18 <= hour <= 21:
                reasons.append(f"下班后娱乐消遣的黄金时段")
        elif platform == "official":
            if 8 <= hour <= 10:
                reasons.append(f"职场人士获取资讯的主要时段")
        elif platform == "friend_circle":
            if 17 <= hour <= 20:
                reasons.append(f"朋友圈浏览的活跃时段")

        # 分数高的通用理由
        if score >= 70:
            reasons.append("流量高峰期，曝光量大")
        elif score < 40:
            reasons.append("流量低谷期，建议避开")

        return reasons[0] if reasons else f"{day_name} {time_name} 时段"

    def get_suggestions(
        self,
        platform: str = "xiaohongshu",
        industry: str = "通用",
        days_ahead: int = 7,
    ) -> PostingTimeSuggestion:
        """
        获取发布时间建议

        Args:
            platform: 目标平台
            industry: 所属行业
            days_ahead: 提前多少天建议（默认7天）

        Returns:
            PostingTimeSuggestion: 包含最佳和最差时段的建议
        """
        all_time_slots: List[TimeSlot] = []

        # 生成接下来N天的建议
        now = datetime.now()
        for day_offset in range(days_ahead):
            target_date = now + timedelta(days=day_offset)
            day_of_week = target_date.weekday()  # 0=周一, 6=周日

            # 生成每天的小时建议（只建议6点到23点）
            for hour in range(6, 23):
                score = self._calculate_score(platform, industry, day_of_week, hour)
                time_str = f"{hour:02d}:00"

                all_time_slots.append(TimeSlot(
                    time=time_str,
                    day_of_week=self._get_day_name(day_of_week),
                    score=score,
                    exposure=self._get_exposure_level(score),
                    engagement=self._get_engagement_level(score),
                    reason=self._generate_reason(platform, day_of_week, hour, score),
                ))

        # 按分数排序
        all_time_slots.sort(key=lambda x: x.score, reverse=True)

        # 取最佳和最差时段
        best_times = all_time_slots[:10]
        worst_times = all_time_slots[-5:] if len(all_time_slots) > 5 else all_time_slots[-3:]

        # 生成建议tips
        tips = self._generate_tips(platform, industry)

        return PostingTimeSuggestion(
            platform=platform,
            industry=industry,
            best_times=best_times,
            worst_times=worst_times,
            tips=tips,
        )

    def _generate_tips(self, platform: str, industry: str) -> List[str]:
        """生成发布时间建议tips"""
        tips = []

        platform_names = {
            "xiaohongshu": "小红书",
            "tiktok": "抖音",
            "official": "公众号",
            "friend_circle": "朋友圈",
        }

        # 通用建议
        tips.append("保持规律更新，培养用户期待")

        # 平台特定建议
        if platform == "xiaohongshu":
            tips.append("晚间18-22点发布效果最佳")
            tips.append("周末下午14-16点是流量高峰期")
            tips.append("避免在深夜23点后发布")
        elif platform == "tiktok":
            tips.append("午休12-13点和晚间18-21点是黄金时段")
            tips.append("短视频完播率很重要，控制时长")
        elif platform == "official":
            tips.append("工作日上午8-10点发布最适合")
            tips.append("文章类内容建议在午前发布")
        elif platform == "friend_circle":
            tips.append("晚间17-20点互动率最高")
            tips.append("周末全天都有较高活跃度")

        # 行业特定建议
        if industry in ["时尚", "美妆", "美食", "旅行"]:
            tips.append(f"{industry}内容在周末发布效果更好")
        elif industry in ["数码", "教育", "家居"]:
            tips.append(f"{industry}内容在工作日发布效果更好")

        return tips

    def get_weekly_summary(
        self,
        platform: str = "xiaohongshu",
        industry: str = "通用",
    ) -> Dict[str, Any]:
        """
        获取每周时段汇总

        Args:
            platform: 目标平台
            industry: 所属行业

        Returns:
            Dict: 每周每日最佳时段的汇总
        """
        weekly_data = {}

        for day_offset in range(7):
            day_of_week = day_offset  # 0=周一
            day_name = self._get_day_name(day_of_week)

            # 计算该天各时段分数
            hourly_scores = []
            for hour in range(6, 23):
                score = self._calculate_score(platform, industry, day_of_week, hour)
                hourly_scores.append((hour, score))

            # 找出最佳时段
            hourly_scores.sort(key=lambda x: x[1], reverse=True)
            best_hour = hourly_scores[0][0] if hourly_scores else 12

            weekly_data[day_name] = {
                "best_hour": f"{best_hour:02d}:00",
                "best_hour_name": self._get_time_slot_name(best_hour),
                "score": hourly_scores[0][1],
                "is_weekend": day_offset in [0, 6],
            }

        return weekly_data


# 全局实例
posting_time_service = PostingTimeService()


if __name__ == "__main__":
    service = PostingTimeService()

    # 测试建议
    result = service.get_suggestions("xiaohongshu", "美妆", 7)

    print(f"平台: {result.platform}")
    print(f"行业: {result.industry}")
    print(f"\n最佳时段 Top 5:")
    for slot in result.best_times[:5]:
        print(f"  {slot.day_of_week} {slot.time} - 分数:{slot.score} ({slot.exposure}曝光)")

    print(f"\n建议:")
    for tip in result.tips:
        print(f"  - {tip}")

    print(f"\n每周汇总:")
    weekly = service.get_weekly_summary("xiaohongshu", "美妆")
    for day, info in weekly.items():
        print(f"  {day}: {info['best_hour']} ({info['best_hour_name']})")