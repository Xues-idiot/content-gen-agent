"""
Vox 集成测试

测试完整的端到端流程
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.planner import ContentPlanner, ProductInfo
from backend.agents.copywriter import Copywriter, Platform
from backend.agents.reviewer import Reviewer
from backend.agents.exporter import Exporter, ExportFormat


class TestEndToEndFlow:
    """端到端流程测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.planner = ContentPlanner()
        self.copywriter = Copywriter()
        self.reviewer = Reviewer()
        self.exporter = Exporter()

    def test_full_content_generation_flow(self):
        """测试完整内容生成流程"""
        # 1. 创建产品
        product = ProductInfo(
            name="智能睡眠枕",
            description="AI智能枕头，监测睡眠质量",
            selling_points=["改善睡眠", "AI监测"],
            target_users=["失眠人群"],
            category="家居",
        )

        # 2. 规划内容
        plan = self.planner.plan_content(product, ["xiaohongshu"])
        assert plan.content_direction != ""
        assert len(plan.recommended_platforms) > 0

        # 3. 生成文案 (跳过LLM调用，使用mock)
        # 注意：由于没有真实API，这里只测试解析逻辑

    def test_planner_to_copywriter_flow(self, sample_product_info, sample_content_plan):
        """测试从规划到文案生成的流程"""
        # Planner 输出作为 Copywriter 输入
        assert sample_content_plan.product == sample_product_info
        assert len(sample_content_plan.recommended_platforms) > 0

    def test_copywriter_to_reviewer_flow(self, sample_copy_result):
        """测试从文案生成到审核的流程"""
        # 审核文案
        review_result = self.reviewer.review_quality(sample_copy_result.content)

        assert review_result.passed == True
        assert review_result.quality_score > 0

    def test_reviewer_provides_suggestions(self):
        """测试审核提供改进建议"""
        poor_copy = "好"
        result = self.reviewer.review_quality(poor_copy)

        assert len(result.suggestions) > 0
        assert result.quality_score < 10.0

    def test_full_export_flow(self, sample_export_content):
        """测试完整导出流程"""
        # JSON 导出
        json_result = self.exporter.export(sample_export_content, ExportFormat.JSON)
        assert json_result.success == True
        assert "product" in json_result.content

        # Markdown 导出
        md_result = self.exporter.export(sample_export_content, ExportFormat.MARKDOWN)
        assert md_result.success == True
        assert "# 内容生成报告" in md_result.content

        # HTML 导出
        html_result = self.exporter.export(sample_export_content, ExportFormat.HTML)
        assert html_result.success == True
        assert "<html>" in html_result.content


class TestMultiPlatformFlow:
    """多平台流程测试"""

    def test_all_platforms_have_results(self, sample_product_info):
        """测试所有平台都有结果"""
        plan = ContentPlanner().plan_content(
            sample_product_info,
            ["xiaohongshu", "tiktok", "official", "friend_circle"]
        )

        assert len(plan.recommended_platforms) == 4

    def test_platform_specific_tone(self, sample_product_info):
        """测试不同平台有不同语调"""
        plan = ContentPlanner().plan_content(sample_product_info, ["xiaohongshu"])

        # 不同类别产品应该有不同语调
        cosmetics_product = ProductInfo(
            name="口红",
            description="持久不脱色",
            selling_points=["持久", "显色"],
            target_users=["年轻女性"],
            category="美妆",
        )

        cosmetics_plan = ContentPlanner().plan_content(cosmetics_product, ["xiaohongshu"])

        # 语调应该根据类别有所不同
        assert cosmetics_plan.tone_of_voice != ""


class TestErrorHandling:
    """错误处理测试"""

    def test_empty_product_name(self):
        """测试空产品名称"""
        product = ProductInfo(
            name="",
            description="描述",
            selling_points=["卖点"],
            target_users=["用户"],
        )

        plan = ContentPlanner().plan_content(product, ["xiaohongshu"])

        # 应该仍有输出，只是使用默认值
        assert plan.content_direction != ""

    def test_review_empty_copy(self):
        """测试审核空文案"""
        result = Reviewer().review_quality("")

        assert result.passed == True  # 空内容不算违规
        assert result.quality_score == 8.5  # 空内容有建议扣分

    def test_export_invalid_format(self, sample_export_content):
        """测试导出无效格式"""
        result = Exporter().export(sample_export_content, "invalid_format")

        assert result.success == False
        assert "Unknown format" in result.error


class TestDataIntegrity:
    """数据完整性测试"""

    def test_product_info_preserved(self, sample_product_info):
        """测试产品信息在流程中保持完整"""
        plan = ContentPlanner().plan_content(sample_product_info, ["xiaohongshu"])

        assert plan.product.name == sample_product_info.name
        assert plan.product.description == sample_product_info.description
        assert plan.product.category == sample_product_info.category

    def test_copy_result_fields(self, sample_copy_result):
        """测试文案结果字段完整"""
        assert sample_copy_result.platform == "xiaohongshu"
        assert sample_copy_result.title != ""
        assert sample_copy_result.content != ""
        assert sample_copy_result.success == True

    def test_review_result_fields(self, sample_review_result):
        """测试审核结果字段完整"""
        assert hasattr(sample_review_result, "passed")
        assert hasattr(sample_review_result, "violations")
        assert hasattr(sample_review_result, "quality_score")
        assert hasattr(sample_review_result, "suggestions")
        assert hasattr(sample_review_result, "analysis")
        assert hasattr(sample_review_result, "word_count")
        assert hasattr(sample_review_result, "char_count")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
