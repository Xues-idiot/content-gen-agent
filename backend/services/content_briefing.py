"""
Vox Content Briefing Service 模块

内容简报服务
- 基于产品或主题生成内容简报
- 提取关键卖点和目标受众
- 推荐内容角度和平台策略
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class ContentBriefing:
    """内容简报"""
    title: str  # 简报标题
    summary: str  # 简要概述
    target_audience: List[str]  # 目标受众
    key_messages: List[str]  # 核心信息点
    recommended_angles: List[str]  # 推荐内容角度
    platform_recommendations: Dict[str, str]  # 平台推荐及理由
    content_formats: List[str]  # 推荐内容格式
    hashtags_suggestions: List[str]  # 推荐话题标签
    posting_time_suggestions: str  # 发布时间建议
    competitors_analysis: str  # 竞品分析提示
    call_to_action: str  # 行动号召建议


class ContentBriefingService:
    """
    内容简报服务

    基于产品或主题生成完整的内容简报
    """

    def __init__(self):
        self.llm = llm_service

    async def generate_briefing(
        self,
        product_name: str = "",
        product_description: str = "",
        selling_points: List[str] = None,
        target_users: List[str] = None,
        category: str = "",
        competitors: str = "",
        goals: str = "",
    ) -> ContentBriefing:
        """
        生成内容简报

        Args:
            product_name: 产品名称
            product_description: 产品描述
            selling_points: 卖点列表
            target_users: 目标用户列表
            category: 产品类别
            competitors: 竞品信息
            goals: 内容目标

        Returns:
            ContentBriefing: 内容简报
        """
        try:
            selling_points = selling_points or []
            target_users = target_users or []

            prompt = f"""请为以下产品/主题生成一个完整的内容营销简报。

产品/主题名称：{product_name}
产品描述：{product_description}
产品类别：{category or "通用"}

卖点：
{chr(10).join([f"- {sp}" for sp in selling_points]) if selling_points else "- 无"}

目标用户：
{chr(10).join([f"- {u}" for u in target_users]) if target_users else "- 普通消费者"}

竞品信息：{competitors or "无"}
内容目标：{goals or "提升品牌知名度和产品销量"}

请生成包含以下方面的内容简报：

1. **简报标题** - 一个吸引人的标题
2. **简要概述** - 2-3句话概括这个内容营销计划
3. **目标受众** - 具体的目标人群描述（3-5个）
4. **核心信息点** - 需要传达的关键信息（3-5个）
5. **推荐内容角度** - 不同角度的内容创意（4-6个）
6. **平台推荐** - 推荐在哪些平台发布及理由
7. **内容格式** - 推荐的发布形式（图文、短视频、直播等）
8. **话题标签** - 推荐的Hashtag（8-10个）
9. **发布时间建议** - 最佳发布时间段
10. **竞品分析提示** - 分析竞品内容的建议
11. **行动号召** - 推荐的CTA（点赞、评论、关注等）

请以JSON格式返回：
{{
    "title": "简报标题",
    "summary": "简要概述",
    "target_audience": ["受众1", "受众2", "受众3"],
    "key_messages": ["信息点1", "信息点2", "信息点3"],
    "recommended_angles": ["角度1", "角度2", "角度3", "角度4"],
    "platform_recommendations": {{
        "平台名": "推荐理由"
    }},
    "content_formats": ["格式1", "格式2", "格式3"],
    "hashtags_suggestions": ["#标签1", "#标签2", "#标签3"],
    "posting_time_suggestions": "发布时间建议",
    "competitors_analysis": "竞品分析提示",
    "call_to_action": "行动号召建议"
}}

只返回JSON，不要其他内容："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                if match:
                    result = json.loads(match.group())
                else:
                    result = self._get_default_briefing(product_name)

            return ContentBriefing(
                title=result.get("title", f"{product_name} 内容营销简报"),
                summary=result.get("summary", ""),
                target_audience=result.get("target_audience", []),
                key_messages=result.get("key_messages", []),
                recommended_angles=result.get("recommended_angles", []),
                platform_recommendations=result.get("platform_recommendations", {}),
                content_formats=result.get("content_formats", []),
                hashtags_suggestions=result.get("hashtags_suggestions", []),
                posting_time_suggestions=result.get("posting_time_suggestions", ""),
                competitors_analysis=result.get("competitors_analysis", ""),
                call_to_action=result.get("call_to_action", ""),
            )

        except Exception as e:
            logger.error(f"生成内容简报失败: {e}")
            return self._get_default_briefing(product_name)

    def _get_default_briefing(self, product_name: str) -> Dict[str, Any]:
        """获取默认简报（当LLM不可用时）"""
        return {
            "title": f"{product_name} 内容营销简报",
            "summary": "基于提供的信息生成的内容营销计划",
            "target_audience": ["普通消费者"],
            "key_messages": ["产品核心价值"],
            "recommended_angles": ["产品测评", "使用体验", "对比推荐"],
            "platform_recommendations": {
                "小红书": "种草安利",
                "抖音": "短视频展示"
            },
            "content_formats": ["图文笔记", "短视频"],
            "hashtags_suggestions": [f"#{product_name}", "#好物推荐"],
            "posting_time_suggestions": "建议在工作日午休或晚间发布",
            "competitors_analysis": "分析竞品的优势和不足",
            "call_to_action": "欢迎评论区留言讨论"
        }

    async def generate_briefing_from_url(self, url: str) -> ContentBriefing:
        """
        从URL生成内容简报

        Args:
            url: 产品或主题的URL

        Returns:
            ContentBriefing: 内容简报
        """
        # 这里可以扩展为实际抓取网页内容
        # 目前只是一个占位符实现
        return await self.generate_briefing(
            product_name="URL内容",
            product_description=f"基于URL生成: {url}",
        )


# 全局实例
content_briefing_service = ContentBriefingService()


if __name__ == "__main__":
    import asyncio

    service = ContentBriefingService()

    async def test():
        briefing = await service.generate_briefing(
            product_name="智能手环Pro",
            product_description="一款功能强大的健康监测智能手环",
            selling_points=[
                "24小时心率监测",
                "睡眠质量分析",
                "7天超长续航",
                "防水设计",
            ],
            target_users=[
                "健身爱好者",
                "上班族",
                "中老年人",
            ],
            category="智能穿戴",
            goals="提升品牌知名度",
        )

        print(f"简报标题: {briefing.title}")
        print(f"概述: {briefing.summary}")
        print(f"\n目标受众:")
        for aud in briefing.target_audience:
            print(f"  - {aud}")
        print(f"\n核心信息点:")
        for msg in briefing.key_messages:
            print(f"  - {msg}")
        print(f"\n推荐内容角度:")
        for angle in briefing.recommended_angles:
            print(f"  - {angle}")
        print(f"\n平台推荐:")
        for platform, reason in briefing.platform_recommendations.items():
            print(f"  {platform}: {reason}")
        print(f"\n推荐话题:")
        print(f"  {', '.join(briefing.hashtags_suggestions)}")
        print(f"\n发布时间: {briefing.posting_time_suggestions}")
        print(f"\n行动号召: {briefing.call_to_action}")

    asyncio.run(test())
