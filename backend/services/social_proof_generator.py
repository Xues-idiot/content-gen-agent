"""
Vox Social Proof Generator Service 模块

社会证明生成服务
- 用户评价生成
- 数据统计生成
- 信任背书生成
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class SocialProofElement:
    """社会证明元素"""
    proof_type: str
    content: str
    source: str
    credibility: str  # high/medium/low


class SocialProofGeneratorService:
    """
    社会证明生成服务

    生成各种社会证明元素增强内容可信度
    """

    def __init__(self):
        self.llm = llm_service

    # 社会证明类型
    PROOF_TYPES = {
        "testimonial": {
            "name": "用户评价",
            "template": "{用户画像}：\"{评价内容}\"",
            "examples": [
                "干皮敏感肌用户：\"用了两周皮肤明显变好了\"",
                "上班族宝妈：\"方便又好用，推荐给姐妹们\"",
            ],
        },
        "stats": {
            "name": "数据统计",
            "template": "{数字}{单位}的{描述}",
            "examples": [
                "100万+用户的共同选择",
                "复购率超过85%",
                "累计销量突破500万瓶",
            ],
        },
        "endorsement": {
            "name": "权威背书",
            "template": "{权威来源}认证/推荐",
            "examples": [
                "皮肤科医生推荐",
                "荣获2024年度美妆大奖",
                "登上《时尚芭莎》推荐榜单",
            ],
        },
        "social_mention": {
            "name": "社交提及",
            "template": "{平台}{数字}人都在讨论",
            "examples": [
                "小红书 10万+ 笔记都在推",
                "抖音 #话题# 播放量破亿",
            ],
        },
        "comparison": {
            "name": "对比证明",
            "template": "比{竞品}{优势}",
            "examples": [
                "比同类产品多含30%精华成分",
                "使用感比肩千元大牌",
            ],
        },
    }

    async def generate_testimonials(
        self,
        product_info: Dict[str, Any],
        num: int = 5,
        platform: str = "xiaohongshu",
    ) -> List[SocialProofElement]:
        """
        生成用户评价

        Args:
            product_info: 产品信息
            num: 生成数量
            platform: 平台

        Returns:
            List[SocialProofElement]: 用户评价列表
        """
        try:
            prompt = f"""请为以下产品生成{num}条真实用户评价。

产品名称：{product_info.get('name', '未知')}
产品描述：{product_info.get('description', '未知')}
产品特点：{', '.join(product_info.get('selling_points', []))}
目标用户：{', '.join(product_info.get('target_users', []))}

要求：
1. 不同用户画像（年龄、职业、肤质等）
2. 多样化的使用场景
3. 真实的语言风格
4. 包含具体细节

请以JSON格式返回：
{{
    "testimonials": [
        {{
            "user_profile": "用户画像描述",
            "content": "评价内容",
            "source": "评价来源平台/渠道",
            "credibility": "高/中/低"
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

            testimonials = result.get("testimonials", [])
        except Exception as e:
            logger.error(f"生成用户评价失败: {e}")
            testimonials = []

        # 如果生成失败，返回默认评价
        if not testimonials:
            testimonials = [
                {
                    "user_profile": "普通用户",
                    "content": f"产品很好用，会继续回购",
                    "source": "小红书",
                    "credibility": "中",
                }
            ]

        return [
            SocialProofElement(
                proof_type="testimonial",
                content=t.get("content", ""),
                source=t.get("source", "用户评价"),
                credibility=t.get("credibility", "中"),
            )
            for t in testimonials[:num]
        ]

    async def generate_stats(
        self,
        product_info: Dict[str, Any],
        num: int = 5,
    ) -> List[SocialProofElement]:
        """
        生成数据统计

        Args:
            product_info: 产品信息
            num: 生成数量

        Returns:
            List[SocialProofElement]: 数据统计列表
        """
        try:
            prompt = f"""请为以下产品生成{num}条有说服力的数据统计。

产品名称：{product_info.get('name', '未知')}
产品描述：{product_info.get('description', '未知')}
产品特点：{', '.join(product_info.get('selling_points', []))}

要求：
1. 数据类型多样（销量、用户数、评分、复购率等）
2. 数据真实可信
3. 表达简洁有力
4. 避免过度夸大

请以JSON格式返回：
{{
    "stats": [
        {{
            "number": "数字+单位",
            "description": "数据描述",
            "source": "数据来源",
            "credibility": "高/中/低"
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

            stats_list = result.get("stats", [])
        except Exception as e:
            logger.error(f"生成数据统计失败: {e}")
            stats_list = []

        if not stats_list:
            stats_list = [
                {
                    "number": "10万+",
                    "description": "用户的共同选择",
                    "source": "官方数据",
                    "credibility": "高",
                }
            ]

        return [
            SocialProofElement(
                proof_type="stats",
                content=f"{s.get('number', '')} {s.get('description', '')}",
                source=s.get("source", "官方数据"),
                credibility=s.get("credibility", "高"),
            )
            for s in stats_list[:num]
        ]

    async def generate_endorsements(
        self,
        product_info: Dict[str, Any],
        num: int = 3,
    ) -> List[SocialProofElement]:
        """
        生成权威背书

        Args:
            product_info: 产品信息
            num: 生成数量

        Returns:
            List[SocialProofElement]: 权威背书列表
        """
        try:
            prompt = f"""请为以下产品生成{num}条权威背书。

产品名称：{product_info.get('name', '未知')}
产品类别：{product_info.get('category', '通用')}

可选背书类型：皮肤科医生推荐、明星推荐、达人推荐、机构认证、奖项认证、媒体推荐

要求：
1. 背书类型多样化
2. 描述真实可信
3. 符合行业规范

请以JSON格式返回：
{{
    "endorsements": [
        {{
            "type": "背书类型",
            "content": "背书内容",
            "source": "背书来源",
            "credibility": "高/中/低"
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

            endorsements = result.get("endorsements", [])
        except Exception as e:
            logger.error(f"生成权威背书失败: {e}")
            endorsements = []

        if not endorsements:
            endorsements = [
                {
                    "type": "专家推荐",
                    "content": "业内专家认可推荐",
                    "source": "行业专家",
                    "credibility": "高",
                }
            ]

        return [
            SocialProofElement(
                proof_type="endorsement",
                content=e.get("content", ""),
                source=e.get("source", ""),
                credibility=e.get("credibility", "高"),
            )
            for e in endorsements[:num]
        ]

    async def generate_social_mentions(
        self,
        product_info: Dict[str, Any],
        platform: str = "xiaohongshu",
    ) -> SocialProofElement:
        """
        生成社交提及

        Args:
            product_info: 产品信息
            platform: 平台

        Returns:
            SocialProofElement: 社交提及
        """
        platform_names = {
            "xiaohongshu": "小红书",
            "tiktok": "抖音",
            "weibo": "微博",
        }
        name = platform_names.get(platform, platform)

        try:
            prompt = f"""请为以下产品生成一条{name}平台的社交热度描述。

产品名称：{product_info.get('name', '未知')}
产品特点：{', '.join(product_info.get('selling_points', []))}

要求：
1. 体现平台热度
2. 数据有据可依
3. 语言符合平台风格

请以JSON格式返回：
{{
    "platform": "{platform}",
    "content": "热度描述内容",
    "credibility": "高/中/低"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            content = result.get("content", f"{name}热门推荐")
        except Exception as e:
            logger.error(f"生成社交提及失败: {e}")
            content = f"{name}热门推荐"

        return SocialProofElement(
            proof_type="social_mention",
            content=content,
            source=name,
            credibility="中",
        )

    def get_proof_type_list(self) -> List[str]:
        """
        获取所有社会证明类型

        Returns:
            List[str]: 证明类型列表
        """
        return list(self.PROOF_TYPES.keys())


# 全局实例
social_proof_generator_service = SocialProofGeneratorService()


if __name__ == "__main__":
    import asyncio

    service = SocialProofGeneratorService()

    async def test():
        print("=== 社会证明类型 ===")
        types = service.get_proof_type_list()
        print(f"类型: {', '.join(types)}")

        product = {
            "name": "某品牌面霜",
            "description": "保湿修护面霜",
            "selling_points": ["保湿", "修护", "温和"],
            "target_users": ["干皮", "敏感肌"],
        }

        print("\n=== 生成用户评价 ===")
        testimonials = await service.generate_testimonials(product, 3)
        for t in testimonials:
            print(f"[{t.credibility}] {t.content}")

        print("\n=== 生成数据统计 ===")
        stats = await service.generate_stats(product, 3)
        for s in stats:
            print(f"[{s.credibility}] {s.content}")

        print("\n=== 生成权威背书 ===")
        endorsements = await service.generate_endorsements(product, 2)
        for e in endorsements:
            print(f"[{e.credibility}] {e.content}")

    asyncio.run(test())