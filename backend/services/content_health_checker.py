"""
Vox Content Health Checker Service 模块

内容健康检查服务
- 内容完整性检查
- 内容质量评分
- 优化建议生成
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    is_healthy: bool
    health_score: int  # 0-100
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]


class ContentHealthCheckerService:
    """
    内容健康检查服务

    检查内容健康度并提供优化建议
    """

    def __init__(self):
        self.llm = llm_service

    # 健康检查维度
    CHECK_DIMENSIONS = {
        "completeness": {
            "name": "完整性",
            "weight": 20,
            "description": "内容是否完整（标题、正文、配图、CTA等）",
        },
        "quality": {
            "name": "质量",
            "weight": 25,
            "description": "内容质量（语言表达、逻辑结构、信息价值）",
        },
        "engagement": {
            "name": "互动性",
            "weight": 20,
            "description": "互动引导（CTA、问题、情感共鸣）",
        },
        "seo": {
            "name": "SEO",
            "weight": 15,
            "description": "搜索引擎优化（关键词、标签、hashtag）",
        },
        "compliance": {
            "name": "合规性",
            "weight": 20,
            "description": "内容合规（违规词、敏感词、版权）",
        },
    }

    async def check_content_health(
        self,
        content: str,
        title: str = "",
        platform: str = "xiaohongshu",
    ) -> HealthCheckResult:
        """
        检查内容健康度

        Args:
            content: 内容正文
            title: 内容标题
            platform: 平台

        Returns:
            HealthCheckResult: 健康检查结果
        """
        try:
            prompt = f"""请检查以下内容的健康度。

平台：{platform}
标题：{title}
正文：{content[:1000]}

请从以下维度检查：
1. 完整性（标题、正文、配图建议、CTA等）
2. 质量（语言表达、逻辑结构、信息价值）
3. 互动性（CTA、问题设置、情感共鸣）
4. SEO（关键词、hashtag、标签）
5. 合规性（违规词、敏感词）

请以JSON格式返回：
{{
    "is_healthy": true/false,
    "health_score": 0-100,
    "issues": ["问题1", "问题2"],
    "warnings": ["警告1"],
    "suggestions": ["建议1", "建议2"],
    "dimension_scores": {{
        "completeness": 0-100,
        "quality": 0-100,
        "engagement": 0-100,
        "seo": 0-100,
        "compliance": 0-100
    }}
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return HealthCheckResult(
                is_healthy=result.get("is_healthy", True),
                health_score=result.get("health_score", 70),
                issues=result.get("issues", []),
                warnings=result.get("warnings", []),
                suggestions=result.get("suggestions", []),
            )

        except Exception as e:
            logger.error(f"检查内容健康度失败: {e}")
            return HealthCheckResult(
                is_healthy=True,
                health_score=70,
                issues=[],
                warnings=["检查服务异常"],
                suggestions=["请人工检查内容"],
            )

    async def check_completeness(
        self,
        content: str,
        title: str = "",
    ) -> Dict[str, Any]:
        """
        检查内容完整性

        Args:
            content: 内容正文
            title: 标题

        Returns:
            Dict: 完整性检查结果
        """
        issues = []
        suggestions = []
        score = 100

        # 检查标题
        if not title:
            issues.append("缺少标题")
            suggestions.append("添加吸引人的标题")
            score -= 20
        elif len(title) < 5:
            issues.append("标题过短")
            suggestions.append("标题建议在10-30字之间")
            score -= 10
        elif len(title) > 50:
            issues.append("标题过长")
            suggestions.append("标题建议控制在30字以内")
            score -= 5

        # 检查正文长度
        content_length = len(content)
        if content_length < 50:
            issues.append("正文过短")
            suggestions.append("建议内容至少100字以上")
            score -= 30
        elif content_length < 100:
            issues.append("正文较短")
            suggestions.append("建议丰富内容，增加信息量")
            score -= 15
        elif content_length > 2000:
            issues.append("正文过长")
            suggestions.append("建议精简内容，避免阅读疲劳")
            score -= 10

        # 检查段落
        paragraphs = content.split("\n")
        if len(paragraphs) < 2 and content_length > 200:
            issues.append("缺少段落分隔")
            suggestions.append("建议分段，提升阅读体验")
            score -= 10

        # 检查emoji
        emoji_count = sum(1 for c in content if ord(c) > 127000)
        if emoji_count == 0:
            suggestions.append("建议添加适量emoji增加亲和力")
            score -= 5
        elif emoji_count > 15:
            issues.append("emoji使用过多")
            suggestions.append("建议控制emoji数量在10个以内")
            score -= 5

        # 检查hashtag
        hashtag_count = content.count("#")
        if hashtag_count == 0:
            suggestions.append("建议添加相关hashtag增加曝光")
            score -= 10
        elif hashtag_count > 10:
            issues.append("hashtag过多")
            suggestions.append("建议控制hashtag在5-10个以内")
            score -= 5

        return {
            "score": max(0, score),
            "issues": issues,
            "suggestions": suggestions,
            "checks": {
                "title": "✅" if title and 5 <= len(title) <= 50 else "❌",
                "content_length": "✅" if 100 <= content_length <= 2000 else "❌",
                "paragraphs": "✅" if len(paragraphs) >= 2 else "❌",
                "emoji": "✅" if 1 <= emoji_count <= 10 else "❌",
                "hashtag": "✅" if 1 <= hashtag_count <= 10 else "❌",
            },
        }

    async def get_health_report(
        self,
        content: str,
        title: str = "",
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        获取完整健康报告

        Args:
            content: 内容正文
            title: 标题
            platform: 平台

        Returns:
            Dict: 完整健康报告
        """
        health = await self.check_content_health(content, title, platform)
        completeness = await self.check_completeness(content, title)

        return {
            "is_healthy": health.is_healthy,
            "overall_score": health.health_score,
            "completeness_score": completeness["score"],
            "issues": health.issues + completeness["issues"],
            "warnings": health.warnings,
            "suggestions": health.suggestions + completeness["suggestions"],
            "completeness_checks": completeness["checks"],
            "platform": platform,
        }


# 全局实例
content_health_checker_service = ContentHealthCheckerService()


if __name__ == "__main__":
    import asyncio

    service = ContentHealthCheckerService()

    async def test():
        print("=== 健康检查 ===")
        result = await service.check_content_health(
            "这款面霜真的太好用了！用了两周皮肤明显变好...",
            "某品牌面霜测评推荐",
            "xiaohongshu"
        )
        print(f"健康: {result.is_healthy}")
        print(f"分数: {result.health_score}")
        print(f"问题: {', '.join(result.issues[:2])}")
        print(f"建议: {', '.join(result.suggestions[:2])}")

        print("\n=== 完整性检查 ===")
        complete = await service.check_completeness(
            "这款面霜太好用了！推荐给大家！",
            "面霜推荐"
        )
        print(f"分数: {complete['score']}")
        print(f"检查: {complete['checks']}")

    asyncio.run(test())