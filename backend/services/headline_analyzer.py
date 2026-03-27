"""
Vox Headline Analyzer Service 模块

标题分析服务
- 标题吸引力分析
- SEO优化建议
- 标题模板推荐
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class HeadlineAnalysis:
    """标题分析结果"""
    attractiveness_score: int  # 0-100
    readability_score: int  # 0-100
    seo_score: int  # 0-100
    emotional_appeal: str
    power_words: List[str]
    issues: List[str]
    suggestions: List[str]


class HeadlineAnalyzerService:
    """
    标题分析服务

    分析和优化内容标题
    """

    def __init__(self):
        self.llm = llm_service

    # 强力词汇
    POWER_WORDS = {
        "positive": ["必看", "绝了", "超赞", "爆款", "神器", "宝藏", "私藏", "干货", "推荐", "种草"],
        "negative": ["踩雷", "避坑", "骗局", "吐槽", "失望", "后悔", "翻车", "翻车"],
        "urgency": ["限时", "立即", "马上", "最后", "紧急", "错过", "赶紧", "速抢"],
        "curiosity": ["没想到", "竟然", "原来", "秘密", "真相", "内幕", "曝光", "揭秘"],
        "social_proof": ["10万+", "万人", "爆火", "刷屏", "热搜", "达人", "明星", "网红"],
    }

    # 平台标题偏好
    PLATFORM_TITLE_STYLES = {
        "xiaohongshu": {
            "length": "10-30字",
            "style": "种草/测评/分享风格",
            "elements": ["痛点", "效果", "情感"],
        },
        "tiktok": {
            "length": "5-20字",
            "style": "冲击/悬念/情绪化",
            "elements": ["悬念", "冲突", "数字"],
        },
        "weibo": {
            "length": "15-40字",
            "style": "观点鲜明/有态度",
            "elements": ["观点", "话题", "标签"],
        },
        "official": {
            "length": "10-30字",
            "style": "专业/简洁/有价值",
            "elements": ["价值", "专业", "数据"],
        },
    }

    async def analyze_headline(
        self,
        headline: str,
        platform: str = "xiaohongshu",
    ) -> HeadlineAnalysis:
        """
        分析标题

        Args:
            headline: 标题
            platform: 平台

        Returns:
            HeadlineAnalysis: 分析结果
        """
        try:
            prompt = f"""请分析以下标题的吸引力、质量和SEO效果。

平台：{platform}
标题：{headline}

请从以下维度分析：
1. 吸引力分数（0-100）- 是否能吸引用户点击
2. 可读性分数（0-100）- 是否容易阅读理解
3. SEO分数（0-100）- 是否包含关键词
4. 情感诉求（理性/感性/混合）
5. 强力词汇使用
6. 问题分析
7. 改进建议

请以JSON格式返回：
{{
    "attractiveness_score": 85,
    "readability_score": 80,
    "seo_score": 70,
    "emotional_appeal": "感性",
    "power_words": ["必看", "干货"],
    "issues": ["缺少数字"],
    "suggestions": ["建议添加具体数字"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return HeadlineAnalysis(
                attractiveness_score=result.get("attractiveness_score", 70),
                readability_score=result.get("readability_score", 70),
                seo_score=result.get("seo_score", 70),
                emotional_appeal=result.get("emotional_appeal", ""),
                power_words=result.get("power_words", []),
                issues=result.get("issues", []),
                suggestions=result.get("suggestions", []),
            )

        except Exception as e:
            logger.error(f"分析标题失败: {e}")
            return HeadlineAnalysis(
                attractiveness_score=70,
                readability_score=70,
                seo_score=70,
                emotional_appeal="",
                power_words=[],
                issues=[],
                suggestions=[],
            )

    async def optimize_headline(
        self,
        headline: str,
        platform: str = "xiaohongshu",
        target_score: int = 90,
    ) -> Dict[str, Any]:
        """
        优化标题

        Args:
            headline: 原始标题
            platform: 平台
            target_score: 目标分数

        Returns:
            Dict: 优化结果
        """
        try:
            prompt = f"""请优化以下标题，使其更具吸引力。

平台：{platform}
原始标题：{headline}
目标分数：{target_score}

请提供：
1. 优化后的标题（3个版本）
2. 每个版本的改进点
3. 适用的内容类型

请以JSON格式返回：
{{
    "optimized_headlines": [
        {{
            "headline": "优化后的标题",
            "improvement": "改进点",
            "content_type": "适用内容类型"
        }}
    ]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "original_headline": headline,
                "platform": platform,
                "target_score": target_score,
                "optimized_headlines": result.get("optimized_headlines", []),
            }

        except Exception as e:
            logger.error(f"优化标题失败: {e}")
            return {
                "original_headline": headline,
                "platform": platform,
                "target_score": target_score,
                "optimized_headlines": [],
            }

    def get_power_words(self) -> Dict[str, List[str]]:
        """
        获取强力词汇

        Returns:
            Dict: 强力词汇分类
        """
        return self.POWER_WORDS

    def analyze_headline_structure(self, headline: str) -> Dict[str, Any]:
        """
        分析标题结构

        Args:
            headline: 标题

        Returns:
            Dict: 结构分析
        """
        length = len(headline)
        has_number = bool(re.search(r'\d+', headline))
        has_question = "？" in headline or "？" in headline
        has_emoji = any(ord(c) > 127000 for c in headline)
        has_colon = ":" in headline or ":" in headline
        has_parentheses = "（" in headline or "(" in headline

        # 提取数字
        numbers = re.findall(r'\d+', headline)

        # 分析结构类型
        structure_type = "unknown"
        if " vs " in headline.lower() or "对比" in headline:
            structure_type = "comparison"
        elif has_question:
            structure_type = "question"
        elif re.search(r'^\[.*\]', headline) or re.search(r'^【.*】', headline):
            structure_type = "tagged"
        elif "教程" in headline or "指南" in headline:
            structure_type = "tutorial"
        elif "推荐" in headline or "测评" in headline:
            structure_type = "recommendation"

        return {
            "headline": headline,
            "length": length,
            "has_number": has_number,
            "has_question": has_question,
            "has_emoji": has_emoji,
            "has_colon": has_colon,
            "has_parentheses": has_parentheses,
            "numbers": numbers,
            "structure_type": structure_type,
            "is_optimal_length": 10 <= length <= 30,
        }


# 全局实例
headline_analyzer_service = HeadlineAnalyzerService()


if __name__ == "__main__":
    import asyncio

    service = HeadlineAnalyzerService()

    async def test():
        print("=== 标题分析 ===")
        result = await service.analyze_headline("这款面霜太绝了！用了皮肤超好", "xiaohongshu")
        print(f"吸引力: {result.attractiveness_score}")
        print(f"可读性: {result.readability_score}")
        print(f"SEO: {result.seo_score}")
        print(f"情感: {result.emotional_appeal}")

        print("\n=== 标题优化 ===")
        opt = await service.optimize_headline("面霜推荐", "xiaohongshu")
        for h in opt["optimized_headlines"][:2]:
            print(f"- {h['headline']}")

        print("\n=== 强力词汇 ===")
        words = service.get_power_words()
        print(f"正面词: {', '.join(words['positive'][:5])}")

    asyncio.run(test())