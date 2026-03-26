"""
Vox Title A/B Test Service 模块

标题 A/B 测试生成服务
- 为同一内容生成多个不同风格的标题
- 提供点击率和转化率预估
- 帮助选择最佳标题
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class TitleVariation:
    """标题变体"""
    title: str
    style: str  # 悬念型/数字型/情感型/问题型/命令型
    emoji_used: bool
    length: int
    ctr_score: int  # 预估点击率 0-100
    engagement_score: int  # 预估互动率 0-100
    strengths: List[str]  # 优势
    weaknesses: List[str]  # 劣势


class TitleABTestService:
    """
    标题 A/B 测试服务

    支持生成多种风格标题并进行对比分析
    """

    TITLE_STYLES = {
        "悬念型": {
            "description": "引发好奇心，促使用户点击",
            "emoji_preference": "可用",
            "length_preference": "15-25字",
            "examples": ["没想到...最后竟然...", "这个秘密90%的人都不知道"],
        },
        "数字型": {
            "description": "具体数字增加可信度",
            "emoji_preference": "少用",
            "length_preference": "15-20字",
            "examples": ["5个技巧让你...", "3分钟搞定..."],
        },
        "情感型": {
            "description": "触动情感，引发共鸣",
            "emoji_preference": "推荐",
            "length_preference": "15-25字",
            "examples": ["太感动了...", "真心推荐..."],
        },
        "问题型": {
            "description": "提出问题，引发思考",
            "emoji_preference": "可用",
            "length_preference": "15-20字",
            "examples": ["还在为...烦恼吗？", "你知道...吗？"],
        },
        "命令型": {
            "description": "直接号召行动",
            "emoji_preference": "少用",
            "length_preference": "10-15字",
            "examples": ["赶紧收藏！", "一定要看..."],
        },
        "对比型": {
            "description": "通过对比突出亮点",
            "emoji_preference": "可用",
            "length_preference": "15-25字",
            "examples": ["从...到...只用了...", "...vs..."],
        },
        "蹭热点型": {
            "description": "结合当前热点话题",
            "emoji_preference": "推荐",
            "length_preference": "15-25字",
            "examples": ["继...之后，这款...", "和...一样火..."],
        },
    }

    def __init__(self):
        self.llm = llm_service

    def _estimate_ctr(self, title: str, style: str, platform: str) -> int:
        """估算点击率"""
        base_score = 50

        # 风格加成
        style_bonus = {
            "悬念型": 15,
            "数字型": 12,
            "情感型": 10,
            "问题型": 8,
            "命令型": 5,
            "对比型": 12,
            "蹭热点型": 18,
        }
        base_score += style_bonus.get(style, 0)

        # Emoji 加成（适度使用）
        emoji_count = len([c for c in title if c in "😀😍🎉🔥💄✨📷🏷️🏖️💡"])
        if 1 <= emoji_count <= 3:
            base_score += 5

        # 长度惩罚
        if len(title) > 30:
            base_score -= 10
        elif len(title) < 10:
            base_score -= 5

        # 平台特性
        if platform == "xiaohongshu":
            if any(kw in title for kw in ["必看", "收藏", "干货", "分享"]):
                base_score += 10
        elif platform == "tiktok":
            if any(kw in title for kw in ["绝了", "太牛了", "笑死"]):
                base_score += 8

        return max(20, min(95, base_score))

    def _estimate_engagement(self, title: str, style: str) -> int:
        """估算互动率"""
        base_score = 50

        # 情感型更容易引发互动
        if style in ["情感型", "问题型"]:
            base_score += 15
        elif style in ["命令型", "数字型"]:
            base_score += 8

        # 问号和感叹号增加互动
        if "？" in title or "?" in title:
            base_score += 8
        if "！" in title or "!" in title:
            base_score += 5

        # 过短或过长降低互动
        if len(title) > 28:
            base_score -= 10
        elif len(title) < 12:
            base_score -= 5

        return max(15, min(90, base_score))

    def _analyze_strengths_weaknesses(self, title: str, style: str) -> tuple:
        """分析标题优劣势"""
        strengths = []
        weaknesses = []

        # 长度分析
        if 15 <= len(title) <= 25:
            strengths.append("长度适中")
        elif len(title) < 15:
            weaknesses.append("可能信息量不足")
        else:
            weaknesses.append("可能过于冗长")

        # 风格特点
        if style == "悬念型":
            if any(kw in title for kw in ["没想到", "竟然", "秘密", "不知道"]):
                strengths.append("悬念感强")
            else:
                weaknesses.append("悬念感不够强烈")
        elif style == "数字型":
            if any(c.isdigit() for c in title):
                strengths.append("数字增强可信度")
            else:
                weaknesses.append("缺少具体数字")
        elif style == "情感型":
            if any(kw in title for kw in ["太", "真的", "超", "巨"]):
                strengths.append("情感表达充沛")
            else:
                weaknesses.append("情感表达可加强")

        return strengths, weaknesses

    async def generate_variations(
        self,
        content: str,
        platform: str = "xiaohongshu",
        amount: int = 6,
        product_info: Optional[Dict[str, Any]] = None,
    ) -> List[TitleVariation]:
        """
        为内容生成多个标题变体

        Args:
            content: 原始内容
            platform: 目标平台
            amount: 生成数量
            product_info: 产品信息（可选）

        Returns:
            List[TitleVariation]: 标题变体列表
        """
        try:
            product_context = ""
            if product_info:
                product_context = f"""
产品信息：
- 名称：{product_info.get('name', '')}
- 描述：{product_info.get('description', '')}
- 卖点：{', '.join(product_info.get('selling_points', []))}
"""

            # 选择多种风格
            all_styles = list(self.TITLE_STYLES.keys())
            selected_styles = all_styles[:amount]

            prompt = f"""请为以下内容生成 {amount} 个不同风格的标题变体。

内容：
{content}
{product_context}

目标平台：{platform}

请为以下每种风格生成一个标题：
{', '.join(selected_styles)}

要求：
1. 每个标题要符合对应风格的特点
2. 标题要吸引人，有传播性
3. 长度控制在10-25字之间
4. 适当使用 emoji 但不要过多
5. 只返回JSON数组格式，不要其他内容

输出格式：
[
  {{"style": "悬念型", "title": "标题内容"}},
  {{"style": "数字型", "title": "标题内容"}}
]"""

            response = self.llm.generate(prompt)

            if response.startswith("Error:"):
                logger.error(f"LLM 标题生成失败: {response}")
                return self._get_fallback_variations(content, amount)

            # 解析响应
            import json
            import re

            try:
                variations_data = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\[.*]', response, re.DOTALL)
                if match:
                    try:
                        variations_data = json.loads(match.group())
                    except json.JSONDecodeError:
                        logger.warning(f"无法解析标题 JSON: {response[:100]}")
                        return self._get_fallback_variations(content, amount)
                else:
                    return self._get_fallback_variations(content, amount)

            # 构建 TitleVariation 对象
            results: List[TitleVariation] = []
            for item in variations_data[:amount]:
                if isinstance(item, dict) and "title" in item:
                    title = item["title"]
                    style = item.get("style", "通用型")
                    emoji_used = "emoji" in title.lower() or any(c in title for c in "😀😍🎉🔥💄✨📷🏷️🏖️💡")

                    ctr_score = self._estimate_ctr(title, style, platform)
                    engagement_score = self._estimate_engagement(title, style)
                    strengths, weaknesses = self._analyze_strengths_weaknesses(title, style)

                    results.append(TitleVariation(
                        title=title,
                        style=style,
                        emoji_used=emoji_used,
                        length=len(title),
                        ctr_score=ctr_score,
                        engagement_score=engagement_score,
                        strengths=strengths,
                        weaknesses=weaknesses,
                    ))

            logger.info(f"生成 {len(results)} 个标题变体")
            return results

        except Exception as e:
            logger.error(f"标题变体生成失败: {e}")
            return self._get_fallback_variations(content, amount)

    def _get_fallback_variations(self, content: str, amount: int) -> List[TitleVariation]:
        """获取备用标题变体"""
        results: List[TitleVariation] = []

        # 提取内容前50字作为基础
        base = content[:50] if len(content) > 50 else content

        fallback_titles = [
            ("悬念型", f"没想到...{base[:15]}...最后竟然..."),
            ("数字型", f"5个技巧让你轻松搞定{base[:10]}"),
            ("情感型", f"太感动了！{base[:20]}"),
            ("问题型", f"还在为{base[:10]}烦恼吗？"),
            ("命令型", f"赶紧收藏！{base[:15]}"),
            ("对比型", f"从不会到精通，我只用了{base[:10]}"),
        ]

        for style, title in fallback_titles[:amount]:
            ctr_score = self._estimate_ctr(title, style, "xiaohongshu")
            engagement_score = self._estimate_engagement(title, style)
            strengths, weaknesses = self._analyze_strengths_weaknesses(title, style)

            results.append(TitleVariation(
                title=title,
                style=style,
                emoji_used=False,
                length=len(title),
                ctr_score=ctr_score,
                engagement_score=engagement_score,
                strengths=strengths,
                weaknesses=weaknesses,
            ))

        return results

    def compare_variations(
        self,
        variations: List[TitleVariation],
    ) -> Dict[str, Any]:
        """
        对比标题变体，给出最佳推荐

        Args:
            variations: 标题变体列表

        Returns:
            Dict: 对比分析结果
        """
        if not variations:
            return {}

        # 按综合得分排序
        scored_variations = []
        for v in variations:
            # 综合得分 = CTR * 0.6 + 互动率 * 0.4
            combined_score = v.ctr_score * 0.6 + v.engagement_score * 0.4
            scored_variations.append((v, combined_score))

        scored_variations.sort(key=lambda x: x[1], reverse=True)

        best = scored_variations[0][0]
        worst = scored_variations[-1][0]

        # 统计各风格平均分
        style_scores: Dict[str, float] = {}
        for v, score in scored_variations:
            if v.style not in style_scores:
                style_scores[v.style] = []
            style_scores[v.style].append(score)

        style_avg = {
            style: sum(scores) / len(scores)
            for style, scores in style_scores.items()
        }

        return {
            "best_title": best,
            "worst_title": worst,
            "style_rankings": sorted(style_avg.items(), key=lambda x: x[1], reverse=True),
            "recommendation": f"推荐「{best.title}」，综合得分最高（CTR:{best.ctr_score}, 互动:{best.engagement_score}）",
        }


# 全局实例
title_abtest_service = TitleABTestService()


if __name__ == "__main__":
    import asyncio

    service = TitleABTestService()

    async def test():
        content = "分享一款非常好用的面霜，质地清爽不油腻，保湿效果超级棒，用了一个月皮肤明显变好了"
        results = await service.generate_variations(content, "xiaohongshu", 6)

        print("生成的标题变体：")
        for v in results:
            print(f"\n[{v.style}] {v.title}")
            print(f"  点击率: {v.ctr_score} | 互动率: {v.engagement_score}")
            print(f"  优势: {', '.join(v.strengths)}")
            print(f"  劣势: {', '.join(v.weaknesses)}")

        # 对比分析
        comparison = service.compare_variations(results)
        print(f"\n推荐: {comparison['recommendation']}")

    asyncio.run(test())