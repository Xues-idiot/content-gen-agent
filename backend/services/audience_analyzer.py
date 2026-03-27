"""
Vox Audience Analyzer Service 模块

受众分析服务
- 受众画像分析
- 受众兴趣分析
- 受众行为预测
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class AudienceProfile:
    """受众画像"""
    age_range: str
    gender: str
    interests: List[str]
    pain_points: List[str]
    motivations: List[str]
    preferred_content_style: str


class AudienceAnalyzerService:
    """
    受众分析服务

    分析内容受众和创建受众画像
    """

    def __init__(self):
        self.llm = llm_service

    # 平台受众特征
    PLATFORM_AUDIENCES = {
        "xiaohongshu": {
            "primary_age": "18-35",
            "gender": "女性为主",
            "interests": ["美妆护肤", "时尚穿搭", "生活方式", "旅游", "美食"],
            "content_style": "真实分享、种草推荐、图文并茂",
        },
        "tiktok": {
            "primary_age": "16-35",
            "gender": "男女均衡",
            "interests": ["娱乐", "搞笑", "舞蹈", "美食", "科技"],
            "content_style": "短视频、节奏快、有创意、视觉冲击",
        },
        "weibo": {
            "primary_age": "20-40",
            "gender": "男女均衡",
            "interests": ["热点新闻", "明星娱乐", "社会话题", "科技", "游戏"],
            "content_style": "观点鲜明、有态度、配图吸引",
        },
        "official": {
            "primary_age": "25-50",
            "gender": "男女均衡",
            "interests": ["行业资讯", "专业知识", "商业洞察", "管理"],
            "content_style": "专业严谨、数据支撑、深度分析",
        },
    }

    async def analyze_audience(
        self,
        content_topic: str,
        platform: str = "xiaohongshu",
    ) -> AudienceProfile:
        """
        分析受众画像

        Args:
            content_topic: 内容主题
            platform: 平台

        Returns:
            AudienceProfile: 受众画像
        """
        try:
            prompt = f"""请分析"{content_topic}"主题内容的目标受众画像。

平台：{platform}

请分析：
1. 年龄范围
2. 性别特征
3. 兴趣标签
4. 痛点需求
5. 行为动机
6. 偏好的内容风格

请以JSON格式返回：
{{
    "age_range": "18-25岁",
    "gender": "女性为主",
    "interests": ["兴趣1", "兴趣2"],
    "pain_points": ["痛点1", "痛点2"],
    "motivations": ["动机1", "动机2"],
    "preferred_content_style": "内容风格描述"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return AudienceProfile(
                age_range=result.get("age_range", "未知"),
                gender=result.get("gender", "未知"),
                interests=result.get("interests", []),
                pain_points=result.get("pain_points", []),
                motivations=result.get("motivations", []),
                preferred_content_style=result.get("preferred_content_style", ""),
            )

        except Exception as e:
            logger.error(f"分析受众失败: {e}")
            return AudienceProfile(
                age_range="未知",
                gender="未知",
                interests=[],
                pain_points=[],
                motivations=[],
                preferred_content_style="",
            )

    async def get_platform_audience(
        self,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        获取平台受众特征

        Args:
            platform: 平台

        Returns:
            Dict: 平台受众特征
        """
        audience = self.PLATFORM_AUDIENCES.get(
            platform, self.PLATFORM_AUDIENCES["xiaohongshu"]
        )

        return {
            "platform": platform,
            "primary_age": audience["primary_age"],
            "gender": audience["gender"],
            "interests": audience["interests"],
            "content_style": audience["content_style"],
        }

    async def suggest_content_for_audience(
        self,
        audience_profile: Dict[str, Any],
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        根据受众推荐内容策略

        Args:
            audience_profile: 受众画像
            platform: 平台

        Returns:
            Dict: 内容策略建议
        """
        try:
            prompt = f"""请根据以下受众画像推荐内容策略。

平台：{platform}
受众年龄：{audience_profile.get('age_range', '未知')}
受众性别：{audience_profile.get('gender', '未知')}
受众兴趣：{', '.join(audience_profile.get('interests', []))}
受众痛点：{', '.join(audience_profile.get('pain_points', []))}
受众动机：{', '.join(audience_profile.get('motivations', []))}

请提供：
1. 推荐的内容类型
2. 标题风格建议
3. 内容结构建议
4. 互动引导策略
5. 最佳发布时机

请以JSON格式返回：
{{
    "recommended_content_types": ["类型1", "类型2"],
    "title_style": "标题风格",
    "content_structure": "内容结构建议",
    "engagement_strategy": "互动引导策略",
    "best_posting_time": "最佳发布时机"
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                result = json.loads(match.group()) if match else {}

            return {
                "audience": audience_profile,
                "platform": platform,
                "recommended_content_types": result.get("recommended_content_types", []),
                "title_style": result.get("title_style", ""),
                "content_structure": result.get("content_structure", ""),
                "engagement_strategy": result.get("engagement_strategy", ""),
                "best_posting_time": result.get("best_posting_time", ""),
            }

        except Exception as e:
            logger.error(f"推荐内容策略失败: {e}")
            return {
                "audience": audience_profile,
                "platform": platform,
                "recommended_content_types": [],
                "title_style": "",
                "content_structure": "",
                "engagement_strategy": "",
                "best_posting_time": "",
            }

    def calculate_audience_match(
        self,
        content_tags: List[str],
        audience_interests: List[str],
    ) -> Dict[str, Any]:
        """
        计算内容与受众的匹配度

        Args:
            content_tags: 内容标签
            audience_interests: 受众兴趣

        Returns:
            Dict: 匹配度分析
        """
        if not content_tags or not audience_interests:
            return {
                "match_score": 0,
                "matched_interests": [],
                "unmatched_tags": content_tags,
                "recommendation": "内容标签或受众兴趣为空",
            }

        matched = set()
        for tag in content_tags:
            for interest in audience_interests:
                if tag in interest or interest in tag:
                    matched.add(interest)

        match_score = int(len(matched) / len(audience_interests) * 100)

        return {
            "match_score": match_score,
            "matched_interests": list(matched),
            "unmatched_tags": [t for t in content_tags if t not in matched],
            "recommendation": self._get_match_recommendation(match_score),
        }

    def _get_match_recommendation(self, score: int) -> str:
        """根据匹配度返回建议"""
        if score >= 80:
            return "内容与受众高度匹配"
        elif score >= 60:
            return "内容与受众较为匹配，建议优化部分标签"
        elif score >= 40:
            return "内容与受众匹配度一般，建议调整内容方向"
        else:
            return "内容与受众匹配度低，建议重新定位目标受众"


# 全局实例
audience_analyzer_service = AudienceAnalyzerService()


if __name__ == "__main__":
    import asyncio

    service = AudienceAnalyzerService()

    async def test():
        print("=== 受众分析 ===")
        profile = await service.analyze_audience("护肤面霜推荐", "xiaohongshu")
        print(f"年龄: {profile.age_range}")
        print(f"性别: {profile.gender}")
        print(f"兴趣: {', '.join(profile.interests[:3])}")
        print(f"痛点: {', '.join(profile.pain_points[:2])}")

        print("\n=== 平台受众 ===")
        audience = service.get_platform_audience("xiaohongshu")
        print(f"平台: {audience['platform']}")
        print(f"年龄: {audience['primary_age']}")
        print(f"风格: {audience['content_style']}")

        print("\n=== 内容策略推荐 ===")
        strategy = await service.suggest_content_for_audience(
            {
                "age_range": "20-30岁",
                "gender": "女性",
                "interests": ["美妆", "护肤", "时尚"],
                "pain_points": ["皮肤干燥", "选产品难"],
                "motivations": ["变美", "省钱"],
            },
            "xiaohongshu"
        )
        print(f"内容类型: {', '.join(strategy['recommended_content_types'][:2])}")
        print(f"标题风格: {strategy['title_style']}")

        print("\n=== 匹配度计算 ===")
        match = service.calculate_audience_match(
            ["护肤", "面霜", "测评"],
            ["美妆", "护肤", "时尚", "生活方式"]
        )
        print(f"匹配度: {match['match_score']}%")
        print(f"匹配兴趣: {', '.join(match['matched_interests'])}")

    asyncio.run(test())