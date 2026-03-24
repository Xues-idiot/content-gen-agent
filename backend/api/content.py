"""
Vox Content API

提供内容生成的 REST API 接口
支持 CORS、请求验证和错误处理
"""

from typing import List, Optional
from dataclasses import asdict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator, Body
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.logging_config import get_logger
from backend.constants import VERSION
from backend.agents.planner import ProductInfo

logger = get_logger("api")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Vox Content API starting up...")
    yield
    logger.info("Vox Content API shutting down...")


app = FastAPI(
    title="Vox Content API",
    version=VERSION,
    description="多平台营销内容生成 API",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "请求过于频繁，请稍后再试",
            "detail": str(exc),
        }
    )


# Request/Response Models
class ProductInput(BaseModel):
    """产品输入"""
    name: str = Field(..., min_length=1, max_length=100, description="产品名称")
    description: str = Field(..., min_length=1, max_length=2000, description="产品描述")
    selling_points: List[str] = Field(default_factory=list, max_length=20, description="卖点列表")
    target_users: List[str] = Field(default_factory=list, max_length=20, description="目标用户")
    category: str = Field(default="", max_length=50, description="产品类别")
    price_range: str = Field(default="", max_length=50, description="价格区间")

    @field_validator("selling_points", "target_users", mode="before")
    @classmethod
    def split_string_to_list(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v


class ContentRequest(BaseModel):
    """内容生成请求"""
    product: ProductInput
    platforms: List[str] = Field(
        default=["xiaohongshu"],
        description="目标平台列表"
    )
    enable_research: bool = Field(
        default=True,
        description="是否启用市场调研（获取趋势和竞品分析）"
    )

    @field_validator("platforms")
    @classmethod
    def validate_platforms(cls, v):
        valid_platforms = {"xiaohongshu", "tiktok", "official", "friend_circle"}
        for platform in v:
            if platform not in valid_platforms:
                raise ValueError(f"Invalid platform: {platform}")
        return v


class ViolationModel(BaseModel):
    """违规词模型"""
    word: str
    position: int
    suggestion: str
    severity: str


class ReviewResultModel(BaseModel):
    """审核结果模型"""
    passed: bool
    violations: List[ViolationModel]
    quality_score: float
    suggestions: List[str]


class CopyResultModel(BaseModel):
    """文案结果模型"""
    platform: str
    title: str = ""
    content: str = ""
    script: str = ""
    tags: List[str] = Field(default_factory=list)
    image_suggestions: List[str] = Field(default_factory=list)
    cta: str = Field(default="", description="行动号召/Call-to-Action")
    review: Optional[ReviewResultModel] = None
    success: bool = True
    error: str = ""


class ContentResponse(BaseModel):
    """内容生成响应"""
    success: bool
    platform_results: List[CopyResultModel]
    errors: List[str] = []
    market_insights: List[str] = Field(default_factory=list, description="市场洞察")
    trend_topics: List[str] = Field(default_factory=list, description="趋势话题")
    competitor_content: List[dict] = Field(default_factory=list, description="竞品内容")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    api_key_configured: bool
    tavily_api_configured: bool = False


class PlatformsResponse(BaseModel):
    """平台列表响应"""
    platforms: List[dict]


class CategoriesResponse(BaseModel):
    """类别列表响应"""
    categories: List[dict]


class StatsResponse(BaseModel):
    """统计信息响应"""
    total_requests: int
    total_platforms: int
    supported_platforms: List[str]


class RegenerateRequest(BaseModel):
    """重新生成请求"""
    product: ProductInput
    platform: str = Field(..., description="目标平台")
    enable_research: bool = Field(default=False, description="是否启用市场调研")


# Initialize agents (延迟初始化避免循环导入)
_planner: Optional["ContentPlanner"] = None
_copywriter: Optional["Copywriter"] = None
_reviewer: Optional["Reviewer"] = None
_request_count: int = 0


def get_planner() -> "ContentPlanner":
    global _planner
    if _planner is None:
        from backend.agents.planner import ContentPlanner
        _planner = ContentPlanner()
    return _planner


def get_copywriter() -> "Copywriter":
    global _copywriter
    if _copywriter is None:
        from backend.agents.copywriter import Copywriter
        _copywriter = Copywriter()
    return _copywriter


def get_reviewer() -> "Reviewer":
    global _reviewer
    if _reviewer is None:
        from backend.agents.reviewer import Reviewer
        _reviewer = Reviewer()
    return _reviewer


@app.get("/", response_model=dict)
async def root():
    """根路径"""
    return {
        "name": "Vox Content API",
        "version": VERSION,
        "description": "多平台营销内容生成 API",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """健康检查"""
    from backend.services.llm import llm_client
    from backend.config import config

    return HealthResponse(
        status="healthy",
        version=VERSION,
        api_key_configured=llm_client.validate_config(),
        tavily_api_configured=bool(config.tavily_api_key),
    )


@app.get("/api/v1/platforms", response_model=PlatformsResponse)
async def get_platforms():
    """获取支持的平台列表"""
    return PlatformsResponse(
        platforms=[
            {
                "id": "xiaohongshu",
                "name": "小红书",
                "description": "种草笔记",
                "icon": "📕",
            },
            {
                "id": "tiktok",
                "name": "抖音",
                "description": "短视频口播",
                "icon": "📺",
            },
            {
                "id": "official",
                "name": "公众号",
                "description": "长文",
                "icon": "📰",
            },
            {
                "id": "friend_circle",
                "name": "朋友圈",
                "description": "简短分享",
                "icon": "👥",
            },
        ]
    )


@app.get("/api/v1/categories", response_model=CategoriesResponse)
async def get_categories():
    """获取产品类别列表"""
    return CategoriesResponse(
        categories=[
            {"id": "beauty", "name": "美妆", "icon": "💄"},
            {"id": "digital", "name": "数码", "icon": "📱"},
            {"id": "food", "name": "食品", "icon": "🍜"},
            {"id": "home", "name": "家居", "icon": "🏠"},
            {"id": "fashion", "name": "服装", "icon": "👗"},
            {"id": "health", "name": "健康", "icon": "💊"},
            {"id": "education", "name": "教育", "icon": "📚"},
            {"id": "travel", "name": "旅游", "icon": "✈️"},
            {"id": "other", "name": "其他", "icon": "📦"},
        ]
    )


@app.post("/api/v1/content/generate", response_model=ContentResponse)
@limiter.limit("10/minute")  # 每分钟10次请求
async def generate_content(request: Request, body: ContentRequest):
    """
    生成多平台内容

    支持平台：
    - xiaohongshu: 小红书种草笔记
    - tiktok: 抖音短视频口播脚本
    - official: 公众号长文
    - friend_circle: 朋友圈简短分享
    """
    global _request_count
    _request_count += 1

    try:
        planner = get_planner()
        copywriter = get_copywriter()
        reviewer = get_reviewer()

        # 创建产品对象
        product_obj = ProductInfo(
            name=body.product.name,
            description=body.product.description,
            selling_points=body.product.selling_points,
            target_users=body.product.target_users,
            category=body.product.category,
            price_range=body.product.price_range,
        )

        # 规划内容（包含市场调研）
        plan = planner.plan_content(
            product_obj,
            body.platforms,
            enable_research=body.enable_research,
        )

        # 生成文案
        copy_results = copywriter.generate_all(product_obj, plan)

        # 构建响应
        platform_results = []
        errors = []

        for platform, result in copy_results.items():
            platform_key = str(platform)

            # 审核文案
            review_result = None
            if result.content:
                review = reviewer.review_quality(result.content)
                review_result = ReviewResultModel(
                    passed=review.passed,
                    violations=[ViolationModel(**asdict(v)) for v in review.violations],
                    quality_score=review.quality_score,
                    suggestions=review.suggestions,
                )

            platform_results.append(CopyResultModel(
                platform=platform_key,
                title=result.title,
                content=result.content,
                script=result.script,
                tags=result.tags,
                image_suggestions=result.image_suggestions,
                cta=result.cta,
                review=review_result,
                success=result.success,
                error=result.error,
            ))

            if not result.success:
                errors.append(f"{platform_key}: {result.error}")

        return ContentResponse(
            success=len(errors) == 0,
            platform_results=platform_results,
            errors=errors,
            market_insights=plan.market_insights,
            trend_topics=plan.trend_topics,
            competitor_content=[
                {"name": c.get("name", ""), "title": c.get("title", ""), "url": c.get("url", "")}
                for c in plan.competitor_content
            ] if plan.competitor_content else [],
        )

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "参数验证错误",
                "detail": str(e),
                "type": "validation"
            }
        )
    except TimeoutError as e:
        logger.error(f"Generation timeout: {e}")
        raise HTTPException(
            status_code=504,
            detail={
                "error": "生成超时，请稍后重试",
                "detail": str(e),
                "type": "timeout"
            }
        )
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "服务暂时不可用，请稍后重试",
                "detail": str(e),
                "type": "connection"
            }
        )
    except Exception as e:
        logger.error(f"Generate content error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "内容生成失败，请稍后重试",
                "detail": str(e),
                "type": "internal"
            }
        )


@app.post("/api/v1/content/review")
async def review_content(content: str = Body(..., embed=True)):
    """
    审核单条文案

    检测广告法违规词并计算质量评分
    """
    try:
        reviewer = get_reviewer()
        result = reviewer.review_quality(content)
        return {
            "passed": result.passed,
            "violations": [asdict(v) for v in result.violations],
            "quality_score": result.quality_score,
            "suggestions": result.suggestions,
            "analysis": result.analysis,
        }
    except Exception as e:
        logger.error(f"Review content error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats", response_model=StatsResponse)
async def get_stats():
    """获取 API 统计信息"""
    return StatsResponse(
        total_requests=_request_count,
        total_platforms=4,
        supported_platforms=["xiaohongshu", "tiktok", "official", "friend_circle"],
    )


@app.post("/api/v1/content/regenerate")
async def regenerate_content(body: RegenerateRequest):
    """
    重新生成单个平台的内容

    比 generate 更轻量，只生成指定平台的内容
    """
    global _request_count
    _request_count += 1

    try:
        planner = get_planner()
        copywriter = get_copywriter()
        reviewer = get_reviewer()

        # 验证平台
        valid_platforms = {"xiaohongshu", "tiktok", "official", "friend_circle"}
        if body.platform not in valid_platforms:
            raise ValueError(f"Invalid platform: {body.platform}")

        # 创建产品对象
        product_obj = ProductInfo(
            name=body.product.name,
            description=body.product.description,
            selling_points=body.product.selling_points,
            target_users=body.product.target_users,
            category=body.product.category,
            price_range=body.product.price_range,
        )

        # 规划内容
        plan = planner.plan_content(
            product_obj,
            [body.platform],
            enable_research=body.enable_research,
        )

        # 生成单个平台的文案
        from backend.agents.copywriter import Platform as CopyPlatform
        result = copywriter.regenerate(
            product_obj,
            plan,
            CopyPlatform(body.platform)
        )

        # 审核文案
        review_result = None
        if result.content:
            review = reviewer.review_quality(result.content)
            review_result = ReviewResultModel(
                passed=review.passed,
                violations=[ViolationModel(**asdict(v)) for v in review.violations],
                quality_score=review.quality_score,
                suggestions=review.suggestions,
            )

        return {
            "success": result.success,
            "platform": body.platform,
            "result": CopyResultModel(
                platform=body.platform,
                title=result.title,
                content=result.content,
                script=result.script,
                tags=result.tags,
                image_suggestions=result.image_suggestions,
                cta=result.cta,
                review=review_result,
                success=result.success,
                error=result.error,
            ),
            "error": result.error if not result.success else None,
        }

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Regenerate content error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/suggestions/{platform}")
async def get_platform_suggestions(platform: str, content: str):
    """
    获取指定平台的优化建议

    根据内容特点和目标平台返回个性化优化建议
    """
    try:
        reviewer = get_reviewer()
        suggestions = reviewer.suggest_platform_optimization(content, platform)
        return {
            "platform": platform,
            "suggestions": suggestions,
        }
    except Exception as e:
        logger.error(f"Get platform suggestions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
