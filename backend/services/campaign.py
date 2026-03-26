"""
Vox Campaign 模块 - 营销活动管理

管理多平台、多内容的营销活动
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class CampaignStatus(Enum):
    """活动状态"""
    DRAFT = "draft"
    PLANNING = "planning"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignType(Enum):
    """活动类型"""
    PRODUCT_LAUNCH = "product_launch"
    SEASONAL = "seasonal"
    FESTIVAL = "festival"
    FLASH_SALE = "flash_sale"
    BRAND = "brand"
    COLLABORATION = "collaboration"


@dataclass
class CampaignContent:
    """活动内容项"""
    id: str
    platform: str
    title: str
    content: str
    scheduled_time: Optional[str] = None
    status: str = "draft"
    published_time: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Campaign:
    """营销活动"""
    id: str
    name: str
    description: str
    campaign_type: str
    status: str = "draft"
    contents: List[CampaignContent] = field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    tags: List[str] = field(default_factory=list)
    notes: str = ""


class CampaignManager:
    """
    营销活动管理器

    功能：
    - 创建和管理营销活动
    - 多平台内容协调
    - 活动时间线管理
    - 活动效果追踪
    """

    def __init__(self):
        self._campaigns: Dict[str, Campaign] = {}
        self._content_store: Dict[str, List[CampaignContent]] = {}

    def create_campaign(
        self,
        name: str,
        description: str,
        campaign_type: str = "product_launch",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Campaign:
        """
        创建营销活动

        Args:
            name: 活动名称
            description: 活动描述
            campaign_type: 活动类型
            start_date: 开始日期
            end_date: 结束日期
            tags: 标签

        Returns:
            Campaign: 创建的活动
        """
        campaign_id = f"camp_{uuid.uuid4().hex[:8]}"

        campaign = Campaign(
            id=campaign_id,
            name=name,
            description=description,
            campaign_type=campaign_type,
            start_date=start_date,
            end_date=end_date,
            tags=tags or [],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        self._campaigns[campaign_id] = campaign
        self._content_store[campaign_id] = []

        return campaign

    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """获取活动详情"""
        return self._campaigns.get(campaign_id)

    def update_campaign(
        self,
        campaign_id: str,
        **kwargs,
    ) -> Optional[Campaign]:
        """
        更新活动信息

        Args:
            campaign_id: 活动ID
            **kwargs: 要更新的字段

        Returns:
            Campaign: 更新后的活动
        """
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return None

        for key, value in kwargs.items():
            if hasattr(campaign, key):
                setattr(campaign, key, value)

        campaign.updated_at = datetime.now().isoformat()
        return campaign

    def add_content_to_campaign(
        self,
        campaign_id: str,
        platform: str,
        title: str,
        content: str,
        scheduled_time: Optional[str] = None,
    ) -> Optional[CampaignContent]:
        """
        向活动添加内容

        Args:
            campaign_id: 活动ID
            platform: 平台
            title: 内容标题
            content: 内容正文
            scheduled_time: 计划发布时间

        Returns:
            CampaignContent: 添加的内容项
        """
        if campaign_id not in self._campaigns:
            return None

        content_id = f"content_{uuid.uuid4().hex[:8]}"

        campaign_content = CampaignContent(
            id=content_id,
            platform=platform,
            title=title,
            content=content,
            scheduled_time=scheduled_time,
        )

        self._content_store[campaign_id].append(campaign_content)
        return campaign_content

    def get_campaign_contents(self, campaign_id: str) -> List[CampaignContent]:
        """获取活动的所有内容"""
        return self._content_store.get(campaign_id, [])

    def update_content_status(
        self,
        campaign_id: str,
        content_id: str,
        status: str,
    ) -> bool:
        """
        更新内容状态

        Args:
            campaign_id: 活动ID
            content_id: 内容ID
            status: 新状态

        Returns:
            bool: 是否成功
        """
        contents = self._content_store.get(campaign_id, [])
        for content in contents:
            if content.id == content_id:
                content.status = status
                if status == "published":
                    content.published_time = datetime.now().isoformat()
                return True
        return False

    def set_campaign_status(self, campaign_id: str, status: str) -> bool:
        """
        设置活动状态

        Args:
            campaign_id: 活动ID
            status: 新状态

        Returns:
            bool: 是否成功
        """
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return False

        campaign.status = status
        campaign.updated_at = datetime.now().isoformat()
        return True

    def get_campaigns(
        self,
        status: Optional[str] = None,
        campaign_type: Optional[str] = None,
    ) -> List[Campaign]:
        """
        获取活动列表

        Args:
            status: 按状态过滤
            campaign_type: 按类型过滤

        Returns:
            list: 活动列表
        """
        campaigns = list(self._campaigns.values())

        if status:
            campaigns = [c for c in campaigns if c.status == status]

        if campaign_type:
            campaigns = [c for c in campaigns if c.campaign_type == campaign_type]

        return sorted(campaigns, key=lambda x: x.created_at, reverse=True)

    def get_campaign_timeline(self, campaign_id: str) -> Dict[str, Any]:
        """
        获取活动时间线

        Args:
            campaign_id: 活动ID

        Returns:
            dict: 时间线信息
        """
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return {}

        contents = self._content_store.get(campaign_id, [])

        return {
            "campaign": {
                "id": campaign.id,
                "name": campaign.name,
                "start_date": campaign.start_date,
                "end_date": campaign.end_date,
            },
            "milestones": [
                {
                    "type": "created",
                    "date": campaign.created_at,
                    "description": "活动创建",
                },
                {
                    "type": "contents_scheduled",
                    "date": campaign.start_date,
                    "description": f"{len(contents)}个内容已排期",
                },
                {
                    "type": "completed",
                    "date": campaign.end_date,
                    "description": "活动结束",
                },
            ],
            "contents": [
                {
                    "id": c.id,
                    "platform": c.platform,
                    "title": c.title,
                    "scheduled_time": c.scheduled_time,
                    "status": c.status,
                }
                for c in sorted(contents, key=lambda x: x.scheduled_time or "")
            ],
        }

    def get_campaign_summary(self, campaign_id: str) -> Dict[str, Any]:
        """
        获取活动摘要

        Args:
            campaign_id: 活动ID

        Returns:
            dict: 活动摘要统计
        """
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return {}

        contents = self._content_store.get(campaign_id, [])

        # 平台分布
        platform_counts = {}
        for content in contents:
            platform_counts[content.platform] = platform_counts.get(content.platform, 0) + 1

        # 状态分布
        status_counts = {}
        for content in contents:
            status_counts[content.status] = status_counts.get(content.status, 0) + 1

        return {
            "campaign_id": campaign_id,
            "name": campaign.name,
            "status": campaign.status,
            "total_contents": len(contents),
            "by_platform": platform_counts,
            "by_status": status_counts,
            "start_date": campaign.start_date,
            "end_date": campaign.end_date,
            "duration_days": self._calculate_duration(campaign.start_date, campaign.end_date),
        }

    def _calculate_duration(self, start: Optional[str], end: Optional[str]) -> int:
        """计算活动持续天数"""
        if not start or not end:
            return 0

        try:
            start_date = datetime.fromisoformat(start)
            end_date = datetime.fromisoformat(end)
            return (end_date - start_date).days
        except (ValueError, TypeError):
            return 0

    def delete_campaign(self, campaign_id: str) -> bool:
        """
        删除活动

        Args:
            campaign_id: 活动ID

        Returns:
            bool: 是否成功
        """
        if campaign_id in self._campaigns:
            del self._campaigns[campaign_id]
        if campaign_id in self._content_store:
            del self._content_store[campaign_id]
        return True


# 全局活动管理器
campaign_manager = CampaignManager()


if __name__ == "__main__":
    # 测试
    manager = CampaignManager()

    # 创建活动
    campaign = manager.create_campaign(
        name="618大促活动",
        description="618电商节营销活动",
        campaign_type="flash_sale",
        start_date="2025-06-01",
        end_date="2025-06-20",
        tags=["电商", "促销", "618"],
    )
    print(f"Created campaign: {campaign.id}")

    # 添加内容
    content = manager.add_content_to_campaign(
        campaign.id,
        platform="xiaohongshu",
        title="618必买清单",
        content="今年618这些好物绝对不能错过...",
        scheduled_time="2025-06-01 10:00",
    )
    print(f"Added content: {content.id}")

    # 获取摘要
    summary = manager.get_campaign_summary(campaign.id)
    print(f"Summary: {summary}")