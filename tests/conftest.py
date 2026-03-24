"""
Vox 测试配置和 Fixtures
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_product_info():
    """示例产品信息"""
    from backend.agents.planner import ProductInfo

    return ProductInfo(
        name="智能睡眠枕",
        description="一款基于AI技术的智能枕头，能够监测睡眠质量并自动调节硬度和高度",
        selling_points=["改善睡眠质量", "AI智能监测", "个性化调节", "静音设计"],
        target_users=["加班族", "失眠人群", "白领"],
        category="家居",
        price_range="500-800元",
    )


@pytest.fixture
def sample_content_plan(sample_product_info):
    """示例内容规划"""
    from backend.agents.planner import ContentPlanner

    planner = ContentPlanner()
    return planner.plan_content(sample_product_info, ["xiaohongshu", "tiktok"])


@pytest.fixture
def sample_copy_result():
    """示例文案结果"""
    from backend.agents.copywriter import CopyResult

    return CopyResult(
        platform="xiaohongshu",
        title="睡眠质量差的救星！这款AI枕头让我每天精神满满",
        content="""
        最近工作压力太大，每天睡眠质量都很差。

        朋友推荐了这款智能睡眠枕，用了一周真的改善明显！

        最让我惊喜的是AI监测功能，能实时监测我的睡眠状态，自动调节最适合我的硬度和高度。

        现在每天起床都精神满满，推荐给所有睡眠不好的朋友们！

        #智能家居 #睡眠好物 #AI科技
        """,
        tags=["#智能家居", "#睡眠好物", "#AI科技"],
        image_suggestions=["卧室场景图", "枕头特写", "睡眠数据截图"],
        success=True,
        error="",
    )


@pytest.fixture
def sample_review_result():
    """示例审核结果"""
    from backend.agents.reviewer import ReviewResult, Violation

    return ReviewResult(
        passed=True,
        violations=[],
        quality_score=8.5,
        suggestions=["建议添加更多具体数据"],
        analysis={"has_emoji": False, "has_numbers": False, "has_hashtags": True},
        word_count=150,
        char_count=300,
    )


@pytest.fixture
def sample_export_content(sample_product_info, sample_copy_result):
    """示例导出内容"""
    return {
        "product": {
            "name": sample_product_info.name,
            "description": sample_product_info.description,
            "selling_points": sample_product_info.selling_points,
            "category": sample_product_info.category,
        },
        "copies": {
            "xiaohongshu": {
                "copy": {
                    "title": sample_copy_result.title,
                    "content": sample_copy_result.content,
                    "tags": sample_copy_result.tags,
                },
                "review": {
                    "passed": True,
                    "quality_score": 8.5,
                },
            }
        },
    }


@pytest.fixture
def api_client():
    """API 测试客户端"""
    from fastapi.testclient import TestClient
    from backend.api.content import app

    return TestClient(app)


@pytest.fixture
def invalid_product_input():
    """无效的产品输入"""
    return {
        "name": "",  # 名称为空，应该验证失败
        "description": "描述",
        "selling_points": [],
        "target_users": [],
    }
