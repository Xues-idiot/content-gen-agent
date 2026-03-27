"""
Vox Content Engagement Booster Service 模块

内容互动增强服务
- 分析内容互动问题
- 提供增强互动建议
- 生成互动引导文案
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class EngagementSuggestion:
    """互动增强建议"""
    action: str  # 具体操作
    description: str  # 描述
    expected_impact: str  # 预期效果
    difficulty: str  # 难度: easy/medium/hard
    priority: int  # 优先级 1-5


class EngagementBoosterService:
    """
    内容互动增强服务

    帮助提升内容互动率
    """

    def __init__(self):
        self.llm = llm_service

    async def analyze_and_suggest(
        self,
        content: str,
        current_metrics: Dict[str, int],
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        分析内容并提供互动增强建议

        Args:
            content: 内容文本
            current_metrics: 当前指标 {views, likes, comments, shares, saves}
            platform: 平台

        Returns:
            Dict: 分析和建议结果
        """
        try:
            views = current_metrics.get("views", 0)
            likes = current_metrics.get("likes", 0)
            comments = current_metrics.get("comments", 0)
            shares = current_metrics.get("shares", 0)
            saves = current_metrics.get("saves", 0)

            # 计算比率
            like_rate = likes / views * 100 if views > 0 else 0
            comment_rate = comments / views * 100 if views > 0 else 0
            share_rate = shares / views * 100 if views > 0 else 0
            save_rate = saves / views * 100 if views > 0 else 0

            prompt = f"""请分析以下内容的互动情况，并提供增强互动的建议。

平台：{platform}
内容：{content[:500]}

当前数据：
- 浏览量：{views:,}
- 点赞数：{likes:,} (点赞率: {like_rate:.2f}%)
- 评论数：{comments:,} (评论率: {comment_rate:.2f}%)
- 分享数：{shares:,} (分享率: {share_rate:.2f}%)
- 收藏数：{saves:,} (收藏率: {save_rate:.2f}%)

请分析：
1. 当前互动数据的问题（哪方面最低）
2. 可能的原因
3. 具体的增强建议（5-8个）

请以JSON格式返回：
{{
    "problem_analysis": "问题分析",
    "suggestions": [
        {{
            "action": "具体操作",
            "description": "描述",
            "expected_impact": "预期效果",
            "difficulty": "easy/medium/hard",
            "priority": 1-5
        }}
    ]
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
                    result = self._get_default_suggestions()

            return result

        except Exception as e:
            logger.error(f"分析互动增强失败: {e}")
            return self._get_default_suggestions()

    def _get_default_suggestions(self) -> Dict[str, Any]:
        """获取默认建议"""
        return {
            "problem_analysis": "需要更多数据才能准确分析，建议先增加曝光量",
            "suggestions": [
                {
                    "action": "优化发布时间",
                    "description": "在目标平台的高峰时段发布内容",
                    "expected_impact": "提高初始曝光",
                    "difficulty": "easy",
                    "priority": 1,
                },
                {
                    "action": "添加互动引导",
                    "description": "在内容结尾添加评论引导，如"你们觉得呢？"",
                    "expected_impact": "提高评论率",
                    "difficulty": "easy",
                    "priority": 2,
                },
                {
                    "action": "优化标题",
                    "description": "使用更有吸引力的标题",
                    "expected_impact": "提高点击率",
                    "difficulty": "medium",
                    "priority": 2,
                },
            ],
        }

    async def generate_interaction_cta(
        self,
        content: str,
        cta_type: str = "comment",
        platform: str = "xiaohongshu",
    ) -> str:
        """
        生成互动引导文案

        Args:
            content: 内容文本
            cta_type: 引导类型: comment/share/like/save
            platform: 平台

        Returns:
            str: 引导文案
        """
        try:
            cta_types = {
                "comment": "评论",
                "share": "分享",
                "like": "点赞",
                "save": "收藏",
            }

            prompt = f"""请为以下{platform}内容生成一个{cta_types.get(cta_type, '评论')}引导文案。

内容：{content[:300]}

要求：
1. 引导文案要自然，不要太生硬
2. 适合在{platform}平台
3. 字数控制在20字以内
4. 可以使用emoji增加亲和力

直接返回引导文案，不要其他内容："""

            result = self.llm.generate(prompt)
            return result.strip()

        except Exception as e:
            logger.error(f"生成互动引导失败: {e}")
            default_ctas = {
                "comment": "评论区告诉我你的想法！",
                "share": "觉得有用就转发给朋友吧！",
                "like": "喜欢的话点个赞吧！",
                "save": "收藏起来慢慢看！",
            }
            return default_ctas.get(cta_type, "欢迎留言讨论！")

    def get_engagement_tips(
        self,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        获取互动提升技巧

        Args:
            platform: 平台

        Returns:
            Dict: 技巧汇总
        """
        tips = {
            "xiaohongshu": {
                "like_rate_avg": "3-5%",
                "comment_rate_avg": "0.5-1%",
                "best_practices": [
                    "开头3行要抓眼球",
                    "使用吸引人的封面和标题",
                    "添加高质量图片",
                    "结尾引导互动",
                    "使用合适的标签",
                    "保持内容垂直",
                ],
                "common_mistakes": [
                    "标题党导致高跳出率",
                    "内容与标签不符",
                    "发布频率不稳定",
                    "忽视评论区运营",
                ],
                "engagement_boosters": [
                    "发起投票或问答",
                    "回复评论增加互动",
                    "使用热门话题标签",
                    "定期举办抽奖活动",
                ],
            },
            "tiktok": {
                "like_rate_avg": "5-10%",
                "comment_rate_avg": "0.3-0.5%",
                "best_practices": [
                    "开头3秒要抓住注意力",
                    "内容要短平快",
                    "使用热门音乐",
                    "添加字幕",
                    "保持画面稳定",
                ],
                "common_mistakes": [
                    "开头太慢导致流失",
                    "视频太长",
                    "音乐选择不当",
                    "缺乏视觉吸引力",
                ],
                "engagement_boosters": [
                    "使用热门挑战",
                    "回复热门评论",
                    "发布后持续互动",
                    "引导关注",
                ],
            },
        }

        return tips.get(platform, tips["xiaohongshu"])


# 全局实例
engagement_booster_service = EngagementBoosterService()


if __name__ == "__main__":
    import asyncio

    service = EngagementBoosterService()

    async def test():
        print("=== 互动增强分析 ===")
        content = "今天分享一款超级好用的面霜！质地清爽不油腻..."

        result = await service.analyze_and_suggest(
            content=content,
            current_metrics={"views": 1000, "likes": 30, "comments": 5, "shares": 2, "saves": 10},
            platform="xiaohongshu",
        )

        print(f"问题分析: {result.get('problem_analysis', '')}")
        print("\n建议:")
        for s in result.get("suggestions", []):
            print(f"  [{s['priority']}] {s['action']} - {s['description']} (预期: {s['expected_impact']})")

        print("\n=== 互动引导文案 ===")
        cta = await service.generate_interaction_cta(content, "comment")
        print(f"评论引导: {cta}")

        print("\n=== 平台技巧 ===")
        tips = service.get_engagement_tips("xiaohongshu")
        print(f"平均点赞率: {tips['like_rate_avg']}")
        print("最佳实践:", ", ".join(tips["best_practices"][:3]))

    asyncio.run(test())
