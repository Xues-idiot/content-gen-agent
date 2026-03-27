"""
Vox Content Gap Analyzer Service 模块

内容差距分析服务
- 内容覆盖分析
- 竞争对手差距
- 内容机会识别
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


class ContentGapAnalyzerService:
    """
    内容差距分析服务

    分析内容覆盖度和差距
    """

    def __init__(self):
        self.llm = llm_service

    # 内容维度
    CONTENT_DIMENSIONS = [
        "产品介绍",
        "使用教程",
        "效果展示",
        "用户评价",
        "对比测评",
        "行业知识",
        "问题解答",
        "场景应用",
        "品牌故事",
        "优惠信息",
    ]

    async def analyze_gap(
        self,
        existing_content: List[str],
        target_topics: List[str],
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        分析内容差距

        Args:
            existing_content: 现有内容列表
            target_topics: 目标话题
            platform: 平台

        Returns:
            Dict: 差距分析结果
        """
        try:
            prompt = f"""请分析以下内容的覆盖差距。

平台：{platform}
现有内容：{', '.join(existing_content)}
目标话题：{', '.join(target_topics)}

请分析：
1. 已覆盖的内容维度
2. 未覆盖/覆盖不足的维度
3. 内容机会
4. 优先级建议

请以JSON格式返回：
{{
    "covered_dimensions": ["维度1", "维度2"],
    "gap_dimensions": ["维度1", "维度2"],
    "opportunities": ["机会1", "机会2"],
    "priorities": ["优先级1", "优先级2"]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "existing_count": len(existing_content),
                "target_count": len(target_topics),
                "covered_dimensions": result.get("covered_dimensions", []),
                "gap_dimensions": result.get("gap_dimensions", []),
                "opportunities": result.get("opportunities", []),
                "priorities": result.get("priorities", []),
            }

        except Exception as e:
            logger.error(f"分析内容差距失败: {e}")
            return {
                "existing_count": len(existing_content),
                "target_count": len(target_topics),
                "covered_dimensions": [],
                "gap_dimensions": [],
                "opportunities": [],
                "priorities": [],
            }

    async def find_content_opportunities(
        self,
        industry: str,
        platform: str = "xiaohongshu",
        num: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        找内容机会

        Args:
            industry: 行业
            platform: 平台
            num: 数量

        Returns:
            List[Dict]: 机会列表
        """
        try:
            prompt = f"""请为{industry}行业在{platform}平台找出内容机会。

行业：{industry}
平台：{platform}

请找出{num}个内容机会，每个包括：
1. 机会标题
2. 内容角度
3. 预计效果
4. 制作难度

请以JSON格式返回：
{{
    "opportunities": [
        {{
            "title": "机会标题",
            "angle": "内容角度",
            "expected_impact": "高/中/低",
            "difficulty": "高/中/低"
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

            return result.get("opportunities", [])

        except Exception as e:
            logger.error(f"找内容机会失败: {e}")
            return []

    def get_content_dimensions(self) -> List[str]:
        """
        获取内容维度

        Returns:
            List[str]: 维度列表
        """
        return self.CONTENT_DIMENSIONS


# 全局实例
content_gap_analyzer_service = ContentGapAnalyzerService()


if __name__ == "__main__":
    import asyncio

    service = ContentGapAnalyzerService()

    async def test():
        print("=== 内容差距分析 ===")
        result = await service.analyze_gap(
            ["产品介绍", "使用教程"],
            ["产品介绍", "使用教程", "效果展示", "用户评价", "对比测评"],
            "xiaohongshu"
        )
        print(f"现有: {result['existing_count']}")
        print(f"差距: {', '.join(result['gap_dimensions'][:2])}")
        print(f"机会: {', '.join(result['opportunities'][:2])}")

        print("\n=== 找内容机会 ===")
        opps = await service.find_content_opportunities("美妆", "xiaohongshu", 3)
        for o in opps[:2]:
            print(f"- {o.get('title', '')}")

    asyncio.run(test())