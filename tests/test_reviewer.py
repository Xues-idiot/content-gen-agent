"""
Vox Reviewer 模块测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.reviewer import Reviewer, Violation, ReviewResult, AD_VIOLATION_WORDS, ALL_VIOLATION_WORDS


class TestReviewer:
    """Reviewer 测试"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.reviewer = Reviewer()

    def test_check_ad_words_no_violation(self):
        """测试无违规词"""
        copy = "这是一个很好的产品，值得推荐。"
        violations = self.reviewer.check_ad_words(copy)

        assert len(violations) == 0

    def test_check_ad_words_with_violation(self):
        """测试有违规词"""
        copy = "这是最好的产品，绝对让你满意！"
        violations = self.reviewer.check_ad_words(copy)

        assert len(violations) >= 2
        assert any(v.word == "最好" for v in violations)
        assert any(v.word == "绝对" for v in violations)

    def test_check_ad_words_position(self):
        """测试违规词位置"""
        copy = "这是最好的产品"
        violations = self.reviewer.check_ad_words(copy)

        assert len(violations) >= 1
        best_violations = [v for v in violations if v.word == "最好"]
        assert len(best_violations) == 1
        assert best_violations[0].position == 2  # "最好" starts at index 2

    def test_check_ad_words_severity(self):
        """测试违规严重程度"""
        # 测试最高级词汇 - 应该是 error
        copy = "全球最好，第一选择"
        violations = self.reviewer.check_ad_words(copy)

        error_violations = [v for v in violations if v.severity == "error"]
        assert len(error_violations) > 0

    def test_check_ad_words_category(self):
        """测试违规分类"""
        copy = "这是最好的产品"
        violations = self.reviewer.check_ad_words(copy)

        if violations:
            assert violations[0].category != ""

    def test_review_quality_pass(self):
        """测试质量审核通过"""
        copy = "这个产品用了一段时间，效果很好。推荐给大家。"
        result = self.reviewer.review_quality(copy)

        assert result.passed == True
        assert result.quality_score > 0
        assert result.char_count > 0
        assert result.word_count > 0

    def test_review_quality_fail(self):
        """测试质量审核不通过"""
        copy = "这是最好的、第一的产品！绝对不能错过！"
        result = self.reviewer.review_quality(copy)

        assert result.passed == False
        assert len(result.violations) > 0

    def test_review_quality_score(self):
        """测试质量评分"""
        copy = "好"
        result = self.reviewer.review_quality(copy)

        # 太短的文案应该扣分
        assert result.quality_score < 10.0

    def test_review_quality_score_full(self):
        """测试完整文案评分"""
        copy = """
        这款智能睡眠枕真的很棒！用了两个月了，睡眠质量明显改善。

        特点：
        1. AI智能监测睡眠
        2. 个性化调节硬度
        3. 改善睡眠质量

        推荐给失眠人群和加班族！
        """
        result = self.reviewer.review_quality(copy)

        assert result.quality_score > 5.0
        assert result.passed == True

    def test_suggestions_generated(self):
        """测试建议生成"""
        copy = "好"  # 太短且没有标点
        result = self.reviewer.review_quality(copy)

        assert len(result.suggestions) > 0

    def test_analyze_structure(self):
        """测试结构分析"""
        copy = """
        这是一款很好的产品！😀

        特点：
        1. 功能强大
        2. 使用方便

        #产品推荐
        """
        analysis = self.reviewer.analyze_structure(copy)

        assert "has_emoji" in analysis
        assert "has_numbers" in analysis
        assert "has_hashtags" in analysis
        assert "paragraph_count" in analysis
        assert analysis["has_emoji"] == True
        assert analysis["has_numbers"] == True
        assert analysis["has_hashtags"] == True

    def test_batch_review(self):
        """测试批量审核"""
        copies = [
            "这是一个好产品",
            "这是最好的产品",
            "普通文案测试"
        ]
        results = self.reviewer.batch_review(copies)

        assert len(results) == 3
        assert results[0].passed == True
        assert results[1].passed == False

    def test_get_suggestion(self):
        """测试替换建议"""
        assert self.reviewer._get_suggestion("最好") == "优秀"
        assert self.reviewer._get_suggestion("第一") == "领先"
        assert self.reviewer._get_suggestion("未知词") == "请修改为更客观的表述"


class TestViolationWords:
    """违规词列表测试"""

    def test_all_violation_words_not_empty(self):
        """验证展平后的违规词列表不为空"""
        assert len(ALL_VIOLATION_WORDS) > 0

    def test_violation_words_categories(self):
        """验证违规词分类"""
        assert "最高级" in AD_VIOLATION_WORDS
        assert "绝对化" in AD_VIOLATION_WORDS
        assert "虚假夸大" in AD_VIOLATION_WORDS

    def test_common_violations_present(self):
        """验证常见违规词存在"""
        common_violations = ["最好", "第一", "最佳", "最优", "绝对"]
        for word in common_violations:
            assert word in ALL_VIOLATION_WORDS

    def test_violation_words_structure(self):
        """验证违规词结构"""
        for category, words in AD_VIOLATION_WORDS.items():
            assert isinstance(category, str)
            assert isinstance(words, list)
            assert len(words) > 0


class TestViolation:
    """Violation 数据类测试"""

    def test_violation_creation(self):
        """测试 Violation 创建"""
        violation = Violation(
            word="最好",
            position=5,
            suggestion="优秀",
            severity="error",
            category="最高级"
        )

        assert violation.word == "最好"
        assert violation.position == 5
        assert violation.suggestion == "优秀"
        assert violation.severity == "error"
        assert violation.category == "最高级"


class TestReviewResult:
    """ReviewResult 数据类测试"""

    def test_review_result_defaults(self):
        """测试默认值"""
        result = ReviewResult()

        assert result.passed == True
        assert result.violations == []
        assert result.quality_score == 0.0
        assert result.suggestions == []
        assert result.analysis == {}

    def test_review_result_with_data(self):
        """测试带数据的 ReviewResult"""
        result = ReviewResult(
            passed=False,
            violations=[],
            quality_score=7.5,
            suggestions=["建议1", "建议2"],
            analysis={"has_emoji": True},
            word_count=100,
            char_count=200,
        )

        assert result.passed == False
        assert result.quality_score == 7.5
        assert len(result.suggestions) == 2
        assert result.word_count == 100
        assert result.char_count == 200


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
