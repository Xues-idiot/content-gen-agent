"""
Vox Hashtag Service 模块

智能 Hashtag 推荐服务
- 根据内容分析推荐最佳 hashtag
- 提供 hashtag 分类（品牌/行业/热门/情感）
- 估算 hashtag 热度与曝光量
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from loguru import logger

from backend.config import config
from backend.services.llm import llm_service


@dataclass
class HashtagInfo:
    """Hashtag 信息"""
    tag: str
    category: str  # brand, industry, trending, emotional
    heat_score: int  # 0-100, 预估热度
    exposure: str  # 低/中/高
    reason: str  # 推荐理由


class HashtagService:
    """
    智能 Hashtag 推荐服务

    支持：
    - 小红书 hashtag 推荐
    - 抖音 hashtag 推荐
    - 公众号 hashtag 推荐
    """

    # 常见行业 hashtag 库（中文）
    INDUSTRY_HASHTAGS = {
        "美妆": ["#美妆分享", "#护肤心得", "#化妆教程", "#口红试色", "#护肤打卡",
                "#素人改造", "#日常妆容", "#护肤好物", "#化妆品推荐", "# beauty"],
        "时尚": ["#时尚穿搭", "#每日穿搭", "#OOTD", "#穿搭分享", "#时尚博主",
                "#潮流搭配", "#穿搭灵感", "#衣橱必备", "#街头时尚", "# fashion"],
        "美食": ["#美食分享", "#探店打卡", "#美食推荐", "#吃货日记", "#在家做美食",
                "#网红餐厅", "#料理教程", "#吃货必看", "# foodie", "#delicious"],
        "旅行": ["#旅行打卡", "#旅行攻略", "#小众旅行地", "#旅行拍照", "#旅行博主",
                "#周末去哪玩", "#旅行记录", "#风景美拍", "# travel", "#wanderlust"],
        "健身": ["#健身打卡", "#减肥日记", "#瑜伽日常", "#增肌训练", "#健康生活",
                "#健身教程", "#体态改善", "#健康饮食", "# fitness", "#workout"],
        "母婴": ["#辣妈分享", "#育儿经验", "#宝宝辅食", "#亲子时光", "#育儿日记",
                "#妈妈必看", "#宝宝成长", "#母婴好物", "# parenting"],
        "家居": ["#家居设计", "#软装搭配", "#北欧风格", "#收纳好物", "#租房改造",
                "# Home", "#interior", "#家居博主"],
        "数码": ["#数码科技", "#手机测评", "#数码好物", "#科技前沿", "#开箱分享",
                "# gadget", "#tech"],
        "宠物": ["#宠物日记", "#猫奴日常", "#狗子萌照", "#宠物用品", "#撸猫",
                "# pet", "#puppy", "#catlife"],
        "教育": ["#学习方法", "#知识分享", "#自我提升", "#读书笔记", "#技能get",
                "# education", "#study"],
    }

    # 通用热门 hashtag（跨行业）
    TRENDING_HASHTAGS = [
        "#今日话题", "#打卡", "#分享", "#好物推荐", "#种草", "#必看",
        "#建议收藏", "#干货", "#涨知识", "#ootd", "# fyp", "# viral",
        "# trending", "#foru", "#explore", "# instagood",
    ]

    # 情感类 hashtag
    EMOTIONAL_HASHTAGS = [
        "#治愈系", "#温暖", "#正能量", "#治愈", "#生活感悟", "#心情日记",
        "#小确幸", "#生活美学", "#慢生活", "#极简生活",
    ]

    def __init__(self):
        self.llm = llm_service

    def _extract_keywords_from_content(self, content: str) -> List[str]:
        """从内容中提取关键词"""
        # 移除 hashtag 和 @提及
        text = re.sub(r'#\S+', '', content)
        text = re.sub(r'@\S+', '', text)

        # 移除标点和多余空格
        text = re.sub(r'[^\w\u4e00-\u9fff]', ' ', text)
        text = ' '.join(text.split())

        # 提取 2-4 个字的中文词组和英文单词
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
        english_words = re.findall(r'[a-zA-Z]{2,}', text)

        # 合并并去重，优先保留中文
        keywords = list(dict.fromkeys(chinese_words[:10])) + list(dict.fromkeys(english_words[:5]))
        return keywords[:15]

    def _detect_industry(self, content: str, product_info: Optional[Dict[str, Any]] = None) -> str:
        """检测内容所属行业"""
        industry_keywords = {
            "美妆": ["美妆", "化妆", "护肤", "口红", "粉底", "眼影", "美容", "妆容", "素颜", "妆"],
            "时尚": ["穿搭", "衣服", "服装", "时尚", "搭配", "衣橱", "裙子", "裤子", "鞋子", "包"],
            "美食": ["美食", "吃", "餐厅", "料理", "烹饪", "菜谱", "烘焙", "蛋糕", "咖啡", "奶茶"],
            "旅行": ["旅行", "旅游", "酒店", "机票", "景点", "打卡", "拍照", "风景", "度假"],
            "健身": ["健身", "运动", "跑步", "瑜伽", "减肥", "增肌", "训练", "体能", "健康"],
            "母婴": ["宝宝", "育儿", "妈妈", "孩子", "儿童", "辅食", "亲子", "孕妇", "宝贝"],
            "家居": ["家居", "装修", "房间", "卧室", "客厅", "收纳", "家具", "绿植", "装饰"],
            "数码": ["手机", "电脑", "相机", "数码", "科技", "平板", "耳机", "智能"],
            "宠物": ["宠物", "猫", "狗", "猫咪", "狗狗", "萌宠", "动物", "铲屎官"],
            "教育": ["学习", "教育", "知识", "读书", "考试", "培训", "技能", "课程"],
        }

        content_lower = content.lower()
        scores: Dict[str, int] = {}

        for industry, keywords in industry_keywords.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                scores[industry] = score

        if scores:
            return max(scores, key=scores.get)  # type: ignore

        # 如果有产品信息，用产品类别
        if product_info and product_info.get("category"):
            return product_info["category"]

        return "通用"

    def _estimate_heat_score(self, hashtag: str, category: str) -> int:
        """估算 hashtag 热度分数"""
        # 非常热门的 hashtag
        super_hot = ["# fyp", "#fyp", "#viral", "#trending", "#explore", "#instagood",
                     "#美食分享", "#穿搭分享", "#好物推荐", "#种草", "#ootd"]
        if hashtag.lower() in [h.lower() for h in super_hot]:
            return 95

        # 较热门的 hashtag
        hot_tags = ["#今日话题", "#打卡", "#必看", "#建议收藏", "#干货", "#涨知识"]
        if hashtag in hot_tags:
            return 80

        # 行业特定 hashtag
        if category == "industry":
            return 60
        elif category == "brand":
            return 50
        elif category == "emotional":
            return 45
        else:
            return 40

    def _get_exposure_level(self, score: int) -> str:
        """根据热度分数判断曝光等级"""
        if score >= 80:
            return "高"
        elif score >= 50:
            return "中"
        return "低"

    async def recommend_hashtags(
        self,
        content: str,
        platform: str = "xiaohongshu",
        amount: int = 10,
        product_info: Optional[Dict[str, Any]] = None,
    ) -> List[HashtagInfo]:
        """
        为内容推荐最佳 hashtag

        Args:
            content: 内容文本（标题+正文）
            platform: 平台 (xiaohongshu/tiktok/official)
            amount: 推荐数量
            product_info: 产品信息（可选）

        Returns:
            List[HashtagInfo]: 推荐的 hashtag 列表
        """
        try:
            # 1. 提取内容关键词
            keywords = self._extract_keywords_from_content(content)
            industry = self._detect_industry(content, product_info)

            logger.info(f"Hashtag 分析: 行业={industry}, 关键词={keywords}")

            # 2. 使用 LLM 生成智能 hashtag
            product_context = ""
            if product_info:
                product_context = f"""
产品信息：
- 名称：{product_info.get('name', '')}
- 描述：{product_info.get('description', '')}
- 卖点：{', '.join(product_info.get('selling_points', []))}
"""

            # 平台特定提示
            platform_hints = {
                "xiaohongshu": "小红书平台，hashtag以#开头，中英混搭效果好",
                "tiktok": "抖音平台，hashtag简短有力，容易病毒传播",
                "official": "公众号，hashtag更正式，更专业",
            }

            prompt = f"""请为以下内容生成 {amount} 个最适合{platform_hints.get(platform, '')} 的 hashtag。

内容：
{content}
{product_context}

已识别的关键词：{', '.join(keywords)}
所属行业：{industry}

要求：
1. 结合内容关键词和行业特点生成 hashtag
2. 包含 2-3 个高热度通用 hashtag
3. 包含 3-5 个行业专用 hashtag
4. 包含 1-2 个品牌/产品特色 hashtag（如适用）
5. 每个 hashtag 要有推荐理由
6. 只返回 JSON 数组格式，不要其他内容

输出格式：
[
  {{"tag": "#美妆分享", "reason": "高热度行业词，曝光量大"}},
  {{"tag": "#这款口红绝了", "reason": "产品特色，突出卖点"}}
]"""

            response = self.llm.generate(prompt)

            if response.startswith("Error:"):
                logger.error(f"LLM hashtag 生成失败: {response}")
                return self._get_fallback_hashtags(industry, amount)

            # 3. 解析 LLM 响应
            import json
            try:
                hashtag_data = json.loads(response)
            except json.JSONDecodeError:
                # 尝试从响应中提取 JSON
                match = re.search(r'\[.*]', response, re.DOTALL)
                if match:
                    try:
                        hashtag_data = json.loads(match.group())
                    except json.JSONDecodeError:
                        logger.warning(f"无法解析 hashtag JSON: {response[:100]}")
                        return self._get_fallback_hashtags(industry, amount)
                else:
                    return self._get_fallback_hashtags(industry, amount)

            # 4. 构建 HashtagInfo 列表
            results: List[HashtagInfo] = []
            for item in hashtag_data[:amount]:
                if isinstance(item, dict) and "tag" in item:
                    tag = item["tag"]
                    # 分类判断
                    category = "trending"
                    if any(kw in tag for kw in ["种草", "推荐", "分享", "必看"]):
                        category = "trending"
                    elif any(kw in tag for kw in ["日记", "日常", "打卡", "心情"]):
                        category = "emotional"
                    elif product_info and product_info.get("name", "") in tag:
                        category = "brand"
                    else:
                        category = "industry"

                    heat_score = self._estimate_heat_score(tag, category)
                    results.append(HashtagInfo(
                        tag=tag,
                        category=category,
                        heat_score=heat_score,
                        exposure=self._get_exposure_level(heat_score),
                        reason=item.get("reason", ""),
                    ))

            # 5. 如果结果不足，用备用方案补充
            if len(results) < amount:
                fallback = self._get_fallback_hashtags(industry, amount - len(results))
                results.extend(fallback)

            logger.info(f"生成 {len(results)} 个 hashtag 推荐")
            return results[:amount]

        except Exception as e:
            logger.error(f"Hashtag 推荐失败: {e}")
            return self._get_fallback_hashtags("通用", amount)

    def _get_fallback_hashtags(self, industry: str, amount: int) -> List[HashtagInfo]:
        """获取备用 hashtag（当 LLM 不可用时）"""
        fallback_tags = []

        # 添加行业 hashtag
        industry_tags = self.INDUSTRY_HASHTAGS.get(industry, self.INDUSTRY_HASHTAGS["通用"])
        for tag in industry_tags[:3]:
            fallback_tags.append(HashtagInfo(
                tag=tag,
                category="industry",
                heat_score=60,
                exposure="中",
                reason=f"行业常用标签，{industry}内容适用",
            ))

        # 添加热门 hashtag
        for tag in self.TRENDING_HASHTAGS[:3]:
            fallback_tags.append(HashtagInfo(
                tag=tag,
                category="trending",
                heat_score=80,
                exposure="高",
                reason="跨行业热门标签，曝光量大",
            ))

        # 添加情感 hashtag
        for tag in self.EMOTIONAL_HASHTAGS[:2]:
            fallback_tags.append(HashtagInfo(
                tag=tag,
                category="emotional",
                heat_score=45,
                exposure="中",
                reason="情感共鸣标签，增加互动",
            ))

        return fallback_tags[:amount]

    def get_trending_hashtags(
        self,
        platform: str = "xiaohongshu",
        industry: Optional[str] = None,
        amount: int = 10,
    ) -> List[HashtagInfo]:
        """
        获取平台热门 hashtag 列表

        Args:
            platform: 平台
            industry: 行业（可选）
            amount: 数量

        Returns:
            List[HashtagInfo]: 热门 hashtag 列表
        """
        results: List[HashtagInfo] = []

        # 平台热门
        for tag in self.TRENDING_HASHTAGS[:5]:
            results.append(HashtagInfo(
                tag=tag,
                category="trending",
                heat_score=85,
                exposure="高",
                reason="平台热门标签，曝光量大",
            ))

        # 行业热门
        if industry and industry in self.INDUSTRY_HASHTAGS:
            for tag in self.INDUSTRY_HASHTAGS[industry][:5]:
                results.append(HashtagInfo(
                    tag=tag,
                    category="industry",
                    heat_score=65,
                    exposure="中",
                    reason=f"{industry}行业热门标签",
                ))

        return results[:amount]

    def suggest_hashtag_combinations(
        self,
        hashtags: List[str],
        platform: str = "xiaohongshu",
    ) -> List[Dict[str, Any]]:
        """
        推荐 hashtag 组合方案

        Args:
            hashtags: 候选 hashtag 列表
            platform: 平台

        Returns:
            List[Dict]: 组合方案列表
        """
        if not hashtags:
            return []

        # 组合方案1: 热门优先（3个高热度）
        hot_combination = {
            "name": "热门爆发型",
            "description": "以高热度标签为主，追求最大曝光",
            "hashtags": hashtags[:3],
            "expected_exposure": "高",
            "best_for": "想要快速获取流量的新账号",
        }

        # 组合方案2: 行业专注型
        industry_tags = [h for h in hashtags if any(cat in h for cat in ["分享", "推荐", "日记"])]
        if industry_tags:
            combination = {
                "name": "行业专注型",
                "description": "以行业标签为主，吸引精准受众",
                "hashtags": industry_tags[:3],
                "expected_exposure": "中",
                "best_for": "想要吸引精准用户的账号",
            }
        else:
            combination = hot_combination

        # 组合方案3: 品牌打造型
        if len(hashtags) >= 3:
            brand_combination = {
                "name": "品牌打造型",
                "description": "结合品牌和行业标签，建立品牌认知",
                "hashtags": hashtags[:2],
                "expected_exposure": "中",
                "best_for": "想要建立品牌影响力的账号",
            }
        else:
            brand_combination = hot_combination

        return [hot_combination, combination, brand_combination]


# 全局实例
hashtag_service = HashtagService()


if __name__ == "__main__":
    import asyncio

    service = HashtagService()

    # 测试推荐
    async def test():
        content = """
        今天分享一款超级好用的面霜！
        质地清爽不油腻，保湿效果一级棒。
        用了一个月，皮肤明显变好了。
        强烈推荐给各位小仙女！
        """
        results = await service.recommend_hashtags(content, "xiaohongshu", 10)
        for r in results:
            print(f"{r.tag} ({r.exposure}) - {r.reason}")

    asyncio.run(test())