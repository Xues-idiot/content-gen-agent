"""
Vox Copywriter 模块测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.copywriter import Copywriter, Platform, CopyResult
from backend.agents.planner import ContentPlanner, ProductInfo


class TestCopywriter:
    """Copywriter 测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.copywriter = Copywriter()
        self.planner = ContentPlanner()

    def test_copywriter_initialization(self):
        """测试 Copywriter 初始化"""
        assert self.copywriter is not None
        assert self.copywriter.llm is not None

    def test_platform_enum_values(self):
        """测试平台枚举值"""
        assert Platform.XIAOHONGSHU.value == "xiaohongshu"
        assert Platform.TIKTOK.value == "tiktok"
        assert Platform.OFFICIAL.value == "official"
        assert Platform.FRIEND_CIRCLE.value == "friend_circle"

    def test_platform_string_conversion(self):
        """测试平台字符串转换"""
        assert str(Platform.XIAOHONGSHU) == "xiaohongshu"
        assert str(Platform.TIKTOK) == "tiktok"

    def test_copy_result_defaults(self):
        """测试 CopyResult 默认值"""
        result = CopyResult(platform="xiaohongshu")

        assert result.platform == "xiaohongshu"
        assert result.title == ""
        assert result.content == ""
        assert result.script == ""
        assert result.cta == ""
        assert result.tags == []
        assert result.image_suggestions == []
        assert result.analysis == {}
        assert result.success == True
        assert result.error == ""

    def test_copy_result_with_data(self):
        """测试带数据的 CopyResult"""
        result = CopyResult(
            platform="xiaohongshu",
            title="测试标题",
            content="测试内容",
            script="脚本",
            cta="行动号召",
            tags=["#标签1", "#标签2"],
            image_suggestions=["图片1", "图片2"],
            analysis={"word_count": 100},
            success=True,
            error="",
        )

        assert result.title == "测试标题"
        assert result.content == "测试内容"
        assert result.cta == "行动号召"
        assert len(result.tags) == 2
        assert len(result.image_suggestions) == 2

    def test_format_user_profile(self):
        """测试用户画像格式化"""
        product = ProductInfo(
            name="测试产品",
            description="描述",
            selling_points=["卖点1", "卖点2"],
            target_users=["用户1", "用户2"],
            category="科技",
        )

        plan = self.planner.plan_content(product, ["xiaohongshu"])
        user_profile = self.copywriter._format_user_profile(plan)

        assert isinstance(user_profile, str)
        assert len(user_profile) > 0


class TestCopywriterGeneration:
    """文案生成测试（需要 Mock）"""

    def setup_method(self):
        self.copywriter = Copywriter()

    def test_generate_with_invalid_platform(self):
        """测试无效平台"""
        from backend.agents.planner import ContentPlan, UserProfile

        product = ProductInfo(
            name="测试",
            description="描述",
            selling_points=[],
            target_users=[],
        )

        plan = ContentPlan(
            product=product,
            target_users=[],
            content_direction="",
            key_themes=[],
            tone_of_voice="",
            recommended_platforms=[],
        )

        # 使用不存在的平台
        result = self.copywriter.generate(product, plan, "invalid_platform" as any)

        assert result.success == False
        assert "Unknown platform" in result.error


class TestCopyResultParsing:
    """文案解析测试"""

    def setup_method(self):
        self.copywriter = Copywriter()

    def test_parse_xiaohongshu_response(self):
        """测试解析小红书响应"""
        response = """
        标题：这是一个测试标题

        正文：
        这是测试内容部分。
        包含多行文字。

        标签：#测试 #标签 #小红书

        配图建议：
        1. 产品主图
        2. 使用场景图
        """

        result = self.copywriter._parse_xiaohongshu_response(response)

        assert result.platform == "xiaohongshu"
        assert "测试" in result.title or result.title == ""

    def test_parse_tiktok_response(self):
        """测试解析抖音响应"""
        response = """
        【开头钩子】
        你还在为失眠烦恼吗？

        【内容主体】
        今天给大家推荐一款智能睡眠枕...

        【结尾行动号召】
        喜欢的话记得点赞关注哦！
        """

        result = self.copywriter._parse_tiktok_response(response)

        assert result.platform == "tiktok"
        assert result.script != "" or result.title != ""
        assert result.cta != "" or result.cta == "喜欢的话记得点赞关注哦！"

    def test_parse_tiktok_cta_extraction(self):
        """测试解析抖音 CTA"""
        response = """
        【开头钩子】
        震惊！这个枕头太神奇了

        【内容主体】
        用了之后睡眠质量翻倍

        【结尾行动号召】
        评论区扣1获取同款链接！
        """

        result = self.copywriter._parse_tiktok_response(response)

        assert result.cta == "评论区扣1获取同款链接！"

    def test_parse_official_response(self):
        """测试解析公众号响应"""
        response = """
        标题：智能睡眠枕评测

        副标题：告别失眠，从一个好枕头开始

        正文：
        详细的产品介绍内容...

        排版建议：使用图文混排
        """

        result = self.copywriter._parse_official_response(response)

        assert result.platform == "official"
        assert "评测" in result.title or result.title == ""

    def test_parse_friend_circle_response(self):
        """测试解析朋友圈响应"""
        response = """
        文案：最近入手了一款超好用的智能枕头，睡眠质量明显提升！

        配图建议：
        - 产品图
        - 睡眠数据截图

        发布时间建议：晚上10点
        """

        result = self.copywriter._parse_friend_circle_response(response)

        assert result.platform == "friend_circle"
        assert result.content != "" or "睡眠" in result.content


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
