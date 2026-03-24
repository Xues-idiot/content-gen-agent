"""
Vox Web Search 模块测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from backend.tools.web_search import WebSearchTool, SearchResult, SearchResponse


class TestWebSearchTool:
    """WebSearchTool 测试"""

    def test_search_result_creation(self):
        """测试搜索结果创建"""
        result = SearchResult(
            title="测试标题",
            url="https://example.com",
            content="测试内容",
            score=0.95,
        )

        assert result.title == "测试标题"
        assert result.url == "https://example.com"
        assert result.content == "测试内容"
        assert result.score == 0.95

    def test_search_response_creation(self):
        """测试搜索响应创建"""
        result = SearchResult(
            title="测试",
            url="https://test.com",
            content="内容",
            score=0.9,
        )
        response = SearchResponse(
            success=True,
            results=[result],
            query="测试查询",
        )

        assert response.success is True
        assert len(response.results) == 1
        assert response.query == "测试查询"
        assert response.error is None

    def test_search_response_failure(self):
        """测试搜索失败响应"""
        response = SearchResponse(
            success=False,
            results=[],
            query="测试",
            error="Network error",
        )

        assert response.success is False
        assert len(response.results) == 0
        assert response.error == "Network error"

    def test_web_search_tool_init(self):
        """测试工具初始化"""
        tool = WebSearchTool(api_key="test-key")
        assert tool.api_key == "test-key"
        assert tool.base_url == "https://api.tavily.com/search"
        assert tool.timeout == 30.0


class TestSearchResult:
    """SearchResult 测试"""

    def test_with_published_date(self):
        """测试带发布日期的结果"""
        result = SearchResult(
            title="新闻标题",
            url="https://news.com",
            content="新闻内容",
            score=0.88,
            published_date="2024-01-15",
        )

        assert result.published_date == "2024-01-15"

    def test_without_published_date(self):
        """测试不带发布日期的结果"""
        result = SearchResult(
            title="无日期",
            url="https://test.com",
            content="内容",
            score=0.5,
        )

        assert result.published_date is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
