"""
Vox Web Search 模块 - Tavily API 集成

用于市场调研、内容灵感获取、竞品分析
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import httpx
from loguru import logger

from backend.config import config


@dataclass
class SearchResult:
    """搜索结果"""
    title: str
    url: str
    content: str
    score: float
    published_date: Optional[str] = None


@dataclass
class SearchResponse:
    """搜索响应"""
    success: bool
    results: List[SearchResult]
    query: str
    error: Optional[str] = None


class WebSearchTool:
    """
    Web Search 工具 - 基于 Tavily API

    功能：
    - 关键词搜索
    - 内容灵感获取
    - 竞品分析素材收集
    - 趋势研究
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.tavily_api_key
        self.base_url = "https://api.tavily.com/search"
        self.timeout = 30.0

    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "medium",
    ) -> SearchResponse:
        """
        执行搜索

        Args:
            query: 搜索关键词
            max_results: 最大结果数
            search_depth: 搜索深度 (basic/medium/deep)

        Returns:
            SearchResponse: 搜索响应
        """
        if not self.api_key:
            logger.error("TAVILY_API_KEY is not set")
            return SearchResponse(
                success=False,
                results=[],
                query=query,
                error="API key not configured"
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_answer": True,
            "include_raw_content": False,
            "include_images": False,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("results", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        content=item.get("content", ""),
                        score=item.get("score", 0.0),
                        published_date=item.get("published_date"),
                    ))

                logger.info(f"Search completed for query: {query}, found {len(results)} results")
                return SearchResponse(
                    success=True,
                    results=results,
                    query=query,
                )

        except httpx.TimeoutException:
            logger.error(f"Search timeout for query: {query}")
            return SearchResponse(
                success=False,
                results=[],
                query=query,
                error="Search timeout"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Search HTTP error: {e.response.status_code}")
            return SearchResponse(
                success=False,
                results=[],
                query=query,
                error=f"HTTP error: {e.response.status_code}"
            )
        except Exception as e:
            logger.error(f"Search error: {e}")
            return SearchResponse(
                success=False,
                results=[],
                query=query,
                error=str(e)
            )

    def search_for_content_inspiration(
        self,
        product_name: str,
        category: str,
        platform: str,
        max_results: int = 3,
    ) -> SearchResponse:
        """
        搜索内容灵感

        Args:
            product_name: 产品名称
            category: 产品类别
            platform: 目标平台
            max_results: 最大结果数

        Returns:
            SearchResponse: 搜索响应
        """
        # 构建适合平台的搜索查询
        platform_keywords = {
            "xiaohongshu": "小红书 热门笔记 种草",
            "tiktok": "抖音 热门视频 带货",
            "official": "公众号 热门文章 营销",
            "friend_circle": "朋友圈 营销案例",
        }

        keyword = platform_keywords.get(platform, "")
        query = f"{category} {product_name} {keyword} 2024 2025"

        return self.search(query, max_results=max_results, search_depth="medium")

    def search_for_trends(
        self,
        category: str,
        max_results: int = 5,
    ) -> SearchResponse:
        """
        搜索行业趋势

        Args:
            category: 产品类别
            max_results: 最大结果数

        Returns:
            SearchResponse: 搜索响应
        """
        query = f"{category} 行业趋势 热点 2024 2025 营销"

        return self.search(query, max_results=max_results, search_depth="deep")

    def search_for_comp分析(
        self,
        competitor_name: str,
        max_results: int = 5,
    ) -> SearchResponse:
        """
        搜索竞品分析

        Args:
            competitor_name: 竞品名称
            max_results: 最大结果数

        Returns:
            SearchResponse: 搜索响应
        """
        query = f"{competitor_name} 营销策略 内容运营 社交媒体"

        return self.search(query, max_results=max_results, search_depth="medium")


# 全局 WebSearchTool 实例
web_search_tool = WebSearchTool()


if __name__ == "__main__":
    # 测试
    tool = WebSearchTool()

    if not tool.api_key:
        print("Warning: TAVILY_API_KEY is not configured")

    # 测试搜索
    result = tool.search("人工智能 营销 内容生成", max_results=3)
    print(f"Success: {result.success}")
    print(f"Query: {result.query}")
    print(f"Results: {len(result.results)}")
    for r in result.results:
        print(f"  - {r.title}: {r.url}")