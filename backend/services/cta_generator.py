"""
Vox CTA Generator Service 模块

行动号召(Call-to-Action)生成服务
- CTA文案生成
- CTA位置建议
- CTA效果优化
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class CTAGenerator:
    """CTA生成器"""
    cta_text: str
    cta_type: str  # immediate/conversation/-information
    placement: str  # start/middle/end
    style: str  # direct/gentle/question


class CTAGeneratorService:
    """
    CTA生成服务

    生成各种类型的行动号召
    """

    def __init__(self):
        self.llm = llm_service

    # CTA模板库
    CTA_TEMPLATES = {
        "immediate": {
            "name": "立即行动型",
            "examples": [
                "点击链接立即购买",
                "扫码领取优惠券",
                "立刻下单享受折扣",
            ],
        },
        "conversation": {
            "name": "互动引导型",
            "examples": [
                "评论区告诉我你的想法",
                "有相同经历的举手",
                "你们还想看什么内容",
            ],
        },
        "information": {
            "name": "信息获取型",
            "examples": [
                "点击头像了解更多",
                "关注我获取更多攻略",
                "私信领取完整资料",
            ],
        },
        "share": {
            "name": "分享型",
            "examples": [
                "收藏起来慢慢看",
                "转发给需要的朋友",
                "分享到朋友圈",
            ],
        },
    }

    # 平台CTA偏好
    PLATFORM_CTA_PREFERENCES = {
        "xiaohongshu": {
            "preferred_types": ["conversation", "share", "information"],
            "style": "亲切、自然、不生硬",
            "avoid": "过于商业化、强硬推销",
        },
        "tiktok": {
            "preferred_types": ["immediate", "share", "conversation"],
            "style": "简短有力、节奏快、有感染力",
            "avoid": "太长、太正式",
        },
        "weibo": {
            "preferred_types": ["conversation", "share", "information"],
            "style": "观点鲜明、有态度",
            "avoid": "平淡无奇",
        },
        "official": {
            "preferred_types": ["information", "immediate"],
            "style": "专业、简洁、有价值",
            "avoid": "过于热情、夸张",
        },
    }

    async def generate_cta(
        self,
        content_type: str,
        platform: str = "xiaohongshu",
        num: int = 3,
    ) -> List[CTAGenerator]:
        """
        生成CTA

        Args:
            content_type: 内容类型
            platform: 平台
            num: 生成数量

        Returns:
            List[CTAGenerator]: CTA列表
        """
        try:
            prompt = f"""请为{platform}平台的{content_type}类型内容生成{num}个CTA（行动号召）。

平台：{platform}
内容类型：{content_type}

要求：
1. CTA类型多样（立即行动/互动引导/信息获取/分享型）
2. 符合平台风格
3. 简短有力
4. 有感染力

请以JSON格式返回：
{{
    "ctas": [
        {{
            "cta_text": "CTA文案",
            "cta_type": "immediate/conversation/information/share",
            "placement": "start/middle/end",
            "style": "direct/gentle/question"
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

            ctas = result.get("ctas", [])
        except Exception as e:
            logger.error(f"生成CTA失败: {e}")
            ctas = []

        if not ctas:
            ctas = [
                {
                    "cta_text": "评论区告诉我你的想法",
                    "cta_type": "conversation",
                    "placement": "end",
                    "style": "question",
                }
            ]

        return [
            CTAGenerator(
                cta_text=c.get("cta_text", ""),
                cta_type=c.get("cta_type", "conversation"),
                placement=c.get("placement", "end"),
                style=c.get("style", "gentle"),
            )
            for c in ctas[:num]
        ]

    async def get_platform_cta_guide(
        self,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        获取平台CTA指南

        Args:
            platform: 平台

        Returns:
            Dict: 平台CTA指南
        """
        pref = self.PLATFORM_CTA_PREFERENCES.get(
            platform, self.PLATFORM_CTA_PREFERENCES["xiaohongshu"]
        )

        return {
            "platform": platform,
            "preferred_types": pref["preferred_types"],
            "style": pref["style"],
            "avoid": pref["avoid"],
            "examples": [
                t["examples"][0] for t in self.CTA_TEMPLATES.values()
                if t["name"].lower().replace("型", "") in pref["preferred_types"]
            ][:3],
        }

    async def optimize_cta(
        self,
        original_cta: str,
        platform: str = "xiaohongshu",
        target_type: str = "immediate",
    ) -> Dict[str, Any]:
        """
        优化CTA

        Args:
            original_cta: 原始CTA
            platform: 平台
            target_type: 目标类型

        Returns:
            Dict: 优化后的CTA和建议
        """
        try:
            prompt = f"""请优化以下CTA，使其更有效。

原始CTA：{original_cta}
目标平台：{platform}
目标类型：{target_type}

请提供：
1. 优化后的CTA
2. 优化理由
3. 备选方案

请以JSON格式返回：
{{
    "optimized_cta": "优化后的CTA",
    "reason": "优化理由",
    "alternatives": ["备选1", "备选2"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "original_cta": original_cta,
                "platform": platform,
                "target_type": target_type,
                "optimized_cta": result.get("optimized_cta", original_cta),
                "reason": result.get("reason", ""),
                "alternatives": result.get("alternatives", []),
            }

        except Exception as e:
            logger.error(f"优化CTA失败: {e}")
            return {
                "original_cta": original_cta,
                "platform": platform,
                "target_type": target_type,
                "optimized_cta": original_cta,
                "reason": "优化失败",
                "alternatives": [],
            }

    def get_cta_types(self) -> List[str]:
        """
        获取所有CTA类型

        Returns:
            List[str]: CTA类型列表
        """
        return list(self.CTA_TEMPLATES.keys())


# 全局实例
cta_generator_service = CTAGeneratorService()


if __name__ == "__main__":
    import asyncio

    service = CTAGeneratorService()

    async def test():
        print("=== CTA类型 ===")
        types = service.get_cta_types()
        print(f"类型: {', '.join(types)}")

        print("\n=== 生成CTA ===")
        ctas = await service.generate_cta("种草推荐", "xiaohongshu", 3)
        for c in ctas:
            print(f"[{c.cta_type}] {c.cta_text} ({c.placement})")

        print("\n=== 平台CTA指南 ===")
        guide = await service.get_platform_cta_guide("xiaohongshu")
        print(f"平台: {guide['platform']}")
        print(f"偏好: {', '.join(guide['preferred_types'])}")
        print(f"风格: {guide['style']}")

        print("\n=== CTA优化 ===")
        opt = await service.optimize_cta("买它买它", "xiaohongshu", "conversation")
        print(f"原文: {opt['original_cta']}")
        print(f"优化: {opt['optimized_cta']}")
        print(f"理由: {opt['reason']}")

    asyncio.run(test())