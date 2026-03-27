"""
Vox Keyword Research Service 模块

关键词研究服务
- 关键词挖掘和分析
- 关键词竞争度分析
- SEO优化建议
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class KeywordInfo:
    """关键词信息"""
    keyword: str
    search_volume: int  # 搜索量
    competition: str  # 竞争度: low/medium/high
    difficulty: int  # 难度 0-100
    related_keywords: List[str]  # 相关关键词
    suggestions: List[str]  # 使用建议


class KeywordResearchService:
    """
    关键词研究服务

    帮助找到最佳关键词
    """

    def __init__(self):
        self.llm = llm_service

    async def research_keywords(
        self,
        seed_keyword: str,
        platform: str = "xiaohongshu",
        num_results: int = 10,
    ) -> List[KeywordInfo]:
        """
        研究关键词

        Args:
            seed_keyword: 种子关键词
            platform: 平台
            num_results: 返回数量

        Returns:
            List[KeywordInfo]: 关键词列表
        """
        try:
            prompt = f"""请为"{seed_keyword}"进行关键词研究。

目标平台：{platform}
返回数量：{num_results}个关键词

请提供以下信息：
1. 关键词本身
2. 预估搜索量（相对值：高/中/低）
3. 竞争程度（低/中/高）
4. SEO难度（0-100）
5. 相关关键词（3-5个）
6. 使用建议

请以JSON格式返回：
{{
    "keywords": [
        {{
            "keyword": "关键词",
            "search_volume": "高/中/低",
            "competition": "低/中/高",
            "difficulty": 45,
            "related_keywords": ["相关词1", "相关词2"],
            "suggestions": ["建议1", "建议2"]
        }}
    ]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
                keywords_data = result.get("keywords", [])
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                if match:
                    try:
                        result = json.loads(match.group())
                        keywords_data = result.get("keywords", [])
                    except:
                        keywords_data = self._get_fallback_keywords(seed_keyword)
                else:
                    keywords_data = self._get_fallback_keywords(seed_keyword)

            return [
                KeywordInfo(
                    keyword=k.get("keyword", ""),
                    search_volume=self._parse_volume(k.get("search_volume", "中")),
                    competition=k.get("competition", "中"),
                    difficulty=k.get("difficulty", 50),
                    related_keywords=k.get("related_keywords", []),
                    suggestions=k.get("suggestions", []),
                )
                for k in keywords_data[:num_results]
            ]

        except Exception as e:
            logger.error(f"关键词研究失败: {e}")
            return self._get_fallback_keywords_obj(seed_keyword)

    def _parse_volume(self, volume_str: str) -> int:
        """解析搜索量字符串"""
        volume_map = {"高": 10000, "中": 5000, "低": 1000}
        return volume_map.get(volume_str, 5000)

    def _get_fallback_keywords(self, seed: str) -> List[Dict]:
        """获取默认关键词"""
        return [
            {
                "keyword": seed,
                "search_volume": "中",
                "competition": "中",
                "difficulty": 50,
                "related_keywords": [f"{seed}推荐", f"{seed}测评", f"如何选择{seed}"],
                "suggestions": [f"适合作为核心关键词", f"可以组合长尾词使用"],
            },
            {
                "keyword": f"{seed}推荐",
                "search_volume": "高",
                "competition": "高",
                "difficulty": 70,
                "related_keywords": [f"最好的{seed}", f"{seed}排行榜"],
                "suggestions": ["竞争激烈，需要差异化"],
            },
            {
                "keyword": f"{seed}测评",
                "search_volume": "中",
                "competition": "中",
                "difficulty": 45,
                "related_keywords": [f"{seed}对比", f"{seed}体验"],
                "suggestions": ["适合做测评类内容"],
            },
        ]

    def _get_fallback_keywords_obj(self, seed: str) -> List[KeywordInfo]:
        """获取默认关键词对象"""
        data = self._get_fallback_keywords(seed)
        return [
            KeywordInfo(
                keyword=d["keyword"],
                search_volume=self._parse_volume(d["search_volume"]),
                competition=d["competition"],
                difficulty=d["difficulty"],
                related_keywords=d["related_keywords"],
                suggestions=d["suggestions"],
            )
            for d in data
        ]

    async def analyze_keyword_difficulty(
        self,
        keyword: str,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        分析关键词难度

        Args:
            keyword: 关键词
            platform: 平台

        Returns:
            Dict: 难度分析结果
        """
        try:
            prompt = f"""请分析关键词"{keyword}"在{platform}平台的SEO难度。

请分析：
1. 难度评分（0-100）
2. 主要竞争对手
3. 突破难度的方法
4. 建议的内容策略

请以JSON格式返回：
{{
    "keyword": "{keyword}",
    "difficulty_score": 55,
    "competition_analysis": "竞争分析",
    "breakthrough_methods": ["方法1", "方法2"],
    "content_strategy": "内容策略建议"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "keyword": keyword,
                "difficulty_score": result.get("difficulty_score", 50),
                "competition_analysis": result.get("competition_analysis", ""),
                "breakthrough_methods": result.get("breakthrough_methods", []),
                "content_strategy": result.get("content_strategy", ""),
            }

        except Exception as e:
            logger.error(f"分析关键词难度失败: {e}")
            return {
                "keyword": keyword,
                "difficulty_score": 50,
                "competition_analysis": "分析失败",
                "breakthrough_methods": [],
                "content_strategy": "",
            }

    def generate_keyword_clusters(
        self,
        keywords: List[str],
    ) -> Dict[str, List[str]]:
        """
        生成关键词簇

        将关键词分组到不同的主题簇

        Args:
            keywords: 关键词列表

        Returns:
            Dict[str, List[str]]: 关键词簇
        """
        # 简单实现 - 实际应该用NLP
        clusters = {
            "核心词": [],
            "长尾词": [],
            "问答词": [],
            "品牌词": [],
        }

        for kw in keywords:
            if "如何" in kw or "怎么" in kw or "为什么" in kw:
                clusters["问答词"].append(kw)
            elif anybrand in kw.lower() for anybrand in ["品牌", "推荐", "排行"]):
                clusters["品牌词"].append(kw)
            elif len(kw) > 6:
                clusters["长尾词"].append(kw)
            else:
                clusters["核心词"].append(kw)

        return {k: v for k, v in clusters.items() if v}

    def suggest_keyword_combinations(
        self,
        primary_keyword: str,
        secondary_keywords: List[str],
    ) -> List[str]:
        """
        建议关键词组合

        Args:
            primary_keyword: 主要关键词
            secondary_keywords: 次要关键词列表

        Returns:
            List[str]: 组合后的关键词
        """
        combinations = []

        # 主要 + 次要
        for sec in secondary_keywords[:5]:
            combinations.append(f"{primary_keyword} {sec}")
            combinations.append(f"{sec} {primary_keyword}")

        # 加上修饰词
        modifiers = ["2024", "最新", "测评", "推荐", "攻略"]
        for mod in modifiers:
            combinations.append(f"{mod} {primary_keyword}")

        return list(set(combinations))[:10]


# 全局实例
keyword_research_service = KeywordResearchService()


if __name__ == "__main__":
    import asyncio

    service = KeywordResearchService()

    async def test():
        print("=== 关键词研究 ===")
        keywords = await service.research_keywords("面霜", num_topics=5)

        for kw in keywords:
            print(f"\n关键词: {kw.keyword}")
            print(f"  搜索量: {kw.search_volume}")
            print(f"  竞争度: {kw.competition}")
            print(f"  难度: {kw.difficulty}")
            print(f"  相关词: {', '.join(kw.related_keywords[:3])}")

        print("\n=== 关键词难度分析 ===")
        analysis = await service.analyze_keyword_difficulty("面霜推荐")
        print(f"关键词: {analysis['keyword']}")
        print(f"难度: {analysis['difficulty_score']}")
        print(f"分析: {analysis['competition_analysis']}")

        print("\n=== 关键词组合 ===")
        combos = service.suggest_keyword_combinations("面霜", ["干皮", "油皮", "敏感肌"])
        print(f"组合: {', '.join(combos[:5])}")

    asyncio.run(test())
