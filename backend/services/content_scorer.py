"""
Vox Content Scorer Service 模块

内容质量评分服务
- 对生成的内容进行多维度评分
- 提供改进建议
- 帮助优化内容质量
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class ContentScore:
    """内容评分"""
    overall_score: int  # 0-100 总分
    engagement_score: int  # 吸引力评分
    compliance_score: int  # 合规性评分
    readability_score: int  # 可读性评分
    seo_score: int  # SEO评分
    platform_fit_score: int  # 平台适配评分
    scores: Dict[str, int]  # 各维度分数
    strengths: List[str]  # 优点
    weaknesses: List[str]  # 缺点
    suggestions: List[str]  # 改进建议


class ContentScorerService:
    """
    内容质量评分服务

    对文案进行多维度分析并评分
    """

    # 各维度权重
    DIMENSION_WEIGHTS = {
        "engagement": 0.25,      # 吸引力
        "compliance": 0.25,       # 合规性
        "readability": 0.20,      # 可读性
        "seo": 0.15,              # SEO
        "platform_fit": 0.15,     # 平台适配
    }

    def __init__(self):
        self.llm = llm_service

    def _calculate_overall_score(self, scores: Dict[str, int]) -> int:
        """计算加权总分"""
        total = 0.0
        for dimension, weight in self.DIMENSION_WEIGHTS.items():
            total += scores.get(dimension, 0) * weight
        return int(total)

    async def score_content(
        self,
        content: str,
        platform: str = "xiaohongshu",
        title: str = "",
        tags: Optional[List[str]] = None,
    ) -> ContentScore:
        """
        对内容进行评分

        Args:
            content: 文案内容
            platform: 目标平台
            title: 标题（可选）
            tags: 标签列表（可选）

        Returns:
            ContentScore: 评分结果
        """
        try:
            tags_str = ", ".join(tags) if tags else "无"

            prompt = f"""请对以下内容进行多维度评分分析。

目标平台：{platform}
标题：{title or "无"}
内容：
{content}
标签：{tags_str}

请从以下5个维度进行评分（每个维度0-100分）：
1. engagement（吸引力）- 开头是否吸引人，是否有悬念/痛点
2. compliance（合规性）- 是否有违规词、过度承诺、虚假宣传
3. readability（可读性）- 段落结构、表情使用、字数是否适中
4. seo（SEO友好度）- 关键词分布、标签使用
5. platform_fit（平台适配）- 是否符合{platform}平台风格

同时请识别：
- 优点（strengths）：内容中做得好的地方
- 缺点（weaknesses）：需要改进的地方
- 改进建议（suggestions）：具体的改进方向

请返回JSON格式：
{{
  "scores": {{
    "engagement": 评分数字,
    "compliance": 评分数字,
    "readability": 评分数字,
    "seo": 评分数字,
    "platform_fit": 评分数字
  }},
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["缺点1", "缺点2"],
  "suggestions": ["建议1", "建议2"]
}}"""

            response = self.llm.generate(prompt)

            if response.startswith("Error:"):
                logger.error(f"LLM 评分失败: {response}")
                return self._get_default_score()

            # 解析响应
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                if match:
                    try:
                        result = json.loads(match.group())
                    except json.JSONDecodeError:
                        logger.warning(f"无法解析评分 JSON: {response[:100]}")
                        return self._get_default_score()
                else:
                    return self._get_default_score()

            scores = result.get("scores", {})
            overall = self._calculate_overall_score(scores)

            return ContentScore(
                overall_score=overall,
                engagement_score=scores.get("engagement", 0),
                compliance_score=scores.get("compliance", 0),
                readability_score=scores.get("readability", 0),
                seo_score=scores.get("seo", 0),
                platform_fit_score=scores.get("platform_fit", 0),
                scores=scores,
                strengths=result.get("strengths", []),
                weaknesses=result.get("weaknesses", []),
                suggestions=result.get("suggestions", []),
            )

        except Exception as e:
            logger.error(f"内容评分失败: {e}")
            return self._get_default_score()

    def _get_default_score(self) -> ContentScore:
        """获取默认评分（当LLM不可用时）"""
        return ContentScore(
            overall_score=50,
            engagement_score=50,
            compliance_score=50,
            readability_score=50,
            seo_score=50,
            platform_fit_score=50,
            scores={
                "engagement": 50,
                "compliance": 50,
                "readability": 50,
                "seo": 50,
                "platform_fit": 50,
            },
            strengths=["内容结构完整"],
            weaknesses=["无法进行深度分析"],
            suggestions=["请确保后端 LLM 服务正常运行"],
        )

    def get_score_level(self, score: int) -> str:
        """获取评分等级"""
        if score >= 85:
            return "优秀"
        elif score >= 70:
            return "良好"
        elif score >= 50:
            return "一般"
        else:
            return "较差"

    def compare_contents(
        self,
        contents: List[Dict[str, str]],
        platform: str = "xiaohongshu",
    ) -> List[ContentScore]:
        """
        对比多个内容的质量

        Args:
            contents: 内容列表，每项包含 title 和 content
            platform: 目标平台

        Returns:
            List[ContentScore]: 评分列表（按总分排序）
        """
        results = []
        for item in contents:
            score = self.score_content(
                content=item.get("content", ""),
                platform=platform,
                title=item.get("title", ""),
            )
            results.append(score)

        # 按总分排序
        results.sort(key=lambda x: x.overall_score, reverse=True)
        return results


# 全局实例
content_scorer_service = ContentScorerService()


if __name__ == "__main__":
    import asyncio

    service = ContentScorerService()

    async def test():
        content = """
        今天分享一款超级好用的面霜！

        质地清爽不油腻，保湿效果一级棒
        用了一个月，皮肤明显变好了

        必须推荐给你们！#美妆 #护肤
        """

        result = await service.score_content(content, "xiaohongshu", "这款面霜太好用了")

        print(f"总分: {result.overall_score} ({service.get_score_level(result.overall_score)})")
        print(f"吸引力: {result.engagement_score}")
        print(f"合规性: {result.compliance_score}")
        print(f"可读性: {result.readability_score}")
        print(f"SEO: {result.seo_score}")
        print(f"平台适配: {result.platform_fit_score}")
        print(f"\n优点: {', '.join(result.strengths)}")
        print(f"缺点: {', '.join(result.weaknesses)}")
        print(f"建议: {', '.join(result.suggestions)}")

    asyncio.run(test())