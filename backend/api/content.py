"""
Vox Content API

提供内容生成的 REST API 接口
支持 CORS、请求验证和错误处理
"""

from typing import Dict, List, Optional
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
_exporter: Optional["Exporter"] = None  # type: ignore
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


def get_exporter() -> "Exporter":
    global _exporter
    if _exporter is None:
        from backend.agents.exporter import Exporter
        _exporter = Exporter()
    return _exporter


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


class BatchGenerateRequest(BaseModel):
    """批量生成请求"""
    products: List[ProductInput]
    platforms: List[str] = Field(default=["xiaohongshu"])
    enable_research: bool = Field(default=False)


@app.post("/api/v1/content/batch-generate")
@limiter.limit("5/minute")  # 批量生成更耗资源，限制更严
async def batch_generate_content(request: Request, body: BatchGenerateRequest):
    """
    批量生成多个产品的内容

    一次请求生成多个产品的多平台内容
    """
    global _request_count

    results = []
    errors = []

    for i, product_input in enumerate(body.products):
        _request_count += 1
        try:
            planner = get_planner()
            copywriter = get_copywriter()
            reviewer = get_reviewer()

            product_obj = ProductInfo(
                name=product_input.name,
                description=product_input.description,
                selling_points=product_input.selling_points,
                target_users=product_input.target_users,
                category=product_input.category,
                price_range=product_input.price_range,
            )

            plan = planner.plan_content(
                product_obj,
                body.platforms,
                enable_research=body.enable_research,
            )

            copy_results = copywriter.generate_all(product_obj, plan)

            platform_results = []
            for platform, result in copy_results.items():
                platform_key = str(platform)
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
                    errors.append(f"产品{i+1} {platform_key}: {result.error}")

            results.append({
                "product_index": i,
                "product_name": product_input.name,
                "success": True,
                "platform_results": platform_results,
            })

        except Exception as e:
            logger.error(f"Batch generate error for product {i}: {e}")
            errors.append(f"产品{i+1}: {str(e)}")
            results.append({
                "product_index": i,
                "product_name": product_input.name,
                "success": False,
                "error": str(e),
            })

    return {
        "success": len(errors) == 0,
        "total_products": len(body.products),
        "successful": len([r for r in results if r.get("success")]),
        "failed": len([r for r in results if not r.get("success")]),
        "results": results,
        "errors": errors,
    }


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


@app.post("/api/v1/content/ab-suggestions")
async def get_ab_test_suggestions(body: PerformanceRequest):
    """
    获取 A/B 测试建议

    根据内容特征建议可以测试的变量
    """
    try:
        reviewer = get_reviewer()
        suggestions = reviewer.suggest_ab_tests(body.content, body.platform)
        return suggestions
    except Exception as e:
        logger.error(f"A/B test suggestions error: {e}")
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


@app.get("/api/v1/scheduling/{platform}")
async def get_scheduling_suggestions(platform: str, content_type: str = "general"):
    """
    获取指定平台的发布时段建议

    根据平台特性和内容类型返回最佳发布时段
    """
    try:
        reviewer = get_reviewer()
        scheduling = reviewer.suggest_scheduling(platform, content_type)
        return {
            "platform": platform,
            "content_type": content_type,
            "scheduling": scheduling,
        }
    except Exception as e:
        logger.error(f"Get scheduling suggestions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class AnalyticsRequest(BaseModel):
    """分析请求"""
    copies: List[dict]  # 包含 platform, content, review 的列表


@app.post("/api/v1/content/analytics")
async def get_content_analytics(body: AnalyticsRequest):
    """
    获取多平台内容的分析摘要

    汇总分析多个平台文案的质量分数、违规词等
    """
    try:
        reviewer = get_reviewer()
        summary = reviewer.generate_analytics_summary(body.copies)
        return summary
    except Exception as e:
        logger.error(f"Get content analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ConvertFormatRequest(BaseModel):
    """格式转换请求"""
    content: str
    from_platform: str
    to_platform: str


@app.post("/api/v1/content/convert")
async def convert_content_format(body: ConvertFormatRequest):
    """
    将内容从一种平台格式转换到另一种平台格式

    自动调整内容结构、长度和格式以适应目标平台
    """
    try:
        exporter = get_exporter()
        result = exporter.convert_format(
            content=body.content,
            from_platform=body.from_platform,
            to_platform=body.to_platform,
        )
        return result
    except Exception as e:
        logger.error(f"Convert content format error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class DuplicateCheckRequest(BaseModel):
    """重复检测请求"""
    content: str
    existing_contents: List[str] = Field(default_factory=list)


@app.post("/api/v1/content/check-duplicate")
async def check_content_duplicate(body: DuplicateCheckRequest):
    """
    检测内容是否重复

    检查新内容与已有内容的相似度
    """
    try:
        reviewer = get_reviewer()
        result = reviewer.check_duplicate_in_batch(body.content, body.existing_contents)
        return result
    except Exception as e:
        logger.error(f"Check duplicate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class SeoKeywordsRequest(BaseModel):
    """SEO关键词请求"""
    content: str
    platform: str = "general"


@app.post("/api/v1/seo/keywords")
async def get_seo_keywords(body: SeoKeywordsRequest):
    """
    提取 SEO 关键词

    使用分词和词频统计提取核心关键词和长尾关键词
    """
    try:
        reviewer = get_reviewer()
        keywords = reviewer.extract_seo_keywords(body.content, body.platform)
        return keywords
    except Exception as e:
        logger.error(f"Get SEO keywords error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class CompareRequest(BaseModel):
    """内容对比请求"""
    content1: str
    content2: str


@app.post("/api/v1/content/compare")
async def compare_contents(body: CompareRequest):
    """
    对比两个内容的差异

    比较长度、质量、违规词、结构等方面
    """
    try:
        reviewer = get_reviewer()
        comparison = reviewer.compare_contents(body.content1, body.content2)
        return comparison
    except Exception as e:
        logger.error(f"Compare contents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class HashtagRequest(BaseModel):
    """标签建议请求"""
    content: str
    platform: str = "xiaohongshu"
    max_tags: int = Field(default=5, ge=1, le=10)


@app.post("/api/v1/hashtags/suggest")
async def suggest_hashtags(body: HashtagRequest):
    """
    根据内容推荐话题标签

    使用关键词提取和平台特性生成推荐标签
    """
    try:
        reviewer = get_reviewer()
        tags = reviewer.suggest_hashtags(body.content, body.platform, body.max_tags)
        return {
            "platform": body.platform,
            "hashtags": tags,
        }
    except Exception as e:
        logger.error(f"Suggest hashtags error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class PerformanceRequest(BaseModel):
    """表现预测请求"""
    content: str
    platform: str = "xiaohongshu"


@app.post("/api/v1/content/predict")
async def predict_performance(body: PerformanceRequest):
    """
    预测内容表现

    基于内容特征预测可能的用户互动和传播效果
    """
    try:
        reviewer = get_reviewer()
        prediction = reviewer.predict_performance(body.content, body.platform)
        return prediction
    except Exception as e:
        logger.error(f"Predict performance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class SaveTemplateRequest(BaseModel):
    """保存模板请求"""
    name: str
    platform: str
    content: str
    tags: List[str] = Field(default_factory=list)


@app.post("/api/v1/templates")
async def save_template(body: SaveTemplateRequest):
    """保存内容为模板"""
    try:
        exporter = get_exporter()
        template = exporter.save_as_template(
            name=body.name,
            platform=body.platform,
            content=body.content,
            tags=body.tags,
        )
        return {
            "success": True,
            "template": {
                "id": template.id,
                "name": template.name,
                "platform": template.platform,
                "created_at": template.created_at,
            },
        }
    except Exception as e:
        logger.error(f"Save template error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/templates/{platform}")
async def get_templates(platform: str):
    """获取平台模板列表"""
    try:
        exporter = get_exporter()
        templates = exporter.get_templates(platform)
        return {
            "platform": platform,
            "templates": [
                {
                    "id": t.id,
                    "name": t.name,
                    "content": t.content,
                    "tags": t.tags,
                    "usage_count": t.usage_count,
                    "created_at": t.created_at,
                }
                for t in templates
            ],
        }
    except Exception as e:
        logger.error(f"Get templates error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/templates/{platform}/{template_id}")
async def delete_template(platform: str, template_id: str):
    """删除模板"""
    try:
        exporter = get_exporter()
        success = exporter.delete_template(platform, template_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Delete template error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/trending/{platform}")
async def get_trending_topics(platform: str, category: str = "general"):
    """
    获取热门话题

    搜索平台热门话题和趋势
    """
    try:
        from backend.tools.web_search import web_search_tool
        result = web_search_tool.search_trending_topics(category, platform, max_results=10)
        return {
            "platform": platform,
            "category": category,
            "success": result.success,
            "results": [
                {"title": r.title, "url": r.url, "content": r.content[:200], "score": r.score}
                for r in result.results
            ] if result.success else [],
            "error": result.error,
        }
    except Exception as e:
        logger.error(f"Get trending topics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/hot-keywords")
async def get_hot_keywords(category: str = "general"):
    """
    获取热门关键词

    搜索类别的热门关键词
    """
    try:
        from backend.tools.web_search import web_search_tool
        result = web_search_tool.get_hot_keywords(category, max_results=10)
        return result
    except Exception as e:
        logger.error(f"Get hot keywords error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Content Calendar & Scheduling =====

class ScheduledContent(BaseModel):
    """计划发布的内容"""
    id: str
    product_name: str
    platform: str
    title: str
    content: str
    tags: List[str] = []
    scheduled_time: str
    status: str = "pending"  # pending, published, failed
    created_at: str


class ContentCalendarRequest(BaseModel):
    """内容日历请求"""
    start_date: str
    end_date: str
    platforms: Optional[List[str]] = None


class CalendarResponse(BaseModel):
    """日历响应"""
    success: bool
    scheduled_content: List[ScheduledContent]
    total: int


# In-memory storage for scheduled content (替换为数据库)
_scheduled_content_store: List[ScheduledContent] = []


@app.post("/api/v1/schedule", response_model=CalendarResponse)
async def schedule_content(
    product_name: str,
    platform: str,
    title: str,
    content: str,
    tags: List[str] = [],
    scheduled_time: str = "",
):
    """
    添加计划发布的内容

    将内容添加到发布日历
    """
    try:
        import uuid
        from datetime import datetime

        scheduled = ScheduledContent(
            id=str(uuid.uuid4())[:8],
            product_name=product_name,
            platform=platform,
            title=title,
            content=content,
            tags=tags,
            scheduled_time=scheduled_time or datetime.now().isoformat(),
            status="pending",
            created_at=datetime.now().isoformat(),
        )
        _scheduled_content_store.append(scheduled)

        return CalendarResponse(
            success=True,
            scheduled_content=[scheduled],
            total=len(_scheduled_content_store),
        )
    except Exception as e:
        logger.error(f"Schedule content error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/calendar", response_model=CalendarResponse)
async def get_content_calendar(
    start_date: str = "",
    end_date: str = "",
    platform: Optional[str] = None,
):
    """
    获取内容日历

    获取指定日期范围和平台的内容计划
    """
    try:
        filtered = _scheduled_content_store

        if platform:
            filtered = [c for c in filtered if c.platform == platform]

        return CalendarResponse(
            success=True,
            scheduled_content=filtered,
            total=len(filtered),
        )
    except Exception as e:
        logger.error(f"Get calendar error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/schedule/{schedule_id}")
async def delete_scheduled_content(schedule_id: str):
    """
    删除计划的内容

    从日历中移除计划发布的内容
    """
    try:
        global _scheduled_content_store
        original_count = len(_scheduled_content_store)
        _scheduled_content_store = [
            c for c in _scheduled_content_store if c.id != schedule_id
        ]

        if len(_scheduled_content_store) == original_count:
            raise HTTPException(status_code=404, detail="Schedule not found")

        return {"success": True, "message": "Schedule deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete schedule error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/schedule/{schedule_id}/publish")
async def mark_as_published(schedule_id: str):
    """
    标记内容为已发布

    更新内容状态为 published
    """
    try:
        for content in _scheduled_content_store:
            if content.id == schedule_id:
                content.status = "published"
                return {"success": True, "content": content}

        raise HTTPException(status_code=404, detail="Schedule not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mark published error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Content Version Management =====

class ContentVersion(BaseModel):
    """内容版本"""
    id: str
    content_id: str
    version_number: int
    title: str
    content: str
    platform: str
    created_at: str
    change_summary: str = ""


_content_versions_store: Dict[str, List[ContentVersion]] = {}


@app.post("/api/v1/versions")
async def save_content_version(
    content_id: str,
    version_number: int,
    title: str,
    content: str,
    platform: str,
    change_summary: str = "",
):
    """
    保存内容版本

    创建新的内容版本快照
    """
    try:
        from datetime import datetime
        import uuid

        version = ContentVersion(
            id=str(uuid.uuid4())[:8],
            content_id=content_id,
            version_number=version_number,
            title=title,
            content=content,
            platform=platform,
            created_at=datetime.now().isoformat(),
            change_summary=change_summary,
        )

        if content_id not in _content_versions_store:
            _content_versions_store[content_id] = []

        _content_versions_store[content_id].append(version)

        return {"success": True, "version": version}
    except Exception as e:
        logger.error(f"Save version error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/versions/{content_id}")
async def get_content_versions(content_id: str):
    """
    获取内容版本历史

    获取指定内容的版本列表
    """
    try:
        versions = _content_versions_store.get(content_id, [])
        return {
            "success": True,
            "content_id": content_id,
            "versions": versions,
            "total": len(versions),
        }
    except Exception as e:
        logger.error(f"Get versions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/versions/{content_id}/v/{version_number}")
async def get_specific_version(content_id: str, version_number: int):
    """
    获取特定版本

    获取指定内容ID和版本号的内容
    """
    try:
        versions = _content_versions_store.get(content_id, [])
        for v in versions:
            if v.version_number == version_number:
                return {"success": True, "version": v}

        raise HTTPException(status_code=404, detail="Version not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get specific version error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Platform Best Practices =====

PLATFORM_BEST_PRATICES = {
    "xiaohongshu": {
        "name": "小红书",
        "optimal_length": "300-800字",
        "hashtag_format": "#话题#",
        "emoji_usage": "适中",
        "best_posting_times": ["12:00-13:00", "18:00-20:00", "21:00-22:00"],
        "tips": [
            "标题要吸引人，有悬念感",
            "开头3行要抓眼球",
            "多用emoji增加可读性",
            "添加高质量图片",
            "结尾引导互动（评论、收藏）",
        ],
    },
    "tiktok": {
        "name": "抖音",
        "optimal_length": "15-60秒视频文案",
        "hashtag_format": "#话题",
        "emoji_usage": "少",
        "best_posting_times": ["12:00-14:00", "18:00-20:00", "21:00-23:00"],
        "tips": [
            "开头3秒要抓住注意力",
            "文案要口语化",
            "使用热门音乐",
            "添加字幕",
            "结尾引导关注",
        ],
    },
    "official": {
        "name": "公众号",
        "optimal_length": "800-2000字",
        "hashtag_format": "",
        "emoji_usage": "少",
        "best_posting_times": ["08:00-09:00", "12:00-13:00", "20:00-21:00"],
        "tips": [
            "标题要专业有吸引力",
            "开头要有价值铺垫",
            "段落清晰，排版美观",
            "添加相关图片",
            "结尾引导关注和点在看",
        ],
    },
    "friend_circle": {
        "name": "朋友圈",
        "optimal_length": "50-200字",
        "hashtag_format": "#话题#",
        "emoji_usage": "多",
        "best_posting_times": ["08:00-09:00", "12:00-13:00", "17:30-18:30", "21:00-22:00"],
        "tips": [
            "文案要生活化、真实",
            "配图3-9张最佳",
            "避免过度营销感",
            "使用当地emoji",
            "发布时间要合适",
        ],
    },
}


@app.get("/api/v1/best-practices/{platform}")
async def get_platform_best_practices(platform: str):
    """
    获取平台最佳实践

    获取指定平台的最佳发布时间、内容长度等建议
    """
    if platform not in PLATFORM_BEST_PRATICES:
        raise HTTPException(status_code=404, detail="Platform not found")

    return {
        "success": True,
        "platform": platform,
        "practices": PLATFORM_BEST_PRATICES[platform],
    }


@app.get("/api/v1/best-practices")
async def get_all_best_practices():
    """
    获取所有平台最佳实践

    返回所有平台的最佳实践
    """
    return {
        "success": True,
        "platforms": PLATFORM_BEST_PRATICES,
    }


# ===== Content Analytics =====

@app.post("/api/v1/analytics/record")
async def record_content_analytics(
    platform: str,
    quality_score: float,
    word_count: int,
    char_count: int,
    violation_count: int = 0,
    emoji_count: int = 0,
    hashtag_count: int = 0,
):
    """
    记录内容分析数据

    用于追踪内容质量和表现
    """
    try:
        from backend.services.analytics import content_analytics

        content_data = {
            "platform": platform,
            "quality_score": quality_score,
            "word_count": word_count,
            "char_count": char_count,
            "violation_count": violation_count,
            "emoji_count": emoji_count,
            "hashtag_count": hashtag_count,
        }

        content_id = content_analytics.record_content(content_data)

        return {
            "success": True,
            "content_id": content_id,
            "message": "Content recorded successfully",
        }
    except Exception as e:
        logger.error(f"Record analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/platform")
async def get_analytics_by_platform(platform: Optional[str] = None):
    """
    获取平台分析数据

    获取指定平台或所有平台的统计分析
    """
    try:
        from backend.services.analytics import content_analytics

        result = content_analytics.get_platform_analytics(platform)
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"Get platform analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/trends")
async def get_quality_trends(days: int = 7):
    """
    获取质量趋势

    获取最近N天的内容质量趋势
    """
    try:
        from backend.services.analytics import content_analytics

        trends = content_analytics.get_quality_trends(days)
        return {
            "success": True,
            "trends": [
                {
                    "date": t.date,
                    "avg_score": t.avg_score,
                    "content_count": t.content_count,
                    "violation_rate": t.violation_rate,
                }
                for t in trends
            ],
        }
    except Exception as e:
        logger.error(f"Get quality trends error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/compare")
async def compare_platform_analytics():
    """
    对比平台表现

    对比各平台的内容质量和其他指标
    """
    try:
        from backend.services.analytics import content_analytics

        result = content_analytics.compare_platforms()
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"Compare platforms error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/health/{content_id}")
async def get_content_health(content_id: str):
    """
    获取内容健康分

    获取指定内容的健康评分和改进建议
    """
    try:
        from backend.services.analytics import content_analytics

        result = content_analytics.get_content_health_score(content_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return {"success": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get content health error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Content Improvement & Inspiration =====

@app.post("/api/v1/content/improve")
async def get_improvement_suggestions(
    content: str = Body(..., embed=True),
    platform: str = Body("xiaohongshu", embed=True),
):
    """
    获取内容改进建议

    基于内容分析提供具体改进方案
    """
    try:
        reviewer = get_reviewer()
        suggestions = reviewer.generate_improvement_suggestions(content, platform)
        return {"success": True, **suggestions}
    except Exception as e:
        logger.error(f"Get improvement suggestions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/content/angles")
async def suggest_content_angles(
    product_name: str = Body(..., embed=True),
    description: str = Body("", embed=True),
    selling_points: str = Body("", embed=True),
    platform: str = Body("xiaohongshu", embed=True),
):
    """
    建议内容角度

    基于产品信息生成多种内容创作角度
    """
    try:
        reviewer = get_reviewer()
        product_info = {
            "name": product_name,
            "description": description,
            "selling_points": [s.strip() for s in selling_points.split(",") if s.strip()] if selling_points else [],
        }
        angles = reviewer.suggest_content_angles(product_info, platform)
        return {"success": True, "angles": angles}
    except Exception as e:
        logger.error(f"Suggest content angles error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/content/batch-review")
async def batch_review_contents(
    contents: List[Dict[str, str]] = Body(..., description="内容列表，每项包含content和platform"),
):
    """
    批量审核内容

    一次性审核多条内容
    """
    try:
        reviewer = get_reviewer()
        results = reviewer.batch_review_contents(contents)
        return {
            "success": True,
            "results": results,
            "total": len(results),
            "passed": len([r for r in results if r.get("passed", False)]),
            "needs_improvement": len([r for r in results if r.get("needs_improvement", False)]),
        }
    except Exception as e:
        logger.error(f"Batch review error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Keyword Research =====

@app.get("/api/v1/keywords/{platform}")
async def get_platform_keywords(
    platform: str,
    category: str = "general",
    limit: int = 10,
):
    """
    获取平台关键词

    获取指定平台的热搜关键词和趋势词
    """
    try:
        from backend.tools.web_search import web_search_tool

        # 搜索趋势
        trends = web_search_tool.search_trending_topics(category, platform, max_results=limit)
        keywords = web_search_tool.get_hot_keywords(category, max_results=limit)

        return {
            "success": True,
            "platform": platform,
            "category": category,
            "trending_topics": [
                {"title": r.title, "url": r.url, "score": r.score}
                for r in trends.results
            ] if trends.success else [],
            "hot_keywords": keywords.get("hot_keywords", [])[:limit],
        }
    except Exception as e:
        logger.error(f"Get platform keywords error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Content Template Library =====

# 预置内容模板
CONTENT_TEMPLATES = {
    "xiaohongshu": {
        "product_review": {
            "name": "产品测评模板",
            "structure": ["痛点引入", "产品介绍", "使用体验", "效果展示", "总结推荐"],
            "example_title": "这款[产品名]真的绝了！用了[时间]效果太惊艳",
        },
        "tutorial": {
            "name": "教程分享模板",
            "structure": ["问题背景", "解决方案", "步骤详解", "注意事项", "效果对比"],
            "example_title": "手把手教你[技能]，新手必看！",
        },
        "comparison": {
            "name": "对比测评模板",
            "structure": ["选择背景", "产品A介绍", "产品B介绍", "多维度对比", "个人推荐"],
            "example_title": "[产品A] vs [产品B]？真实对比告诉你答案！",
        },
    },
    "tiktok": {
        "hook": {
            "name": "爆款开头模板",
            "structure": ["3秒悬念", "价值承诺", "内容预告"],
            "example_title": "这个[话题]你一定要知道！",
        },
        "tutorial": {
            "name": "抖音教程模板",
            "structure": ["痛点激发", "解决方案", "实操展示", "效果证明"],
            "example_title": "只需3步，轻松搞定[问题]！",
        },
    },
    "official": {
        "deep_analysis": {
            "name": "深度分析模板",
            "structure": ["行业背景", "核心观点", "案例解读", "趋势预测", "总结建议"],
            "example_title": "[行业]深度报告：2025年发展趋势分析",
        },
        "product_intro": {
            "name": "产品介绍模板",
            "structure": ["产品背景", "核心卖点", "功能详解", "应用场景", "购买引导"],
            "example_title": "一文读懂[产品名]：功能、优势与适用场景",
        },
    },
}


@app.get("/api/v1/templates/library/{platform}")
async def get_template_library(platform: str):
    """
    获取平台模板库

    获取指定平台的预置内容模板
    """
    if platform not in CONTENT_TEMPLATES:
        raise HTTPException(status_code=404, detail="Platform templates not found")

    return {
        "success": True,
        "platform": platform,
        "templates": CONTENT_TEMPLATES[platform],
    }


@app.get("/api/v1/templates/library")
async def get_all_templates():
    """
    获取所有平台模板库

    返回所有平台的预置内容模板
    """
    return {
        "success": True,
        "templates": CONTENT_TEMPLATES,
    }


# ===== Content Archive =====

@app.post("/api/v1/archive")
async def archive_content(
    content: Dict[str, Any],
    name: str = "",
    category: str = "general",
):
    """
    归档内容

    将内容添加到归档库
    """
    try:
        from backend.agents.exporter import _content_archive

        result = _content_archive.archive_content(content, name, category)
        return result
    except Exception as e:
        logger.error(f"Archive content error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/archive")
async def get_archives(
    category: Optional[str] = None,
    limit: int = 50,
):
    """
    获取归档列表

    获取已归档的内容列表
    """
    try:
        from backend.agents.exporter import _content_archive

        archives = _content_archive.get_archives(category, limit)
        summary = _content_archive.export_archive_summary()

        return {
            "success": True,
            "archives": [
                {
                    "id": a["id"],
                    "name": a["name"],
                    "category": a["category"],
                    "created_at": a["created_at"],
                    "size": a["size"],
                }
                for a in archives
            ],
            "summary": summary,
        }
    except Exception as e:
        logger.error(f"Get archives error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/archive/{archive_id}")
async def get_archive(archive_id: str):
    """
    获取归档内容

    获取指定归档的完整内容
    """
    try:
        from backend.agents.exporter import _content_archive

        archive = _content_archive.get_archive(archive_id)
        if not archive:
            raise HTTPException(status_code=404, detail="Archive not found")

        return {"success": True, "archive": archive}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get archive error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/archive/{archive_id}")
async def delete_archive(archive_id: str):
    """
    删除归档

    从归档库中移除内容
    """
    try:
        from backend.agents.exporter import _content_archive

        success = _content_archive.delete_archive(archive_id)
        if not success:
            raise HTTPException(status_code=404, detail="Archive not found")

        return {"success": True, "message": "Archive deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete archive error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/archive/search")
async def search_archives(keyword: str):
    """
    搜索归档

    在归档库中搜索内容
    """
    try:
        from backend.agents.exporter import _content_archive

        results = _content_archive.search_archives(keyword)
        return {
            "success": True,
            "results": [
                {
                    "id": a["id"],
                    "name": a["name"],
                    "category": a["category"],
                    "created_at": a["created_at"],
                }
                for a in results
            ],
            "total": len(results),
        }
    except Exception as e:
        logger.error(f"Search archives error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Advanced Export =====

@app.post("/api/v1/export/advanced")
async def advanced_export_content(
    content: Dict[str, Any],
    format: str = "csv",
):
    """
    高级导出

    导出内容为CSV/XML/PDF_HTML/EMAIL_HTML格式
    """
    try:
        from backend.agents.exporter import advanced_exporter

        valid_formats = ["csv", "xml", "pdf_html", "email_html"]
        if format not in valid_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format. Must be one of: {valid_formats}"
            )

        result = advanced_exporter.advanced_export(content, format)
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        return {
            "success": True,
            "content": result.content,
            "format": format,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Advanced export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Content Collaboration =====

class ContentNote(BaseModel):
    """内容笔记"""
    id: str
    content_id: str
    platform: str
    note: str
    author: str
    created_at: str
    updated_at: str
    tags: List[str] = []


class ContentComment(BaseModel):
    """内容评论"""
    id: str
    content_id: str
    comment: str
    author: str
    created_at: str


# 内存存储
_content_notes: List[ContentNote] = []
_content_comments: List[ContentComment] = []
_note_id_counter = 0
_comment_id_counter = 0


@app.post("/api/v1/notes")
async def add_content_note(
    content_id: str,
    platform: str,
    note: str,
    author: str = "Anonymous",
    tags: List[str] = [],
):
    """
    添加内容笔记

    为内容添加备注或说明
    """
    global _note_id_counter
    try:
        from datetime import datetime

        _note_id_counter += 1
        note_obj = ContentNote(
            id=f"note_{_note_id_counter:06d}",
            content_id=content_id,
            platform=platform,
            note=note,
            author=author,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            tags=tags,
        )
        _content_notes.append(note_obj)

        return {"success": True, "note": note_obj}
    except Exception as e:
        logger.error(f"Add note error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/notes/{content_id}")
async def get_content_notes(content_id: str):
    """
    获取内容的笔记

    获取指定内容的所有笔记
    """
    try:
        notes = [n for n in _content_notes if n.content_id == content_id]
        return {
            "success": True,
            "notes": notes,
            "total": len(notes),
        }
    except Exception as e:
        logger.error(f"Get notes error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/notes/{note_id}")
async def delete_note(note_id: str):
    """
    删除笔记

    删除指定的笔记
    """
    global _content_notes
    try:
        original_count = len(_content_notes)
        _content_notes = [n for n in _content_notes if n.id != note_id]

        if len(_content_notes) == original_count:
            raise HTTPException(status_code=404, detail="Note not found")

        return {"success": True, "message": "Note deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete note error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/comments")
async def add_content_comment(
    content_id: str,
    comment: str,
    author: str = "Anonymous",
):
    """
    添加内容评论

    为内容添加反馈或评论
    """
    global _comment_id_counter
    try:
        from datetime import datetime

        _comment_id_counter += 1
        comment_obj = ContentComment(
            id=f"comment_{_comment_id_counter:06d}",
            content_id=content_id,
            comment=comment,
            author=author,
            created_at=datetime.now().isoformat(),
        )
        _content_comments.append(comment_obj)

        return {"success": True, "comment": comment_obj}
    except Exception as e:
        logger.error(f"Add comment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/comments/{content_id}")
async def get_content_comments(content_id: str):
    """
    获取内容的评论

    获取指定内容的所有评论
    """
    try:
        comments = [c for c in _content_comments if c.content_id == content_id]
        return {
            "success": True,
            "comments": comments,
            "total": len(comments),
        }
    except Exception as e:
        logger.error(f"Get comments error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Content Batch Operations =====

@app.post("/api/v1/batch/approve")
async def batch_approve_contents(
    content_ids: List[str],
):
    """
    批量审批内容

    一次性审批多条内容
    """
    try:
        from datetime import datetime

        results = []
        for content_id in content_ids:
            # 模拟审批操作
            results.append({
                "content_id": content_id,
                "status": "approved",
                "approved_at": datetime.now().isoformat(),
            })

        return {
            "success": True,
            "results": results,
            "total": len(results),
        }
    except Exception as e:
        logger.error(f"Batch approve error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/batch/reject")
async def batch_reject_contents(
    content_ids: List[str],
    reason: str = "",
):
    """
    批量拒绝内容

    一次性拒绝多条内容
    """
    try:
        from datetime import datetime

        results = []
        for content_id in content_ids:
            results.append({
                "content_id": content_id,
                "status": "rejected",
                "reason": reason,
                "rejected_at": datetime.now().isoformat(),
            })

        return {
            "success": True,
            "results": results,
            "total": len(results),
        }
    except Exception as e:
        logger.error(f"Batch reject error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/batch/export")
async def batch_export_contents(
    content_ids: List[str],
    format: str = "json",
):
    """
    批量导出内容

    一次性导出多条内容
    """
    try:
        from backend.agents.exporter import _content_archive

        exported = []
        for content_id in content_ids:
            archive = _content_archive.get_archive(content_id)
            if archive:
                exported.append({
                    "content_id": content_id,
                    "content": archive["content"],
                    "exported": True,
                })
            else:
                exported.append({
                    "content_id": content_id,
                    "exported": False,
                    "error": "Content not found",
                })

        return {
            "success": True,
            "exported": exported,
            "total": len(exported),
            "successful": len([e for e in exported if e.get("exported", False)]),
        }
    except Exception as e:
        logger.error(f"Batch export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/batch/delete")
async def batch_delete_contents(
    content_ids: List[str],
):
    """
    批量删除内容

    一次性删除多条内容
    """
    try:
        from backend.agents.exporter import _content_archive

        deleted = []
        for content_id in content_ids:
            success = _content_archive.delete_archive(content_id)
            deleted.append({
                "content_id": content_id,
                "deleted": success,
            })

        return {
            "success": True,
            "results": deleted,
            "total": len(deleted),
            "successful": len([d for d in deleted if d.get("deleted", False)]),
        }
    except Exception as e:
        logger.error(f"Batch delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Content Utilities =====

@app.post("/api/v1/validate/content")
async def validate_content(
    content: str = Body(..., embed=True),
):
    """
    验证内容

    全面验证内容质量和合规性
    """
    try:
        reviewer = get_reviewer()

        review = reviewer.review_quality(content)
        violations = reviewer.check_ad_words(content)
        analysis = reviewer.analyze_structure(content)

        return {
            "success": True,
            "validation": {
                "passed": review.passed,
                "quality_score": review.quality_score,
                "violations": [
                    {
                        "word": v.word,
                        "position": v.position,
                        "severity": v.severity,
                        "category": v.category,
                    }
                    for v in violations
                ],
                "structure": analysis,
                "suggestions": review.suggestions,
            },
            "is_compliant": len([v for v in violations if v.severity == "error"]) == 0,
        }
    except Exception as e:
        logger.error(f"Validate content error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/summarize")
async def summarize_content(
    content: str = Body(..., embed=True),
    max_length: int = 100,
):
    """
    生成内容摘要

    将长内容压缩为简短摘要
    """
    try:
        reviewer = get_reviewer()

        # 简单摘要逻辑
        sentences = content.replace("！", "。").replace("？", "。").split("。")
        summary_sentences = []

        current_length = 0
        for sentence in sentences:
            if current_length + len(sentence) <= max_length:
                summary_sentences.append(sentence)
                current_length += len(sentence)
            else:
                break

        summary = "。".join(summary_sentences).strip()
        if summary and not summary.endswith("。"):
            summary += "。"

        return {
            "success": True,
            "original_length": len(content),
            "summary": summary,
            "compression_ratio": round(len(summary) / len(content), 2) if content else 0,
        }
    except Exception as e:
        logger.error(f"Summarize content error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/expand")
async def expand_content(
    content: str = Body(..., embed=True),
    target_length: int = 500,
):
    """
    扩展内容

    将短内容扩展为更长、更详细的内容
    """
    try:
        reviewer = get_reviewer()

        # 分析现有内容结构
        analysis = reviewer.analyze_structure(content)

        # 简单的扩展逻辑
        expanded = content

        # 添加开头
        if len(content) < target_length:
            expanded = f"关于这个话题，我想分享一些见解。{expanded}"

        # 添加结尾
        if len(expanded) < target_length:
            expanded = f"{expanded}希望这些信息对你有帮助！"

        return {
            "success": True,
            "original_length": len(content),
            "expanded": expanded,
            "target_length": target_length,
            "expansion_ratio": round(len(expanded) / len(content), 2) if content else 0,
        }
    except Exception as e:
        logger.error(f"Expand content error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/paraphrase")
async def paraphrase_content(
    content: str = Body(..., embed=True),
    style: str = "natural",
):
    """
    改写内容

    将内容改写为不同风格
    """
    try:
        # 简单的改写逻辑
        paraphrased = content

        # 根据风格调整
        if style == "formal":
            paraphrased = paraphrased.replace("啦", "了").replace("呀", "")
        elif style == "casual":
            paraphrased = paraphrased.replace("非常", "特别").replace("优秀", "棒")

        return {
            "success": True,
            "original": content,
            "paraphrased": paraphrased,
            "style": style,
        }
    except Exception as e:
        logger.error(f"Paraphrase content error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/word-count")
async def get_word_count(
    content: str,
):
    """
    获取字数统计

    统计内容的各种字数指标
    """
    try:
        reviewer = get_reviewer()
        analysis = reviewer.analyze_structure(content)

        # 中文字符数
        chinese_chars = len([c for c in content if '\u4e00' <= c <= '\u9fff'])
        # 英文字数
        english_words = len([c for c in content if c.isalpha() and ord(c) < 128])
        # 数字个数
        numbers = len([c for c in content if c.isdigit()])
        # emoji个数
        emojis = analysis.get("emoji_count", 0)

        return {
            "success": True,
            "total_characters": len(content),
            "chinese_characters": chinese_chars,
            "english_words": english_words,
            "numbers": numbers,
            "emojis": emojis,
            "paragraphs": analysis.get("paragraph_count", 0),
        }
    except Exception as e:
        logger.error(f"Get word count error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/extract/hashtags")
async def extract_hashtags(
    content: str = Body(..., embed=True),
):
    """
    提取话题标签

    从内容中提取所有话题标签
    """
    import re
    try:
        # 提取 #标签# 格式
        hashtags1 = re.findall(r'#([^#]+)#', content)
        # 提取 #标签 格式
        hashtags2 = re.findall(r'#(\S+)', content)

        all_tags = list(set(hashtags1 + hashtags2))

        return {
            "success": True,
            "hashtags": all_tags,
            "total": len(all_tags),
        }
    except Exception as e:
        logger.error(f"Extract hashtags error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Style Variations & A/B Testing =====

@app.post("/api/v1/copy/variations")
async def generate_style_variations(
    product_name: str,
    product_description: str,
    selling_points: str,
    platform: str,
    base_content: str,
    styles: Optional[List[str]] = None,
):
    """
    生成多种风格的文案变体

    将基础文案改写为不同风格
    """
    try:
        from backend.agents.copywriter import Copywriter
        from backend.agents.planner import ProductInfo

        product = ProductInfo(
            name=product_name,
            description=product_description,
            selling_points=[s.strip() for s in selling_points.split(",") if s.strip()],
        )

        copywriter = get_copywriter()
        variations = copywriter.generate_style_variations(product, platform, base_content, styles)

        return {
            "success": True,
            "platform": platform,
            "variations": variations,
        }
    except Exception as e:
        logger.error(f"Generate variations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/copy/ab-test")
async def generate_ab_copies(
    product_name: str,
    product_description: str,
    selling_points: str,
    platform: str,
    num_variants: int = 3,
):
    """
    生成A/B测试用的多个文案版本

    生成不同角度的文案用于A/B测试
    """
    try:
        from backend.agents.copywriter import Copywriter
        from backend.agents.planner import ProductInfo

        product = ProductInfo(
            name=product_name,
            description=product_description,
            selling_points=[s.strip() for s in selling_points.split(",") if s.strip()],
        )

        copywriter = get_copywriter()
        results = copywriter.generate_ab_copies(product, platform, num_variants)

        return {
            "success": True,
            "platform": platform,
            "copies": [
                {
                    "title": r.title,
                    "content": r.content,
                    "tags": r.tags,
                    "angle": r.analysis.get("angle", ""),
                    "success": r.success,
                }
                for r in results
            ],
        }
    except Exception as e:
        logger.error(f"Generate A/B copies error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/copy/regenerate-with-feedback")
async def regenerate_with_feedback(
    original_title: str,
    original_content: str,
    feedback: str,
    product_name: str,
    product_description: str,
    selling_points: str,
    platform: str,
):
    """
    根据反馈重新生成文案

    改进不满意的部分生成新文案
    """
    try:
        from backend.agents.copywriter import Copywriter, CopyResult
        from backend.agents.planner import ProductInfo

        product = ProductInfo(
            name=product_name,
            description=product_description,
            selling_points=[s.strip() for s in selling_points.split(",") if s.strip()],
        )

        original = CopyResult(
            platform=platform,
            title=original_title,
            content=original_content,
        )

        copywriter = get_copywriter()
        result = copywriter.regenerate_with_feedback(original, feedback, product)

        return {
            "success": True,
            "result": {
                "title": result.title,
                "content": result.content,
                "tags": result.tags,
                "analysis": result.analysis,
            },
        }
    except Exception as e:
        logger.error(f"Regenerate with feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Seasonal Copy =====

@app.post("/api/v1/copy/seasonal")
async def generate_seasonal_copy(
    product_name: str,
    product_description: str,
    selling_points: str,
    platform: str,
    season: str = "spring",
    festival: str = "",
):
    """
    生成季节性文案

    根据季节或节日生成应景的营销文案
    """
    try:
        from backend.agents.copywriter import SeasonalCopywriter
        from backend.agents.planner import ProductInfo

        product = ProductInfo(
            name=product_name,
            description=product_description,
            selling_points=[s.strip() for s in selling_points.split(",") if s.strip()],
        )

        seasonal_writer = SeasonalCopywriter()
        result = seasonal_writer.generate_seasonal_copy(product, platform, season, festival)

        return {
            "success": True,
            "seasonal_copy": {
                "season": result.season,
                "theme": result.theme,
                "title": result.title,
                "content": result.content,
                "hashtags": result.hashtags,
            },
        }
    except Exception as e:
        logger.error(f"Generate seasonal copy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/seasons")
async def get_available_seasons():
    """
    获取可选的季节列表

    返回支持的季节和节日
    """
    from backend.agents.copywriter import SEASONAL_TEMPLATES

    return {
        "success": True,
        "seasons": [
            {"id": key, "name": value["name"], "keywords": value["keywords"]}
            for key, value in SEASONAL_TEMPLATES.items()
        ],
    }


# ===== Report Generation =====

@app.post("/api/v1/reports/summary")
async def generate_summary_report(
    content_data: List[Dict[str, Any]],
    title: str = "内容报告",
    include_sections: Optional[List[str]] = None,
):
    """
    生成综合报告

    根据内容数据生成统计报告
    """
    try:
        from backend.services.reporting import ContentReporter, ReportConfig

        if include_sections is None:
            include_sections = ["overview", "platform_breakdown", "quality_analysis", "violation_report"]

        config = ReportConfig(
            title=title,
            include_sections=include_sections,
        )

        reporter = ContentReporter()
        report = reporter.generate_summary_report(content_data, config)

        return {
            "success": True,
            "report": report.report,
            "generated_at": report.generated_at,
        }
    except Exception as e:
        logger.error(f"Generate summary report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/reports/comparison")
async def generate_comparison_report(
    content1: Dict[str, Any],
    content2: Dict[str, Any],
):
    """
    生成内容对比报告

    对比两个内容的质量和效果
    """
    try:
        from backend.services.reporting import ContentReporter

        reporter = ContentReporter()
        report = reporter.generate_comparison_report(content1, content2)

        return {
            "success": True,
            "report": report.report,
            "generated_at": report.generated_at,
        }
    except Exception as e:
        logger.error(f"Generate comparison report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
