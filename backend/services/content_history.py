"""
Vox Content History Service 模块

内容历史记录服务
- 存储和检索生成的内容历史
- 支持搜索和筛选
- 管理内容草稿
"""

import json
import os
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from loguru import logger


@dataclass
class ContentRecord:
    """内容记录"""
    id: str
    platform: str
    title: str
    content: str
    tags: List[str]
    created_at: str
    updated_at: str
    is_draft: bool = False
    product_name: str = ""
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "platform": self.platform,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_draft": self.is_draft,
            "product_name": self.product_name,
            "metadata": self.metadata or {},
        }


class ContentHistoryService:
    """
    内容历史记录服务

    功能：
    - 保存生成的内容
    - 搜索历史内容
    - 管理草稿
    """

    def __init__(self):
        self.data_dir = Path("output/history")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.records_file = self.data_dir / "content_history.json"
        self._records: List[ContentRecord] = []
        self._load_records()

    def _load_records(self):
        """加载历史记录"""
        if self.records_file.exists():
            try:
                with open(self.records_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._records = [ContentRecord(**item) for item in data]
            except Exception as e:
                logger.warning(f"Failed to load history: {e}")
                self._records = []
        logger.info(f"Loaded {len(self._records)} history records")

    def _save_records(self):
        """保存历史记录"""
        try:
            with open(self.records_file, "w", encoding="utf-8") as f:
                data = [r.to_dict() for r in self._records]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def add_record(
        self,
        platform: str,
        title: str,
        content: str,
        tags: List[str],
        product_name: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        is_draft: bool = False,
    ) -> str:
        """
        添加新记录

        Args:
            platform: 平台
            title: 标题
            content: 内容
            tags: 标签
            product_name: 产品名称
            metadata: 元数据
            is_draft: 是否为草稿

        Returns:
            str: 记录ID
        """
        record_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()

        record = ContentRecord(
            id=record_id,
            platform=platform,
            title=title,
            content=content,
            tags=tags,
            created_at=now,
            updated_at=now,
            is_draft=is_draft,
            product_name=product_name,
            metadata=metadata or {},
        )

        self._records.insert(0, record)  # 新记录插入到最前面
        self._save_records()
        logger.info(f"Added history record: {record_id}")
        return record_id

    def get_record(self, record_id: str) -> Optional[ContentRecord]:
        """获取单条记录"""
        for record in self._records:
            if record.id == record_id:
                return record
        return None

    def search_records(
        self,
        keyword: str = "",
        platform: str = "",
        is_draft: Optional[bool] = None,
        limit: int = 20,
    ) -> List[ContentRecord]:
        """
        搜索历史记录

        Args:
            keyword: 关键词（搜索标题和内容）
            platform: 平台筛选
            is_draft: 草稿筛选
            limit: 返回数量

        Returns:
            List[ContentRecord]: 匹配的记录
        """
        results = self._records

        # 关键词筛选
        if keyword:
            keyword_lower = keyword.lower()
            results = [
                r for r in results
                if keyword_lower in r.title.lower() or keyword_lower in r.content.lower()
            ]

        # 平台筛选
        if platform:
            results = [r for r in results if r.platform == platform]

        # 草稿筛选
        if is_draft is not None:
            results = [r for r in results if r.is_draft == is_draft]

        return results[:limit]

    def update_record(
        self,
        record_id: str,
        title: str = None,
        content: str = None,
        tags: List[str] = None,
        is_draft: bool = None,
    ) -> bool:
        """
        更新记录

        Returns:
            bool: 是否成功
        """
        for record in self._records:
            if record.id == record_id:
                if title is not None:
                    record.title = title
                if content is not None:
                    record.content = content
                if tags is not None:
                    record.tags = tags
                if is_draft is not None:
                    record.is_draft = is_draft
                record.updated_at = datetime.now().isoformat()
                self._save_records()
                logger.info(f"Updated history record: {record_id}")
                return True
        return False

    def delete_record(self, record_id: str) -> bool:
        """删除记录"""
        for i, record in enumerate(self._records):
            if record.id == record_id:
                del self._records[i]
                self._save_records()
                logger.info(f"Deleted history record: {record_id}")
                return True
        return False

    def get_all_platforms(self) -> List[str]:
        """获取所有使用过的平台"""
        platforms = set()
        for record in self._records:
            if record.platform:
                platforms.add(record.platform)
        return sorted(list(platforms))

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self._records)
        drafts = len([r for r in self._records if r.is_draft])
        platforms = self.get_all_platforms()

        return {
            "total": total,
            "drafts": drafts,
            "published": total - drafts,
            "platforms": platforms,
        }


# 全局实例
content_history_service = ContentHistoryService()


if __name__ == "__main__":
    service = ContentHistoryService()

    # 添加测试记录
    record_id = service.add_record(
        platform="xiaohongshu",
        title="测试标题",
        content="这是测试内容",
        tags=["测试", "示例"],
        product_name="测试产品",
    )
    print(f"Added record: {record_id}")

    # 搜索
    results = service.search_records(keyword="测试")
    print(f"Found {len(results)} records")

    # 统计
    stats = service.get_stats()
    print(f"Stats: {stats}")