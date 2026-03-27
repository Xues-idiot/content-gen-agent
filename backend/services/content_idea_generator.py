"""
Vox Content Idea Generator Service 模块

内容创意生成服务
- 根据主题生成内容创意
- 趋势结合创意
- 多角度创意发散
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ContentIdeaGeneratorService:
    """
    内容创意生成服务

    生成各种类型的内容创意
    """

    def __init__(self):
        self.llm = llm_service

    # 内容角度类型
    IDEA_ANGLE_TYPES = [
        "产品测评",
        "教程分享",
        "好物推荐",
        "日常分享",
        "对比测评",
        "经验分享",
        "问题解决",
        "热点结合",
        "故事叙述",
        "清单列表",
    ]

    async def generate_ideas(
        self,
        topic: str,
        platform: str = "xiaohongshu",
        num: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        生成内容创意

        Args:
            topic: 主题
            platform: 平台
            num: 数量

        Returns:
            List[Dict]: 内容创意列表
        """
        try:
            prompt = f"""请为"{topic}"主题生成{num}个内容创意。

平台：{platform}

请为每个创意提供：
1. 创意标题
2. 内容角度
3. 核心要点
4. 适合的受众

请以JSON格式返回：
{{
    "ideas": [
        {{
            "title": "创意标题",
            "angle": "内容角度",
            "key_points": ["要点1", "要点2"],
            "target_audience": "目标受众"
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

            return result.get("ideas", [])

        except Exception as e:
            logger.error(f"生成内容创意失败: {e}")
            return []

    async def generate_from_trend(
        self,
        trend_topic: str,
        product_info: Dict[str, Any],
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        结合趋势生成内容

        Args:
            trend_topic: 趋势话题
            product_info: 产品信息
            platform: 平台

        Returns:
            Dict: 创意内容
        """
        try:
            prompt = f"""请将趋势话题与产品结合生成内容创意。

趋势话题：{trend_topic}
产品名称：{product_info.get('name', '')}
产品特点：{', '.join(product_info.get('selling_points', []))}
平台：{platform}

请提供：
1. 创意标题
2. 内容框架
3. 结合点
4. 发布时机建议

请以JSON格式返回：
{{
    "title": "创意标题",
    "framework": "内容框架",
    "connection_points": ["结合点1", "结合点2"],
    "posting_time": "发布时机建议"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "trend_topic": trend_topic,
                "product_name": product_info.get("name", ""),
                **result,
            }

        except Exception as e:
            logger.error(f"结合趋势生成内容失败: {e}")
            return {
                "trend_topic": trend_topic,
                "product_name": product_info.get("name", ""),
                "title": "",
                "framework": "",
                "connection_points": [],
                "posting_time": "",
            }

    def get_idea_angle_types(self) -> List[str]:
        """
        获取内容角度类型

        Returns:
            List[str]: 角度类型列表
        """
        return self.IDEA_ANGLE_TYPES


# 全局实例
content_idea_generator_service = ContentIdeaGeneratorService()


if __name__ == "__main__":
    import asyncio

    service = ContentIdeaGeneratorService()

    async def test():
        print("=== 生成内容创意 ===")
        ideas = await service.generate_ideas("春季护肤", "xiaohongshu", 3)
        for idea in ideas[:2]:
            print(f"- {idea.get('title', '')}")

        print("\n=== 结合趋势 ===")
        result = await service.generate_from_trend(
            "春日穿搭",
            {"name": "某品牌衣服", "selling_points": ["时尚", "舒适"]},
            "xiaohongshu"
        )
        print(f"标题: {result.get('title', '')}")

    asyncio.run(test())