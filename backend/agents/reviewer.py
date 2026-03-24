"""Vox Reviewer 模块 - 内容审核

提供广告法违规词检测、文案质量评估、改进建议等功能
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
import re

# 违规词列表（广告法）- 分类整理
AD_VIOLATION_WORDS = {
    "最高级": [
        "最好", "第一", "顶级", "极品", "最佳", "最优", "最强", "全球", "世界", "宇宙",
        "之首", "之最", "顶尖", "领先", "卓越", "非凡", "超级", "至上", "至高",
        "独创", "专供", "VIP", "高端", "高档",
    ],
    "绝对化": [
        "绝对", "彻底", "完美", "万能", "特效", "无敌", "100%", "全网", "全体",
        "彻底解决", "完全", "全面", "始终", "保证", "承诺", "必须", "一定",
        "包治", "根治", "立竿见影", "立即", "马上",
    ],
    "虚假夸大": [
        "遥遥领先", "史无前例", "空前绝后", "独家", "唯一", "首选", "首发",
        "绝无仅有", "无与伦比", "叹为观止", "不可思议", "前所未有",
        "销量第一", "市场第一", "行业第一", "遥遥领先",
    ],
    "疑似违禁": [
        "国家级", "全网第一", "明星推荐", "网红推荐", "央视推荐",
        "国家免检", "军供", "特供", "内供",
    ],
    "迷信欺诈": [
        "发财", "致富", "日赚", "月入", "稳赚", "保本", "回报", "收益",
        "神效", "神奇", "秘方", "祖传", "宫廷", "御用",
    ],
    "医疗虚假": [
        "治愈", "治疗", "医治", "疗法", "疗程", "药到病除",
        "延年益寿", "长生不老", "返老还童", "增强免疫力",
        "抗衰老", "抗氧化", "降血压", "降血糖", "降血脂",
    ],
    "食品违规": [
        "有机", "绿色", "无添加", "零添加", "纯天然",
        "抗癌", "防癌", "延寿", "保健", "养生",
    ],
}

# 展平为列表
ALL_VIOLATION_WORDS = [word for words in AD_VIOLATION_WORDS.values() for word in words]

# 构建词到分类和严重程度的映射 (用于O(1)查找)
WORD_TO_CATEGORY = {}
for category, words in AD_VIOLATION_WORDS.items():
    severity = "error" if category in ["最高级", "绝对化", "虚假夸大"] else "warning"
    for word in words:
        WORD_TO_CATEGORY[word] = {"category": category, "severity": severity}


@dataclass
class Violation:
    """违规词"""
    word: str
    position: int
    suggestion: str = ""
    severity: str = "warning"  # error, warning, info
    category: str = ""  # 违规分类


@dataclass
class ReviewResult:
    """审核结果"""
    passed: bool = True
    violations: List[Violation] = field(default_factory=list)
    quality_score: float = 0.0  # 0-10
    suggestions: List[str] = field(default_factory=list)
    analysis: Dict[str, Any] = field(default_factory=dict)
    word_count: int = 0
    char_count: int = 0


class Reviewer:
    """
    内容审核 Agent

    功能：
    - 广告法违规词检测
    - 文案质量评分
    - 改进建议生成
    """

    # 替换建议映射
    SUGGESTIONS = {
        "最好": "优秀",
        "第一": "领先",
        "顶级": "高端",
        "最佳": "优秀",
        "最优": "出色",
        "最强": "出众",
        "独家": "专属",
        "唯一": "专属",
        "绝对": "非常",
        "彻底": "完全",
        "完美": "出色",
        "万能": "多用",
        "特效": "有效",
        "无敌": "卓越",
        "遥遥领先": "表现突出",
        "史无前例": "罕见",
        "空前绝后": "独特",
        "全球": "国内外",
        "世界": "行业",
        "宇宙": "领域",
        "顶尖": "一流",
        "领先": "表现优异",
        "超级": "优秀",
        "独创": "自主研发",
        "专供": "精选",
        "保证": "承诺提供",
        "100%": "高",
        "全网": "众多",
        "立竿见影": "效果明显",
        "日赚": "额外收入",
        "月入": "收入",
        "稳赚": "可靠",
        "神效": "显著效果",
        "神奇": "显著",
        "秘方": "配方",
        "祖传": "传统",
        "宫廷": "经典",
    }

    def check_ad_words(self, copy: str) -> List[Violation]:
        """检测广告法违规词"""
        violations = []
        seen_words = set()  # 避免重复报告同一个词

        for word in ALL_VIOLATION_WORDS:
            # 使用正则匹配，考虑标点符号分隔
            pattern = rf'(?<![\u4e00-\u9fa5])({re.escape(word)})(?![\u4e00-\u9fa5])'
            for match in re.finditer(pattern, copy):
                # 使用预计算的映射进行O(1)查找
                word_info = WORD_TO_CATEGORY.get(word, {})
                category = word_info.get("category", "")
                severity = word_info.get("severity", "warning")

                # 避免重复报告同一个词
                if word not in seen_words:
                    seen_words.add(word)
                    violations.append(Violation(
                        word=word,
                        position=match.start(),
                        suggestion=self._get_suggestion(word),
                        severity=severity,
                        category=category,
                    ))
        return violations

    def analyze_structure(self, copy: str) -> Dict[str, Any]:
        """分析文案结构"""
        analysis = {
            "has_title": False,
            "has_emoji": False,
            "has_numbers": False,
            "has_hashtags": False,
            "paragraph_count": 0,
            "avg_paragraph_length": 0,
        }

        # 检测标题标记
        analysis["has_title"] = bool(re.search(r'^#{1,3}\s|\n.{0,20}\n.*═', copy))

        # 检测 emoji
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "]+"
        )
        analysis["has_emoji"] = bool(emoji_pattern.search(copy))

        # 检测数字
        analysis["has_numbers"] = bool(re.search(r'\d+', copy))

        # 检测标签
        analysis["has_hashtags"] = bool(re.search(r'#\w+', copy))

        # 段落分析
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', copy) if p.strip()]
        analysis["paragraph_count"] = len(paragraphs)
        if paragraphs:
            analysis["avg_paragraph_length"] = sum(len(p) for p in paragraphs) / len(paragraphs)

        return analysis

    def review_quality(self, copy: str) -> ReviewResult:
        """
        审核文案质量

        综合评估文案质量，包括：
        - 违规词检测
        - 结构分析
        - 可读性评估
        """
        result = ReviewResult()

        # 基础统计
        result.char_count = len(copy)
        result.word_count = len(copy.replace("\n", "").replace(" ", ""))

        # 违规词检测
        violations = self.check_ad_words(copy)
        result.violations = violations
        result.passed = len([v for v in violations if v.severity == "error"]) == 0

        # 质量评分
        result.quality_score = self._calculate_quality_score(copy, violations)

        # 结构分析
        result.analysis = self.analyze_structure(copy)

        # 改进建议
        result.suggestions = self._generate_suggestions(copy, violations, result.analysis)

        return result

    def _get_suggestion(self, word: str) -> str:
        """获取替换建议"""
        return self.SUGGESTIONS.get(word, "请修改为更客观的表述")

    def _calculate_quality_score(self, copy: str, violations: List[Violation]) -> float:
        """计算文案质量分数"""
        score = 10.0

        # 违规词扣分
        for v in violations:
            if v.severity == "error":
                score -= 2.0
            elif v.severity == "warning":
                score -= 0.5

        # 长度评分
        if len(copy) < 50:
            score -= 1.0
        elif len(copy) < 100:
            score -= 0.5
        elif len(copy) > 2000:
            score -= 0.5

        # 标点符号评分
        if not any(e in copy for e in ["！", "？", "?"]):
            score -= 0.3

        # 数字评分（增强说服力）
        if not any(c.isdigit() for c in copy):
            score -= 0.2

        return max(0.0, min(10.0, round(score, 1)))

    def _generate_suggestions(
        self,
        copy: str,
        violations: List[Violation],
        analysis: Dict[str, Any],
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []

        # 结构建议
        if not analysis["has_emoji"]:
            suggestions.append("建议添加表情符号增强亲和力")
        if not analysis["has_numbers"]:
            suggestions.append("建议添加具体数字增强说服力")
        if not analysis["has_hashtags"]:
            suggestions.append("建议添加相关话题标签增加曝光")

        # 长度建议
        if len(copy) < 100:
            suggestions.append("文案偏短，建议增加更多细节描写")
        elif len(copy) > 1000:
            suggestions.append("文案较长，建议精简内容，突出重点")

        # 段落建议
        if analysis["paragraph_count"] < 2:
            suggestions.append("建议分段书写，增强可读性")

        # 违规词建议（最多3条）
        violation_suggestions = []
        for v in violations[:3]:
            violation_suggestions.append(f"替换「{v.word}」为更客观的表述")
        suggestions.extend(violation_suggestions[:3])

        # 去重并限制数量
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)

        return unique_suggestions[:5]

    def suggest_platform_optimization(self, copy: str, platform: str) -> List[str]:
        """生成平台特定的优化建议"""
        suggestions = []
        analysis = self.analyze_structure(copy)

        if platform == "xiaohongshu":
            if not analysis["has_emoji"]:
                suggestions.append("小红书用户偏好活泼风格，建议多使用emoji")
            if not analysis["has_hashtags"]:
                suggestions.append("建议添加3-5个小红书话题标签")
            if len(copy) < 200:
                suggestions.append("小红书笔记建议300-500字效果更好")
            if analysis["avg_paragraph_length"] > 100:
                suggestions.append("建议增加段落分隔，每段控制在100字以内")

        elif platform == "tiktok":
            if analysis["has_hashtags"]:
                suggestions.append("抖音视频描述建议精简标签，1-2个即可")
            if len(copy) > 150:
                suggestions.append("抖音开场白建议简洁有力，前3秒抓住用户")
            if not analysis["has_numbers"]:
                suggestions.append("建议添加具体数据或时间节点增强代入感")

        elif platform == "official":
            if analysis["paragraph_count"] < 5:
                suggestions.append("公众号文章建议多段落增强可读性")
            if not analysis["has_numbers"]:
                suggestions.append("建议添加数据支撑或案例分析增强说服力")
            if len(copy) < 500:
                suggestions.append("公众号深度文章建议800-1500字")

        elif platform == "friend_circle":
            if analysis["has_hashtags"]:
                suggestions.append("朋友圈文案不建议添加标签")
            if len(copy) > 200:
                suggestions.append("朋友圈文案建议控制在200字以内")
            if not analysis["has_emoji"]:
                suggestions.append("朋友圈内容建议添加1-3个表情符号")

        return suggestions

    def batch_review(self, copies: List[str]) -> List[ReviewResult]:
        """批量审核文案"""
        return [self.review_quality(copy) for copy in copies]

    def suggest_scheduling(self, platform: str, content_type: str = "general") -> Dict[str, Any]:
        """生成发布时段建议"""
        scheduling = {
            "best_times": [],
            "avoid_times": [],
            "frequency": "",
            "reasoning": "",
        }

        if platform == "xiaohongshu":
            scheduling["best_times"] = ["19:00-21:00", "12:00-13:00", "22:00-23:00"]
            scheduling["avoid_times"] = ["6:00-9:00", "14:00-17:00"]
            scheduling["frequency"] = "每周3-5篇，保持活跃度"
            scheduling["reasoning"] = "小红书用户活跃时间集中在午休和晚间，与生活方式类内容契合"
        elif platform == "tiktok":
            scheduling["best_times"] = ["12:00-14:00", "18:00-21:00"]
            scheduling["avoid_times"] = ["23:00-次日7:00"]
            scheduling["frequency"] = "每天1-2条，保持更新节奏"
            scheduling["reasoning"] = "抖音流量高峰期在中午和晚间，短视频需要持续更新"
        elif platform == "official":
            scheduling["best_times"] = ["12:00-13:00", "20:00-22:00"]
            scheduling["avoid_times"] = ["周末"]
            scheduling["frequency"] = "每周1-2篇，注重内容深度"
            scheduling["reasoning"] = "公众号用户多在通勤和睡前阅读，适合深度内容"
        elif platform == "friend_circle":
            scheduling["best_times"] = ["20:00-22:00", "12:00-13:00"]
            scheduling["avoid_times"] = ["工作时间"]
            scheduling["frequency"] = "每周2-3次，避免刷屏"
            scheduling["reasoning"] = "朋友圈内容在晚间浏览量最高，要注意频率避免被屏蔽"

        return scheduling

    def check_similarity(self, content1: str, content2: str) -> float:
        """
        检查两段内容的相似度

        Returns:
            float: 0-1 的相似度分数，1 表示完全相同
        """
        import jieba

        # 分词
        words1 = set(jieba.cut(content1))
        words2 = set(jieba.cut(content2))

        # 计算 Jaccard 相似度
        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def check_duplicate_in_batch(self, content: str, existing_contents: List[str]) -> Dict[str, Any]:
        """
        检查内容是否与已有内容重复

        Returns:
            dict: 包含相似度分数和警告信息
        """
        if not existing_contents:
            return {"is_duplicate": False, "max_similarity": 0.0, "warnings": []}

        similarities = [self.check_similarity(content, existing) for existing in existing_contents]
        max_similarity = max(similarities) if similarities else 0.0

        warnings = []
        if max_similarity > 0.8:
            warnings.append("与已有内容高度相似，建议修改以提高差异化")
        elif max_similarity > 0.6:
            warnings.append("与部分内容有较高相似度，可以进一步差异化")

        return {
            "is_duplicate": max_similarity > 0.8,
            "max_similarity": round(max_similarity, 3),
            "warnings": warnings,
        }

    def suggest_hashtags(self, content: str, platform: str, max_tags: int = 5) -> List[str]:
        """
        根据内容推荐话题标签

        Args:
            content: 文案内容
            platform: 目标平台
            max_tags: 最大标签数量

        Returns:
            List[str]: 推荐的话题标签列表
        """
        import jieba
        import re

        # 提取关键词
        words = jieba.cut(content)
        keywords = [w for w in words if len(w) >= 2 and not re.match(r'^[\d\W]+$', w)]

        # 统计词频
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1

        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        # 平台特定的标签规则
        platform_tags = {
            "xiaohongshu": ["种草", "好物推荐", "分享", "测评", "护肤", "美妆", "生活"],
            "tiktok": ["热门", "推荐", "技巧", "教程", "分享"],
            "official": ["深度", "解读", "分析", "行业", "观点"],
            "friend_circle": ["日常", "分享", "生活"],
        }

        base_tags = platform_tags.get(platform, ["推荐"])

        # 组合推荐标签
        suggested = []
        for word, freq in sorted_words[:max_tags * 2]:
            if word not in ["一个", "这个", "那个", "什么", "怎么"]:
                suggested.append(f"#{word}")

        # 添加平台通用标签
        for tag in base_tags:
            if len(suggested) >= max_tags:
                break
            full_tag = f"#{tag}"
            if full_tag not in suggested:
                suggested.append(full_tag)

        return suggested[:max_tags]

    def predict_performance(self, content: str, platform: str) -> Dict[str, Any]:
        """
        预测内容表现

        基于内容特征预测可能的用户互动和传播效果

        Returns:
            dict: 包含预测分数和影响因素
        """
        analysis = self.analyze_structure(content)
        violations = self.check_ad_words(content)

        # 计算基础分数
        base_score = 70.0

        # 长度因素
        length = len(content)
        if 100 <= length <= 500:
            base_score += 10.0  # 最佳长度范围
        elif length < 100:
            base_score -= 10.0
        elif length > 1000:
            base_score -= 5.0

        # 结构因素
        if analysis["has_emoji"]:
            base_score += 8.0
        if analysis["has_numbers"]:
            base_score += 5.0
        if analysis["has_hashtags"]:
            base_score += 5.0
        if analysis["paragraph_count"] >= 3:
            base_score += 5.0

        # 违规词惩罚
        for v in violations:
            if v.severity == "error":
                base_score -= 15.0
            else:
                base_score -= 5.0

        # 平台特定调整
        if platform == "xiaohongshu":
            if analysis["has_emoji"] and analysis["has_hashtags"]:
                base_score += 10.0  # 小红书偏好
        elif platform == "tiktok":
            if length <= 150:
                base_score += 10.0  # 抖音偏好简短
        elif platform == "official":
            if length >= 500:
                base_score += 10.0  # 公众号偏好深度

        # 限制分数范围
        predicted_score = max(0, min(100, base_score))

        # 评级
        if predicted_score >= 85:
            rating = "A"
        elif predicted_score >= 70:
            rating = "B"
        elif predicted_score >= 55:
            rating = "C"
        else:
            rating = "D"

        # 影响因素
        factors = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
        }

        if analysis["has_emoji"]:
            factors["strengths"].append("使用表情符号增强亲和力")
        if analysis["has_numbers"]:
            factors["strengths"].append("包含具体数据增强说服力")
        if analysis["has_hashtags"]:
            factors["strengths"].append("话题标签有助于曝光")
        if length and 100 <= length <= 500:
            factors["strengths"].append("内容长度适中")

        if violations:
            factors["weaknesses"].append(f"存在 {len([v for v in violations if v.severity == 'error'])} 个严重违规词")
        if not analysis["has_emoji"]:
            factors["opportunities"].append("添加表情符号可能提升互动")
        if not analysis["has_numbers"]:
            factors["opportunities"].append("添加具体数字可能增强说服力")
        if not analysis["has_hashtags"]:
            factors["opportunities"].append("添加话题标签可能增加曝光")

        return {
            "predicted_score": round(predicted_score, 1),
            "rating": rating,
            "platform": platform,
            "factors": factors,
            "confidence": "medium",  # 简化版本，始终返回中等置信度
        }

    def suggest_ab_tests(self, content: str, platform: str) -> Dict[str, Any]:
        """
        生成 A/B 测试建议

        根据内容特征建议可以测试的变量
        """
        analysis = self.analyze_structure(content)

        # 分析可测试的变量
        testable_variables = []

        # 标题测试
        testable_variables.append({
            "variable": "title",
            "description": "标题",
            "current_value": "使用感叹句或疑问句" if "！" in content or "？" in content else "使用陈述句",
            "suggested_alternatives": [
                "使用数字：加入具体数据或统计",
                "使用疑问：引发用户好奇心",
                "使用感叹：增强情感共鸣",
            ],
        })

        # 开头测试
        testable_variables.append({
            "variable": "opening",
            "description": "开头方式",
            "current_value": "直接陈述",
            "suggested_alternatives": [
                "以故事/经历开头",
                "以问题开头",
                "以惊人事实开头",
            ],
        })

        # CTA 测试
        has_cta = bool(re.search(r"点击|关注|评论|分享|购买|立即", content))
        testable_variables.append({
            "variable": "cta",
            "description": "行动号召",
            "current_value": "有CTA" if has_cta else "无CTA",
            "suggested_alternatives": [
                "增强紧迫感：限时、限量",
                "强调价值：具体收益描述",
                "降低门槛：简单直接的指令",
            ],
        })

        # 长度测试
        length = len(content)
        testable_variables.append({
            "variable": "length",
            "description": "内容长度",
            "current_value": f"{length}字（{'适中' if 100 <= length <= 500 else '较长' if length > 500 else '较短'}）",
            "suggested_alternatives": [
                "缩短20%：精简要点",
                "延长50%：增加细节",
                "对比：完整版 vs 精简版",
            ],
        })

        # 标签测试
        has_hashtags = analysis["has_hashtags"]
        testable_variables.append({
            "variable": "hashtags",
            "description": "话题标签",
            "current_value": "有标签" if has_hashtags else "无标签",
            "suggested_alternatives": [
                "使用热门标签",
                "使用长尾标签",
                "不使用标签",
            ],
        })

        # emoji 测试
        has_emoji = analysis["has_emoji"]
        testable_variables.append({
            "variable": "emoji",
            "description": "表情符号",
            "current_value": "有表情" if has_emoji else "无表情",
            "suggested_alternatives": [
                "增加emoji密度",
                "减少emoji使用",
                "使用平台特有表情",
            ],
        })

        return {
            "platform": platform,
            "testable_variables": testable_variables,
            "recommended_tests": [
                {
                    "name": "标题测试",
                    "hypothesis": "不同标题风格会影响点击率",
                    "priority": "high",
                },
                {
                    "name": "CTA测试",
                    "hypothesis": "不同行动号召方式会影响转化率",
                    "priority": "high",
                },
                {
                    "name": "开头测试",
                    "hypothesis": "不同开头方式会影响留存率",
                    "priority": "medium",
                },
            ],
        }

    def generate_analytics_summary(self, copies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成多平台内容的分析摘要

        Args:
            copies: 包含多个平台文案结果的列表

        Returns:
            dict: 汇总分析结果
        """
        if not copies:
            return {
                "total_platforms": 0,
                "avg_quality_score": 0.0,
                "platform_scores": {},
                "common_violations": [],
                "recommendations": [],
            }

        total_score = 0.0
        score_count = 0
        platform_scores = {}
        all_violations = []

        for copy in copies:
            platform = copy.get("platform", "unknown")
            review = copy.get("review", {})
            content = copy.get("content", "")

            # 收集分数
            if review and "quality_score" in review:
                score = review["quality_score"]
                platform_scores[platform] = score
                total_score += score
                score_count += 1

            # 收集违规词
            if review and "violations" in review:
                for v in review["violations"]:
                    all_violations.append({
                        "platform": platform,
                        "word": v.get("word", ""),
                        "severity": v.get("severity", "warning"),
                    })

        # 计算平均分数
        avg_score = total_score / score_count if score_count > 0 else 0.0

        # 找出常见违规词
        violation_counts = {}
        for v in all_violations:
            word = v["word"]
            violation_counts[word] = violation_counts.get(word, 0) + 1

        common_violations = sorted(
            violation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        # 生成建议
        recommendations = []

        if avg_score < 7.0:
            recommendations.append("整体质量分数偏低，建议优化文案内容")
        if common_violations:
            recommendations.append(f"发现 {len(common_violations)} 个常见违规词，需重点关注")
        if len(platform_scores) < 4:
            recommendations.append("建议覆盖更多平台以获得更广泛的受众")

        # 找出分数最低的平台
        if platform_scores:
            lowest_platform = min(platform_scores.items(), key=lambda x: x[1])
            recommendations.append(f"{lowest_platform[0]} 平台分数最低({lowest_platform[1]:.1f})，建议重点优化")

        return {
            "total_platforms": len(copies),
            "avg_quality_score": round(avg_score, 1),
            "platform_scores": {k: round(v, 1) for k, v in platform_scores.items()},
            "common_violations": [
                {"word": w, "count": c} for w, c in common_violations
            ],
            "recommendations": recommendations,
        }

    def extract_seo_keywords(self, content: str, platform: str = "general") -> Dict[str, Any]:
        """
        提取 SEO 关键词

        Args:
            content: 内容文本
            platform: 目标平台

        Returns:
            dict: 包含关键词和建议
        """
        import jieba
        import re

        # 分词
        words = jieba.cut(content)
        words = [w.strip() for w in words if len(w.strip()) >= 2]

        # 停用词
        stop_words = {
            "一个", "这个", "那个", "什么", "怎么", "如何",
            "可以", "就是", "而且", "但是", "所以", "因为",
            "已经", "非常", "特别", "比较", "真的", "其实",
        }
        words = [w for w in words if w not in stop_words and not re.match(r"^\d+$", w)]

        # 词频统计
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        # 提取核心关键词（Top 10）
        core_keywords = [w for w, c in sorted_words[:10]]

        # 提取长尾关键词（2-3个词的组合）
        bigrams = []
        for i in range(len(words) - 1):
            bigram = f"{words[i]}{words[i+1]}"
            if len(bigram) >= 4:
                bigrams.append(bigram)

        # 长尾词频统计
        bigram_freq = {}
        for bg in bigrams:
            bigram_freq[bg] = bigram_freq.get(bg, 0) + 1

        sorted_bigrams = sorted(bigram_freq.items(), key=lambda x: x[1], reverse=True)
        long_tail_keywords = [w for w, c in sorted_bigrams[:5]]

        # 平台特定的关键词建议
        platform_keywords = {
            "xiaohongshu": ["种草", "好物", "分享", "测评", "推荐"],
            "tiktok": ["热门", "技巧", "教程", "揭秘", "推荐"],
            "official": ["解读", "分析", "行业", "趋势", "观点"],
            "friend_circle": ["日常", "分享", "生活"],
        }

        suggested = platform_keywords.get(platform, [])

        return {
            "core_keywords": core_keywords,
            "long_tail_keywords": long_tail_keywords,
            "suggested_keywords": suggested,
            "total_unique_words": len(word_freq),
            "keyword_density": round(len(words) / len(content) * 100, 2) if content else 0,
        }

    def compare_contents(self, content1: str, content2: str) -> Dict[str, Any]:
        """
        对比两个内容的差异

        Returns:
            dict: 包含对比分析结果
        """
        analysis1 = self.analyze_structure(content1)
        analysis2 = self.analyze_structure(content2)

        violations1 = self.check_ad_words(content1)
        violations2 = self.check_ad_words(content2)

        review1 = self.review_quality(content1)
        review2 = self.review_quality(content2)

        # 长度对比
        len_diff = len(content2) - len(content1)
        len_diff_pct = round((len_diff / len(content1) * 100), 1) if content1 else 0

        # 结构对比
        structure_diff = {
            "emoji": analysis1["has_emoji"] != analysis2["has_emoji"],
            "numbers": analysis1["has_numbers"] != analysis2["has_numbers"],
            "hashtags": analysis1["has_hashtags"] != analysis2["has_hashtags"],
            "paragraphs": analysis1["paragraph_count"] != analysis2["paragraph_count"],
        }

        # 质量对比
        quality_diff = review2.quality_score - review1.quality_score

        # 违规词对比
        violations_diff = len(violations2) - len(violations1)

        # 建议
        suggestions = []

        if len_diff_pct > 30:
            suggestions.append(f"内容2比内容1长 {len_diff_pct}%，可能需要精简")
        elif len_diff_pct < -30:
            suggestions.append(f"内容2比内容1短 {abs(len_diff_pct)}%，可能需要补充")

        if quality_diff > 1:
            suggestions.append("内容2质量分数更高（+{:.1f}）".format(quality_diff))
        elif quality_diff < -1:
            suggestions.append("内容1质量分数更高（+{:.1f}）".format(abs(quality_diff)))

        if violations_diff > 0:
            suggestions.append(f"内容2有 {violations_diff} 个额外违规词")
        elif violations_diff < 0:
            suggestions.append(f"内容1有 {abs(violations_diff)} 个额外违规词")

        return {
            "length": {
                "content1": len(content1),
                "content2": len(content2),
                "difference": len_diff,
                "difference_percent": len_diff_pct,
            },
            "quality": {
                "content1": review1.quality_score,
                "content2": review2.quality_score,
                "difference": quality_diff,
            },
            "violations": {
                "content1": len(violations1),
                "content2": len(violations2),
                "difference": violations_diff,
            },
            "structure_differences": {k: v for k, v in structure_diff.items() if v},
            "suggestions": suggestions,
        }

    def generate_improvement_suggestions(self, content: str, platform: str) -> Dict[str, Any]:
        """
        生成内容改进建议

        基于内容分析和平台特性提供具体改进方案

        Returns:
            dict: 包含改进建议
        """
        analysis = self.analyze_structure(content)
        violations = self.check_ad_words(content)
        review = self.review_quality(content)

        suggestions = {
            "overall": [],
            "title": [],
            "content": [],
            "structure": [],
            "seo": [],
        }

        # 总体建议
        if review.quality_score < 7:
            suggestions["overall"].append("内容质量偏低，建议全面优化")
        elif review.quality_score >= 8:
            suggestions["overall"].append("内容质量良好，可以发布")

        # 违规词处理
        if violations:
            error_violations = [v for v in violations if v.severity == "error"]
            warning_violations = [v for v in violations if v.severity == "warning"]
            if error_violations:
                suggestions["content"].append(f"需要修改 {len(error_violations)} 个严重违规词")
            if warning_violations:
                suggestions["content"].append(f"建议修改 {len(warning_violations)} 个警告词汇")

        # 标题建议
        title_patterns = {
            "xiaohongshu": ["感叹句", "疑问句", "数字+惊叹"],
            "tiktok": ["简短有力", "悬念", "热点结合"],
            "official": ["专业正式", "数字化", "价值承诺"],
            "friend_circle": ["生活化", "真实感", "轻松语气"],
        }

        suggestions["title"] = title_patterns.get(platform, [])

        # 内容结构建议
        if analysis["paragraph_count"] < 3:
            suggestions["structure"].append("建议增加段落，分点叙述")
        if not analysis["has_emoji"]:
            suggestions["structure"].append("建议添加表情符号增强可读性")
        if not analysis["has_numbers"]:
            suggestions["structure"].append("建议添加具体数据增强说服力")

        # SEO建议
        word_count = len(content)
        if word_count < 300:
            suggestions["seo"].append("内容偏短，建议补充到300字以上以提升SEO效果")
        if not analysis["has_hashtags"]:
            suggestions["seo"].append("建议添加3-5个相关话题标签")

        # 平台特定建议
        platform_specific = {
            "xiaohongshu": [
                "开头3行要吸引眼球，制造悬念",
                "多使用emoji和符号增加视觉吸引力",
                "结尾引导互动（评论、收藏、关注）",
            ],
            "tiktok": [
                "文案要简短，适合视频口播",
                "开头3秒要有爆点",
                "口语化表达，避免书面语",
            ],
            "official": [
                "标题要专业且有吸引力",
                "内容要有深度和价值",
                "排版要清晰美观",
            ],
            "friend_circle": [
                "语气要自然，像朋友聊天",
                "避免过度营销感",
                "配图要真实生活化",
            ],
        }

        suggestions["platform_specific"] = platform_specific.get(platform, [])

        return {
            "current_score": review.quality_score,
            "suggestions": suggestions,
            "priority_fixes": [v.word for v in violations[:3]] if violations else [],
        }

    def suggest_content_angles(self, product_info: Dict[str, Any], platform: str) -> List[Dict[str, Any]]:
        """
        建议内容角度

        基于产品信息生成多种内容创作角度

        Returns:
            list: 多个内容角度建议
        """
        product_name = product_info.get("name", "")
        description = product_info.get("description", "")
        selling_points = product_info.get("selling_points", [])

        angles = []

        # 痛点解决角度
        angles.append({
            "type": "pain_point",
            "title": "解决痛点型",
            "description": "从目标用户的困扰出发，讲述产品如何解决问题",
            "template": "你是否也为[痛点]烦恼？用了[产品]后，终于找到了解决方案！",
            "tone": "共鸣型",
        })

        # 种草分享角度
        angles.append({
            "type": "sharing",
            "title": "好物分享型",
            "description": "真实分享使用体验，推荐给有需要的人",
            "template": "今天要跟大家分享一款我最近超爱的东西——[产品]！",
            "tone": "亲切型",
        })

        # 测评对比角度
        angles.append({
            "type": "review",
            "title": "测评对比型",
            "description": "客观测评，展示产品优缺点",
            "template": "深度测评[产品]，从[维度1]到[维度2]全面解析",
            "tone": "专业型",
        })

        # 教程指南角度
        angles.append({
            "type": "tutorial",
            "title": "教程指南型",
            "description": "教你如何使用产品，解决什么问题",
            "template": "如何用[产品]实现[效果]？跟着这篇教程做就对了！",
            "tone": "实用型",
        })

        # 热点结合角度
        angles.append({
            "type": "trending",
            "title": "热点结合型",
            "description": "结合当下热点话题，提升曝光",
            "template": "最近全网都在讨论[热点]，[产品]竟然也能派上用场！",
            "tone": "时效型",
        })

        # 限时优惠角度
        angles.append({
            "type": "promotion",
            "title": "优惠促销型",
            "description": "强调性价比和限时优惠，刺激购买",
            "template": "姐妹们！[产品]限时特价，错过就没了！",
            "tone": "紧迫型",
        })

        return angles

    def batch_review_contents(self, contents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        批量审核内容

        一次性审核多条内容

        Returns:
            list: 审核结果列表
        """
        results = []
        for item in contents:
            content = item.get("content", "")
            platform = item.get("platform", "xiaohongshu")
            review = self.review_quality(content)
            violations = self.check_ad_words(content)
            analysis = self.analyze_structure(content)

            results.append({
                "content": content[:50] + "..." if len(content) > 50 else content,
                "platform": platform,
                "passed": review.passed,
                "quality_score": review.quality_score,
                "violation_count": len(violations),
                "structure": analysis,
                "needs_improvement": not review.passed or review.quality_score < 7,
            })

        return results


if __name__ == "__main__":
    reviewer = Reviewer()
    test_copy = "这是最好的产品，绝对让你满意！用了都说好，销量第一！"
    result = reviewer.review_quality(test_copy)

    print(f"Passed: {result.passed}")
    print(f"Score: {result.quality_score}")
    print(f"Violations: {[(v.word, v.severity, v.category) for v in result.violations]}")
    print(f"Suggestions: {result.suggestions}")
    print(f"Analysis: {result.analysis}")
