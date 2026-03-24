"""
Vox API 模块测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestContentRequest:
    """ContentRequest 模型测试"""

    def test_product_input_validation(self):
        """测试产品输入验证"""
        from backend.api.content import ProductInput

        # 有效输入
        product = ProductInput(
            name="测试产品",
            description="这是测试描述",
            selling_points=["卖点1", "卖点2"],
            target_users=["用户1", "用户2"],
            category="科技",
            price_range="100-200元",
        )

        assert product.name == "测试产品"
        assert len(product.selling_points) == 2

    def test_product_input_string_conversion(self):
        """测试字符串转列表"""
        from backend.api.content import ProductInput

        product = ProductInput(
            name="测试产品",
            description="描述",
            selling_points="卖点1, 卖点2, 卖点3",  # 字符串而非列表
            target_users="用户1, 用户2",
        )

        assert isinstance(product.selling_points, list)
        assert len(product.selling_points) == 3

    def test_content_request_platform_validation(self):
        """测试平台验证"""
        from backend.api.content import ContentRequest, ProductInput
        from pydantic import ValidationError

        # 有效平台
        request = ContentRequest(
            product=ProductInput(
                name="测试",
                description="描述",
                selling_points=[],
                target_users=[],
            ),
            platforms=["xiaohongshu", "tiktok"],
        )
        assert len(request.platforms) == 2

    def test_content_request_invalid_platform(self):
        """测试无效平台"""
        from backend.api.content import ContentRequest, ProductInput
        from pydantic import ValidationError

        try:
            ContentRequest(
                product=ProductInput(
                    name="测试",
                    description="描述",
                    selling_points=[],
                    target_users=[],
                ),
                platforms=["invalid_platform"],
            )
            assert False, "Should have raised ValidationError"
        except ValidationError:
            pass


class TestCopyResultModel:
    """CopyResultModel 测试"""

    def test_copy_result_model_creation(self):
        """测试 CopyResultModel 创建"""
        from backend.api.content import CopyResultModel

        result = CopyResultModel(
            platform="xiaohongshu",
            title="测试标题",
            content="测试内容",
            script="",
            tags=["标签1", "标签2"],
            image_suggestions=["图片建议1"],
            success=True,
            error="",
        )

        assert result.platform == "xiaohongshu"
        assert result.title == "测试标题"
        assert len(result.tags) == 2

    def test_copy_result_model_defaults(self):
        """测试默认值"""
        from backend.api.content import CopyResultModel

        result = CopyResultModel(
            platform="xiaohongshu",
            title="标题",
            content="内容",
            tags=[],
            image_suggestions=[],
        )

        assert result.script == ""
        assert result.success == True
        assert result.error == ""


class TestHealthEndpoint:
    """健康检查端点测试"""

    def test_health_response(self):
        """测试健康响应"""
        from backend.api.content import HealthResponse

        response = HealthResponse(
            status="healthy",
            version="0.1.0",
            api_key_configured=False,
        )

        assert response.status == "healthy"
        assert response.version == "0.1.0"
        assert response.api_key_configured == False


class TestPlatformsEndpoint:
    """平台列表端点测试"""

    def test_platforms_response(self):
        """测试平台响应"""
        from backend.api.content import PlatformsResponse

        response = PlatformsResponse(
            platforms=[
                {"id": "xiaohongshu", "name": "小红书", "description": "种草笔记"},
            ]
        )

        assert len(response.platforms) == 1
        assert response.platforms[0]["id"] == "xiaohongshu"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
