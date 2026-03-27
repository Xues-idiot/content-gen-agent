"""
Vox Smart Posting Scheduler 模块

智能发布调度服务
- 最优发布时间推荐
- 内容排程优化
- 发布提醒生成
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from loguru import logger


@dataclass
class ScheduledPost:
    """计划发布的帖子"""
    id: str
    platform: str
    title: str
    scheduled_time: datetime
    status: str  # pending/scheduled/published
    optimal_score: int  # 0-100 推荐分数


class PostingSchedulerService:
    """
    智能发布调度服务

    优化内容发布时间和排程
    """

    # 各平台最佳时段
    PLATFORM_PEAK_HOURS = {
        "xiaohongshu": {
            "weekday": [(7, 9), (12, 13), (18, 20), (21, 22)],
            "weekend": [(10, 12), (14, 16), (18, 20)],
        },
        "tiktok": {
            "weekday": [(7, 9), (12, 14), (18, 20), (21, 23)],
            "weekend": [(9, 12), (14, 17), (18, 21)],
        },
        "weibo": {
            "weekday": [(7, 8), (12, 13), (17, 19), (21, 22)],
            "weekend": [(9, 11), (17, 19)],
        },
        "official": {
            "weekday": [(8, 9), (12, 13), (20, 21)],
            "weekend": [(9, 10), (17, 18)],
        },
    }

    def __init__(self):
        pass

    def get_optimal_times(
        self,
        platform: str = "xiaohongshu",
        industry: str = "",
        num_slots: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        获取最优发布时间

        Args:
            platform: 平台
            industry: 行业
            num_slots: 返回数量

        Returns:
            List[Dict]: 最优时间槽
        """
        today = datetime.now()
        slots = []

        # 生成接下来7天的时间槽
        for day_offset in range(7):
            current_date = today + timedelta(days=day_offset)
            is_weekend = current_date.weekday() >= 5

            peak_hours = self.PLATFORM_PEAK_HOURS.get(platform, {})
            hours = peak_hours.get("weekend" if is_weekend else "weekday", [])

            day_name = current_date.strftime("%A")
            for start_hour, end_hour in hours:
                for hour in range(start_hour, end_hour + 1):
                    if len(slots) >= num_slots:
                        break

                    slot_time = current_date.replace(hour=hour, minute=0, second=0)
                    if slot_time <= datetime.now():
                        continue

                    # 计算推荐分数
                    score = self._calculate_time_score(
                        hour, is_weekend, platform, industry
                    )

                    slots.append({
                        "datetime": slot_time.isoformat(),
                        "date": slot_time.strftime("%Y-%m-%d"),
                        "time": f"{hour:02d}:00",
                        "day_of_week": day_name,
                        "is_weekend": is_weekend,
                        "score": score,
                        "exposure_level": "高" if score >= 80 else ("中" if score >= 60 else "低"),
                    })

        # 按分数排序
        slots.sort(key=lambda x: x["score"], reverse=True)
        return slots[:num_slots]

    def _calculate_time_score(
        self,
        hour: int,
        is_weekend: bool,
        platform: str,
        industry: str,
    ) -> int:
        """计算时间推荐分数"""
        base_score = 70

        # 高峰时段加分
        if is_weekend:
            if 10 <= hour <= 12:
                base_score += 15
            elif 14 <= hour <= 17:
                base_score += 12
            elif 18 <= hour <= 20:
                base_score += 10
        else:
            if 7 <= hour <= 9:
                base_score += 15
            elif 12 <= hour <= 13:
                base_score += 12
            elif 18 <= hour <= 20:
                base_score += 15
            elif 21 <= hour <= 22:
                base_score += 10

        # 非高峰时段减分
        if 2 <= hour <= 6:
            base_score -= 30

        return max(0, min(100, base_score))

    def schedule_content(
        self,
        posts: List[Dict[str, Any]],
    ) -> List[ScheduledPost]:
        """
        排程内容

        为多个内容安排最优发布时间

        Args:
            posts: 帖子列表 [{platform, title, priority}]

        Returns:
            List[ScheduledPost]: 安排好的帖子
        """
        scheduled = []
        used_slots = set()  # 避免时间冲突

        # 按优先级排序
        posts.sort(key=lambda x: x.get("priority", 5), reverse=True)

        for post in posts:
            platform = post.get("platform", "xiaohongshu")
            optimal_times = self.get_optimal_times(platform, num_slots=10)

            for slot in optimal_times:
                slot_key = f"{slot['date']} {slot['time']}"
                if slot_key not in used_slots:
                    scheduled.append(ScheduledPost(
                        id=f"post_{len(scheduled)}",
                        platform=platform,
                        title=post.get("title", "无标题"),
                        scheduled_time=datetime.fromisoformat(slot["datetime"]),
                        status="scheduled",
                        optimal_score=slot["score"],
                    ))
                    used_slots.add(slot_key)
                    break

        return scheduled

    def generate_posting_reminder(
        self,
        platform: str,
        scheduled_time: datetime,
        content_title: str,
    ) -> str:
        """
        生成发布提醒

        Args:
            platform: 平台
            scheduled_time: 计划时间
            content_title: 内容标题

        Returns:
            str: 提醒文本
        """
        time_str = scheduled_time.strftime("%m月%d日 %H:%M")
        platform_names = {
            "xiaohongshu": "小红书",
            "tiktok": "抖音",
            "weibo": "微博",
            "official": "公众号",
        }
        name = platform_names.get(platform, platform)

        return f"""📅 发布提醒

平台：{name}
时间：{time_str}
内容：{content_title}

请提前准备好：
✅ 最终内容检查
✅ 图片/视频素材
✅ Hashtag准备
✅ 互动引导文案

Good luck! 🚀"""

    def get_platform_schedule_summary(
        self,
        platform: str,
    ) -> Dict[str, Any]:
        """
        获取平台发布计划摘要

        Args:
            platform: 平台

        Returns:
            Dict: 发布计划摘要
        """
        optimal = self.get_optimal_times(platform, num_slots=7)

        return {
            "platform": platform,
            "recommended_slots": optimal,
            "best_day": optimal[0]["day_of_week"] if optimal else "未知",
            "best_time": optimal[0]["time"] if optimal else "未知",
            "weekly_distribution": self._get_weekly_distribution(optimal),
        }

    def _get_weekly_distribution(
        self,
        slots: List[Dict[str, Any]],
    ) -> Dict[str, int]:
        """获取每周分布"""
        distribution = {}
        for slot in slots:
            day = slot["day_of_week"]
            distribution[day] = distribution.get(day, 0) + 1
        return distribution


# 全局实例
posting_scheduler_service = PostingSchedulerService()


if __name__ == "__main__":
    service = PostingSchedulerService()

    print("=== 最优发布时间 ===")
    slots = service.get_optimal_times("xiaohongshu", num_slots=5)
    for slot in slots:
        print(f"{slot['date']} {slot['time']} ({slot['day_of_week']}) - 分数: {slot['score']} - 曝光: {slot['exposure_level']}")

    print("\n=== 内容排程 ===")
    posts = [
        {"platform": "xiaohongshu", "title": "面霜测评", "priority": 1},
        {"platform": "tiktok", "title": "开箱视频", "priority": 2},
        {"platform": "weibo", "title": "产品介绍", "priority": 3},
    ]
    scheduled = service.schedule_content(posts)
    for p in scheduled:
        print(f"{p.platform}: {p.title} @ {p.scheduled_time.strftime('%m-%d %H:%M')} (分数: {p.optimal_score})")

    print("\n=== 发布提醒 ===")
    reminder = service.generate_posting_reminder(
        "xiaohongshu",
        datetime.now() + timedelta(hours=2),
        "我的第一篇测评"
    )
    print(reminder)
