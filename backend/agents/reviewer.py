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
}

# 展平为列表
ALL_VIOLATION_WORDS = [word for words in AD_VIOLATION_WORDS.values() for word in words]


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
        for word in ALL_VIOLATION_WORDS:
            # 使用正则匹配，考虑标点符号分隔
            pattern = rf'(?<![\u4e00-\u9fa5])({re.escape(word)})(?![\u4e00-\u9fa5])'
            for match in re.finditer(pattern, copy):
                # 确定违规分类
                category = ""
                for cat, words in AD_VIOLATION_WORDS.items():
                    if word in words:
                        category = cat
                        break

                # 确定严重程度
                severity = "error" if category in ["最高级", "绝对化", "虚假夸大"] else "warning"

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

    def batch_review(self, copies: List[str]) -> List[ReviewResult]:
        """批量审核文案"""
        return [self.review_quality(copy) for copy in copies]


if __name__ == "__main__":
    reviewer = Reviewer()
    test_copy = "这是最好的产品，绝对让你满意！用了都说好，销量第一！"
    result = reviewer.review_quality(test_copy)

    print(f"Passed: {result.passed}")
    print(f"Score: {result.quality_score}")
    print(f"Violations: {[(v.word, v.severity, v.category) for v in result.violations]}")
    print(f"Suggestions: {result.suggestions}")
    print(f"Analysis: {result.analysis}")
