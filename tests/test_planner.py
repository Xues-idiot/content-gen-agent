"""
Vox Planner 模块测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.planner import ContentPlanner, ProductInfo, ContentPlan


class TestContentPlanner:
    """Planner 测试"""

    def test_plan_content_basic(self):
        """测试基本内容规划"""
        planner = ContentPlanner()

        product = ProductInfo(
            name="智能睡眠枕",
            description="AI智能枕头",
            selling_points=["改善睡眠", "AI监测", "个性化调节"],
            target_users=["加班族", "失眠人群"],
            category="家居",
        )

        plan = planner.plan_content(product, ["xiaohongshu", "tiktok"])

        assert isinstance(plan, ContentPlan)
        assert plan.product == product
        assert plan.content_direction != ""
        assert len(plan.key_themes) > 0
        assert plan.tone_of_voice != ""

    def test_plan_content_with_platforms(self):
        """测试多平台规划"""
        planner = ContentPlanner()

        product = ProductInfo(
            name="测试产品",
            description="测试描述",
            selling_points=["卖点1", "卖点2"],
            target_users=["用户1"],
        )

        platforms = ["xiaohongshu", "tiktok", "official", "friend_circle"]
        plan = planner.plan_content(product, platforms)

        assert len(plan.recommended_platforms) == len(platforms)

    def test_analyze_target_user(self):
        """测试目标用户分析"""
        planner = ContentPlanner()

        product = ProductInfo(
            name="测试产品",
            description="测试描述",
            selling_points=["改善效率", "节省时间"],
            target_users=["上班族", "学生"],
        )

        users = planner.analyze_target_user(product)

        assert len(users) > 0
        assert users[0].occupation in ["上班族", "学生"]

    def test_recommend_platforms(self):
        """测试平台推荐"""
        planner = ContentPlanner()

        product = ProductInfo(
            name="测试",
            description="测试",
            selling_points=[],
            target_users=[],
        )

        platforms = planner._recommend_platforms(product, ["xiaohongshu"])
        assert "xiaohongshu" in platforms

        platforms = planner._recommend_platforms(product, [])
        assert len(platforms) > 0  # 至少返回默认平台


class TestProductInfo:
    """ProductInfo 测试"""

    def test_product_info_creation(self):
        """测试产品信息创建"""
        product = ProductInfo(
            name="测试产品",
            description="这是一个测试产品",
            selling_points=["卖点1", "卖点2", "卖点3"],
            target_users=["用户A", "用户B"],
            category="科技",
            price_range="100-200元",
        )

        assert product.name == "测试产品"
        assert product.description == "这是一个测试产品"
        assert len(product.selling_points) == 3
        assert len(product.target_users) == 2


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
