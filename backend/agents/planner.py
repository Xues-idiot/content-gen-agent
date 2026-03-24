"""
Vox Planner 模块 - 内容规划

负责分析产品信息，确定内容方向和目标用户
集成 Tavily 搜索用于市场调研和内容灵感
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from loguru import logger

from backend.tools.web_search import web_search_tool


@dataclass
class ProductInfo:
    """产品信息"""
    name: str                           # 产品名称
    description: str                    # 产品描述
    selling_points: List[str]           # 卖点列表
    target_users: List[str]             # 目标用户群体
    category: str = ""                  # 产品类别
    price_range: str = ""               # 价格区间
    competitors: List[str] = field(default_factory=list)  # 竞品


@dataclass
class UserProfile:
    """用户画像"""
    age_range: str = ""                 # 年龄范围
    gender: str = ""                    # 性别
    occupation: str = ""                # 职业
    interests: List[str] = field(default_factory=list)  # 兴趣
    pain_points: List[str] = field(default_factory=list)  # 痛点
    buying_motivations: List[str] = field(default_factory=list)  # 购买动机


@dataclass
class ContentPlan:
    """内容规划"""
    product: ProductInfo
    target_users: List[UserProfile]
    content_direction: str              # 内容方向
    key_themes: List[str]              # 主题
    tone_of_voice: str                 # 语调风格
    recommended_platforms: List[str]    # 推荐平台
    content_ratio: dict = field(default_factory=dict)  # 内容比例
    market_insights: List[str] = field(default_factory=list)  # 市场洞察
    trend_topics: List[str] = field(default_factory=list)  # 趋势话题
    competitor_content: List[Dict[str, str]] = field(default_factory=list)  # 竞品内容


class ContentPlanner:
    """
    内容规划 Agent

    分析产品信息，确定：
    - 目标用户画像
    - 内容方向
    - 推荐平台
    - 市场洞察（集成 Tavily 搜索）
    """

    def __init__(self):
        self.web_search = web_search_tool

    def plan_content(
        self,
        product: ProductInfo,
        platforms: List[str] = None,
        enable_research: bool = True,
    ) -> ContentPlan:
        """
        规划内容方向

        Args:
            product: 产品信息
            platforms: 目标平台列表
            enable_research: 是否启用市场调研（默认启用）

        Returns:
            ContentPlan: 内容规划结果
        """
        platforms = platforms or ["xiaohongshu", "tiktok", "official"]

        # 分析目标用户
        target_users = self.analyze_target_user(product)

        # 确定内容方向
        content_direction = self._determine_content_direction(product)

        # 确定主题
        key_themes = self._extract_key_themes(product)

        # 确定语调
        tone = self._determine_tone(product)

        # 推荐平台
        recommended = self._recommend_platforms(product, platforms)

        # 内容比例
        content_ratio = self._calculate_content_ratio(recommended)

        # 市场调研（可选）
        market_insights = []
        trend_topics = []
        competitor_content = []

        if enable_research:
            market_insights, trend_topics, competitor_content = self._gather_market_research(
                product, recommended
            )

        return ContentPlan(
            product=product,
            target_users=target_users,
            content_direction=content_direction,
            key_themes=key_themes,
            tone_of_voice=tone,
            recommended_platforms=recommended,
            content_ratio=content_ratio,
            market_insights=market_insights,
            trend_topics=trend_topics,
            competitor_content=competitor_content,
        )

    def _gather_market_research(
        self,
        product: ProductInfo,
        platforms: List[str],
    ) -> tuple:
        """
        收集市场调研信息

        Args:
            product: 产品信息
            platforms: 目标平台

        Returns:
            tuple: (market_insights, trend_topics, competitor_content)
        """
        market_insights = []
        trend_topics = []
        competitor_content = []

        try:
            # 搜索趋势话题
            trend_response = self.web_search.search_for_trends(
                category=product.category or product.name,
                max_results=3,
            )

            if trend_response.success:
                for result in trend_response.results:
                    if result.content:
                        trend_topics.append(result.content[:200])

            # 搜索竞品内容（如果存在竞品）
            for competitor in product.competitors[:2]:
                competitor_response = self.web_search.search_for_comp分析(
                    competitor_name=competitor,
                    max_results=2,
                )
                if competitor_response.success:
                    for result in competitor_response.results:
                        competitor_content.append({
                            "name": competitor,
                            "title": result.title,
                            "url": result.url,
                            "snippet": result.content[:150] if result.content else "",
                        })

            # 收集市场洞察
            for platform in platforms[:2]:
                insight_response = self.web_search.search_for_content_inspiration(
                    product_name=product.name,
                    category=product.category,
                    platform=platform,
                    max_results=2,
                )
                if insight_response.success:
                    for result in insight_response.results:
                        if result.content:
                            market_insights.append(result.content[:200])

        except Exception as e:
            # 静默处理调研错误，不影响主流程
            logger.warning(f"Market research skipped: {e}")

        return market_insights, trend_topics, competitor_content
    
    def analyze_target_user(self, product: ProductInfo) -> List[UserProfile]:
        """
        分析目标用户
        
        Args:
            product: 产品信息
            
        Returns:
            List[UserProfile]: 用户画像列表
        """
        profiles = []
        
        for user_desc in product.target_users:
            profile = UserProfile(
                occupation=user_desc,
                pain_points=self._infer_pain_points(product),
                buying_motivations=product.selling_points[:2],
            )
            profiles.append(profile)
        
        # 确保至少有一个默认用户画像
        if not profiles:
            profiles.append(UserProfile(
                occupation="普通消费者",
                pain_points=self._infer_pain_points(product),
                buying_motivations=product.selling_points[:2],
            ))
        
        return profiles
    
    def _infer_pain_points(self, product: ProductInfo) -> List[str]:
        """从产品卖点推断用户痛点"""
        pain_points = []
        for point in product.selling_points:
            # 简单转换：效率低 → 效率高困扰
            pain_points.append(f"面临{point}相关问题")
        return pain_points[:3]
    
    def _determine_content_direction(self, product: ProductInfo) -> str:
        """确定内容方向"""
        if product.category:
            return f"{product.category}解决方案"
        return "产品评测与推荐"
    
    def _extract_key_themes(self, product: ProductInfo) -> List[str]:
        """提取关键主题"""
        themes = []
        
        # 从卖点提取主题
        for point in product.selling_points[:3]:
            themes.append(point)
        
        # 添加产品名称相关主题
        if product.name:
            themes.append(f"{product.name}体验")
        
        return themes
    
    def _determine_tone(self, product: ProductInfo) -> str:
        """确定语调风格"""
        # 根据产品类别确定语调
        category_tones = {
            "美妆": "亲和、时尚、有感染力",
            "数码": "专业、简洁、有说服力",
            "食品": "生动、诱人、生活化",
            "家居": "温馨、舒适、实用",
        }
        return category_tones.get(product.category, "亲切、真实、有价值")
    
    def _recommend_platforms(
        self, 
        product: ProductInfo, 
        requested: List[str]
    ) -> List[str]:
        """推荐适合的平台"""
        all_platforms = {
            "xiaohongshu": {"weight": 0.4, "desc": "种草笔记"},
            "tiktok": {"weight": 0.3, "desc": "短视频"},
            "official": {"weight": 0.2, "desc": "公众号"},
            "friend_circle": {"weight": 0.1, "desc": "朋友圈"},
        }
        
        recommended = []
        for platform in requested:
            if platform in all_platforms:
                recommended.append(platform)
        
        return recommended or ["xiaohongshu"]
    
    def _calculate_content_ratio(self, platforms: List[str]) -> dict:
        """计算内容比例"""
        if len(platforms) == 1:
            return {"main": 1.0}
        
        ratios = {
            "xiaohongshu": {"干货分享": 0.4, "产品推广": 0.3, "用户互动": 0.2, "热点借势": 0.1},
            "tiktok": {"产品展示": 0.5, "使用场景": 0.3, "口碑推荐": 0.2},
            "official": {"深度文章": 0.5, "产品介绍": 0.3, "用户案例": 0.2},
            "friend_circle": {"产品图": 0.5, "口碑推荐": 0.3, "限时活动": 0.2},
        }
        
        result = {}
        for platform in platforms:
            result[platform] = ratios.get(platform, {})
        
        return result


if __name__ == "__main__":
    # 测试
    planner = ContentPlanner()
    
    product = ProductInfo(
        name="智能睡眠枕",
        description="一款基于AI技术的智能枕头",
        selling_points=["改善睡眠质量", "智能监测", "个性化调节"],
        target_users=["加班族", "失眠人群"],
        category="家居",
    )
    
    plan = planner.plan_content(product, ["xiaohongshu", "tiktok"])
    
    print(f"内容方向: {plan.content_direction}")
    print(f"主题: {plan.key_themes}")
    print(f"语调: {plan.tone_of_voice}")
    print(f"平台: {plan.recommended_platforms}")
    print(f"比例: {plan.content_ratio}")
