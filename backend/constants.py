"""
Vox 常量模块

定义项目级常量
"""

from enum import Enum


# API 配置
class APIConfig:
    """API 配置常量"""
    HOST = "0.0.0.0"
    PORT = 8003
    DEBUG = False
    API_PREFIX = "/api/v1"
    CORS_ORIGINS = ["*"]  # 生产环境应限制具体域名


# 前端配置
class FrontendConfig:
    """前端配置常量"""
    HOST = "0.0.0.0"
    PORT = 3666
    API_URL = "http://localhost:8003"


# 平台配置
class PlatformEnum(str, Enum):
    """平台枚举"""
    XIAOHONGSHU = "xiaohongshu"
    TIKTOK = "tiktok"
    OFFICIAL = "official"
    FRIEND_CIRCLE = "friend_circle"

    @classmethod
    def values(cls):
        return [p.value for p in cls]

    @classmethod
    def display_names(cls):
        return {
            cls.XIAOHONGSHU.value: "小红书",
            cls.TIKTOK.value: "抖音",
            cls.OFFICIAL.value: "公众号",
            cls.FRIEND_CIRCLE.value: "朋友圈",
        }


# 导出格式
class ExportFormatEnum(str, Enum):
    """导出格式枚举"""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    TEXT = "text"

    @classmethod
    def values(cls):
        return [f.value for f in cls]


# 工作流状态
class WorkflowStatus(str, Enum):
    """工作流状态"""
    IDLE = "idle"
    PLANNING = "planning"
    WRITING = "writing"
    REVIEWING = "reviewing"
    GENERATING_IMAGES = "generating_images"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"


# 审核配置
class ReviewConfig:
    """审核配置"""
    MIN_COPY_LENGTH = 10
    MAX_COPY_LENGTH = 10000
    MIN_QUALITY_SCORE = 0.0
    MAX_QUALITY_SCORE = 10.0
    VIOLATION_PENALTY_ERROR = 2.0
    VIOLATION_PENALTY_WARNING = 0.5


# 产品类别
class ProductCategory(str, Enum):
    """产品类别"""
    BEAUTY = "美妆"
    DIGITAL = "数码"
    FOOD = "食品"
    HOME = "家居"
    FASHION = "服装"
    HEALTH = "健康"
    EDUCATION = "教育"
    TRAVEL = "旅游"
    OTHER = "其他"

    @classmethod
    def values(cls):
        return [c.value for c in cls]


# 配色方案
class ColorScheme:
    """Vox 配色方案"""
    PRIMARY = "#FF6B35"  # 活力橙
    PRIMARY_HOVER = "#E55A2B"
    SECONDARY = "#FF8C61"  # 珊瑚橙
    ACCENT = "#FFD93D"  # 明黄
    BACKGROUND = "#FFF8F0"  # 暖白
    BACKGROUND_DARK = "#FFF0E5"

    TEXT_PRIMARY = "#1F2937"
    TEXT_SECONDARY = "#6B7280"
    TEXT_MUTED = "#9CA3AF"

    SUCCESS = "#10B981"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"
    INFO = "#3B82F6"


# 版本信息
VERSION = "0.1.0"
APP_NAME = "Vox"
APP_DESCRIPTION = "内容生成 Agent"
