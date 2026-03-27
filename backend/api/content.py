"""
Vox Content API

提供内容生成的 REST API 接口
支持 CORS、请求验证和错误处理
"""

import os
import uuid
from typing import Any, Dict, List, Optional
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Query, Request, Body, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from backend.logging_config import get_logger
from backend.constants import VERSION
from backend.agents.planner import ProductInfo


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
    llm_provider: str = "minimax"


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


class BatchGenerateRequest(BaseModel):
    """批量生成请求"""
    products: List[ProductInput]
    platforms: List[str] = Field(default=["xiaohongshu"])
    enable_research: bool = Field(default=False)


class AnalyticsRequest(BaseModel):
    """分析请求"""
    copies: List[dict]  # 包含 platform, content, review 的列表


class ConvertFormatRequest(BaseModel):
    """格式转换请求"""
    content: str
    from_platform: str
    to_platform: str


class DuplicateCheckRequest(BaseModel):
    """重复检测请求"""
    content: str
    existing_contents: List[str] = Field(default_factory=list)


class SeoKeywordsRequest(BaseModel):
    """SEO关键词请求"""
    content: str
    platform: str = "general"


class CompareRequest(BaseModel):
    """内容对比请求"""
    content1: str
    content2: str


class HashtagRequest(BaseModel):
    """标签建议请求"""
    content: str
    platform: str = "xiaohongshu"
    max_tags: int = Field(default=5, ge=1, le=10)


class PerformanceRequest(BaseModel):
    """表现预测请求"""
    content: str
    platform: str = "xiaohongshu"


class SaveTemplateRequest(BaseModel):
    """保存模板请求"""
    name: str
    platform: str
    content: str
    tags: List[str] = Field(default_factory=list)


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


logger = get_logger("api")

# Create router with prefix
router = APIRouter(prefix="/api/v1", tags=["内容生成"])


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


@router.get("/", response_model=dict)
async def root():
    """根路径"""
    return {
        "name": "Vox Content API",
        "version": VERSION,
        "description": "多平台营销内容生成 API",
        "docs": "/docs"
    }


@router.get("/health", response_model=HealthResponse)
async def health():
    """健康检查"""
    from backend.services.llm import llm_client
    from backend.config import config

    return HealthResponse(
        status="healthy",
        version=VERSION,
        api_key_configured=llm_client.validate_config(),
        tavily_api_configured=bool(config.tavily_api_key),
        llm_provider=llm_client.provider,
    )


@router.get("/platforms", response_model=PlatformsResponse)
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


@router.get("/categories", response_model=CategoriesResponse)
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


@router.post("/content/generate", response_model=ContentResponse)
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
        logger.warning("Validation error")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "参数验证错误",
                "type": "validation"
            }
        )
    except TimeoutError as e:
        logger.error("Generation timeout")
        raise HTTPException(
            status_code=504,
            detail={
                "error": "生成超时，请稍后重试",
                "type": "timeout"
            }
        )
    except ConnectionError as e:
        logger.error("Connection error")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "服务暂时不可用，请稍后重试",
                "type": "connection"
            }
        )
    except Exception as e:
        logger.exception("Generate content error")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "内容生成失败，请稍后重试",
                "type": "internal"
            }
        )


@router.post("/content/batch-generate")
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
            logger.error("Batch generate error")
            errors.append(f"产品{i+1}: 生成失败")
            results.append({
                "product_index": i,
                "product_name": product_input.name,
                "success": False,
                "error": "生成失败，请稍后重试",
            })

    return {
        "success": len(errors) == 0,
        "total_products": len(body.products),
        "successful": len([r for r in results if r.get("success")]),
        "failed": len([r for r in results if not r.get("success")]),
        "results": results,
        "errors": errors,
    }


@router.post("/content/review")
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
        logger.error("Review content error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """获取 API 统计信息"""
    return StatsResponse(
        total_requests=_request_count,
        total_platforms=4,
        supported_platforms=["xiaohongshu", "tiktok", "official", "friend_circle"],
    )


@router.post("/content/regenerate")
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
        logger.warning("Validation error")
        raise HTTPException(status_code=400, detail="参数验证错误")
    except Exception as e:
        logger.error("Regenerate content error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/content/ab-suggestions")
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
        logger.error("A/B test suggestions error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/suggestions/{platform}")
async def get_platform_suggestions(platform: str, content: str):
    """
    获取指定平台的优化建议

    根据内容特点和目标平台返回个性化优化建议
    """
    valid_platforms = {"xiaohongshu", "tiktok", "official", "friend_circle"}
    if platform not in valid_platforms:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
        )
    try:
        reviewer = get_reviewer()
        suggestions = reviewer.suggest_platform_optimization(content, platform)
        return {
            "platform": platform,
            "suggestions": suggestions,
        }
    except Exception as e:
        logger.error("Get platform suggestions error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/scheduling/{platform}")
async def get_scheduling_suggestions(platform: str, content_type: str = "general"):
    """
    获取指定平台的发布时段建议

    根据平台特性和内容类型返回最佳发布时段
    """
    valid_platforms = {"xiaohongshu", "tiktok", "official", "friend_circle"}
    if platform not in valid_platforms:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
        )
    try:
        reviewer = get_reviewer()
        scheduling = reviewer.suggest_scheduling(platform, content_type)
        return {
            "platform": platform,
            "content_type": content_type,
            "scheduling": scheduling,
        }
    except Exception as e:
        logger.error("Get scheduling suggestions error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/content/analytics")
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
        logger.error("Get content analytics error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/content/convert")
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
        logger.error("Convert content format error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/content/check-duplicate")
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
        logger.error("Check duplicate error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/seo/keywords")
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
        logger.error("Get SEO keywords error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/content/compare")
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
        logger.error("Compare contents error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/hashtags/suggest")
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
        logger.error("Suggest hashtags error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/content/predict")
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
        logger.error("Predict performance error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/templates")
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
        logger.error("Save template error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/templates/{platform}")
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
        logger.error("Get templates error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.delete("/templates/{platform}/{template_id}")
async def delete_template(platform: str, template_id: str):
    """删除模板"""
    try:
        exporter = get_exporter()
        success = exporter.delete_template(platform, template_id)
        return {"success": success}
    except Exception as e:
        logger.error("Delete template error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/trending/{platform}")
async def get_trending_topics(platform: str, category: str = "general"):
    """
    获取热门话题

    搜索平台热门话题和趋势
    """
    valid_platforms = {"xiaohongshu", "tiktok", "official", "friend_circle"}
    if platform not in valid_platforms:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
        )
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
        logger.error("Get trending topics error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/hot-keywords")
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
        logger.error("Get hot keywords error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Content Calendar & Scheduling =====

# In-memory storage for scheduled content (替换为数据库)
_scheduled_content_store: List[ScheduledContent] = []


@router.post("/schedule", response_model=CalendarResponse)
async def schedule_content(
    product_name: str,
    platform: str,
    title: str,
    content: str,
    tags: Optional[List[str]] = None,
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
            tags=tags or [],
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
        logger.error("Schedule content error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/calendar", response_model=CalendarResponse)
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
        logger.error("Get calendar error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.delete("/schedule/{schedule_id}")
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
        logger.error("Delete schedule error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.put("/schedule/{schedule_id}/publish")
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
        logger.error("Mark published error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Content Version Management =====

_content_versions_store: Dict[str, List[ContentVersion]] = {}


@router.post("/versions")
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
        logger.error("Save version error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/versions/{content_id}")
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
        logger.error("Get versions error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/versions/{content_id}/v/{version_number}")
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
        logger.error("Get specific version error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


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


@router.get("/best-practices/{platform}")
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


@router.get("/best-practices")
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

@router.post("/analytics/record")
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
        logger.error("Record analytics error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/analytics/platform")
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
        logger.error("Get platform analytics error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/analytics/trends")
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
        logger.error("Get quality trends error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/analytics/compare")
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
        logger.error("Compare platforms error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/analytics/health/{content_id}")
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
        logger.error("Get content health error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Content Improvement & Inspiration =====

@router.post("/content/improve")
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
        logger.error("Get improvement suggestions error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/content/angles")
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
        logger.error("Suggest content angles error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/content/batch-review")
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
        logger.error("Batch review error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Keyword Research =====

@router.get("/keywords/{platform}")
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
        logger.error("Get platform keywords error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


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


@router.get("/templates/library/{platform}")
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


@router.get("/templates/library")
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

@router.post("/archive")
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
        logger.error("Archive content error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/archive")
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
        logger.error("Get archives error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/archive/{archive_id}")
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
        logger.error("Get archive error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.delete("/archive/{archive_id}")
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
        logger.error("Delete archive error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/archive/search")
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
        logger.error("Search archives error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Advanced Export =====

@router.post("/export/advanced")
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
        logger.error("Advanced export error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Content Collaboration =====

# 内存存储
_content_notes: List[ContentNote] = []
_content_comments: List[ContentComment] = []
_note_id_counter = 0
_comment_id_counter = 0


@router.post("/notes")
async def add_content_note(
    content_id: str,
    platform: str,
    note: str,
    author: str = "Anonymous",
    tags: Optional[List[str]] = None,
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
            tags=tags or [],
        )
        _content_notes.append(note_obj)

        return {"success": True, "note": note_obj}
    except Exception as e:
        logger.error("Add note error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/notes/{content_id}")
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
        logger.error("Get notes error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.delete("/notes/{note_id}")
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
        logger.error("Delete note error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/comments")
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
        logger.error("Add comment error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/comments/{content_id}")
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
        logger.error("Get comments error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Content Batch Operations =====

@router.post("/batch/approve")
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
        logger.error("Batch approve error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/batch/reject")
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
        logger.error("Batch reject error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/batch/export")
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
        logger.error("Batch export error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/batch/delete")
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
        logger.error("Batch delete error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Content Utilities =====

@router.post("/validate/content")
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
        logger.error("Validate content error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/summarize")
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
        logger.error("Summarize content error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/expand")
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
        logger.error("Expand content error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/paraphrase")
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
        logger.error("Paraphrase content error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/word-count")
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
        logger.error("Get word count error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/extract/hashtags")
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
        logger.error("Extract hashtags error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Style Variations & A/B Testing =====

@router.post("/copy/variations")
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
        logger.error("Generate variations error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/copy/ab-test")
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
        logger.error("Generate A/B copies error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/copy/regenerate-with-feedback")
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
        logger.error("Regenerate with feedback error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Seasonal Copy =====

@router.post("/copy/seasonal")
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
        logger.error("Generate seasonal copy error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/seasons")
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

@router.post("/reports/summary")
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
        logger.error("Generate summary report error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/reports/comparison")
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
        logger.error("Generate comparison report error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Campaign Management =====

@router.post("/campaigns")
async def create_campaign(
    name: str,
    description: str,
    campaign_type: str = "product_launch",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tags: Optional[List[str]] = None,
):
    """
    创建营销活动

    创建新的营销活动
    """
    try:
        from backend.services.campaign import campaign_manager

        campaign = campaign_manager.create_campaign(
            name=name,
            description=description,
            campaign_type=campaign_type,
            start_date=start_date,
            end_date=end_date,
            tags=tags,
        )

        return {
            "success": True,
            "campaign": {
                "id": campaign.id,
                "name": campaign.name,
                "description": campaign.description,
                "campaign_type": campaign.campaign_type,
                "status": campaign.status,
                "created_at": campaign.created_at,
            },
        }
    except Exception as e:
        logger.error("Create campaign error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/campaigns")
async def get_campaigns(
    status: Optional[str] = None,
    campaign_type: Optional[str] = None,
):
    """
    获取营销活动列表

    获取所有营销活动
    """
    try:
        from backend.services.campaign import campaign_manager

        campaigns = campaign_manager.get_campaigns(status, campaign_type)

        return {
            "success": True,
            "campaigns": [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "campaign_type": c.campaign_type,
                    "status": c.status,
                    "start_date": c.start_date,
                    "end_date": c.end_date,
                    "created_at": c.created_at,
                }
                for c in campaigns
            ],
            "total": len(campaigns),
        }
    except Exception as e:
        logger.error("Get campaigns error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """
    获取活动详情

    获取指定活动的详细信息
    """
    try:
        from backend.services.campaign import campaign_manager

        campaign = campaign_manager.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        contents = campaign_manager.get_campaign_contents(campaign_id)

        return {
            "success": True,
            "campaign": {
                "id": campaign.id,
                "name": campaign.name,
                "description": campaign.description,
                "campaign_type": campaign.campaign_type,
                "status": campaign.status,
                "start_date": campaign.start_date,
                "end_date": campaign.end_date,
                "tags": campaign.tags,
                "notes": campaign.notes,
                "created_at": campaign.created_at,
                "updated_at": campaign.updated_at,
            },
            "contents": [
                {
                    "id": c.id,
                    "platform": c.platform,
                    "title": c.title,
                    "content": c.content,
                    "scheduled_time": c.scheduled_time,
                    "status": c.status,
                }
                for c in contents
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get campaign error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.put("/campaigns/{campaign_id}")
async def update_campaign(
    campaign_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tags: Optional[List[str]] = None,
    notes: Optional[str] = None,
):
    """
    更新活动信息

    更新指定活动的信息
    """
    try:
        from backend.services.campaign import campaign_manager

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if status is not None:
            update_data["status"] = status
        if start_date is not None:
            update_data["start_date"] = start_date
        if end_date is not None:
            update_data["end_date"] = end_date
        if tags is not None:
            update_data["tags"] = tags
        if notes is not None:
            update_data["notes"] = notes

        campaign = campaign_manager.update_campaign(campaign_id, **update_data)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        return {
            "success": True,
            "campaign": {
                "id": campaign.id,
                "name": campaign.name,
                "status": campaign.status,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Update campaign error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """
    删除活动

    删除指定的营销活动
    """
    try:
        from backend.services.campaign import campaign_manager

        success = campaign_manager.delete_campaign(campaign_id)
        if not success:
            raise HTTPException(status_code=404, detail="Campaign not found")

        return {"success": True, "message": "Campaign deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Delete campaign error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/campaigns/{campaign_id}/contents")
async def add_campaign_content(
    campaign_id: str,
    platform: str,
    title: str,
    content: str,
    scheduled_time: Optional[str] = None,
):
    """
    向活动添加内容

    向指定活动添加内容项
    """
    try:
        from backend.services.campaign import campaign_manager

        campaign_content = campaign_manager.add_content_to_campaign(
            campaign_id=campaign_id,
            platform=platform,
            title=title,
            content=content,
            scheduled_time=scheduled_time,
        )

        if not campaign_content:
            raise HTTPException(status_code=404, detail="Campaign not found")

        return {
            "success": True,
            "content": {
                "id": campaign_content.id,
                "platform": campaign_content.platform,
                "title": campaign_content.title,
                "scheduled_time": campaign_content.scheduled_time,
                "status": campaign_content.status,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Add campaign content error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/campaigns/{campaign_id}/timeline")
async def get_campaign_timeline(campaign_id: str):
    """
    获取活动时间线

    获取指定活动的时间线信息
    """
    try:
        from backend.services.campaign import campaign_manager

        timeline = campaign_manager.get_campaign_timeline(campaign_id)
        if not timeline:
            raise HTTPException(status_code=404, detail="Campaign not found")

        return {"success": True, **timeline}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get campaign timeline error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/campaigns/{campaign_id}/summary")
async def get_campaign_summary(campaign_id: str):
    """
    获取活动摘要

    获取指定活动的统计摘要
    """
    try:
        from backend.services.campaign import campaign_manager

        summary = campaign_manager.get_campaign_summary(campaign_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Campaign not found")

        return {"success": True, **summary}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get campaign summary error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Performance Prediction =====

@router.post("/predict/performance")
async def predict_performance(
    content: str,
    platform: str,
    title: str = "",
    tags: Optional[List[str]] = None,
    posting_time: Optional[str] = None,
    category: Optional[str] = None,
):
    """
    预测内容表现

    基于内容特征和平台数据预测内容表现
    """
    try:
        from backend.services.predictor import performance_predictor

        prediction = performance_predictor.predict(
            content=content,
            platform=platform,
            title=title,
            tags=tags,
            posting_time=posting_time,
            category=category,
        )

        return {
            "success": True,
            "prediction": {
                "predicted_views": prediction.predicted_views,
                "predicted_likes": prediction.predicted_likes,
                "predicted_comments": prediction.predicted_comments,
                "predicted_shares": prediction.predicted_shares,
                "engagement_rate": round(prediction.engagement_rate, 4),
                "reach_score": round(prediction.reach_score, 1),
                "confidence": prediction.confidence,
                "factors": prediction.factors,
                "recommendations": prediction.recommendations,
            },
        }
    except Exception as e:
        logger.error("Predict performance error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/predict/platform/{platform}")
async def get_platform_recommendations(platform: str):
    """
    获取平台发布建议

    获取指定平台的发布建议和基准数据
    """
    try:
        from backend.services.predictor import performance_predictor

        recommendations = performance_predictor.get_platform_recommendations(platform)

        return {"success": True, **recommendations}
    except Exception as e:
        logger.error("Get platform recommendations error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/predict/compare")
async def compare_predictions(
    content1: Dict[str, Any],
    content2: Dict[str, Any],
    platform: str,
):
    """
    对比内容预测

    对比两个内容的预测表现
    """
    try:
        from backend.services.predictor import performance_predictor

        # 预测两个内容
        pred1 = performance_predictor.predict(
            content=content1.get("content", ""),
            platform=platform,
            title=content1.get("title", ""),
            tags=content1.get("tags"),
        )

        pred2 = performance_predictor.predict(
            content=content2.get("content", ""),
            platform=platform,
            title=content2.get("title", ""),
            tags=content2.get("tags"),
        )

        # 对比
        comparison = performance_predictor.compare_predictions(pred1, pred2)

        return {
            "success": True,
            "prediction1": {
                "predicted_views": pred1.predicted_views,
                "reach_score": pred1.reach_score,
            },
            "prediction2": {
                "predicted_views": pred2.predicted_views,
                "reach_score": pred2.reach_score,
            },
            "comparison": comparison,
        }
    except Exception as e:
        logger.error("Compare predictions error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Video Generation =====

class VideoSearchRequest(BaseModel):
    """视频素材搜索请求"""
    search_terms: List[str] = Field(..., description="搜索关键词列表")
    video_aspect: str = Field(default="9:16", description="视频比例 (9:16, 16:9, 1:1)")
    source: str = Field(default="pexels", description="素材源 (pexels/pixabay)")


class VideoSearchResponse(BaseModel):
    """视频素材搜索响应"""
    success: bool
    videos: List[dict]
    total: int


@router.post("/video/search-materials", response_model=VideoSearchResponse)
async def search_video_materials(body: VideoSearchRequest):
    """
    搜索视频素材

    从 Pexels 或 Pixabay 搜索视频素材
    """
    try:
        from backend.tools.material_collector import material_collector

        all_videos = []
        seen_urls = set()

        for term in body.search_terms:
            videos = material_collector.search_videos(
                search_term=term,
                video_aspect=body.video_aspect,
                source=body.source,
            )
            for video in videos:
                if video["url"] not in seen_urls:
                    all_videos.append(video)
                    seen_urls.add(video["url"])

        return VideoSearchResponse(
            success=True,
            videos=all_videos,
            total=len(all_videos),
        )
    except Exception as e:
        logger.error("Search video materials error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


class VideoDownloadRequest(BaseModel):
    """视频下载请求"""
    video_urls: List[str] = Field(..., description="视频URL列表")
    save_dir: str = Field(default="", description="保存目录")


class VideoDownloadResponse(BaseModel):
    """视频下载响应"""
    success: bool
    video_paths: List[str]
    total: int


@router.post("/video/download", response_model=VideoDownloadResponse)
async def download_videos(body: VideoDownloadRequest):
    """
    下载视频素材

    下载视频到本地
    """
    try:
        from backend.tools.material_collector import material_collector

        video_paths = []
        for url in body.video_urls:
            path = material_collector.download_video(url, body.save_dir)
            if path:
                video_paths.append(path)

        return VideoDownloadResponse(
            success=len(video_paths) > 0,
            video_paths=video_paths,
            total=len(video_paths),
        )
    except Exception as e:
        logger.error("Download videos error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


class AudioGenerateRequest(BaseModel):
    """音频生成请求"""
    text: str = Field(..., description="要转换的文本")
    voice_name: str = Field(default="zh-CN-XiaoyiNeural", description="声音名称")
    voice_rate: float = Field(default=1.0, description="语速 (0.5-2.0)")


class AudioGenerateResponse(BaseModel):
    """音频生成响应"""
    success: bool
    audio_path: str
    subtitle_path: str
    duration: float


@router.post("/video/generate-audio", response_model=AudioGenerateResponse)
async def generate_audio(body: AudioGenerateRequest):
    """
    生成语音

    使用 Edge TTS 生成语音
    """
    try:
        from backend.services.voice import voice_service

        audio_path, subtitle_path, duration = voice_service.generate_with_subtitles(
            text=body.text,
            voice_name=body.voice_name,
            voice_rate=body.voice_rate,
        )

        return AudioGenerateResponse(
            success=bool(audio_path),
            audio_path=audio_path,
            subtitle_path=subtitle_path,
            duration=duration,
        )
    except Exception as e:
        logger.error("Generate audio error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


class SubtitleGenerateRequest(BaseModel):
    """字幕生成请求"""
    audio_path: str = Field(..., description="音频文件路径")
    language: str = Field(default="zh", description="语音语言")


class SubtitleGenerateResponse(BaseModel):
    """字幕生成响应"""
    success: bool
    subtitle_path: str


@router.post("/video/generate-subtitle", response_model=SubtitleGenerateResponse)
async def generate_subtitle(body: SubtitleGenerateRequest):
    """
    生成字幕

    使用 Whisper 从音频生成字幕
    """
    try:
        from backend.services.subtitle import subtitle_service

        subtitle_path = subtitle_service.generate_subtitle(
            audio_path=body.audio_path,
            language=body.language,
        )

        return SubtitleGenerateResponse(
            success=bool(subtitle_path),
            subtitle_path=subtitle_path,
        )
    except Exception as e:
        logger.error("Generate subtitle error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


class VideoCombineRequest(BaseModel):
    """视频合并请求"""
    video_paths: List[str] = Field(..., description="视频文件路径列表")
    audio_path: str = Field(..., description="音频文件路径")
    output_path: str = Field(default="", description="输出路径")
    video_aspect: str = Field(default="9:16", description="视频比例")
    video_length: str = Field(default="medium", description="视频长度预设 (short/medium/long/custom)")
    video_clip_duration: int = Field(default=5, description="每个片段最大时长（秒）")
    concat_mode: str = Field(default="random", description="拼接模式 (random/sequential)")
    transition_mode: str = Field(default="fade_in", description="转场模式")


class VideoCombineResponse(BaseModel):
    """视频合并响应"""
    success: bool
    video_path: str


@router.post("/video/combine", response_model=VideoCombineResponse)
async def combine_videos(body: VideoCombineRequest):
    """
    合并视频

    将多个视频片段合并为一个视频
    """
    try:
        from backend.tools.video_generator import VideoGenerator, VideoAspect, VideoConcatMode, VideoTransitionMode, VideoLengthPreset, VideoParams

        aspect_map = {
            "9:16": VideoAspect.PORTRAIT,
            "16:9": VideoAspect.LANDSCAPE,
            "1:1": VideoAspect.SQUARE,
        }
        concat_map = {
            "random": VideoConcatMode.RANDOM,
            "sequential": VideoConcatMode.SEQUENTIAL,
        }
        transition_map = {
            "none": VideoTransitionMode.NONE,
            "fade_in": VideoTransitionMode.FADE_IN,
            "fade_out": VideoTransitionMode.FADE_OUT,
            "slide_in": VideoTransitionMode.SLIDE_IN,
            "slide_out": VideoTransitionMode.SLIDE_OUT,
            "shuffle": VideoTransitionMode.SHUFFLE,
        }
        length_map = {
            "short": VideoLengthPreset.SHORT,
            "medium": VideoLengthPreset.MEDIUM,
            "long": VideoLengthPreset.LONG,
            "custom": VideoLengthPreset.CUSTOM,
        }

        params = VideoParams(
            video_aspect=aspect_map.get(body.video_aspect, VideoAspect.PORTRAIT),
            video_length_preset=length_map.get(body.video_length, VideoLengthPreset.MEDIUM),
            video_clip_duration=body.video_clip_duration,
            video_concat_mode=concat_map.get(body.concat_mode, VideoConcatMode.RANDOM),
            video_transition_mode=transition_map.get(body.transition_mode, VideoTransitionMode.FADE_IN),
        )

        generator = VideoGenerator()
        output_path = body.output_path or os.path.join(
            generator.output_dir, f"combined-{uuid.uuid4().hex[:8]}.mp4"
        )

        result = generator.combine_videos(
            video_paths=body.video_paths,
            audio_path=body.audio_path,
            output_path=output_path,
            params=params,
        )

        return VideoCombineResponse(
            success=bool(result),
            video_path=result,
        )
    except Exception as e:
        logger.error("Combine videos error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


class VideoGenerateRequest(BaseModel):
    """视频生成请求"""
    video_path: str = Field(..., description="视频文件路径")
    audio_path: str = Field(..., description="音频文件路径")
    subtitle_path: str = Field(default="", description="字幕文件路径")
    output_path: str = Field(default="", description="输出路径")
    video_aspect: str = Field(default="9:16", description="视频比例")
    video_length: str = Field(default="medium", description="视频长度预设 (short/medium/long/custom)")
    video_clip_duration: int = Field(default=5, ge=1, le=30, description="片段时长（当 video_length 为 custom 时使用）")
    subtitle_enabled: bool = Field(default=True, description="是否启用字幕")
    bgm_type: str = Field(default="none", description="背景音乐类型 (random/none)")
    bgm_volume: float = Field(default=0.3, description="背景音乐音量")


class VideoGenerateResponse(BaseModel):
    """视频生成响应"""
    success: bool
    video_path: str
    duration: float
    error: str = ""


@router.post("/video/generate", response_model=VideoGenerateResponse)
async def generate_video(body: VideoGenerateRequest):
    """
    生成最终视频

    添加字幕和音频生成最终视频
    """
    try:
        from backend.tools.video_generator import VideoGenerator, VideoAspect, VideoLengthPreset, VideoParams

        aspect_map = {
            "9:16": VideoAspect.PORTRAIT,
            "16:9": VideoAspect.LANDSCAPE,
            "1:1": VideoAspect.SQUARE,
        }

        length_map = {
            "short": VideoLengthPreset.SHORT,
            "medium": VideoLengthPreset.MEDIUM,
            "long": VideoLengthPreset.LONG,
            "custom": VideoLengthPreset.CUSTOM,
        }

        params = VideoParams(
            video_aspect=aspect_map.get(body.video_aspect, VideoAspect.PORTRAIT),
            video_length_preset=length_map.get(body.video_length, VideoLengthPreset.MEDIUM),
            video_clip_duration=body.video_clip_duration,
            subtitle_enabled=body.subtitle_enabled,
            bgm_type=body.bgm_type,
            bgm_volume=body.bgm_volume,
        )

        generator = VideoGenerator()
        output_path = body.output_path or os.path.join(
            generator.output_dir, f"final-{uuid.uuid4().hex[:8]}.mp4"
        )

        result = generator.generate_video(
            video_path=body.video_path,
            audio_path=body.audio_path,
            subtitle_path=body.subtitle_path,
            output_path=output_path,
            params=params,
        )

        return VideoGenerateResponse(
            success=result.success,
            video_path=result.video_path,
            duration=result.duration,
            error=result.error,
        )
    except Exception as e:
        logger.error("Generate video error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


class VideoBatchGenerateRequest(BaseModel):
    """批量视频生成请求"""
    videos: List[VideoGenerateRequest] = Field(..., description="视频生成请求列表")
    generate_count: int = Field(default=1, ge=1, le=10, description="每个配置生成的数量")


class VideoBatchGenerateResponse(BaseModel):
    """批量视频生成响应"""
    success: bool
    results: List[VideoGenerateResponse]
    total: int
    successful: int
    failed: int


@router.post("/video/batch-generate", response_model=VideoBatchGenerateResponse)
async def batch_generate_videos(body: VideoBatchGenerateRequest):
    """
    批量生成视频

    根据一组视频生成请求批量生成多个视频
    """
    from backend.tools.video_generator import VideoGenerator, VideoAspect, VideoLengthPreset, VideoParams

    results = []
    successful = 0
    failed = 0

    for video_req in body.videos:
        try:
            aspect_map = {
                "9:16": VideoAspect.PORTRAIT,
                "16:9": VideoAspect.LANDSCAPE,
                "1:1": VideoAspect.SQUARE,
            }

            length_map = {
                "short": VideoLengthPreset.SHORT,
                "medium": VideoLengthPreset.MEDIUM,
                "long": VideoLengthPreset.LONG,
                "custom": VideoLengthPreset.CUSTOM,
            }

            params = VideoParams(
                video_aspect=aspect_map.get(video_req.video_aspect, VideoAspect.PORTRAIT),
                video_length_preset=length_map.get(video_req.video_length, VideoLengthPreset.MEDIUM),
                video_clip_duration=video_req.video_clip_duration,
                subtitle_enabled=video_req.subtitle_enabled,
                bgm_type=video_req.bgm_type,
                bgm_volume=video_req.bgm_volume,
            )

            generator = VideoGenerator()
            output_path = video_req.output_path or os.path.join(
                generator.output_dir, f"final-{uuid.uuid4().hex[:8]}.mp4"
            )

            result = generator.generate_video(
                video_path=video_req.video_path,
                audio_path=video_req.audio_path,
                subtitle_path=video_req.subtitle_path,
                output_path=output_path,
                params=params,
            )

            if result.success:
                successful += 1
            else:
                failed += 1

            results.append(VideoGenerateResponse(
                success=result.success,
                video_path=result.video_path,
                duration=result.duration,
                error=result.error,
            ))
        except Exception as e:
            failed += 1
            results.append(VideoGenerateResponse(
                success=False,
                video_path="",
                duration=0.0,
                error="服务器内部错误，请稍后重试",
            ))

    return VideoBatchGenerateResponse(
        success=failed == 0,
        results=results,
        total=len(results),
        successful=successful,
        failed=failed,
    )


@router.get("/video/voices")
async def get_available_voices():
    """
    获取可用的声音列表

    返回 Edge TTS 支持的声音
    """
    try:
        from backend.services.voice import voice_service
        voices = voice_service.get_available_voices()
        return {
            "success": True,
            "voices": voices,
            "total": len(voices),
        }
    except Exception as e:
        logger.error("Get voices error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Local Materials Management =====

class MaterialUploadResponse(BaseModel):
    """素材上传响应"""
    success: bool
    file_path: str
    file_name: str
    file_size: int
    error: str = ""


class MaterialListResponse(BaseModel):
    """素材列表响应"""
    success: bool
    files: List[dict]
    total: int


@router.post("/materials/videos/upload", response_model=MaterialUploadResponse)
async def upload_video_material(file: UploadFile = File(...)):
    """
    上传本地视频素材

    支持 mp4, mov, avi 格式
    """
    try:
        # 验证文件类型
        allowed_types = ["video/mp4", "video/quicktime", "video/x-msvideo"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="不支持的文件类型，仅支持 mp4, mov, avi")

        # 创建上传目录
        upload_dir = os.path.join(os.getcwd(), "uploads", "videos")
        os.makedirs(upload_dir, exist_ok=True)

        # 生成安全文件名
        import uuid as uuid_lib
        safe_filename = f"{uuid_lib.uuid4().hex[:8]}_{file.filename}"
        file_path = os.path.join(upload_dir, safe_filename)

        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        return MaterialUploadResponse(
            success=True,
            file_path=file_path,
            file_name=file.filename,
            file_size=len(content),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Upload material error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/materials/videos", response_model=MaterialListResponse)
async def list_video_materials():
    """
    获取本地视频素材列表

    返回 uploads/videos 目录下的所有视频文件
    """
    try:
        upload_dir = os.path.join(os.getcwd(), "uploads", "videos")

        if not os.path.exists(upload_dir):
            return MaterialListResponse(success=True, files=[], total=0)

        files = []
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                ext = os.path.splitext(filename)[-1].lower()
                if ext in [".mp4", ".mov", ".avi", ".mkv"]:
                    stat = os.stat(file_path)
                    files.append({
                        "name": filename,
                        "path": file_path,
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                    })

        return MaterialListResponse(
            success=True,
            files=files,
            total=len(files),
        )

    except Exception as e:
        logger.error("List materials error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.delete("/materials/videos/{filename}")
async def delete_video_material(filename: str):
    """
    删除本地视频素材
    """
    try:
        upload_dir = os.path.join(os.getcwd(), "uploads", "videos")
        file_path = os.path.join(upload_dir, filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        os.remove(file_path)

        return {"success": True, "message": "文件已删除"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Delete material error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== BGM Management =====

class BgmListResponse(BaseModel):
    """BGM列表响应"""
    success: bool
    files: List[dict]
    total: int


@router.get("/materials/bgm", response_model=BgmListResponse)
async def list_bgm_materials():
    """
    获取背景音乐素材列表

    返回 resource/songs 目录下的所有音频文件
    """
    try:
        song_dirs = [
            os.path.join(os.getcwd(), "resource", "songs"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "_reference", "resource", "songs"),
        ]

        all_files = []
        for song_dir in song_dirs:
            if not os.path.exists(song_dir):
                continue

            for filename in os.listdir(song_dir):
                file_path = os.path.join(song_dir, filename)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(filename)[-1].lower()
                    if ext in [".mp3", ".wav", ".ogg", ".aac"]:
                        stat = os.stat(file_path)
                        all_files.append({
                            "name": filename,
                            "path": file_path,
                            "size": stat.st_size,
                            "source": "local" if song_dir == song_dirs[0] else "default",
                        })

        return BgmListResponse(
            success=True,
            files=all_files,
            total=len(all_files),
        )

    except Exception as e:
        logger.error("List BGM error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ===== Task Queue =====

class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    state: str
    progress: int
    created_at: str
    updated_at: str
    result: Dict[str, Any] = Field(default_factory=dict)
    error: str = ""


class TaskCreateRequest(BaseModel):
    """任务创建请求"""
    task_type: str = Field(..., description="任务类型: video_generate, batch_generate")
    params: Dict[str, Any] = Field(default_factory=dict, description="任务参数")


class TaskListResponse(BaseModel):
    """任务列表响应"""
    success: bool
    tasks: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int


@router.post("/tasks", response_model=Dict[str, Any])
async def create_task(body: TaskCreateRequest):
    """
    创建异步任务

    任务将在后台执行，可通过 /tasks/{task_id} 查询状态
    """
    try:
        from backend.services.task_queue import async_task_queue, video_generate_task

        task_id = await async_task_queue.submit_task(
            task_type=body.task_type,
            params=body.params,
            coro_func=video_generate_task if body.task_type == "video_generate" else None,
        )

        return {
            "success": True,
            "task_id": task_id,
            "message": f"任务已创建: {task_id}",
        }
    except Exception as e:
        logger.error("Create task error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    获取任务状态

    返回任务的当前状态、进度和结果
    """
    try:
        from backend.services.task_queue import async_task_queue, TaskState

        task = async_task_queue.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

        return TaskStatusResponse(
            task_id=task.task_id,
            state=task.state.value,
            progress=task.progress,
            created_at=task.created_at,
            updated_at=task.updated_at,
            result=task.result,
            error=task.error,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get task error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    state: str = Query(default=None, description="过滤状态: pending, processing, complete, failed"),
):
    """
    获取任务列表

    支持分页和状态过滤
    """
    try:
        from backend.services.task_queue import task_queue, TaskState

        state_filter = TaskState(state) if state else None
        tasks, total = task_queue.get_all_tasks(
            page=page,
            page_size=page_size,
            state=state_filter,
        )

        return TaskListResponse(
            success=True,
            tasks=[t.to_dict() for t in tasks],
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error("List tasks error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """
    删除任务
    """
    try:
        from backend.services.task_queue import task_queue, async_task_queue

        # 先取消正在运行的任务
        async_task_queue.cancel_task(task_id)
        # 删除任务记录
        success = task_queue.delete_task(task_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

        return {"success": True, "message": f"任务已删除: {task_id}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Delete task error")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ==================== Hashtag 推荐接口 ====================

class HashtagRequest(BaseModel):
    """Hashtag 推荐请求"""
    content: str = Field(..., min_length=1, max_length=5000, description="内容文本（标题+正文）")
    platform: str = Field(default="xiaohongshu", description="目标平台")
    amount: int = Field(default=10, ge=1, le=30, description="推荐数量")
    product_info: Optional[Dict[str, Any]] = Field(default=None, description="产品信息")

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v):
        valid_platforms = {"xiaohongshu", "tiktok", "official", "friend_circle"}
        if v not in valid_platforms:
            raise ValueError(f"Invalid platform: {v}")
        return v


class HashtagInfoModel(BaseModel):
    """Hashtag 信息模型"""
    tag: str
    category: str  # brand, industry, trending, emotional
    heat_score: int  # 0-100
    exposure: str  # 低/中/高
    reason: str  # 推荐理由


class HashtagCombinationModel(BaseModel):
    """Hashtag 组合方案模型"""
    name: str
    description: str
    hashtags: List[str]
    expected_exposure: str
    best_for: str


class HashtagRecommendResponse(BaseModel):
    """Hashtag 推荐响应"""
    success: bool
    hashtags: List[HashtagInfoModel]
    combinations: List[HashtagCombinationModel] = Field(default_factory=list, description="推荐组合方案")
    detected_industry: str = Field(default="", description="检测到的行业")


class TrendingHashtagRequest(BaseModel):
    """热门 Hashtag 请求"""
    platform: str = Field(default="xiaohongshu", description="目标平台")
    industry: Optional[str] = Field(default=None, description="行业分类")
    amount: int = Field(default=10, ge=1, le=50, description="推荐数量")


@router.post("/hashtags/recommend", response_model=HashtagRecommendResponse)
async def recommend_hashtags(request: HashtagRequest):
    """
    智能推荐 Hashtag

    根据内容分析自动推荐最佳 hashtag，支持：
    - 小红书 hashtag 推荐
    - 抖音 hashtag 推荐
    - 公众号 hashtag 推荐
    - 多语言混搭推荐
    """
    try:
        from backend.services.hashtag import hashtag_service

        # 调用服务获取推荐
        hashtags = await hashtag_service.recommend_hashtags(
            content=request.content,
            platform=request.platform,
            amount=request.amount,
            product_info=request.product_info,
        )

        # 获取组合方案
        tag_strings = [h.tag for h in hashtags]
        combinations = hashtag_service.suggest_hashtag_combinations(
            hashtags=tag_strings,
            platform=request.platform,
        )

        # 检测行业
        from backend.services.hashtag import hashtag_service as hs
        industry = hs._detect_industry(request.content, request.product_info) if hasattr(hs, '_detect_industry') else ""

        return HashtagRecommendResponse(
            success=True,
            hashtags=[HashtagInfoModel(
                tag=h.tag,
                category=h.category,
                heat_score=h.heat_score,
                exposure=h.exposure,
                reason=h.reason,
            ) for h in hashtags],
            combinations=[HashtagCombinationModel(**c) for c in combinations],
            detected_industry=industry,
        )

    except Exception as e:
        logger.error(f"Hashtag 推荐失败: {e}")
        return HashtagRecommendResponse(
            success=False,
            hashtags=[],
            combinations=[],
            detected_industry="",
        )


@router.post("/hashtags/trending", response_model=HashtagRecommendResponse)
async def get_trending_hashtags(request: TrendingHashtagRequest):
    """
    获取平台热门 Hashtag

    返回当前平台上最热门的 hashtag 列表
    """
    try:
        from backend.services.hashtag import hashtag_service

        hashtags = hashtag_service.get_trending_hashtags(
            platform=request.platform,
            industry=request.industry,
            amount=request.amount,
        )

        # 获取组合方案
        tag_strings = [h.tag for h in hashtags]
        combinations = hashtag_service.suggest_hashtag_combinations(
            hashtags=tag_strings,
            platform=request.platform,
        )

        return HashtagRecommendResponse(
            success=True,
            hashtags=[HashtagInfoModel(
                tag=h.tag,
                category=h.category,
                heat_score=h.heat_score,
                exposure=h.exposure,
                reason=h.reason,
            ) for h in hashtags],
            combinations=[HashtagCombinationModel(**c) for c in combinations],
            detected_industry=request.industry or "通用",
        )

    except Exception as e:
        logger.error(f"获取热门 Hashtag 失败: {e}")
        return HashtagRecommendResponse(
            success=False,
            hashtags=[],
            combinations=[],
            detected_industry="",
        )


# ==================== 最佳发布时间接口 ====================

class PostingTimeRequest(BaseModel):
    """发布时间建议请求"""
    platform: str = Field(default="xiaohongshu", description="目标平台")
    industry: str = Field(default="通用", description="所属行业")
    days_ahead: int = Field(default=7, ge=1, le=30, description="提前多少天建议")


class TimeSlotModel(BaseModel):
    """时间段模型"""
    time: str
    day_of_week: str
    score: int
    exposure: str
    engagement: str
    reason: str


class PostingTimeResponse(BaseModel):
    """发布时间建议响应"""
    success: bool
    platform: str
    industry: str
    best_times: List[TimeSlotModel]
    worst_times: List[TimeSlotModel]
    tips: List[str]


class WeeklySummaryRequest(BaseModel):
    """每周汇总请求"""
    platform: str = Field(default="xiaohongshu", description="目标平台")
    industry: str = Field(default="通用", description="所属行业")


class WeeklySummaryDayModel(BaseModel):
    """每周每日汇总模型"""
    best_hour: str
    best_hour_name: str
    score: int
    is_weekend: bool


class WeeklySummaryResponse(BaseModel):
    """每周汇总响应"""
    success: bool
    platform: str
    industry: str
    weekly_data: Dict[str, WeeklySummaryDayModel]


@router.post("/posting-time/suggest", response_model=PostingTimeResponse)
async def get_posting_time_suggestions(request: PostingTimeRequest):
    """
    获取最佳发布时间建议

    基于平台特性和行业规律，计算并返回最佳发布时间建议
    """
    try:
        from backend.services.posting_time import posting_time_service

        result = posting_time_service.get_suggestions(
            platform=request.platform,
            industry=request.industry,
            days_ahead=request.days_ahead,
        )

        return PostingTimeResponse(
            success=True,
            platform=result.platform,
            industry=result.industry,
            best_times=[TimeSlotModel(
                time=slot.time,
                day_of_week=slot.day_of_week,
                score=slot.score,
                exposure=slot.exposure,
                engagement=slot.engagement,
                reason=slot.reason,
            ) for slot in result.best_times],
            worst_times=[TimeSlotModel(
                time=slot.time,
                day_of_week=slot.day_of_week,
                score=slot.score,
                exposure=slot.exposure,
                engagement=slot.engagement,
                reason=slot.reason,
            ) for slot in result.worst_times],
            tips=result.tips,
        )

    except Exception as e:
        logger.error(f"获取发布时间建议失败: {e}")
        return PostingTimeResponse(
            success=False,
            platform=request.platform,
            industry=request.industry,
            best_times=[],
            worst_times=[],
            tips=["服务器错误，请稍后重试"],
        )


@router.post("/posting-time/weekly", response_model=WeeklySummaryResponse)
async def get_weekly_summary(request: WeeklySummaryRequest):
    """
    获取每周时段汇总

    返回周一到周日每天的最佳发布时间
    """
    try:
        from backend.services.posting_time import posting_time_service

        result = posting_time_service.get_weekly_summary(
            platform=request.platform,
            industry=request.industry,
        )

        return WeeklySummaryResponse(
            success=True,
            platform=request.platform,
            industry=request.industry,
            weekly_data={
                day: WeeklySummaryDayModel(**info)
                for day, info in result.items()
            },
        )

    except Exception as e:
        logger.error(f"获取每周汇总失败: {e}")
        return WeeklySummaryResponse(
            success=False,
            platform=request.platform,
            industry=request.industry,
            weekly_data={},
        )


# ==================== 标题 A/B 测试接口 ====================

class TitleABTestRequest(BaseModel):
    """标题A/B测试请求"""
    content: str = Field(..., min_length=1, max_length=5000, description="原始内容")
    platform: str = Field(default="xiaohongshu", description="目标平台")
    amount: int = Field(default=6, ge=3, le=12, description="生成数量")
    product_info: Optional[Dict[str, Any]] = Field(default=None, description="产品信息")


class TitleVariationModel(BaseModel):
    """标题变体模型"""
    title: str
    style: str
    emoji_used: bool
    length: int
    ctr_score: int
    engagement_score: int
    strengths: List[str]
    weaknesses: List[str]


class TitleABTestResponse(BaseModel):
    """标题A/B测试响应"""
    success: bool
    variations: List[TitleVariationModel]
    best_title: Optional[TitleVariationModel] = None
    recommendation: str = ""


@router.post("/title/abtest", response_model=TitleABTestResponse)
async def generate_title_abtest(request: TitleABTestRequest):
    """
    生成标题 A/B 测试变体

    为同一内容生成多个不同风格的标题，并提供点击率和互动率预估
    """
    try:
        from backend.services.title_generator import title_abtest_service

        variations = await title_abtest_service.generate_variations(
            content=request.content,
            platform=request.platform,
            amount=request.amount,
            product_info=request.product_info,
        )

        # 获取最佳标题推荐
        comparison = title_abtest_service.compare_variations(variations)

        return TitleABTestResponse(
            success=True,
            variations=[TitleVariationModel(
                title=v.title,
                style=v.style,
                emoji_used=v.emoji_used,
                length=v.length,
                ctr_score=v.ctr_score,
                engagement_score=v.engagement_score,
                strengths=v.strengths,
                weaknesses=v.weaknesses,
            ) for v in variations],
            best_title=TitleVariationModel(
                title=comparison["best_title"].title,
                style=comparison["best_title"].style,
                emoji_used=comparison["best_title"].emoji_used,
                length=comparison["best_title"].length,
                ctr_score=comparison["best_title"].ctr_score,
                engagement_score=comparison["best_title"].engagement_score,
                strengths=comparison["best_title"].strengths,
                weaknesses=comparison["best_title"].weaknesses,
            ) if comparison.get("best_title") else None,
            recommendation=comparison.get("recommendation", ""),
        )

    except Exception as e:
        logger.error(f"标题A/B测试生成失败: {e}")
        return TitleABTestResponse(
            success=False,
            variations=[],
            recommendation="服务器错误，请稍后重试",
        )


# ==================== 内容改写/仿写接口 ====================

class ContentRewriteRequest(BaseModel):
    """内容改写请求"""
    content: str = Field(..., min_length=1, max_length=5000, description="原始内容")
    platform: str = Field(default="xiaohongshu", description="目标平台")
    rewrite_style: str = Field(
        default="variation",
        description="改写风格: variation(变换句式), expand(扩展内容), shorten(精简内容), formal(正式化), casual(口语化)"
    )
    product_info: Optional[Dict[str, Any]] = Field(default=None, description="产品信息")


class ContentRewriteResponse(BaseModel):
    """内容改写响应"""
    success: bool
    original_content: str
    rewritten_content: str
    style_applied: str
    changes_made: List[str]


@router.post("/content/rewrite", response_model=ContentRewriteResponse)
async def rewrite_content(request: ContentRewriteRequest):
    """
    改写/仿写内容

    支持多种改写风格：变换句式、扩展内容、精简内容、正式化、口语化
    """
    try:
        from backend.services.llm import llm_service

        product_context = ""
        if request.product_info:
            product_context = f"""
产品信息：
- 名称：{request.product_info.get('name', '')}
- 卖点：{', '.join(request.product_info.get('selling_points', []))}
"""

        style_descriptions = {
            "variation": "保持相同意思但完全不同的表达方式",
            "expand": "在原有内容基础上增加细节和描述",
            "shorten": "精简内容，保留核心要点",
            "formal": "改为更正式、专业的表达",
            "casual": "改为更口语化、亲切的表达",
        }

        prompt = f"""请将以下内容进行改写。

原始内容：
{request.content}
{product_context}

改写风格：{style_descriptions.get(request.rewrite_style, '变换句式')}

要求：
1. 保持原有内容的核心信息不变
2. 完全改变表达方式，避免重复
3. 适合在{request.platform}平台发布
4. 返回JSON格式，包含以下字段：
   - rewritten_content: 改写后的内容
   - changes_made: 说明做了哪些改变（数组形式）

输出格式：
{{"rewritten_content": "...", "changes_made": ["改变1", "改变2", ...]}}"""

        response = llm_service.generate(prompt)

        if response.startswith("Error:"):
            raise Exception(response)

        import json
        import re

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            match = re.search(r'\{.*}', response, re.DOTALL)
            if match:
                result = json.loads(match.group())
            else:
                raise Exception("无法解析响应")

        return ContentRewriteResponse(
            success=True,
            original_content=request.content,
            rewritten_content=result.get("rewritten_content", request.content),
            style_applied=request.rewrite_style,
            changes_made=result.get("changes_made", []),
        )

    except Exception as e:
        logger.error(f"内容改写失败: {e}")
        return ContentRewriteResponse(
            success=False,
            original_content=request.content,
            rewritten_content=request.content,
            style_applied=request.rewrite_style,
            changes_made=["改写失败，请稍后重试"],
        )


# ==================== 图片生成接口 ====================

class ImageGenerateRequest(BaseModel):
    """图片生成请求"""
    prompt: str = Field(..., min_length=1, max_length=500, description="图片描述")
    style: str = Field(default="modern", description="风格: modern/minimal/lifestyle/product/natural/vivid")
    size: str = Field(default="square", description="尺寸: square/portrait/landscape/wide")
    save_local: bool = Field(default=False, description="是否保存到本地")


class ImageGenerateResponse(BaseModel):
    """图片生成响应"""
    success: bool
    url: str
    local_path: str = ""
    prompt: str
    style: str
    width: int
    height: int


@router.post("/image/generate", response_model=ImageGenerateResponse)
async def generate_image(request: ImageGenerateRequest):
    """
    使用 Pollinations AI 生成图片

    Pollinations 是一个免费的 AI 图片生成服务
    """
    try:
        from backend.tools.image_gen import ImageGenerator

        generator = ImageGenerator()

        if request.save_local:
            result = generator.save_image(request.prompt, request.style, request.size)
        else:
            result = generator.generate_image(request.prompt, request.style, request.size)

        return ImageGenerateResponse(
            success=result.success,
            url=result.url,
            local_path=result.local_path,
            prompt=result.prompt,
            style=result.style,
            width=result.width,
            height=result.height,
        )

    except Exception as e:
        logger.error(f"图片生成失败: {e}")
        return ImageGenerateResponse(
            success=False,
            url="",
            prompt=request.prompt,
            style=request.style,
            width=1024,
            height=1024,
        )


# ==================== 多语言翻译接口 ====================

class TranslationRequest(BaseModel):
    """翻译请求"""
    content: str = Field(..., min_length=1, max_length=5000, description="待翻译内容")
    target_lang: str = Field(default="en", description="目标语言: en/ja/ko/es/fr/de")
    source_lang: str = Field(default="auto", description="源语言: auto/zh/en/ja/ko")


class TranslationResponse(BaseModel):
    """翻译响应"""
    success: bool
    original: str
    translated: str
    source_lang: str
    target_lang: str


@router.post("/translate", response_model=TranslationResponse)
async def translate_content(request: TranslationRequest):
    """
    多语言翻译接口

    支持中文、英文、日语、韩语、西班牙语、法语、德语等
    """
    try:
        from backend.services.llm import llm_service

        lang_names = {
            "en": "英文",
            "ja": "日文",
            "ko": "韩文",
            "es": "西班牙文",
            "fr": "法文",
            "de": "德文",
            "zh": "中文",
        }

        prompt = f"""请将以下内容翻译成{lang_names.get(request.target_lang, request.target_lang)}。

原文：
{request.content}

要求：
1. 保持原文风格和语气
2. 符合目标语言的表达习惯
3. 只返回翻译结果，不要解释

直接输出翻译后的内容："""

        translated = llm_service.generate(prompt)

        if translated.startswith("Error:"):
            raise Exception(translated)

        return TranslationResponse(
            success=True,
            original=request.content,
            translated=translated.strip(),
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )

    except Exception as e:
        logger.error(f"翻译失败: {e}")
        return TranslationResponse(
            success=False,
            original=request.content,
            translated=request.content,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )


# ==================== 内容模板接口 ====================

class ContentTemplateRequest(BaseModel):
    """内容模板请求"""
    platform: str = Field(default="xiaohongshu", description="目标平台")
    content_type: str = Field(default="product", description="内容类型: product/promotion/story/tips")
    product_info: Optional[Dict[str, Any]] = Field(default=None, description="产品信息")
    tone: str = Field(default="friendly", description="语气: friendly/professional/casual/humorous")


class ContentTemplateResponse(BaseModel):
    """内容模板响应"""
    success: bool
    platform: str
    content_type: str
    template: str
    placeholders: List[str]
    examples: List[str]


@router.post("/content/template", response_model=ContentTemplateResponse)
async def get_content_template(request: ContentTemplateRequest):
    """
    获取内容模板

    返回适合特定平台和内容类型的文案模板
    """
    try:
        from backend.services.llm import llm_service

        product_context = ""
        if request.product_info:
            product_context = f"""
产品信息：
- 名称：{request.product_info.get('name', '')}
- 描述：{request.product_info.get('description', '')}
- 卖点：{', '.join(request.product_info.get('selling_points', []))}
"""

        tone_descriptions = {
            "friendly": "友好、亲切、像朋友推荐",
            "professional": "专业、正式、有权威感",
            "casual": "轻松、随意、生活化",
            "humorous": "幽默、风趣、有梗",
        }

        content_type_descriptions = {
            "product": "产品种草/推荐",
            "promotion": "促销活动/优惠信息",
            "story": "品牌故事/用户故事",
            "tips": "使用技巧/干货分享",
        }

        prompt = f"""请为以下场景生成一个文案模板。

平台：{request.platform}
内容类型：{content_type_descriptions.get(request.content_type, request.content_type)}
语气风格：{tone_descriptions.get(request.tone, request.tone)}
{product_context}

要求：
1. 提供一个完整的文案模板
2. 用 {{placeholder}} 标记需要替换的内容
3. 模板要适合在{request.platform}发布
4. 提供2个使用该模板的示例

返回JSON格式：
{{"template": "模板内容...", "placeholders": ["placeholder1", "placeholder2"], "examples": ["示例1", "示例2"]}}"""

        response = llm_service.generate(prompt)

        if response.startswith("Error:"):
            raise Exception(response)

        import json
        import re

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            match = re.search(r'\{.*}', response, re.DOTALL)
            if match:
                result = json.loads(match.group())
            else:
                raise Exception("无法解析响应")

        return ContentTemplateResponse(
            success=True,
            platform=request.platform,
            content_type=request.content_type,
            template=result.get("template", ""),
            placeholders=result.get("placeholders", []),
            examples=result.get("examples", []),
        )

    except Exception as e:
        logger.error(f"获取内容模板失败: {e}")
        return ContentTemplateResponse(
            success=False,
            platform=request.platform,
            content_type=request.content_type,
            template="",
            placeholders=[],
            examples=[],
        )


# ==================== 内容质量评分接口 ====================

class ContentScoreRequest(BaseModel):
    """内容评分请求"""
    content: str = Field(..., min_length=1, max_length=5000, description="文案内容")
    platform: str = Field(default="xiaohongshu", description="目标平台")
    title: str = Field(default="", description="标题")
    tags: Optional[List[str]] = Field(default=None, description="标签列表")


class ContentScoreResponse(BaseModel):
    """内容评分响应"""
    success: bool
    overall_score: int
    engagement_score: int
    compliance_score: int
    readability_score: int
    seo_score: int
    platform_fit_score: int
    score_level: str  # 优秀/良好/一般/较差
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]


@router.post("/content/score", response_model=ContentScoreResponse)
async def score_content(request: ContentScoreRequest):
    """
    内容质量评分

    对文案进行多维度分析并评分：
    - 吸引力 (engagement)
    - 合规性 (compliance)
    - 可读性 (readability)
    - SEO友好度 (seo)
    - 平台适配 (platform_fit)
    """
    try:
        from backend.services.content_scorer import content_scorer_service

        result = await content_scorer_service.score_content(
            content=request.content,
            platform=request.platform,
            title=request.title,
            tags=request.tags,
        )

        return ContentScoreResponse(
            success=True,
            overall_score=result.overall_score,
            engagement_score=result.engagement_score,
            compliance_score=result.compliance_score,
            readability_score=result.readability_score,
            seo_score=result.seo_score,
            platform_fit_score=result.platform_fit_score,
            score_level=content_scorer_service.get_score_level(result.overall_score),
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            suggestions=result.suggestions,
        )

    except Exception as e:
        logger.error(f"内容评分失败: {e}")
        return ContentScoreResponse(
            success=False,
            overall_score=0,
            engagement_score=0,
            compliance_score=0,
            readability_score=0,
            seo_score=0,
            platform_fit_score=0,
            score_level="错误",
            strengths=[],
            weaknesses=["评分服务异常"],
            suggestions=["请稍后重试"],
        )


# ==================== 内容历史记录接口 ====================

class ContentHistoryAddRequest(BaseModel):
    """添加内容历史请求"""
    platform: str = Field(..., description="平台")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    product_name: str = Field(default="", description="产品名称")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")
    is_draft: bool = Field(default=False, description="是否为草稿")


class ContentHistoryUpdateRequest(BaseModel):
    """更新内容历史请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    is_draft: Optional[bool] = None


class ContentHistorySearchRequest(BaseModel):
    """搜索内容历史请求"""
    keyword: str = Field(default="", description="关键词")
    platform: str = Field(default="", description="平台筛选")
    is_draft: Optional[bool] = Field(default=None, description="草稿筛选")
    limit: int = Field(default=20, ge=1, le=100, description="返回数量")


class ContentHistoryRecord(BaseModel):
    """内容历史记录模型"""
    id: str
    platform: str
    title: str
    content: str
    tags: List[str]
    created_at: str
    updated_at: str
    is_draft: bool
    product_name: str
    metadata: Dict[str, Any]


class ContentHistoryResponse(BaseModel):
    """内容历史响应"""
    success: bool
    records: List[ContentHistoryRecord] = Field(default_factory=list)
    total: int = 0
    stats: Optional[Dict[str, Any]] = None


@router.post("/content/history", response_model=ContentHistoryResponse)
async def add_content_history(request: ContentHistoryAddRequest):
    """
    添加内容历史记录

    将生成的内容保存到历史记录中
    """
    try:
        from backend.services.content_history import content_history_service

        record_id = content_history_service.add_record(
            platform=request.platform,
            title=request.title,
            content=request.content,
            tags=request.tags,
            product_name=request.product_name,
            metadata=request.metadata,
            is_draft=request.is_draft,
        )

        return ContentHistoryResponse(
            success=True,
            records=[ContentHistoryRecord(
                id=record_id,
                platform=request.platform,
                title=request.title,
                content=request.content,
                tags=request.tags,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                is_draft=request.is_draft,
                product_name=request.product_name,
                metadata=request.metadata or {},
            )],
            total=1,
        )

    except Exception as e:
        logger.error(f"添加内容历史失败: {e}")
        return ContentHistoryResponse(
            success=False,
            records=[],
            total=0,
        )


@router.get("/content/history", response_model=ContentHistoryResponse)
async def get_content_history(
    keyword: str = Query(default="", description="关键词搜索"),
    platform: str = Query(default="", description="平台筛选"),
    is_draft: Optional[bool] = Query(default=None, description="草稿筛选"),
    limit: int = Query(default=20, ge=1, le=100, description="返回数量"),
):
    """
    获取内容历史记录

    支持关键词搜索、平台筛选、草稿筛选
    """
    try:
        from backend.services.content_history import content_history_service

        records = content_history_service.search_records(
            keyword=keyword,
            platform=platform,
            is_draft=is_draft,
            limit=limit,
        )

        return ContentHistoryResponse(
            success=True,
            records=[ContentHistoryRecord(
                id=r.id,
                platform=r.platform,
                title=r.title,
                content=r.content,
                tags=r.tags,
                created_at=r.created_at,
                updated_at=r.updated_at,
                is_draft=r.is_draft,
                product_name=r.product_name,
                metadata=r.metadata or {},
            ) for r in records],
            total=len(records),
            stats=content_history_service.get_stats(),
        )

    except Exception as e:
        logger.error(f"获取内容历史失败: {e}")
        return ContentHistoryResponse(
            success=False,
            records=[],
            total=0,
        )


@router.get("/content/history/{record_id}", response_model=ContentHistoryResponse)
async def get_content_history_record(record_id: str):
    """
    获取单条内容历史记录

    根据ID获取详细内容
    """
    try:
        from backend.services.content_history import content_history_service

        record = content_history_service.get_record(record_id)

        if not record:
            raise HTTPException(status_code=404, detail="记录不存在")

        return ContentHistoryResponse(
            success=True,
            records=[ContentHistoryRecord(
                id=record.id,
                platform=record.platform,
                title=record.title,
                content=record.content,
                tags=record.tags,
                created_at=record.created_at,
                updated_at=record.updated_at,
                is_draft=record.is_draft,
                product_name=record.product_name,
                metadata=record.metadata or {},
            )],
            total=1,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取内容历史记录失败: {e}")
        return ContentHistoryResponse(
            success=False,
            records=[],
            total=0,
        )


@router.put("/content/history/{record_id}", response_model=ContentHistoryResponse)
async def update_content_history_record(
    record_id: str,
    request: ContentHistoryUpdateRequest,
):
    """
    更新内容历史记录

    更新指定记录的标题、内容、标签等
    """
    try:
        from backend.services.content_history import content_history_service

        success = content_history_service.update_record(
            record_id=record_id,
            title=request.title,
            content=request.content,
            tags=request.tags,
            is_draft=request.is_draft,
        )

        if not success:
            raise HTTPException(status_code=404, detail="记录不存在")

        record = content_history_service.get_record(record_id)

        return ContentHistoryResponse(
            success=True,
            records=[ContentHistoryRecord(
                id=record.id,
                platform=record.platform,
                title=record.title,
                content=record.content,
                tags=record.tags,
                created_at=record.created_at,
                updated_at=record.updated_at,
                is_draft=record.is_draft,
                product_name=record.product_name,
                metadata=record.metadata or {},
            )] if record else [],
            total=1 if record else 0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新内容历史失败: {e}")
        return ContentHistoryResponse(
            success=False,
            records=[],
            total=0,
        )


@router.delete("/content/history/{record_id}")
async def delete_content_history_record(record_id: str):
    """
    删除内容历史记录

    删除指定的 历史记录
    """
    try:
        from backend.services.content_history import content_history_service

        success = content_history_service.delete_record(record_id)

        if not success:
            raise HTTPException(status_code=404, detail="记录不存在")

        return {"success": True, "message": "记录已删除"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除内容历史失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.get("/content/history/stats/summary")
async def get_content_history_stats():
    """
    获取内容历史统计信息

    返回总数、草稿数、已发布数、各平台统计
    """
    try:
        from backend.services.content_history import content_history_service

        stats = content_history_service.get_stats()

        return {
            "success": True,
            "stats": stats,
        }

    except Exception as e:
        logger.error(f"获取内容历史统计失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# ==================== 内容再利用接口 ====================

class ContentRepurposeRequest(BaseModel):
    """内容再利用请求"""
    content: str = Field(..., min_length=1, max_length=10000, description="原始内容")
    source_platform: str = Field(default="xiaohongshu", description="来源平台")
    target_platforms: List[str] = Field(..., description="目标平台列表")
    content_type: str = Field(default="auto", description="内容类型: auto/thread/article/script")
    preserve_key_points: bool = Field(default=True, description="是否保留关键点")


class RepurposedContentModel(BaseModel):
    """再利用后的内容模型"""
    platform: str
    content_type: str
    title: str
    content: str
    key_points: List[str]
    adaptations: List[str]


class ContentRepurposeResponse(BaseModel):
    """内容再利用响应"""
    success: bool
    repurposed_contents: List[RepurposedContentModel]
    total: int


class ContentToThreadRequest(BaseModel):
    """内容扩展为Thread请求"""
    content: str = Field(..., min_length=1, max_length=5000, description="原始内容")
    platform: str = Field(default="weibo", description="目标平台")


class ContentToThreadResponse(BaseModel):
    """内容扩展为Thread响应"""
    success: bool
    tweets: List[str]
    total: int


class ContentCondenseRequest(BaseModel):
    """内容压缩请求"""
    content: str = Field(..., min_length=1, max_length=10000, description="原始内容")
    max_length: int = Field(default=150, ge=50, le=500, description="最大长度")


class ContentCondenseResponse(BaseModel):
    """内容压缩响应"""
    success: bool
    condensed: str
    original_length: int
    condensed_length: int


@router.post("/content/repurpose", response_model=ContentRepurposeResponse)
async def repurpose_content(request: ContentRepurposeRequest):
    """
    内容跨平台再利用

    将一篇内容改写成适合不同平台的版本
    """
    try:
        from backend.services.content_repurposer import content_repurposer_service

        results = await content_repurposer_service.repurpose_content(
            content=request.content,
            source_platform=request.source_platform,
            target_platforms=request.target_platforms,
            content_type=request.content_type,
            preserve_key_points=request.preserve_key_points,
        )

        return ContentRepurposeResponse(
            success=True,
            repurposed_contents=[RepurposedContentModel(
                platform=r.platform,
                content_type=r.content_type,
                title=r.title,
                content=r.content,
                key_points=r.key_points,
                adaptations=r.adaptations,
            ) for r in results],
            total=len(results),
        )

    except Exception as e:
        logger.error(f"内容再利用失败: {e}")
        return ContentRepurposeResponse(
            success=False,
            repurposed_contents=[],
            total=0,
        )


@router.post("/content/expand-thread", response_model=ContentToThreadResponse)
async def expand_to_thread(request: ContentToThreadRequest):
    """
    将内容扩展为 Thread

    将一篇内容改写为一个Thread（多条推文）
    """
    try:
        from backend.services.content_repurposer import content_repurposer_service

        tweets = content_repurposer_service.expand_to_thread(
            content=request.content,
            platform=request.platform,
        )

        return ContentToThreadResponse(
            success=True,
            tweets=tweets,
            total=len(tweets),
        )

    except Exception as e:
        logger.error(f"扩展为Thread失败: {e}")
        return ContentToThreadResponse(
            success=False,
            tweets=[],
            total=0,
        )


@router.post("/content/condense", response_model=ContentCondenseResponse)
async def condense_content(request: ContentCondenseRequest):
    """
    压缩内容

    将长内容压缩为简短版本
    """
    try:
        from backend.services.content_repurposer import content_repurposer_service

        condensed = content_repurposer_service.condense_to_brief(
            content=request.content,
            max_length=request.max_length,
        )

        return ContentCondenseResponse(
            success=True,
            condensed=condensed,
            original_length=len(request.content),
            condensed_length=len(condensed),
        )

    except Exception as e:
        logger.error(f"压缩内容失败: {e}")
        return ContentCondenseResponse(
            success=False,
            condensed=request.content[:request.max_length],
            original_length=len(request.content),
            condensed_length=request.max_length,
        )


# ==================== 内容简报接口 ====================

class ContentBriefingRequest(BaseModel):
    """内容简报请求"""
    product_name: str = Field(default="", description="产品名称")
    product_description: str = Field(default="", description="产品描述")
    selling_points: List[str] = Field(default_factory=list, description="卖点列表")
    target_users: List[str] = Field(default_factory=list, description="目标用户列表")
    category: str = Field(default="", description="产品类别")
    competitors: str = Field(default="", description="竞品信息")
    goals: str = Field(default="", description="内容目标")


class ContentBriefingResponse(BaseModel):
    """内容简报响应"""
    success: bool
    title: str
    summary: str
    target_audience: List[str]
    key_messages: List[str]
    recommended_angles: List[str]
    platform_recommendations: Dict[str, str]
    content_formats: List[str]
    hashtags_suggestions: List[str]
    posting_time_suggestions: str
    competitors_analysis: str
    call_to_action: str


@router.post("/content/briefing", response_model=ContentBriefingResponse)
async def generate_content_briefing(request: ContentBriefingRequest):
    """
    生成内容简报

    基于产品信息生成完整的内容营销简报
    """
    try:
        from backend.services.content_briefing import content_briefing_service

        briefing = await content_briefing_service.generate_briefing(
            product_name=request.product_name,
            product_description=request.product_description,
            selling_points=request.selling_points,
            target_users=request.target_users,
            category=request.category,
            competitors=request.competitors,
            goals=request.goals,
        )

        return ContentBriefingResponse(
            success=True,
            title=briefing.title,
            summary=briefing.summary,
            target_audience=briefing.target_audience,
            key_messages=briefing.key_messages,
            recommended_angles=briefing.recommended_angles,
            platform_recommendations=briefing.platform_recommendations,
            content_formats=briefing.content_formats,
            hashtags_suggestions=briefing.hashtags_suggestions,
            posting_time_suggestions=briefing.posting_time_suggestions,
            competitors_analysis=briefing.competitors_analysis,
            call_to_action=briefing.call_to_action,
        )

    except Exception as e:
        logger.error(f"生成内容简报失败: {e}")
        return ContentBriefingResponse(
            success=False,
            title="",
            summary="生成失败",
            target_audience=[],
            key_messages=[],
            recommended_angles=[],
            platform_recommendations={},
            content_formats=[],
            hashtags_suggestions=[],
            posting_time_suggestions="",
            competitors_analysis="",
            call_to_action="",
        )


# ==================== 评论生成接口 ====================

class CommentGenerateRequest(BaseModel):
    """评论生成请求"""
    content: str = Field(default="", description="目标内容")
    content_type: str = Field(default="post", description="内容类型: post/video/product/review")
    platform: str = Field(default="xiaohongshu", description="目标平台")
    num_comments: int = Field(default=5, ge=1, le=20, description="生成数量")
    tone: str = Field(default="auto", description="语气: auto/friendly/professional/humorous/empathetic")


class CommentOptionModel(BaseModel):
    """评论选项模型"""
    text: str
    tone: str
    engagement_score: int
    emoji_used: bool


class CommentGenerateResponse(BaseModel):
    """评论生成响应"""
    success: bool
    comments: List[CommentOptionModel]
    total: int


class CommentReplyRequest(BaseModel):
    """评论回复请求"""
    original_comment: str = Field(..., description="原始评论")
    platform: str = Field(default="xiaohongshu", description="平台")
    tone: str = Field(default="friendly", description="语气")


class CommentReplyResponse(BaseModel):
    """评论回复响应"""
    success: bool
    reply: str


class CommentStrategyResponse(BaseModel):
    """评论策略响应"""
    success: bool
    platform: str
    best_times: List[str]
    response_rate: str
    tips: List[str]
    avoid: List[str]


@router.post("/comments/generate", response_model=CommentGenerateResponse)
async def generate_comments(request: CommentGenerateRequest):
    """
    生成评论选项

    为帖子/视频/产品生成多条互动评论
    """
    try:
        from backend.services.comment_generator import comment_generator_service

        comments = await comment_generator_service.generate_comments(
            content=request.content,
            content_type=request.content_type,
            platform=request.platform,
            num_comments=request.num_comments,
            tone=request.tone,
        )

        return CommentGenerateResponse(
            success=True,
            comments=[CommentOptionModel(
                text=c.text,
                tone=c.tone,
                engagement_score=c.engagement_score,
                emoji_used=c.emoji_used,
            ) for c in comments],
            total=len(comments),
        )

    except Exception as e:
        logger.error(f"生成评论失败: {e}")
        return CommentGenerateResponse(
            success=False,
            comments=[],
            total=0,
        )


@router.post("/comments/reply", response_model=CommentReplyResponse)
async def generate_comment_reply(request: CommentReplyRequest):
    """
    生成评论回复

    为已有评论生成得体的回复
    """
    try:
        from backend.services.comment_generator import comment_generator_service

        reply = await comment_generator_service.generate_reply(
            original_comment=request.original_comment,
            platform=request.platform,
            tone=request.tone,
        )

        return CommentReplyResponse(
            success=True,
            reply=reply,
        )

    except Exception as e:
        logger.error(f"生成回复失败: {e}")
        return CommentReplyResponse(
            success=False,
            reply="感谢回复！",
        )


@router.get("/comments/strategy/{platform}", response_model=CommentStrategyResponse)
async def get_comment_strategy(platform: str):
    """
    获取评论策略

    获取指定平台的评论最佳实践
    """
    try:
        from backend.services.comment_generator import comment_generator_service

        strategy = comment_generator_service.get_comment_strategy(platform)

        return CommentStrategyResponse(
            success=True,
            platform=platform,
            best_times=strategy.get("best_times", []),
            response_rate=strategy.get("response_rate", "中"),
            tips=strategy.get("tips", []),
            avoid=strategy.get("avoid", []),
        )

    except Exception as e:
        logger.error(f"获取评论策略失败: {e}")
        return CommentStrategyResponse(
            success=False,
            platform=platform,
            best_times=[],
            response_rate="中",
            tips=[],
            avoid=[],
        )


# ==================== 热门话题分析接口 ====================

class TrendingTopicsRequest(BaseModel):
    """热门话题分析请求"""
    platform: str = Field(default="xiaohongshu", description="目标平台")
    category: str = Field(default="", description="话题分类")
    num_topics: int = Field(default=10, ge=1, le=30, description="返回数量")


class TrendingTopicModel(BaseModel):
    """热门话题模型"""
    topic: str
    platform: str
    heat_score: int
    category: str
    description: str
    related_hashtags: List[str]
    best_posting_time: str
    growth_trend: str


class TrendingTopicsResponse(BaseModel):
    """热门话题分析响应"""
    success: bool
    topics: List[TrendingTopicModel]
    total: int


class TopicTrendRequest(BaseModel):
    """话题趋势预测请求"""
    topic: str = Field(..., description="话题名称")
    platform: str = Field(default="xiaohongshu", description="平台")


class TopicTrendResponse(BaseModel):
    """话题趋势预测响应"""
    success: bool
    topic: str
    trend_prediction: str
    peak_time: str
    best_timing: str
    risk_notes: str
    confidence: int


class TopicCompareRequest(BaseModel):
    """话题对比请求"""
    topics: List[str] = Field(..., description="话题列表")
    platform: str = Field(default="xiaohongshu", description="平台")


class TopicCompareResponse(BaseModel):
    """话题对比响应"""
    success: bool
    comparison: List[Dict[str, Any]]
    recommendation: str


@router.post("/trending/analyze", response_model=TrendingTopicsResponse)
async def analyze_trending_topics(request: TrendingTopicsRequest):
    """
    分析热门话题

    分析当前平台上的热门话题趋势
    """
    try:
        from backend.services.trending_analyzer import trending_analyzer_service

        topics = await trending_analyzer_service.analyze_trending_topics(
            platform=request.platform,
            category=request.category,
            num_topics=request.num_topics,
        )

        return TrendingTopicsResponse(
            success=True,
            topics=[TrendingTopicModel(
                topic=t.topic,
                platform=t.platform,
                heat_score=t.heat_score,
                category=t.category,
                description=t.description,
                related_hashtags=t.related_hashtags,
                best_posting_time=t.best_posting_time,
                growth_trend=t.growth_trend,
            ) for t in topics],
            total=len(topics),
        )

    except Exception as e:
        logger.error(f"分析热门话题失败: {e}")
        return TrendingTopicsResponse(
            success=False,
            topics=[],
            total=0,
        )


@router.post("/trending/predict", response_model=TopicTrendResponse)
async def predict_topic_trend(request: TopicTrendRequest):
    """
    预测话题趋势

    预测话题的未来热度趋势
    """
    try:
        from backend.services.trending_analyzer import trending_analyzer_service

        result = await trending_analyzer_service.predict_topic_trend(
            topic=request.topic,
            platform=request.platform,
        )

        return TopicTrendResponse(
            success=True,
            topic=result["topic"],
            trend_prediction=result["trend_prediction"],
            peak_time=result["peak_time"],
            best_timing=result["best_timing"],
            risk_notes=result.get("risk_notes", ""),
            confidence=result.get("confidence", 70),
        )

    except Exception as e:
        logger.error(f"预测话题趋势失败: {e}")
        return TopicTrendResponse(
            success=False,
            topic=request.topic,
            trend_prediction="平稳",
            peak_time="未知",
            best_timing="尽快行动",
            risk_notes="",
            confidence=50,
        )


@router.post("/trending/compare", response_model=TopicCompareResponse)
async def compare_topics(request: TopicCompareRequest):
    """
    对比话题热度

    对比多个话题的热度和竞争程度
    """
    try:
        from backend.services.trending_analyzer import trending_analyzer_service

        result = trending_analyzer_service.compare_topics(
            topics=request.topics,
            platform=request.platform,
        )

        return TopicCompareResponse(
            success=True,
            comparison=result.get("comparison", []),
            recommendation=result.get("recommendation", ""),
        )

    except Exception as e:
        logger.error(f"对比话题失败: {e}")
        return TopicCompareResponse(
            success=False,
            comparison=[],
            recommendation="",
        )


# ==================== 内容表现报告接口 ====================

class PerformanceReportRequest(BaseModel):
    """内容表现报告请求"""
    content_data: Dict[str, Any] = Field(..., description="内容数据")
    platform: str = Field(default="xiaohongshu", description="平台")


class PerformanceMetricModel(BaseModel):
    """表现指标模型"""
    value: Any
    evaluation: str
    score: int


class PerformanceReportResponse(BaseModel):
    """内容表现报告响应"""
    success: bool
    content_title: str
    platform: str
    report_date: str
    metrics: Dict[str, PerformanceMetricModel]
    analysis: str
    highlights: List[str]
    issues: List[str]
    suggestions: List[str]
    overall_score: int


class ContentCompareReportRequest(BaseModel):
    """内容对比报告请求"""
    content_list: List[Dict[str, Any]] = Field(..., description="内容列表")
    platform: str = Field(default="xiaohongshu", description="平台")


class ContentCompareReportResponse(BaseModel):
    """内容对比报告响应"""
    success: bool
    best_performer: Dict[str, Any]
    worst_performer: Dict[str, Any]
    common_success_factors: List[str]
    common_weaknesses: List[str]
    differentiation_tips: List[str]


class PerformanceDashboardRequest(BaseModel):
    """表现看板请求"""
    content_list: List[Dict[str, Any]] = Field(..., description="内容列表")
    platform: str = Field(default="xiaohongshu", description="平台")


class PerformanceDashboardResponse(BaseModel):
    """表现看板响应"""
    success: bool
    platform: str
    period: str
    total_contents: int
    total_metrics: Dict[str, int]
    averages: Dict[str, Any]
    best_content: Dict[str, Any]
    worst_content: Dict[str, Any]
    performance_distribution: Dict[str, int]


@router.post("/performance/report", response_model=PerformanceReportResponse)
async def generate_performance_report(request: PerformanceReportRequest):
    """
    生成内容表现报告

    基于内容数据生成详细的表现报告
    """
    try:
        from backend.services.performance_report import performance_report_service

        report = await performance_report_service.generate_report(
            content_data=request.content_data,
            platform=request.platform,
        )

        return PerformanceReportResponse(
            success=True,
            content_title=report.content_title,
            platform=report.platform,
            report_date=report.report_date,
            metrics={
                k: PerformanceMetricModel(**v) if isinstance(v, dict) else PerformanceMetricModel(value=v, evaluation="", score=0)
                for k, v in report.metrics.items()
            },
            analysis=report.analysis,
            highlights=report.highlights,
            issues=report.issues,
            suggestions=report.suggestions,
            overall_score=report.overall_score,
        )

    except Exception as e:
        logger.error(f"生成表现报告失败: {e}")
        return PerformanceReportResponse(
            success=False,
            content_title="",
            platform=request.platform,
            report_date="",
            metrics={},
            analysis="生成失败",
            highlights=[],
            issues=["服务异常"],
            suggestions=["请稍后重试"],
            overall_score=0,
        )


@router.post("/performance/compare", response_model=ContentCompareReportResponse)
async def generate_content_comparison(request: ContentCompareReportRequest):
    """
    生成内容对比报告

    对比多个内容的表现
    """
    try:
        from backend.services.performance_report import performance_report_service

        result = await performance_report_service.compare_content_report(
            content_list=request.content_list,
            platform=request.platform,
        )

        return ContentCompareReportResponse(
            success=True,
            best_performer=result.get("best_performer", {}),
            worst_performer=result.get("worst_performer", {}),
            common_success_factors=result.get("common_success_factors", []),
            common_weaknesses=result.get("common_weaknesses", []),
            differentiation_tips=result.get("differentiation_tips", []),
        )

    except Exception as e:
        logger.error(f"生成对比报告失败: {e}")
        return ContentCompareReportResponse(
            success=False,
            best_performer={},
            worst_performer={},
            common_success_factors=[],
            common_weaknesses=[],
            differentiation_tips=[],
        )


@router.post("/performance/dashboard", response_model=PerformanceDashboardResponse)
async def generate_performance_dashboard(request: PerformanceDashboardRequest):
    """
    生成表现看板

    汇总多个内容的数据生成看板
    """
    try:
        from backend.services.performance_report import performance_report_service

        result = performance_report_service.generate_summary_dashboard(
            content_data_list=request.content_list,
            platform=request.platform,
        )

        return PerformanceDashboardResponse(
            success=True,
            platform=result["platform"],
            period=result["period"],
            total_contents=result["total_contents"],
            total_metrics=result["total_metrics"],
            averages=result["averages"],
            best_content=result["best_content"],
            worst_content=result["worst_content"],
            performance_distribution=result["performance_distribution"],
        )

    except Exception as e:
        logger.error(f"生成看板失败: {e}")
        return PerformanceDashboardResponse(
            success=False,
            platform=request.platform,
            period="",
            total_contents=0,
            total_metrics={},
            averages={},
            best_content={},
            worst_content={},
            performance_distribution={},
        )


# ==================== 内容互动增强接口 ====================

class EngagementBoostRequest(BaseModel):
    """互动增强请求"""
    content: str = Field(..., description="内容文本")
    current_metrics: Dict[str, int] = Field(default_factory=dict, description="当前指标")
    platform: str = Field(default="xiaohongshu", description="平台")


class EngagementSuggestionModel(BaseModel):
    """互动建议模型"""
    action: str
    description: str
    expected_impact: str
    difficulty: str
    priority: int


class EngagementBoostResponse(BaseModel):
    """互动增强响应"""
    success: bool
    problem_analysis: str
    suggestions: List[EngagementSuggestionModel]


class InteractionCTARequest(BaseModel):
    """互动引导文案请求"""
    content: str = Field(..., description="内容文本")
    cta_type: str = Field(default="comment", description="引导类型: comment/share/like/save")
    platform: str = Field(default="xiaohongshu", description="平台")


class InteractionCTAResponse(BaseModel):
    """互动引导文案响应"""
    success: bool
    cta: str


class EngagementTipsResponse(BaseModel):
    """互动技巧响应"""
    success: bool
    platform: str
    like_rate_avg: str
    comment_rate_avg: str
    best_practices: List[str]
    common_mistakes: List[str]
    engagement_boosters: List[str]


@router.post("/engagement/analyze", response_model=EngagementBoostResponse)
async def analyze_and_boost_engagement(request: EngagementBoostRequest):
    """
    分析并增强内容互动

    分析内容互动问题并提供增强建议
    """
    try:
        from backend.services.engagement_booster import engagement_booster_service

        result = await engagement_booster_service.analyze_and_suggest(
            content=request.content,
            current_metrics=request.current_metrics,
            platform=request.platform,
        )

        return EngagementBoostResponse(
            success=True,
            problem_analysis=result.get("problem_analysis", ""),
            suggestions=[
                EngagementSuggestionModel(**s)
                for s in result.get("suggestions", [])
            ],
        )

    except Exception as e:
        logger.error(f"分析互动增强失败: {e}")
        return EngagementBoostResponse(
            success=False,
            problem_analysis="服务异常",
            suggestions=[],
        )


@router.post("/engagement/cta", response_model=InteractionCTAResponse)
async def generate_interaction_cta(request: InteractionCTARequest):
    """
    生成互动引导文案

    为内容生成点赞/评论/分享/收藏引导文案
    """
    try:
        from backend.services.engagement_booster import engagement_booster_service

        cta = await engagement_booster_service.generate_interaction_cta(
            content=request.content,
            cta_type=request.cta_type,
            platform=request.platform,
        )

        return InteractionCTAResponse(
            success=True,
            cta=cta,
        )

    except Exception as e:
        logger.error(f"生成互动引导失败: {e}")
        return InteractionCTAResponse(
            success=False,
            cta="欢迎留言讨论！",
        )


@router.get("/engagement/tips/{platform}", response_model=EngagementTipsResponse)
async def get_engagement_tips(platform: str):
    """
    获取互动提升技巧

    获取指定平台的互动提升最佳实践
    """
    try:
        from backend.services.engagement_booster import engagement_booster_service

        tips = engagement_booster_service.get_engagement_tips(platform)

        return EngagementTipsResponse(
            success=True,
            platform=platform,
            like_rate_avg=tips.get("like_rate_avg", ""),
            comment_rate_avg=tips.get("comment_rate_avg", ""),
            best_practices=tips.get("best_practices", []),
            common_mistakes=tips.get("common_mistakes", []),
            engagement_boosters=tips.get("engagement_boosters", []),
        )

    except Exception as e:
        logger.error(f"获取互动技巧失败: {e}")
        return EngagementTipsResponse(
            success=False,
            platform=platform,
            like_rate_avg="",
            comment_rate_avg="",
            best_practices=[],
            common_mistakes=[],
            engagement_boosters=[],
        )


# ==================== 关键词研究接口 ====================

class KeywordResearchRequest(BaseModel):
    """关键词研究请求"""
    seed_keyword: str = Field(..., description="种子关键词")
    platform: str = Field(default="xiaohongshu", description="平台")
    num_results: int = Field(default=10, ge=1, le=30, description="返回数量")


class KeywordInfoModel(BaseModel):
    """关键词信息模型"""
    keyword: str
    search_volume: int
    competition: str
    difficulty: int
    related_keywords: List[str]
    suggestions: List[str]


class KeywordResearchResponse(BaseModel):
    """关键词研究响应"""
    success: bool
    keywords: List[KeywordInfoModel]
    total: int


class KeywordDifficultyRequest(BaseModel):
    """关键词难度分析请求"""
    keyword: str = Field(..., description="关键词")
    platform: str = Field(default="xiaohongshu", description="平台")


class KeywordDifficultyResponse(BaseModel):
    """关键词难度分析响应"""
    success: bool
    keyword: str
    difficulty_score: int
    competition_analysis: str
    breakthrough_methods: List[str]
    content_strategy: str


class KeywordClustersRequest(BaseModel):
    """关键词簇请求"""
    keywords: List[str] = Field(..., description="关键词列表")


class KeywordClustersResponse(BaseModel):
    """关键词簇响应"""
    success: bool
    clusters: Dict[str, List[str]]


class KeywordCombinationsRequest(BaseModel):
    """关键词组合请求"""
    primary_keyword: str = Field(..., description="主要关键词")
    secondary_keywords: List[str] = Field(..., description="次要关键词列表")


class KeywordCombinationsResponse(BaseModel):
    """关键词组合响应"""
    success: bool
    combinations: List[str]


@router.post("/keywords/research", response_model=KeywordResearchResponse)
async def research_keywords(request: KeywordResearchRequest):
    """
    研究关键词

    基于种子关键词研究相关关键词
    """
    try:
        from backend.services.keyword_research import keyword_research_service

        keywords = await keyword_research_service.research_keywords(
            seed_keyword=request.seed_keyword,
            platform=request.platform,
            num_results=request.num_results,
        )

        return KeywordResearchResponse(
            success=True,
            keywords=[KeywordInfoModel(
                keyword=k.keyword,
                search_volume=k.search_volume,
                competition=k.competition,
                difficulty=k.difficulty,
                related_keywords=k.related_keywords,
                suggestions=k.suggestions,
            ) for k in keywords],
            total=len(keywords),
        )

    except Exception as e:
        logger.error(f"关键词研究失败: {e}")
        return KeywordResearchResponse(
            success=False,
            keywords=[],
            total=0,
        )


@router.post("/keywords/difficulty", response_model=KeywordDifficultyResponse)
async def analyze_keyword_difficulty(request: KeywordDifficultyRequest):
    """
    分析关键词难度

    分析关键词的SEO难度
    """
    try:
        from backend.services.keyword_research import keyword_research_service

        result = await keyword_research_service.analyze_keyword_difficulty(
            keyword=request.keyword,
            platform=request.platform,
        )

        return KeywordDifficultyResponse(
            success=True,
            keyword=result["keyword"],
            difficulty_score=result.get("difficulty_score", 50),
            competition_analysis=result.get("competition_analysis", ""),
            breakthrough_methods=result.get("breakthrough_methods", []),
            content_strategy=result.get("content_strategy", ""),
        )

    except Exception as e:
        logger.error(f"分析关键词难度失败: {e}")
        return KeywordDifficultyResponse(
            success=False,
            keyword=request.keyword,
            difficulty_score=50,
            competition_analysis="分析失败",
            breakthrough_methods=[],
            content_strategy="",
        )


@router.post("/keywords/clusters", response_model=KeywordClustersResponse)
async def generate_keyword_clusters(request: KeywordClustersRequest):
    """
    生成关键词簇

    将关键词分组到主题簇
    """
    try:
        from backend.services.keyword_research import keyword_research_service

        clusters = keyword_research_service.generate_keyword_clusters(
            keywords=request.keywords,
        )

        return KeywordClustersResponse(
            success=True,
            clusters=clusters,
        )

    except Exception as e:
        logger.error(f"生成关键词簇失败: {e}")
        return KeywordClustersResponse(
            success=False,
            clusters={},
        )


@router.post("/keywords/combinations", response_model=KeywordCombinationsResponse)
async def suggest_keyword_combinations(request: KeywordCombinationsRequest):
    """
    建议关键词组合

    生成关键词组合建议
    """
    try:
        from backend.services.keyword_research import keyword_research_service

        combinations = keyword_research_service.suggest_keyword_combinations(
            primary_keyword=request.primary_keyword,
            secondary_keywords=request.secondary_keywords,
        )

        return KeywordCombinationsResponse(
            success=True,
            combinations=combinations,
        )

    except Exception as e:
        logger.error(f"建议关键词组合失败: {e}")
        return KeywordCombinationsResponse(
            success=False,
            combinations=[],
        )


# ==================== 竞品追踪接口 ====================

class CompetitorTrackRequest(BaseModel):
    """竞品追踪请求"""
    competitor_name: str = Field(..., description="竞品名称/账号")
    platform: str = Field(default="xiaohongshu", description="平台")


class CompetitorInfoModel(BaseModel):
    """竞品信息模型"""
    name: str
    platform: str
    followers: int
    avg_views: int
    avg_engagement: float
    content_frequency: str
    top_content_types: List[str]
    strengths: List[str]


class CompetitorTrackResponse(BaseModel):
    """竞品追踪响应"""
    success: bool
    competitor: CompetitorInfoModel


class CompetitorAnalysisRequest(BaseModel):
    """竞品内容分析请求"""
    competitor_name: str = Field(..., description="竞品名称")
    platform: str = Field(default="xiaohongshu", description="平台")


class CompetitorAnalysisResponse(BaseModel):
    """竞品内容分析响应"""
    success: bool
    competitor: str
    platform: str
    topic_tendencies: List[str]
    title_styles: List[str]
    posting_schedule: str
    hashtag_strategy: str
    engagement_strategy: str
    takeaways: List[str]


class CompetitorCompareRequest(BaseModel):
    """竞品对比请求"""
    my_content: str = Field(..., description="自己的内容")
    competitor_name: str = Field(..., description="竞品名称")
    platform: str = Field(default="xiaohongshu", description="平台")


class CompetitorCompareResponse(BaseModel):
    """竞品对比响应"""
    success: bool
    competitor: str
    platform: str
    main_gaps: List[str]
    advantages: List[str]
    disadvantages: List[str]
    improvement_suggestions: List[str]


class BenchmarkMetricsResponse(BaseModel):
    """基准指标响应"""
    success: bool
    platform: str
    avg_like_rate: float
    avg_comment_rate: float
    avg_share_rate: float
    avg_save_rate: float
    good_engagement_rate: float
    excellent_engagement_rate: float


@router.post("/competitor/track", response_model=CompetitorTrackResponse)
async def track_competitor(request: CompetitorTrackRequest):
    """
    追踪竞品

    获取竞品的基本信息
    """
    try:
        from backend.services.competitor_tracker import competitor_tracker_service

        competitor = await competitor_tracker_service.track_competitor(
            competitor_name=request.competitor_name,
            platform=request.platform,
        )

        return CompetitorTrackResponse(
            success=True,
            competitor=CompetitorInfoModel(
                name=competitor.name,
                platform=competitor.platform,
                followers=competitor.followers,
                avg_views=competitor.avg_views,
                avg_engagement=competitor.avg_engagement,
                content_frequency=competitor.content_frequency,
                top_content_types=competitor.top_content_types,
                strengths=competitor.strengths,
            ),
        )

    except Exception as e:
        logger.error(f"追踪竞品失败: {e}")
        return CompetitorTrackResponse(
            success=False,
            competitor=CompetitorInfoModel(
                name=request.competitor_name,
                platform=request.platform,
                followers=0,
                avg_views=0,
                avg_engagement=0.0,
                content_frequency="",
                top_content_types=[],
                strengths=[],
            ),
        )


@router.post("/competitor/analyze", response_model=CompetitorAnalysisResponse)
async def analyze_competitor_content(request: CompetitorAnalysisRequest):
    """
    分析竞品内容策略

    分析竞品的内容策略
    """
    try:
        from backend.services.competitor_tracker import competitor_tracker_service

        result = await competitor_tracker_service.analyze_competitor_content(
            competitor_name=request.competitor_name,
            platform=request.platform,
        )

        return CompetitorAnalysisResponse(
            success=True,
            competitor=result["competitor"],
            platform=result["platform"],
            topic_tendencies=result.get("topic_tendencies", []),
            title_styles=result.get("title_styles", []),
            posting_schedule=result.get("posting_schedule", ""),
            hashtag_strategy=result.get("hashtag_strategy", ""),
            engagement_strategy=result.get("engagement_strategy", ""),
            takeaways=result.get("takeaways", []),
        )

    except Exception as e:
        logger.error(f"分析竞品内容失败: {e}")
        return CompetitorAnalysisResponse(
            success=False,
            competitor=request.competitor_name,
            platform=request.platform,
            topic_tendencies=[],
            title_styles=[],
            posting_schedule="",
            hashtag_strategy="",
            engagement_strategy="",
            takeaways=[],
        )


@router.post("/competitor/compare", response_model=CompetitorCompareResponse)
async def compare_with_competitor(request: CompetitorCompareRequest):
    """
    与竞品对比

    对比自己内容与竞品的差异
    """
    try:
        from backend.services.competitor_tracker import competitor_tracker_service

        result = await competitor_tracker_service.compare_with_competitor(
            my_content=request.my_content,
            competitor_name=request.competitor_name,
            platform=request.platform,
        )

        return CompetitorCompareResponse(
            success=True,
            competitor=result["competitor"],
            platform=result["platform"],
            main_gaps=result.get("main_gaps", []),
            advantages=result.get("advantages", []),
            disadvantages=result.get("disadvantages", []),
            improvement_suggestions=result.get("improvement_suggestions", []),
        )

    except Exception as e:
        logger.error(f"竞品对比失败: {e}")
        return CompetitorCompareResponse(
            success=False,
            competitor=request.competitor_name,
            platform=request.platform,
            main_gaps=[],
            advantages=[],
            disadvantages=[],
            improvement_suggestions=[],
        )


@router.get("/competitor/benchmarks/{platform}", response_model=BenchmarkMetricsResponse)
async def get_benchmark_metrics(platform: str):
    """
    获取平台基准指标

    获取各平台的基准互动指标
    """
    try:
        from backend.services.competitor_tracker import competitor_tracker_service

        benchmarks = competitor_tracker_service.get_benchmark_metrics(platform)

        return BenchmarkMetricsResponse(
            success=True,
            platform=platform,
            avg_like_rate=benchmarks["avg_like_rate"],
            avg_comment_rate=benchmarks["avg_comment_rate"],
            avg_share_rate=benchmarks["avg_share_rate"],
            avg_save_rate=benchmarks["avg_save_rate"],
            good_engagement_rate=benchmarks["good_engagement_rate"],
            excellent_engagement_rate=benchmarks["excellent_engagement_rate"],
        )

    except Exception as e:
        logger.error(f"获取基准指标失败: {e}")
        return BenchmarkMetricsResponse(
            success=False,
            platform=platform,
            avg_like_rate=0.0,
            avg_comment_rate=0.0,
            avg_share_rate=0.0,
            avg_save_rate=0.0,
            good_engagement_rate=0.0,
            excellent_engagement_rate=0.0,
        )


# ==================== 智能发布调度接口 ====================

class OptimalTimesRequest(BaseModel):
    """最优时间请求"""
    platform: str = Field(default="xiaohongshu", description="平台")
    industry: str = Field(default="", description="行业")
    num_slots: int = Field(default=5, ge=1, le=20, description="返回数量")


class TimeSlotModel(BaseModel):
    """时间槽模型"""
    datetime: str
    date: str
    time: str
    day_of_week: str
    is_weekend: bool
    score: int
    exposure_level: str


class OptimalTimesResponse(BaseModel):
    """最优时间响应"""
    success: bool
    platform: str
    slots: List[TimeSlotModel]


class ScheduleContentRequest(BaseModel):
    """排程内容请求"""
    posts: List[Dict[str, Any]] = Field(..., description="帖子列表")


class ScheduledPostModel(BaseModel):
    """计划帖子模型"""
    id: str
    platform: str
    title: str
    scheduled_time: str
    status: str
    optimal_score: int


class ScheduleContentResponse(BaseModel):
    """排程内容响应"""
    success: bool
    scheduled_posts: List[ScheduledPostModel]


class PostingReminderRequest(BaseModel):
    """发布提醒请求"""
    platform: str = Field(default="xiaohongshu", description="平台")
    scheduled_time: str = Field(..., description="计划时间 ISO格式")
    content_title: str = Field(..., description="内容标题")


class PostingReminderResponse(BaseModel):
    """发布提醒响应"""
    success: bool
    reminder: str


class ScheduleSummaryRequest(BaseModel):
    """排程摘要请求"""
    platform: str = Field(default="xiaohongshu", description="平台")


class ScheduleSummaryResponse(BaseModel):
    """排程摘要响应"""
    success: bool
    platform: str
    recommended_slots: List[TimeSlotModel]
    best_day: str
    best_time: str
    weekly_distribution: Dict[str, int]


@router.post("/scheduler/optimal-times", response_model=OptimalTimesResponse)
async def get_optimal_posting_times(request: OptimalTimesRequest):
    """
    获取最优发布时间

    获取平台的最佳发布时间推荐
    """
    try:
        from backend.services.posting_scheduler import posting_scheduler_service

        slots = posting_scheduler_service.get_optimal_times(
            platform=request.platform,
            industry=request.industry,
            num_slots=request.num_slots,
        )

        return OptimalTimesResponse(
            success=True,
            platform=request.platform,
            slots=[TimeSlotModel(**s) for s in slots],
        )

    except Exception as e:
        logger.error(f"获取最优时间失败: {e}")
        return OptimalTimesResponse(
            success=False,
            platform=request.platform,
            slots=[],
        )


@router.post("/scheduler/schedule", response_model=ScheduleContentResponse)
async def schedule_content(request: ScheduleContentRequest):
    """
    排程内容

    为多个内容安排最优发布时间
    """
    try:
        from backend.services.posting_scheduler import posting_scheduler_service

        scheduled = posting_scheduler_service.schedule_content(
            posts=request.posts,
        )

        return ScheduleContentResponse(
            success=True,
            scheduled_posts=[
                ScheduledPostModel(
                    id=p.id,
                    platform=p.platform,
                    title=p.title,
                    scheduled_time=p.scheduled_time.isoformat(),
                    status=p.status,
                    optimal_score=p.optimal_score,
                )
                for p in scheduled
            ],
        )

    except Exception as e:
        logger.error(f"排程内容失败: {e}")
        return ScheduleContentResponse(
            success=False,
            scheduled_posts=[],
        )


@router.post("/scheduler/reminder", response_model=PostingReminderResponse)
async def generate_posting_reminder(request: PostingReminderRequest):
    """
    生成发布提醒

    生成内容发布提醒文本
    """
    try:
        from backend.services.posting_scheduler import posting_scheduler_service
        from datetime import datetime

        scheduled_time = datetime.fromisoformat(request.scheduled_time)

        reminder = posting_scheduler_service.generate_posting_reminder(
            platform=request.platform,
            scheduled_time=scheduled_time,
            content_title=request.content_title,
        )

        return PostingReminderResponse(
            success=True,
            reminder=reminder,
        )

    except Exception as e:
        logger.error(f"生成发布提醒失败: {e}")
        return PostingReminderResponse(
            success=False,
            reminder="生成提醒失败",
        )


@router.post("/scheduler/summary", response_model=ScheduleSummaryResponse)
async def get_schedule_summary(request: ScheduleSummaryRequest):
    """
    获取排程摘要

    获取平台的发布计划摘要
    """
    try:
        from backend.services.posting_scheduler import posting_scheduler_service

        summary = posting_scheduler_service.get_platform_schedule_summary(
            platform=request.platform,
        )

        return ScheduleSummaryResponse(
            success=True,
            platform=summary["platform"],
            recommended_slots=[TimeSlotModel(**s) for s in summary.get("recommended_slots", [])],
            best_day=summary.get("best_day", ""),
            best_time=summary.get("best_time", ""),
            weekly_distribution=summary.get("weekly_distribution", {}),
        )

    except Exception as e:
        logger.error(f"获取排程摘要失败: {e}")
        return ScheduleSummaryResponse(
            success=False,
            platform=request.platform,
            recommended_slots=[],
            best_day="",
            best_time="",
            weekly_distribution={},
        )


# ==================== 趋势预测接口 ====================

class TopicTrendRequest(BaseModel):
    """话题趋势请求"""
    topic: str = Field(..., description="话题")
    platform: str = Field(default="xiaohongshu", description="平台")


class TopicTrendResponse(BaseModel):
    """话题趋势响应"""
    success: bool
    topic: str
    trend_direction: str
    peak_time: str
    duration_days: int
    confidence: int
    viral_potential: str


class ViralPotentialRequest(BaseModel):
    """病毒潜力请求"""
    content: str = Field(..., description="内容")
    platform: str = Field(default="xiaohongshu", description="平台")


class ViralPotentialResponse(BaseModel):
    """病毒潜力响应"""
    success: bool
    content_preview: str
    platform: str
    viral_potential: str
    reasons: List[str]
    risks: List[str]
    improvement_suggestions: List[str]


class TrendWindowRequest(BaseModel):
    """趋势窗口请求"""
    topic: str = Field(..., description="话题")
    platform: str = Field(default="xiaohongshu", description="平台")


class TrendWindowResponse(BaseModel):
    """趋势窗口响应"""
    success: bool
    topic: str
    platform: str
    is_optimal_now: bool
    best_window_start: str
    best_window_end: str
    window_duration_hours: int
    urgency: str
    missed_impact: str


class SeasonalTrendRequest(BaseModel):
    """季节性趋势请求"""
    topic: str = Field(..., description="话题")


class SeasonalTrendResponse(BaseModel):
    """季节性趋势响应"""
    success: bool
    topic: str
    current_season: str
    is_seasonal: bool
    seasonal_keywords: List[str]
    recommendation: str


@router.post("/trends/topic-predict", response_model=TopicTrendResponse)
async def predict_topic_trend(request: TopicTrendRequest):
    """
    预测话题趋势

    预测话题的未来趋势
    """
    try:
        from backend.services.trend_predictor import trend_predictor_service

        pred = await trend_predictor_service.predict_topic_trend(
            topic=request.topic,
            platform=request.platform,
        )

        return TopicTrendResponse(
            success=True,
            topic=pred.topic,
            trend_direction=pred.trend_direction,
            peak_time=pred.peak_time,
            duration_days=pred.duration_days,
            confidence=pred.confidence,
            viral_potential=pred.viral_potential,
        )

    except Exception as e:
        logger.error(f"预测话题趋势失败: {e}")
        return TopicTrendResponse(
            success=False,
            topic=request.topic,
            trend_direction="平稳",
            peak_time="",
            duration_days=7,
            confidence=50,
            viral_potential="中",
        )


@router.post("/trends/viral-potential", response_model=ViralPotentialResponse)
async def predict_viral_potential(request: ViralPotentialRequest):
    """
    预测病毒潜力

    分析内容的病毒式传播潜力
    """
    try:
        from backend.services.trend_predictor import trend_predictor_service

        result = await trend_predictor_service.predict_viral_potential(
            content=request.content,
            platform=request.platform,
        )

        return ViralPotentialResponse(
            success=True,
            content_preview=result["content_preview"],
            platform=result["platform"],
            viral_potential=result["viral_potential"],
            reasons=result["reasons"],
            risks=result["risks"],
            improvement_suggestions=result["improvement_suggestions"],
        )

    except Exception as e:
        logger.error(f"预测病毒潜力失败: {e}")
        return ViralPotentialResponse(
            success=False,
            content_preview=request.content[:100],
            platform=request.platform,
            viral_potential="中",
            reasons=[],
            risks=[],
            improvement_suggestions=[],
        )


@router.post("/trends/window", response_model=TrendWindowResponse)
async def get_trending_window(request: TrendWindowRequest):
    """
    获取趋势发布窗口

    确定最佳发布时间窗口
    """
    try:
        from backend.services.trend_predictor import trend_predictor_service

        result = await trend_predictor_service.get_trending_window(
            topic=request.topic,
            platform=request.platform,
        )

        return TrendWindowResponse(
            success=True,
            topic=result["topic"],
            platform=result["platform"],
            is_optimal_now=result["is_optimal_now"],
            best_window_start=result["best_window_start"],
            best_window_end=result["best_window_end"],
            window_duration_hours=result["window_duration_hours"],
            urgency=result["urgency"],
            missed_impact=result["missed_impact"],
        )

    except Exception as e:
        logger.error(f"获取趋势窗口失败: {e}")
        return TrendWindowResponse(
            success=False,
            topic=request.topic,
            platform=request.platform,
            is_optimal_now=False,
            best_window_start="",
            best_window_end="",
            window_duration_hours=24,
            urgency="中",
            missed_impact="",
        )


@router.post("/trends/seasonal", response_model=SeasonalTrendResponse)
async def analyze_seasonal_trends(request: SeasonalTrendRequest):
    """
    分析季节性趋势

    分析话题的季节性特征
    """
    try:
        from backend.services.trend_predictor import trend_predictor_service

        result = trend_predictor_service.analyze_seasonal_trends(
            topic=request.topic,
        )

        return SeasonalTrendResponse(
            success=True,
            topic=result["topic"],
            current_season=result["current_season"],
            is_seasonal=result["is_seasonal"],
            seasonal_keywords=result["seasonal_keywords"],
            recommendation=result["recommendation"],
        )

    except Exception as e:
        logger.error(f"分析季节性趋势失败: {e}")
        return SeasonalTrendResponse(
            success=False,
            topic=request.topic,
            current_season="",
            is_seasonal=False,
            seasonal_keywords=[],
            recommendation="",
        )


# ==================== Emoji 助手接口 ====================

class EmojiPlatformRequest(BaseModel):
    """平台emoji请求"""
    platform: str = Field(default="xiaohongshu", description="平台")


class EmojiPlatformResponse(BaseModel):
    """平台emoji响应"""
    success: bool
    platform: str
    style: str
    commonly_used: List[str]
    avoid: List[str]


class EmojiSuggestRequest(BaseModel):
    """emoji推荐请求"""
    content_type: str = Field(..., description="内容类型")
    platform: str = Field(default="xiaohongshu", description="平台")
    num: int = Field(default=5, ge=1, le=20, description="返回数量")


class EmojiSuggestResponse(BaseModel):
    """emoji推荐响应"""
    success: bool
    emojis: List[str]


class EmojiAnalyzeRequest(BaseModel):
    """emoji分析请求"""
    content: str = Field(..., description="内容")


class EmojiAnalyzeResponse(BaseModel):
    """emoji分析响应"""
    success: bool
    emoji_count: int
    emoji_list: List[str]
    usage_level: str
    suggestions: List[str]


@router.get("/emoji/platform/{platform}", response_model=EmojiPlatformResponse)
async def get_platform_emojis(platform: str):
    """
    获取平台emoji偏好

    获取指定平台的emoji使用偏好
    """
    try:
        from backend.services.emoji_helper import emoji_helper_service

        info = emoji_helper_service.get_platform_emojis(platform)

        return EmojiPlatformResponse(
            success=True,
            platform=info["platform"],
            style=info["style"],
            commonly_used=info["commonly_used"],
            avoid=info["avoid"],
        )

    except Exception as e:
        logger.error(f"获取平台emoji失败: {e}")
        return EmojiPlatformResponse(
            success=False,
            platform=platform,
            style="",
            commonly_used=[],
            avoid=[],
        )


@router.post("/emoji/suggest", response_model=EmojiSuggestResponse)
async def suggest_emojis(request: EmojiSuggestRequest):
    """
    推荐emoji

    根据内容类型推荐合适的emoji
    """
    try:
        from backend.services.emoji_helper import emoji_helper_service

        emojis = emoji_helper_service.suggest_emojis_for_content(
            content_type=request.content_type,
            platform=request.platform,
            num=request.num,
        )

        return EmojiSuggestResponse(
            success=True,
            emojis=emojis,
        )

    except Exception as e:
        logger.error(f"推荐emoji失败: {e}")
        return EmojiSuggestResponse(
            success=False,
            emojis=[],
        )


@router.post("/emoji/analyze", response_model=EmojiAnalyzeResponse)
async def analyze_emoji_usage(request: EmojiAnalyzeRequest):
    """
    分析emoji使用

    分析内容中emoji的使用情况
    """
    try:
        from backend.services.emoji_helper import emoji_helper_service

        result = emoji_helper_service.analyze_emoji_usage(request.content)

        return EmojiAnalyzeResponse(
            success=True,
            emoji_count=result["emoji_count"],
            emoji_list=result["emoji_list"],
            usage_level=result["usage_level"],
            suggestions=result["suggestions"],
        )

    except Exception as e:
        logger.error(f"分析emoji使用失败: {e}")
        return EmojiAnalyzeResponse(
            success=False,
            emoji_count=0,
            emoji_list=[],
            usage_level="未知",
            suggestions=[],
        )


# Hashtag Intelligence Models
class HashtagAnalyzeRequest(BaseModel):
    """Hashtag分析请求"""
    hashtag: str = Field(..., description="Hashtag")
    platform: str = Field(default="xiaohongshu", description="平台")


class HashtagAnalyzeResponse(BaseModel):
    """Hashtag分析响应"""
    success: bool
    hashtag: str
    popularity: str
    competition: str
    relevance_score: int
    best_posting_time: str


class HashtagOptimizeRequest(BaseModel):
    """Hashtag优化请求"""
    hashtags: List[str] = Field(..., description="原始hashtag列表")
    platform: str = Field(default="xiaohongshu", description="平台")
    target_count: int = Field(default=10, ge=1, le=30, description="目标数量")


class HashtagOptimizeResponse(BaseModel):
    """Hashtag优化响应"""
    success: bool
    original_count: int
    target_count: int
    current_issues: List[str]
    recommended: List[str]
    removed: List[str]
    strategy: str


class HashtagGenerateMixRequest(BaseModel):
    """Hashtag组合生成请求"""
    content_topic: str = Field(..., description="内容主题")
    platform: str = Field(default="xiaohongshu", description="平台")
    num: int = Field(default=10, ge=1, le=30, description="数量")


class HashtagGenerateMixResponse(BaseModel):
    """Hashtag组合生成响应"""
    success: bool
    topic: str
    platform: str
    total_count: int
    core: List[str]
    targeted: List[str]
    long_tail: List[str]
    trending: List[str]
    mix_recommendation: str


class HashtagScoreRequest(BaseModel):
    """Hashtag分数计算请求"""
    hashtag: str = Field(..., description="Hashtag")
    post_time: str = Field(default="evening", description="发布时间")


class HashtagScoreResponse(BaseModel):
    """Hashtag分数响应"""
    success: bool
    hashtag: str
    score: int


@router.post("/hashtags/intelligence/analyze", response_model=HashtagAnalyzeResponse)
async def analyze_hashtag(request: HashtagAnalyzeRequest):
    """
    分析Hashtag

    分析单个hashtag的热度、竞争度、相关性等
    """
    try:
        from backend.services.hashtag_intelligence import hashtag_intelligence_service

        result = await hashtag_intelligence_service.analyze_hashtag(
            request.hashtag, request.platform
        )

        return HashtagAnalyzeResponse(
            success=True,
            hashtag=result.hashtag,
            popularity=result.popularity,
            competition=result.competition,
            relevance_score=result.relevance_score,
            best_posting_time=result.best_posting_time,
        )

    except Exception as e:
        logger.error(f"分析hashtag失败: {e}")
        return HashtagAnalyzeResponse(
            success=False,
            hashtag=request.hashtag,
            popularity="温",
            competition="中",
            relevance_score=60,
            best_posting_time="",
        )


@router.post("/hashtags/intelligence/optimize", response_model=HashtagOptimizeResponse)
async def optimize_hashtag_set(request: HashtagOptimizeRequest):
    """
    优化Hashtag组合

    优化hashtag组合以达到最佳效果
    """
    try:
        from backend.services.hashtag_intelligence import hashtag_intelligence_service

        result = await hashtag_intelligence_service.optimize_hashtag_set(
            request.hashtags, request.platform, request.target_count
        )

        return HashtagOptimizeResponse(
            success=True,
            original_count=result["original_count"],
            target_count=result["target_count"],
            current_issues=result["current_issues"],
            recommended=result["recommended"],
            removed=result["removed"],
            strategy=result["strategy"],
        )

    except Exception as e:
        logger.error(f"优化hashtag组合失败: {e}")
        return HashtagOptimizeResponse(
            success=False,
            original_count=len(request.hashtags),
            target_count=request.target_count,
            current_issues=[],
            recommended=[f"#{h}" for h in request.hashtags[:request.target_count]],
            removed=[],
            strategy="优化失败",
        )


@router.post("/hashtags/intelligence/generate-mix", response_model=HashtagGenerateMixResponse)
async def generate_hashtag_mix(request: HashtagGenerateMixRequest):
    """
    生成Hashtag组合

    根据内容主题生成最佳hashtag组合
    """
    try:
        from backend.services.hashtag_intelligence import hashtag_intelligence_service

        result = await hashtag_intelligence_service.generate_hashtag_mix(
            request.content_topic, request.platform, request.num
        )

        return HashtagGenerateMixResponse(
            success=True,
            topic=result["topic"],
            platform=result["platform"],
            total_count=result["total_count"],
            core=result["core"],
            targeted=result["targeted"],
            long_tail=result["long_tail"],
            trending=result["trending"],
            mix_recommendation=result["mix_recommendation"],
        )

    except Exception as e:
        logger.error(f"生成hashtag组合失败: {e}")
        return HashtagGenerateMixResponse(
            success=False,
            topic=request.content_topic,
            platform=request.platform,
            total_count=0,
            core=[],
            targeted=[],
            long_tail=[],
            trending=[],
            mix_recommendation="",
        )


@router.post("/hashtags/intelligence/score", response_model=HashtagScoreResponse)
async def calculate_hashtag_score(request: HashtagScoreRequest):
    """
    计算Hashtag分数

    计算hashtag的推荐分数
    """
    try:
        from backend.services.hashtag_intelligence import hashtag_intelligence_service

        score = hashtag_intelligence_service.calculate_hashtag_score(
            request.hashtag, request.post_time
        )

        return HashtagScoreResponse(
            success=True,
            hashtag=request.hashtag,
            score=score,
        )

    except Exception as e:
        logger.error(f"计算hashtag分数失败: {e}")
        return HashtagScoreResponse(
            success=False,
            hashtag=request.hashtag,
            score=60,
        )


# Sentiment Analyzer Models
class SentimentAnalyzeRequest(BaseModel):
    """情感分析请求"""
    content: str = Field(..., description="内容")
    platform: str = Field(default="xiaohongshu", description="平台")


class SentimentAnalyzeResponse(BaseModel):
    """情感分析响应"""
    success: bool
    sentiment: str
    confidence: int
    emotions: List[str]
    intensity: str
    suggestions: List[str]


class SentimentAdjustRequest(BaseModel):
    """情感调整请求"""
    content: str = Field(..., description="原始内容")
    target_sentiment: str = Field(default="positive", description="目标情感")
    platform: str = Field(default="xiaohongshu", description="平台")


class SentimentAdjustResponse(BaseModel):
    """情感调整响应"""
    success: bool
    original_content: str
    target_sentiment: str
    adjusted_content: str
    change_explanation: str
    preserved_core: List[str]
    adjustment_suggestions: List[str]


class SentimentTipsRequest(BaseModel):
    """情感建议请求"""
    platform: str = Field(default="xiaohongshu", description="平台")


class SentimentTipsResponse(BaseModel):
    """情感建议响应"""
    success: bool
    platform: str
    preferred_sentiment: str
    tone: str
    avoid: str
    recommended_emojis: List[str]


class EmotionDistributionRequest(BaseModel):
    """情绪分布请求"""
    contents: List[str] = Field(..., description="内容列表")


class EmotionDistributionResponse(BaseModel):
    """情绪分布响应"""
    success: bool
    total_contents: int
    emotion_distribution: Dict[str, int]
    emotion_percentages: Dict[str, float]
    dominant_emotion: str
    recommendations: List[str]


@router.post("/sentiment/analyze", response_model=SentimentAnalyzeResponse)
async def analyze_sentiment(request: SentimentAnalyzeRequest):
    """
    分析情感

    分析内容的情感倾向和情绪
    """
    try:
        from backend.services.sentiment_analyzer import sentiment_analyzer_service

        result = await sentiment_analyzer_service.analyze_sentiment(
            request.content, request.platform
        )

        return SentimentAnalyzeResponse(
            success=True,
            sentiment=result.sentiment,
            confidence=result.confidence,
            emotions=result.emotions,
            intensity=result.intensity,
            suggestions=result.suggestions,
        )

    except Exception as e:
        logger.error(f"分析情感失败: {e}")
        return SentimentAnalyzeResponse(
            success=False,
            sentiment="neutral",
            confidence=50,
            emotions=[],
            intensity="中",
            suggestions=[],
        )


@router.post("/sentiment/adjust", response_model=SentimentAdjustResponse)
async def adjust_sentiment(request: SentimentAdjustRequest):
    """
    调整情感

    将内容调整为指定情感倾向
    """
    try:
        from backend.services.sentiment_analyzer import sentiment_analyzer_service

        result = await sentiment_analyzer_service.adjust_sentiment(
            request.content, request.target_sentiment, request.platform
        )

        return SentimentAdjustResponse(
            success=True,
            original_content=result["original_content"],
            target_sentiment=result["target_sentiment"],
            adjusted_content=result["adjusted_content"],
            change_explanation=result["change_explanation"],
            preserved_core=result["preserved_core"],
            adjustment_suggestions=result["adjustment_suggestions"],
        )

    except Exception as e:
        logger.error(f"调整情感失败: {e}")
        return SentimentAdjustResponse(
            success=False,
            original_content=request.content,
            target_sentiment=request.target_sentiment,
            adjusted_content=request.content,
            change_explanation="调整失败",
            preserved_core=[],
            adjustment_suggestions=[],
        )


@router.post("/sentiment/tips", response_model=SentimentTipsResponse)
async def get_sentiment_tips(request: SentimentTipsRequest):
    """
    获取平台情感建议

    获取指定平台的情感偏好和建议
    """
    try:
        from backend.services.sentiment_analyzer import sentiment_analyzer_service

        tips = await sentiment_analyzer_service.get_platform_sentiment_tips(request.platform)

        return SentimentTipsResponse(
            success=True,
            platform=tips["platform"],
            preferred_sentiment=tips["preferred_sentiment"],
            tone=tips["tone"],
            avoid=tips["avoid"],
            recommended_emojis=tips["recommended_emojis"],
        )

    except Exception as e:
        logger.error(f"获取情感建议失败: {e}")
        return SentimentTipsResponse(
            success=False,
            platform=request.platform,
            preferred_sentiment="",
            tone="",
            avoid="",
            recommended_emojis=[],
        )


@router.post("/sentiment/emotion-distribution", response_model=EmotionDistributionResponse)
async def analyze_emotion_distribution(request: EmotionDistributionRequest):
    """
    分析情绪分布

    分析多内容的情绪分布
    """
    try:
        from backend.services.sentiment_analyzer import sentiment_analyzer_service

        result = sentiment_analyzer_service.analyze_emotion_distribution(request.contents)

        return EmotionDistributionResponse(
            success=True,
            total_contents=result["total_contents"],
            emotion_distribution=result["emotion_distribution"],
            emotion_percentages=result["emotion_percentages"],
            dominant_emotion=result["dominant_emotion"],
            recommendations=result["recommendations"],
        )

    except Exception as e:
        logger.error(f"分析情绪分布失败: {e}")
        return EmotionDistributionResponse(
            success=False,
            total_contents=len(request.contents),
            emotion_distribution={},
            emotion_percentages={},
            dominant_emotion="未知",
            recommendations=[],
        )


# Audience Analyzer Models
class AudienceAnalyzeRequest(BaseModel):
    """受众分析请求"""
    content_topic: str = Field(..., description="内容主题")
    platform: str = Field(default="xiaohongshu", description="平台")


class AudienceAnalyzeResponse(BaseModel):
    """受众分析响应"""
    success: bool
    age_range: str
    gender: str
    interests: List[str]
    pain_points: List[str]
    motivations: List[str]
    preferred_content_style: str


class AudienceStrategyRequest(BaseModel):
    """受众内容策略请求"""
    audience_profile: Dict[str, Any] = Field(..., description="受众画像")
    platform: str = Field(default="xiaohongshu", description="平台")


class AudienceStrategyResponse(BaseModel):
    """受众内容策略响应"""
    success: bool
    audience: Dict[str, Any]
    platform: str
    recommended_content_types: List[str]
    title_style: str
    content_structure: str
    engagement_strategy: str
    best_posting_time: str


class AudienceMatchRequest(BaseModel):
    """受众匹配度请求"""
    content_tags: List[str] = Field(..., description="内容标签")
    audience_interests: List[str] = Field(..., description="受众兴趣")


class AudienceMatchResponse(BaseModel):
    """受众匹配度响应"""
    success: bool
    match_score: int
    matched_interests: List[str]
    unmatched_tags: List[str]
    recommendation: str


@router.post("/audience/analyze", response_model=AudienceAnalyzeResponse)
async def analyze_audience(request: AudienceAnalyzeRequest):
    """
    分析受众画像

    分析内容主题的目标受众画像
    """
    try:
        from backend.services.audience_analyzer import audience_analyzer_service

        result = await audience_analyzer_service.analyze_audience(
            request.content_topic, request.platform
        )

        return AudienceAnalyzeResponse(
            success=True,
            age_range=result.age_range,
            gender=result.gender,
            interests=result.interests,
            pain_points=result.pain_points,
            motivations=result.motivations,
            preferred_content_style=result.preferred_content_style,
        )

    except Exception as e:
        logger.error(f"分析受众失败: {e}")
        return AudienceAnalyzeResponse(
            success=False,
            age_range="未知",
            gender="未知",
            interests=[],
            pain_points=[],
            motivations=[],
            preferred_content_style="",
        )


@router.get("/audience/platform/{platform}", response_model=Dict[str, Any])
async def get_platform_audience(platform: str):
    """
    获取平台受众特征

    获取指定平台的标准受众特征
    """
    try:
        from backend.services.audience_analyzer import audience_analyzer_service

        result = audience_analyzer_service.get_platform_audience(platform)

        return {
            "success": True,
            **result,
        }

    except Exception as e:
        logger.error(f"获取平台受众失败: {e}")
        return {
            "success": False,
            "platform": platform,
            "primary_age": "",
            "gender": "",
            "interests": [],
            "content_style": "",
        }


@router.post("/audience/strategy", response_model=AudienceStrategyResponse)
async def suggest_audience_strategy(request: AudienceStrategyRequest):
    """
    推荐受众内容策略

    根据受众画像推荐内容策略
    """
    try:
        from backend.services.audience_analyzer import audience_analyzer_service

        result = await audience_analyzer_service.suggest_content_for_audience(
            request.audience_profile, request.platform
        )

        return AudienceStrategyResponse(
            success=True,
            audience=result["audience"],
            platform=result["platform"],
            recommended_content_types=result["recommended_content_types"],
            title_style=result["title_style"],
            content_structure=result["content_structure"],
            engagement_strategy=result["engagement_strategy"],
            best_posting_time=result["best_posting_time"],
        )

    except Exception as e:
        logger.error(f"推荐内容策略失败: {e}")
        return AudienceStrategyResponse(
            success=False,
            audience=request.audience_profile,
            platform=request.platform,
            recommended_content_types=[],
            title_style="",
            content_structure="",
            engagement_strategy="",
            best_posting_time="",
        )


@router.post("/audience/match", response_model=AudienceMatchResponse)
async def calculate_audience_match(request: AudienceMatchRequest):
    """
    计算内容与受众匹配度

    计算内容标签与受众兴趣的匹配度
    """
    try:
        from backend.services.audience_analyzer import audience_analyzer_service

        result = audience_analyzer_service.calculate_audience_match(
            request.content_tags, request.audience_interests
        )

        return AudienceMatchResponse(
            success=True,
            match_score=result["match_score"],
            matched_interests=result["matched_interests"],
            unmatched_tags=result["unmatched_tags"],
            recommendation=result["recommendation"],
        )

    except Exception as e:
        logger.error(f"计算匹配度失败: {e}")
        return AudienceMatchResponse(
            success=False,
            match_score=0,
            matched_interests=[],
            unmatched_tags=request.content_tags,
            recommendation="计算失败",
        )


# Content Template Generator Models
class TemplateGenerateRequest(BaseModel):
    """模板生成请求"""
    template_type: str = Field(..., description="模板类型")
    product_info: Dict[str, Any] = Field(..., description="产品信息")
    platform: str = Field(default="xiaohongshu", description="平台")


class TemplateGenerateResponse(BaseModel):
    """模板生成响应"""
    success: bool
    template_type: str
    title_template: str
    content_structure: str
    required_elements: List[str]
    optional_elements: List[str]
    example: str


class TemplateSuggestRequest(BaseModel):
    """模板推荐请求"""
    product_info: Dict[str, Any] = Field(..., description="产品信息")
    platform: str = Field(default="xiaohongshu", description="平台")


class TemplateSuggestResponse(BaseModel):
    """模板推荐响应"""
    success: bool
    product_name: str
    platform: str
    recommended_types: List[str]
    reasons: List[str]
    title_suggestions: List[str]


class TemplateCustomizeRequest(BaseModel):
    """模板定制请求"""
    base_template: str = Field(..., description="基础模板")
    customization: Dict[str, Any] = Field(..., description="定制需求")


class TemplateCustomizeResponse(BaseModel):
    """模板定制响应"""
    success: bool
    original_template: str
    customization: Dict[str, Any]
    customized_title: str
    customized_structure: str
    writing_points: List[str]


@router.get("/templates/types", response_model=List[str])
async def get_template_types():
    """
    获取所有模板类型

    获取可用的内容模板类型列表
    """
    try:
        from backend.services.content_template_generator import content_template_generator_service

        return content_template_generator_service.get_template_types()

    except Exception as e:
        logger.error(f"获取模板类型失败: {e}")
        return []


@router.post("/templates/generate", response_model=TemplateGenerateResponse)
async def generate_template(request: TemplateGenerateRequest):
    """
    生成内容模板

    根据模板类型和产品信息生成内容模板
    """
    try:
        from backend.services.content_template_generator import content_template_generator_service

        result = await content_template_generator_service.generate_template(
            request.template_type, request.product_info, request.platform
        )

        return TemplateGenerateResponse(
            success=True,
            template_type=result.template_type,
            title_template=result.title_template,
            content_structure=result.content_structure,
            required_elements=result.required_elements,
            optional_elements=result.optional_elements,
            example=result.example,
        )

    except Exception as e:
        logger.error(f"生成模板失败: {e}")
        return TemplateGenerateResponse(
            success=False,
            template_type=request.template_type,
            title_template="",
            content_structure="",
            required_elements=[],
            optional_elements=[],
            example="",
        )


@router.post("/templates/suggest", response_model=TemplateSuggestResponse)
async def suggest_template(request: TemplateSuggestRequest):
    """
    推荐模板类型

    为产品推荐最合适的内容模板类型
    """
    try:
        from backend.services.content_template_generator import content_template_generator_service

        result = await content_template_generator_service.suggest_template_for_product(
            request.product_info, request.platform
        )

        return TemplateSuggestResponse(
            success=True,
            product_name=result["product_name"],
            platform=result["platform"],
            recommended_types=result["recommended_types"],
            reasons=result["reasons"],
            title_suggestions=result["title_suggestions"],
        )

    except Exception as e:
        logger.error(f"推荐模板失败: {e}")
        return TemplateSuggestResponse(
            success=False,
            product_name=request.product_info.get("name", ""),
            platform=request.platform,
            recommended_types=[],
            reasons=[],
            title_suggestions=[],
        )


@router.post("/templates/customize", response_model=TemplateCustomizeResponse)
async def customize_template(request: TemplateCustomizeRequest):
    """
    定制模板

    根据需求定制内容模板
    """
    try:
        from backend.services.content_template_generator import content_template_generator_service

        result = await content_template_generator_service.customize_template(
            request.base_template, request.customization
        )

        return TemplateCustomizeResponse(
            success=True,
            original_template=result["original_template"],
            customization=result["customization"],
            customized_title=result["customized_title"],
            customized_structure=result["customized_structure"],
            writing_points=result["writing_points"],
        )

    except Exception as e:
        logger.error(f"定制模板失败: {e}")
        return TemplateCustomizeResponse(
            success=False,
            original_template=request.base_template,
            customization=request.customization,
            customized_title=request.base_template,
            customized_structure="",
            writing_points=[],
        )


# Social Proof Generator Models
class TestimonialRequest(BaseModel):
    """用户评价请求"""
    product_info: Dict[str, Any] = Field(..., description="产品信息")
    num: int = Field(default=5, ge=1, le=10, description="生成数量")
    platform: str = Field(default="xiaohongshu", description="平台")


class TestimonialResponse(BaseModel):
    """用户评价响应"""
    success: bool
    testimonials: List[Dict[str, Any]]


class StatsRequest(BaseModel):
    """数据统计请求"""
    product_info: Dict[str, Any] = Field(..., description="产品信息")
    num: int = Field(default=5, ge=1, le=10, description="生成数量")


class StatsResponse(BaseModel):
    """数据统计响应"""
    success: bool
    stats: List[Dict[str, Any]]


class EndorsementRequest(BaseModel):
    """权威背书请求"""
    product_info: Dict[str, Any] = Field(..., description="产品信息")
    num: int = Field(default=3, ge=1, le=5, description="生成数量")


class EndorsementResponse(BaseModel):
    """权威背书响应"""
    success: bool
    endorsements: List[Dict[str, Any]]


class SocialMentionRequest(BaseModel):
    """社交提及请求"""
    product_info: Dict[str, Any] = Field(..., description="产品信息")
    platform: str = Field(default="xiaohongshu", description="平台")


class SocialMentionResponse(BaseModel):
    """社交提及响应"""
    success: bool
    proof_type: str
    content: str
    source: str
    credibility: str


@router.post("/social-proof/testimonials", response_model=TestimonialResponse)
async def generate_testimonials(request: TestimonialRequest):
    """
    生成用户评价

    生成多条用户评价增强可信度
    """
    try:
        from backend.services.social_proof_generator import social_proof_generator_service

        testimonials = await social_proof_generator_service.generate_testimonials(
            request.product_info, request.num, request.platform
        )

        return TestimonialResponse(
            success=True,
            testimonials=[
                {
                    "proof_type": t.proof_type,
                    "content": t.content,
                    "source": t.source,
                    "credibility": t.credibility,
                }
                for t in testimonials
            ],
        )

    except Exception as e:
        logger.error(f"生成用户评价失败: {e}")
        return TestimonialResponse(success=False, testimonials=[])


@router.post("/social-proof/stats", response_model=StatsResponse)
async def generate_stats(request: StatsRequest):
    """
    生成数据统计

    生成有说服力的数据统计
    """
    try:
        from backend.services.social_proof_generator import social_proof_generator_service

        stats = await social_proof_generator_service.generate_stats(
            request.product_info, request.num
        )

        return StatsResponse(
            success=True,
            stats=[
                {
                    "proof_type": s.proof_type,
                    "content": s.content,
                    "source": s.source,
                    "credibility": s.credibility,
                }
                for s in stats
            ],
        )

    except Exception as e:
        logger.error(f"生成数据统计失败: {e}")
        return StatsResponse(success=False, stats=[])


@router.post("/social-proof/endorsements", response_model=EndorsementResponse)
async def generate_endorsements(request: EndorsementRequest):
    """
    生成权威背书

    生成权威机构或专家背书
    """
    try:
        from backend.services.social_proof_generator import social_proof_generator_service

        endorsements = await social_proof_generator_service.generate_endorsements(
            request.product_info, request.num
        )

        return EndorsementResponse(
            success=True,
            endorsements=[
                {
                    "proof_type": e.proof_type,
                    "content": e.content,
                    "source": e.source,
                    "credibility": e.credibility,
                }
                for e in endorsements
            ],
        )

    except Exception as e:
        logger.error(f"生成权威背书失败: {e}")
        return EndorsementResponse(success=False, endorsements=[])


@router.post("/social-proof/mentions", response_model=SocialMentionResponse)
async def generate_social_mentions(request: SocialMentionRequest):
    """
    生成社交提及

    生成平台社交热度描述
    """
    try:
        from backend.services.social_proof_generator import social_proof_generator_service

        mention = await social_proof_generator_service.generate_social_mentions(
            request.product_info, request.platform
        )

        return SocialMentionResponse(
            success=True,
            proof_type=mention.proof_type,
            content=mention.content,
            source=mention.source,
            credibility=mention.credibility,
        )

    except Exception as e:
        logger.error(f"生成社交提及失败: {e}")
        return SocialMentionResponse(
            success=False,
            proof_type="social_mention",
            content="",
            source=request.platform,
            credibility="低",
        )


# CTA Generator Models
class CTAGenerateRequest(BaseModel):
    """CTA生成请求"""
    content_type: str = Field(..., description="内容类型")
    platform: str = Field(default="xiaohongshu", description="平台")
    num: int = Field(default=3, ge=1, le=10, description="生成数量")


class CTAGenerateResponse(BaseModel):
    """CTA生成响应"""
    success: bool
    ctas: List[Dict[str, Any]]


class CTAOptimizeRequest(BaseModel):
    """CTA优化请求"""
    original_cta: str = Field(..., description="原始CTA")
    platform: str = Field(default="xiaohongshu", description="平台")
    target_type: str = Field(default="immediate", description="目标类型")


class CTAOptimizeResponse(BaseModel):
    """CTA优化响应"""
    success: bool
    original_cta: str
    platform: str
    target_type: str
    optimized_cta: str
    reason: str
    alternatives: List[str]


class CTAGuideRequest(BaseModel):
    """CTA指南请求"""
    platform: str = Field(default="xiaohongshu", description="平台")


class CTAGuideResponse(BaseModel):
    """CTA指南响应"""
    success: bool
    platform: str
    preferred_types: List[str]
    style: str
    avoid: str
    examples: List[str]


@router.post("/cta/generate", response_model=CTAGenerateResponse)
async def generate_cta(request: CTAGenerateRequest):
    """
    生成CTA

    生成行动号召文案
    """
    try:
        from backend.services.cta_generator import cta_generator_service

        ctas = await cta_generator_service.generate_cta(
            request.content_type, request.platform, request.num
        )

        return CTAGenerateResponse(
            success=True,
            ctas=[
                {
                    "cta_text": c.cta_text,
                    "cta_type": c.cta_type,
                    "placement": c.placement,
                    "style": c.style,
                }
                for c in ctas
            ],
        )

    except Exception as e:
        logger.error(f"生成CTA失败: {e}")
        return CTAGenerateResponse(success=False, ctas=[])


@router.post("/cta/optimize", response_model=CTAOptimizeResponse)
async def optimize_cta(request: CTAOptimizeRequest):
    """
    优化CTA

    优化现有CTA使其更有效
    """
    try:
        from backend.services.cta_generator import cta_generator_service

        result = await cta_generator_service.optimize_cta(
            request.original_cta, request.platform, request.target_type
        )

        return CTAOptimizeResponse(
            success=True,
            original_cta=result["original_cta"],
            platform=result["platform"],
            target_type=result["target_type"],
            optimized_cta=result["optimized_cta"],
            reason=result["reason"],
            alternatives=result["alternatives"],
        )

    except Exception as e:
        logger.error(f"优化CTA失败: {e}")
        return CTAOptimizeResponse(
            success=False,
            original_cta=request.original_cta,
            platform=request.platform,
            target_type=request.target_type,
            optimized_cta=request.original_cta,
            reason="优化失败",
            alternatives=[],
        )


@router.post("/cta/guide", response_model=CTAGuideResponse)
async def get_cta_guide(request: CTAGuideRequest):
    """
    获取平台CTA指南

    获取平台的CTA撰写指南
    """
    try:
        from backend.services.cta_generator import cta_generator_service

        guide = await cta_generator_service.get_platform_cta_guide(request.platform)

        return CTAGuideResponse(
            success=True,
            platform=guide["platform"],
            preferred_types=guide["preferred_types"],
            style=guide["style"],
            avoid=guide["avoid"],
            examples=guide["examples"],
        )

    except Exception as e:
        logger.error(f"获取CTA指南失败: {e}")
        return CTAGuideResponse(
            success=False,
            platform=request.platform,
            preferred_types=[],
            style="",
            avoid="",
            examples=[],
        )


@router.get("/cta/types", response_model=List[str])
async def get_cta_types():
    """
    获取所有CTA类型

    获取可用的CTA类型列表
    """
    try:
        from backend.services.cta_generator import cta_generator_service

        return cta_generator_service.get_cta_types()

    except Exception as e:
        logger.error(f"获取CTA类型失败: {e}")
        return []


# Content Health Checker Models
class HealthCheckRequest(BaseModel):
    """内容健康检查请求"""
    content: str = Field(..., description="内容正文")
    title: str = Field(default="", description="内容标题")
    platform: str = Field(default="xiaohongshu", description="平台")


class HealthCheckResponse(BaseModel):
    """内容健康检查响应"""
    success: bool
    is_healthy: bool
    health_score: int
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]


class HealthReportRequest(BaseModel):
    """健康报告请求"""
    content: str = Field(..., description="内容正文")
    title: str = Field(default="", description="内容标题")
    platform: str = Field(default="xiaohongshu", description="平台")


class HealthReportResponse(BaseModel):
    """健康报告响应"""
    success: bool
    is_healthy: bool
    overall_score: int
    completeness_score: int
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]
    completeness_checks: Dict[str, str]
    platform: str


class CompletenessCheckRequest(BaseModel):
    """完整性检查请求"""
    content: str = Field(..., description="内容正文")
    title: str = Field(default="", description="内容标题")


class CompletenessCheckResponse(BaseModel):
    """完整性检查响应"""
    success: bool
    score: int
    issues: List[str]
    suggestions: List[str]
    checks: Dict[str, str]


@router.post("/health/check", response_model=HealthCheckResponse)
async def check_content_health(request: HealthCheckRequest):
    """
    检查内容健康度

    检查内容完整性、质量、互动性、SEO、合规性
    """
    try:
        from backend.services.content_health_checker import content_health_checker_service

        result = await content_health_checker_service.check_content_health(
            request.content, request.title, request.platform
        )

        return HealthCheckResponse(
            success=True,
            is_healthy=result.is_healthy,
            health_score=result.health_score,
            issues=result.issues,
            warnings=result.warnings,
            suggestions=result.suggestions,
        )

    except Exception as e:
        logger.error(f"检查内容健康度失败: {e}")
        return HealthCheckResponse(
            success=False,
            is_healthy=True,
            health_score=70,
            issues=[],
            warnings=["检查服务异常"],
            suggestions=["请人工检查内容"],
        )


@router.post("/health/report", response_model=HealthReportResponse)
async def get_health_report(request: HealthReportRequest):
    """
    获取完整健康报告

    获取详细的内容健康度报告
    """
    try:
        from backend.services.content_health_checker import content_health_checker_service

        result = await content_health_checker_service.get_health_report(
            request.content, request.title, request.platform
        )

        return HealthReportResponse(
            success=True,
            is_healthy=result["is_healthy"],
            overall_score=result["overall_score"],
            completeness_score=result["completeness_score"],
            issues=result["issues"],
            warnings=result["warnings"],
            suggestions=result["suggestions"],
            completeness_checks=result["completeness_checks"],
            platform=result["platform"],
        )

    except Exception as e:
        logger.error(f"获取健康报告失败: {e}")
        return HealthReportResponse(
            success=False,
            is_healthy=True,
            overall_score=70,
            completeness_score=70,
            issues=[],
            warnings=["服务异常"],
            suggestions=["请人工检查"],
            completeness_checks={},
            platform=request.platform,
        )


@router.post("/health/completeness", response_model=CompletenessCheckResponse)
async def check_completeness(request: CompletenessCheckRequest):
    """
    检查内容完整性

    检查标题、正文长度、段落、emoji、hashtag等
    """
    try:
        from backend.services.content_health_checker import content_health_checker_service

        result = await content_health_checker_service.check_completeness(
            request.content, request.title
        )

        return CompletenessCheckResponse(
            success=True,
            score=result["score"],
            issues=result["issues"],
            suggestions=result["suggestions"],
            checks=result["checks"],
        )

    except Exception as e:
        logger.error(f"检查完整性失败: {e}")
        return CompletenessCheckResponse(
            success=False,
            score=70,
            issues=[],
            suggestions=["检查失败"],
            checks={},
        )


# Headline Analyzer Models
class HeadlineAnalyzeRequest(BaseModel):
    """标题分析请求"""
    headline: str = Field(..., description="标题")
    platform: str = Field(default="xiaohongshu", description="平台")


class HeadlineAnalyzeResponse(BaseModel):
    """标题分析响应"""
    success: bool
    attractiveness_score: int
    readability_score: int
    seo_score: int
    emotional_appeal: str
    power_words: List[str]
    issues: List[str]
    suggestions: List[str]


class HeadlineOptimizeRequest(BaseModel):
    """标题优化请求"""
    headline: str = Field(..., description="原始标题")
    platform: str = Field(default="xiaohongshu", description="平台")
    target_score: int = Field(default=90, ge=50, le=100, description="目标分数")


class HeadlineOptimizeResponse(BaseModel):
    """标题优化响应"""
    success: bool
    original_headline: str
    platform: str
    target_score: int
    optimized_headlines: List[Dict[str, Any]]


class HeadlineStructureRequest(BaseModel):
    """标题结构分析请求"""
    headline: str = Field(..., description="标题")


class HeadlineStructureResponse(BaseModel):
    """标题结构分析响应"""
    success: bool
    headline: str
    length: int
    has_number: bool
    has_question: bool
    has_emoji: bool
    has_colon: bool
    has_parentheses: bool
    numbers: List[str]
    structure_type: str
    is_optimal_length: bool


@router.post("/headline/analyze", response_model=HeadlineAnalyzeResponse)
async def analyze_headline(request: HeadlineAnalyzeRequest):
    """
    分析标题

    分析标题的吸引力、可读性、SEO效果
    """
    try:
        from backend.services.headline_analyzer import headline_analyzer_service

        result = await headline_analyzer_service.analyze_headline(
            request.headline, request.platform
        )

        return HeadlineAnalyzeResponse(
            success=True,
            attractiveness_score=result.attractiveness_score,
            readability_score=result.readability_score,
            seo_score=result.seo_score,
            emotional_appeal=result.emotional_appeal,
            power_words=result.power_words,
            issues=result.issues,
            suggestions=result.suggestions,
        )

    except Exception as e:
        logger.error(f"分析标题失败: {e}")
        return HeadlineAnalyzeResponse(
            success=False,
            attractiveness_score=70,
            readability_score=70,
            seo_score=70,
            emotional_appeal="",
            power_words=[],
            issues=[],
            suggestions=[],
        )


@router.post("/headline/optimize", response_model=HeadlineOptimizeResponse)
async def optimize_headline(request: HeadlineOptimizeRequest):
    """
    优化标题

    优化标题使其更具吸引力
    """
    try:
        from backend.services.headline_analyzer import headline_analyzer_service

        result = await headline_analyzer_service.optimize_headline(
            request.headline, request.platform, request.target_score
        )

        return HeadlineOptimizeResponse(
            success=True,
            original_headline=result["original_headline"],
            platform=result["platform"],
            target_score=result["target_score"],
            optimized_headlines=result["optimized_headlines"],
        )

    except Exception as e:
        logger.error(f"优化标题失败: {e}")
        return HeadlineOptimizeResponse(
            success=False,
            original_headline=request.headline,
            platform=request.platform,
            target_score=request.target_score,
            optimized_headlines=[],
        )


@router.post("/headline/structure", response_model=HeadlineStructureResponse)
async def analyze_headline_structure(request: HeadlineStructureRequest):
    """
    分析标题结构

    分析标题的结构特征
    """
    try:
        from backend.services.headline_analyzer import headline_analyzer_service

        result = headline_analyzer_service.analyze_headline_structure(request.headline)

        return HeadlineStructureResponse(
            success=True,
            headline=result["headline"],
            length=result["length"],
            has_number=result["has_number"],
            has_question=result["has_question"],
            has_emoji=result["has_emoji"],
            has_colon=result["has_colon"],
            has_parentheses=result["has_parentheses"],
            numbers=result["numbers"],
            structure_type=result["structure_type"],
            is_optimal_length=result["is_optimal_length"],
        )

    except Exception as e:
        logger.error(f"分析标题结构失败: {e}")
        return HeadlineStructureResponse(
            success=False,
            headline=request.headline,
            length=len(request.headline),
            has_number=False,
            has_question=False,
            has_emoji=False,
            has_colon=False,
            has_parentheses=False,
            numbers=[],
            structure_type="unknown",
            is_optimal_length=False,
        )


# Content Idea Generator Models
class IdeaGenerateRequest(BaseModel):
    """内容创意生成请求"""
    topic: str = Field(..., description="主题")
    platform: str = Field(default="xiaohongshu", description="平台")
    num: int = Field(default=5, ge=1, le=20, description="数量")


class IdeaGenerateResponse(BaseModel):
    """内容创意生成响应"""
    success: bool
    ideas: List[Dict[str, Any]]


class IdeaTrendRequest(BaseModel):
    """趋势结合创意请求"""
    trend_topic: str = Field(..., description="趋势话题")
    product_info: Dict[str, Any] = Field(..., description="产品信息")
    platform: str = Field(default="xiaohongshu", description="平台")


class IdeaTrendResponse(BaseModel):
    """趋势结合创意响应"""
    success: bool
    trend_topic: str
    product_name: str
    title: str
    framework: str
    connection_points: List[str]
    posting_time: str


@router.post("/ideas/generate", response_model=IdeaGenerateResponse)
async def generate_content_ideas(request: IdeaGenerateRequest):
    """
    生成内容创意

    根据主题生成多个内容创意
    """
    try:
        from backend.services.content_idea_generator import content_idea_generator_service

        ideas = await content_idea_generator_service.generate_ideas(
            request.topic, request.platform, request.num
        )

        return IdeaGenerateResponse(success=True, ideas=ideas)

    except Exception as e:
        logger.error(f"生成内容创意失败: {e}")
        return IdeaGenerateResponse(success=False, ideas=[])


@router.post("/ideas/from-trend", response_model=IdeaTrendResponse)
async def generate_idea_from_trend(request: IdeaTrendRequest):
    """
    结合趋势生成创意

    将趋势话题与产品结合生成内容创意
    """
    try:
        from backend.services.content_idea_generator import content_idea_generator_service

        result = await content_idea_generator_service.generate_from_trend(
            request.trend_topic, request.product_info, request.platform
        )

        return IdeaTrendResponse(
            success=True,
            trend_topic=result["trend_topic"],
            product_name=result["product_name"],
            title=result.get("title", ""),
            framework=result.get("framework", ""),
            connection_points=result.get("connection_points", []),
            posting_time=result.get("posting_time", ""),
        )

    except Exception as e:
        logger.error(f"结合趋势生成创意失败: {e}")
        return IdeaTrendResponse(
            success=False,
            trend_topic=request.trend_topic,
            product_name=request.product_info.get("name", ""),
            title="",
            framework="",
            connection_points=[],
            posting_time="",
        )


# Engagement Predictor Models
class EngagementPredictRequest(BaseModel):
    """互动预测请求"""
    content: str = Field(..., description="内容")
    title: str = Field(default="", description="标题")
    platform: str = Field(default="xiaohongshu", description="平台")
    follower_count: int = Field(default=10000, ge=0, description="粉丝数")


class EngagementPredictResponse(BaseModel):
    """互动预测响应"""
    success: bool
    predicted_likes: int
    predicted_comments: int
    predicted_shares: int
    engagement_rate: float
    confidence: str
    factors: List[str]


class EngagementOptimizeRequest(BaseModel):
    """互动优化请求"""
    content: str = Field(..., description="内容")
    platform: str = Field(default="xiaohongshu", description="平台")


class EngagementOptimizeResponse(BaseModel):
    """互动优化响应"""
    success: bool
    current_potential: str
    barriers: List[str]
    suggestions: List[str]


@router.post("/engagement/predict", response_model=EngagementPredictResponse)
async def predict_engagement(request: EngagementPredictRequest):
    """
    预测互动

    预测内容的互动表现
    """
    try:
        from backend.services.engagement_predictor import engagement_predictor_service

        result = await engagement_predictor_service.predict_engagement(
            request.content, request.title, request.platform, request.follower_count
        )

        return EngagementPredictResponse(
            success=True,
            predicted_likes=result.predicted_likes,
            predicted_comments=result.predicted_comments,
            predicted_shares=result.predicted_shares,
            engagement_rate=result.engagement_rate,
            confidence=result.confidence,
            factors=result.factors,
        )

    except Exception as e:
        logger.error(f"预测互动失败: {e}")
        return EngagementPredictResponse(
            success=False,
            predicted_likes=0,
            predicted_comments=0,
            predicted_shares=0,
            engagement_rate=0.0,
            confidence="低",
            factors=[],
        )


@router.post("/engagement/optimize", response_model=EngagementOptimizeResponse)
async def get_engagement_optimization(request: EngagementOptimizeRequest):
    """
    获取互动优化建议

    获取提高内容互动的建议
    """
    try:
        from backend.services.engagement_predictor import engagement_predictor_service

        result = await engagement_predictor_service.get_optimization_suggestions(
            request.content, request.platform
        )

        return EngagementOptimizeResponse(
            success=True,
            current_potential=result.get("current_potential", ""),
            barriers=result.get("barriers", []),
            suggestions=result.get("suggestions", []),
        )

    except Exception as e:
        logger.error(f"获取优化建议失败: {e}")
        return EngagementOptimizeResponse(
            success=False,
            current_potential="",
            barriers=[],
            suggestions=[],
        )


# Content ROI Calculator Models
class ROICalculateRequest(BaseModel):
    """ROI计算请求"""
    content_metrics: Dict[str, Any] = Field(..., description="内容指标")
    cost_breakdown: Dict[str, float] = Field(..., description="成本明细")
    platform: str = Field(default="xiaohongshu", description="平台")


class ROICalculateResponse(BaseModel):
    """ROI计算响应"""
    success: bool
    total_cost: float
    estimated_reach: int
    estimated_conversions: int
    estimated_revenue: float
    roi_percentage: float
    cost_per_reach: float
    cost_per_conversion: float


class ROIPotentialRequest(BaseModel):
    """ROI潜力估算请求"""
    content_type: str = Field(..., description="内容类型")
    platform: str = Field(default="xiaohongshu", description="平台")
    budget: float = Field(default=1000, ge=0, description="预算")


class ROIPotentialResponse(BaseModel):
    """ROI潜力估算响应"""
    success: bool
    content_type: str
    platform: str
    budget: float
    reach_range: Dict[str, int]
    engagement_estimate: Dict[str, int]
    conversion_estimate: int
    budget_allocation: Dict[str, float]


@router.post("/roi/calculate", response_model=ROICalculateResponse)
async def calculate_content_roi(request: ROICalculateRequest):
    """
    计算内容ROI

    计算内容的投资回报率
    """
    try:
        from backend.services.content_roi_calculator import content_roi_calculator_service

        result = await content_roi_calculator_service.calculate_roi(
            request.content_metrics, request.cost_breakdown, request.platform
        )

        return ROICalculateResponse(
            success=True,
            total_cost=result.total_cost,
            estimated_reach=result.estimated_reach,
            estimated_conversions=result.estimated_conversions,
            estimated_revenue=result.estimated_revenue,
            roi_percentage=result.roi_percentage,
            cost_per_reach=result.cost_per_reach,
            cost_per_conversion=result.cost_per_conversion,
        )

    except Exception as e:
        logger.error(f"计算ROI失败: {e}")
        return ROICalculateResponse(
            success=False,
            total_cost=0,
            estimated_reach=0,
            estimated_conversions=0,
            estimated_revenue=0,
            roi_percentage=0,
            cost_per_reach=0,
            cost_per_conversion=0,
        )


@router.post("/roi/estimate", response_model=ROIPotentialResponse)
async def estimate_potential(request: ROIPotentialRequest):
    """
    估算潜力

    估算内容类型的潜力
    """
    try:
        from backend.services.content_roi_calculator import content_roi_calculator_service

        result = await content_roi_calculator_service.estimate_potential(
            request.content_type, request.platform, request.budget
        )

        return ROIPotentialResponse(
            success=True,
            content_type=result["content_type"],
            platform=result["platform"],
            budget=result["budget"],
            reach_range=result.get("reach_range", {"min": 0, "max": 0}),
            engagement_estimate=result.get("engagement_estimate", {"likes": 0, "comments": 0}),
            conversion_estimate=result.get("conversion_estimate", 0),
            budget_allocation=result.get("budget_allocation", {}),
        )

    except Exception as e:
        logger.error(f"估算潜力失败: {e}")
        return ROIPotentialResponse(
            success=False,
            content_type=request.content_type,
            platform=request.platform,
            budget=request.budget,
            reach_range={"min": 0, "max": 0},
            engagement_estimate={"likes": 0, "comments": 0},
            conversion_estimate=0,
            budget_allocation={},
        )


# A/B Testing Analyzer Models
class ABTestDesignRequest(BaseModel):
    """A/B测试设计请求"""
    content_type: str = Field(..., description="内容类型")
    test_variable: str = Field(..., description="测试变量")
    platform: str = Field(default="xiaohongshu", description="平台")


class ABTestDesignResponse(BaseModel):
    """A/B测试设计响应"""
    success: bool
    content_type: str
    test_variable: str
    platform: str
    sample_size: int
    test_duration_days: int
    metrics_to_track: List[str]


class ABTestAnalyzeRequest(BaseModel):
    """A/B测试分析请求"""
    control_metrics: Dict[str, float] = Field(..., description="对照组指标")
    treatment_metrics: Dict[str, float] = Field(..., description="实验组指标")
    sample_size: int = Field(..., description="样本量")


class ABTestAnalyzeResponse(BaseModel):
    """A/B测试分析响应"""
    success: bool
    winner: str
    confidence_level: float
    is_significant: bool
    recommendation: str
    metrics_comparison: Dict[str, Any]


@router.post("/abtest/design", response_model=ABTestDesignResponse)
async def design_ab_test(request: ABTestDesignRequest):
    """
    设计A/B测试

    设计一个A/B测试方案
    """
    try:
        from backend.services.ab_testing_analyzer import ab_testing_analyzer_service

        result = await ab_testing_analyzer_service.design_test(
            request.content_type, request.test_variable, request.platform
        )

        return ABTestDesignResponse(
            success=True,
            content_type=result["content_type"],
            test_variable=result["test_variable"],
            platform=result["platform"],
            sample_size=result["sample_size"],
            test_duration_days=result["test_duration_days"],
            metrics_to_track=result["metrics_to_track"],
        )

    except Exception as e:
        logger.error(f"设计A/B测试失败: {e}")
        return ABTestDesignResponse(
            success=False,
            content_type=request.content_type,
            test_variable=request.test_variable,
            platform=request.platform,
            sample_size=1000,
            test_duration_days=7,
            metrics_to_track=[],
        )


@router.post("/abtest/analyze", response_model=ABTestAnalyzeResponse)
async def analyze_ab_test(request: ABTestAnalyzeRequest):
    """
    分析A/B测试结果

    分析A/B测试结果并给出建议
    """
    try:
        from backend.services.ab_testing_analyzer import ab_testing_analyzer_service

        result = await ab_testing_analyzer_service.analyze_results(
            request.control_metrics, request.treatment_metrics, request.sample_size
        )

        return ABTestAnalyzeResponse(
            success=True,
            winner=result.winner,
            confidence_level=result.confidence_level,
            is_significant=result.is_significant,
            recommendation=result.recommendation,
            metrics_comparison=result.metrics_comparison,
        )

    except Exception as e:
        logger.error(f"分析A/B测试失败: {e}")
        return ABTestAnalyzeResponse(
            success=False,
            winner="none",
            confidence_level=0,
            is_significant=False,
            recommendation="分析失败",
            metrics_comparison={},
        )


# Content Gap Analyzer Models
class ContentGapRequest(BaseModel):
    """内容差距分析请求"""
    existing_content: List[str] = Field(..., description="现有内容")
    target_topics: List[str] = Field(..., description="目标话题")
    platform: str = Field(default="xiaohongshu", description="平台")


class ContentGapResponse(BaseModel):
    """内容差距分析响应"""
    success: bool
    existing_count: int
    target_count: int
    covered_dimensions: List[str]
    gap_dimensions: List[str]
    opportunities: List[str]
    priorities: List[str]


class ContentOpportunityRequest(BaseModel):
    """内容机会请求"""
    industry: str = Field(..., description="行业")
    platform: str = Field(default="xiaohongshu", description="平台")
    num: int = Field(default=5, ge=1, le=20, description="数量")


class ContentOpportunityResponse(BaseModel):
    """内容机会响应"""
    success: bool
    opportunities: List[Dict[str, Any]]


@router.post("/content/gap", response_model=ContentGapResponse)
async def analyze_content_gap(request: ContentGapRequest):
    """
    分析内容差距

    分析现有内容与目标内容的差距
    """
    try:
        from backend.services.content_gap_analyzer import content_gap_analyzer_service

        result = await content_gap_analyzer_service.analyze_gap(
            request.existing_content, request.target_topics, request.platform
        )

        return ContentGapResponse(
            success=True,
            existing_count=result["existing_count"],
            target_count=result["target_count"],
            covered_dimensions=result["covered_dimensions"],
            gap_dimensions=result["gap_dimensions"],
            opportunities=result["opportunities"],
            priorities=result["priorities"],
        )

    except Exception as e:
        logger.error(f"分析内容差距失败: {e}")
        return ContentGapResponse(
            success=False,
            existing_count=len(request.existing_content),
            target_count=len(request.target_topics),
            covered_dimensions=[],
            gap_dimensions=[],
            opportunities=[],
            priorities=[],
        )


@router.post("/content/opportunities", response_model=ContentOpportunityResponse)
async def find_content_opportunities(request: ContentOpportunityRequest):
    """
    找内容机会

    找出内容创作的机会
    """
    try:
        from backend.services.content_gap_analyzer import content_gap_analyzer_service

        opportunities = await content_gap_analyzer_service.find_content_opportunities(
            request.industry, request.platform, request.num
        )

        return ContentOpportunityResponse(success=True, opportunities=opportunities)

    except Exception as e:
        logger.error(f"找内容机会失败: {e}")
        return ContentOpportunityResponse(success=False, opportunities=[])


# Caption Generator Models
class CaptionGenerateRequest(BaseModel):
    """文案生成请求"""
    content_type: str = Field(..., description="内容类型")
    topic: str = Field(..., description="话题")
    platform: str = Field(default="xiaohongshu", description="平台")
    style: str = Field(default="casual", description="风格")
    length: str = Field(default="medium", description="长度")


class CaptionGenerateResponse(BaseModel):
    """文案生成响应"""
    success: bool
    content_type: str
    topic: str
    platform: str
    style: str
    main_caption: str
    short_version: str
    hashtags: List[str]
    emojis: List[str]


class CaptionAdaptRequest(BaseModel):
    """文案适配请求"""
    original_caption: str = Field(..., description="原始文案")
    from_platform: str = Field(..., description="源平台")
    to_platform: str = Field(..., description="目标平台")


class CaptionAdaptResponse(BaseModel):
    """文案适配响应"""
    success: bool
    original_caption: str
    from_platform: str
    to_platform: str
    adapted_caption: str
    changes: List[str]
    tips: List[str]


@router.post("/caption/generate", response_model=CaptionGenerateResponse)
async def generate_caption(request: CaptionGenerateRequest):
    """
    生成文案

    生成各平台的文案
    """
    try:
        from backend.services.caption_generator import caption_generator_service

        result = await caption_generator_service.generate_caption(
            request.content_type, request.topic, request.platform, request.style, request.length
        )

        return CaptionGenerateResponse(
            success=True,
            content_type=result["content_type"],
            topic=result["topic"],
            platform=result["platform"],
            style=result["style"],
            main_caption=result.get("main_caption", ""),
            short_version=result.get("short_version", ""),
            hashtags=result.get("hashtags", []),
            emojis=result.get("emojis", []),
        )

    except Exception as e:
        logger.error(f"生成文案失败: {e}")
        return CaptionGenerateResponse(
            success=False,
            content_type=request.content_type,
            topic=request.topic,
            platform=request.platform,
            style=request.style,
            main_caption="",
            short_version="",
            hashtags=[],
            emojis=[],
        )


@router.post("/caption/adapt", response_model=CaptionAdaptResponse)
async def adapt_caption(request: CaptionAdaptRequest):
    """
    适配文案

    将文案适配到不同平台
    """
    try:
        from backend.services.caption_generator import caption_generator_service

        result = await caption_generator_service.adapt_caption(
            request.original_caption, request.from_platform, request.to_platform
        )

        return CaptionAdaptResponse(
            success=True,
            original_caption=result["original_caption"],
            from_platform=result["from_platform"],
            to_platform=result["to_platform"],
            adapted_caption=result.get("adapted_caption", ""),
            changes=result.get("changes", []),
            tips=result.get("tips", []),
        )

    except Exception as e:
        logger.error(f"适配文案失败: {e}")
        return CaptionAdaptResponse(
            success=False,
            original_caption=request.original_caption,
            from_platform=request.from_platform,
            to_platform=request.to_platform,
            adapted_caption=request.original_caption,
            changes=[],
            tips=[],
        )


# Video Hook Generator Models
class VideoHookRequest(BaseModel):
    """视频钩子请求"""
    topic: str = Field(..., description="主题")
    duration: int = Field(default=60, ge=5, le=300, description="时长(秒)")
    platform: str = Field(default="tiktok", description="平台")


class VideoHookResponse(BaseModel):
    """视频钩子响应"""
    success: bool
    topic: str
    duration: int
    platform: str
    hook_text: str
    visual_suggestion: str
    audio_suggestion: str


@router.post("/video/hook", response_model=VideoHookResponse)
async def generate_video_hook(request: VideoHookRequest):
    """生成视频开头钩子"""
    try:
        from backend.services.video_hook_generator import video_hook_generator_service
        result = await video_hook_generator_service.generate_hook(
            request.topic, request.duration, request.platform
        )
        return VideoHookResponse(
            success=True,
            topic=result["topic"],
            duration=result["duration"],
            platform=result["platform"],
            hook_text=result.get("hook_text", ""),
            visual_suggestion=result.get("visual_suggestion", ""),
            audio_suggestion=result.get("audio_suggestion", ""),
        )
    except Exception as e:
        logger.error(f"生成视频钩子失败: {e}")
        return VideoHookResponse(
            success=False, topic=request.topic, duration=request.duration,
            platform=request.platform, hook_text="", visual_suggestion="", audio_suggestion=""
        )


# Thread Generator Models
class ThreadGenerateRequest(BaseModel):
    """推文串请求"""
    topic: str = Field(..., description="主题")
    num_tweets: int = Field(default=5, ge=2, le=20, description="推文数量")
    platform: str = Field(default="twitter", description="平台")


class ThreadGenerateResponse(BaseModel):
    """推文串响应"""
    success: bool
    thread: List[Dict[str, Any]]


@router.post("/thread/generate", response_model=ThreadGenerateResponse)
async def generate_thread(request: ThreadGenerateRequest):
    """生成推文串"""
    try:
        from backend.services.thread_generator import thread_generator_service
        thread = await thread_generator_service.generate_thread(
            request.topic, request.num_tweets, request.platform
        )
        return ThreadGenerateResponse(success=True, thread=thread)
    except Exception as e:
        logger.error(f"生成推文串失败: {e}")
        return ThreadGenerateResponse(success=False, thread=[])


# FAQ Generator Models
class FAQGenerateRequest(BaseModel):
    """FAQ请求"""
    topic: str = Field(..., description="主题")
    num: int = Field(default=5, ge=1, le=20, description="数量")


class FAQGenerateResponse(BaseModel):
    """FAQ响应"""
    success: bool
    faqs: List[Dict[str, Any]]


@router.post("/faq/generate", response_model=FAQGenerateResponse)
async def generate_faq(request: FAQGenerateRequest):
    """生成FAQ"""
    try:
        from backend.services.faq_generator import faq_generator_service
        faqs = await faq_generator_service.generate_faq(request.topic, request.num)
        return FAQGenerateResponse(success=True, faqs=faqs)
    except Exception as e:
        logger.error(f"生成FAQ失败: {e}")
        return FAQGenerateResponse(success=False, faqs=[])


# HowTo Generator Models
class HowToGenerateRequest(BaseModel):
    """教程请求"""
    topic: str = Field(..., description="主题")
    difficulty: str = Field(default="medium", description="难度")
    platform: str = Field(default="xiaohongshu", description="平台")


class HowToGenerateResponse(BaseModel):
    """教程响应"""
    success: bool
    topic: str
    difficulty: str
    platform: str
    title: str
    steps: List[Dict[str, Any]]
    common_mistakes: List[str]
    pro_tips: List[str]


@router.post("/howto/generate", response_model=HowToGenerateResponse)
async def generate_howto(request: HowToGenerateRequest):
    """生成教程"""
    try:
        from backend.services.howto_generator import howto_generator_service
        result = await howto_generator_service.generate_howto(
            request.topic, request.difficulty, request.platform
        )
        return HowToGenerateResponse(
            success=True,
            topic=result["topic"],
            difficulty=result["difficulty"],
            platform=result["platform"],
            title=result.get("title", ""),
            steps=result.get("steps", []),
            common_mistakes=result.get("common_mistakes", []),
            pro_tips=result.get("pro_tips", []),
        )
    except Exception as e:
        logger.error(f"生成教程失败: {e}")
        return HowToGenerateResponse(
            success=False, topic=request.topic, difficulty=request.difficulty,
            platform=request.platform, title="", steps=[], common_mistakes=[], pro_tips=[]
        )


# Listicle Generator Models
class ListicleGenerateRequest(BaseModel):
    """清单请求"""
    topic: str = Field(..., description="主题")
    num_items: int = Field(default=5, ge=3, le=20, description="条目数量")
    list_type: str = Field(default="ranking", description="清单类型")
    platform: str = Field(default="xiaohongshu", description="平台")


class ListicleGenerateResponse(BaseModel):
    """清单响应"""
    success: bool
    topic: str
    num_items: int
    list_type: str
    platform: str
    title: str
    intro: str
    items: List[Dict[str, Any]]
    conclusion: str


@router.post("/listicle/generate", response_model=ListicleGenerateResponse)
async def generate_listicle(request: ListicleGenerateRequest):
    """生成清单"""
    try:
        from backend.services.listicle_generator import listicle_generator_service
        result = await listicle_generator_service.generate_listicle(
            request.topic, request.num_items, request.list_type, request.platform
        )
        return ListicleGenerateResponse(
            success=True,
            topic=result["topic"],
            num_items=result["num_items"],
            list_type=result["list_type"],
            platform=result["platform"],
            title=result.get("title", ""),
            intro=result.get("intro", ""),
            items=result.get("items", []),
            conclusion=result.get("conclusion", ""),
        )
    except Exception as e:
        logger.error(f"生成清单失败: {e}")
        return ListicleGenerateResponse(
            success=False, topic=request.topic, num_items=request.num_items,
            list_type=request.list_type, platform=request.platform,
            title="", intro="", items=[], conclusion=""
        )


# Comparison Generator Models
class ComparisonGenerateRequest(BaseModel):
    """对比请求"""
    item_a: str = Field(..., description="对比项A")
    item_b: str = Field(..., description="对比项B")
    comparison_dimensions: List[str] = Field(..., description="对比维度")
    platform: str = Field(default="xiaohongshu", description="平台")


class ComparisonGenerateResponse(BaseModel):
    """对比响应"""
    success: bool
    item_a: str
    item_b: str
    platform: str
    comparison_table: List[Dict[str, Any]]
    summary: str
    recommendation: str


@router.post("/comparison/generate", response_model=ComparisonGenerateResponse)
async def generate_comparison(request: ComparisonGenerateRequest):
    """生成对比"""
    try:
        from backend.services.comparison_generator import comparison_generator_service
        result = await comparison_generator_service.generate_comparison(
            request.item_a, request.item_b, request.comparison_dimensions, request.platform
        )
        return ComparisonGenerateResponse(
            success=True,
            item_a=result["item_a"],
            item_b=result["item_b"],
            platform=result["platform"],
            comparison_table=result.get("comparison_table", []),
            summary=result.get("summary", ""),
            recommendation=result.get("recommendation", ""),
        )
    except Exception as e:
        logger.error(f"生成对比失败: {e}")
        return ComparisonGenerateResponse(
            success=False, item_a=request.item_a, item_b=request.item_b,
            platform=request.platform, comparison_table=[], summary="", recommendation=""
        )


# Testimonial Generator Models
class TestimonialGenerateRequest(BaseModel):
    """用户评价请求"""
    product_name: str = Field(..., description="产品名称")
    num: int = Field(default=5, ge=1, le=20, description="数量")
    platform: str = Field(default="xiaohongshu", description="平台")


class TestimonialGenerateResponse(BaseModel):
    """用户评价响应"""
    success: bool
    testimonials: List[Dict[str, Any]]


@router.post("/testimonial/generate", response_model=TestimonialGenerateResponse)
async def generate_testimonials(request: TestimonialGenerateRequest):
    """生成用户评价"""
    try:
        from backend.services.testimonial_generator import testimonial_generator_service
        testimonials = await testimonial_generator_service.generate_testimonials(
            request.product_name, request.num, request.platform
        )
        return TestimonialGenerateResponse(success=True, testimonials=testimonials)
    except Exception as e:
        logger.error(f"生成用户评价失败: {e}")
        return TestimonialGenerateResponse(success=False, testimonials=[])


# Story Generator Models
class StoryGenerateRequest(BaseModel):
    """故事请求"""
    topic: str = Field(..., description="主题")
    story_type: str = Field(default="personal", description="故事类型")
    platform: str = Field(default="xiaohongshu", description="平台")


class StoryGenerateResponse(BaseModel):
    """故事响应"""
    success: bool
    topic: str
    story_type: str
    platform: str
    title: str
    setting: str
    characters: List[str]
    plot_points: List[str]
    emotional_takeaway: str


@router.post("/story/generate", response_model=StoryGenerateResponse)
async def generate_story(request: StoryGenerateRequest):
    """生成故事"""
    try:
        from backend.services.story_generator import story_generator_service
        result = await story_generator_service.generate_story(
            request.topic, request.story_type, request.platform
        )
        return StoryGenerateResponse(
            success=True,
            topic=result["topic"],
            story_type=result["story_type"],
            platform=result["platform"],
            title=result.get("title", ""),
            setting=result.get("setting", ""),
            characters=result.get("characters", []),
            plot_points=result.get("plot_points", []),
            emotional_takeaway=result.get("emotional_takeaway", ""),
        )
    except Exception as e:
        logger.error(f"生成故事失败: {e}")
        return StoryGenerateResponse(
            success=False, topic=request.topic, story_type=request.story_type,
            platform=request.platform, title="", setting="", characters=[],
            plot_points=[], emotional_takeaway=""
        )


# Poll Generator Models
class PollGenerateRequest(BaseModel):
    """投票请求"""
    topic: str = Field(..., description="主题")
    num_options: int = Field(default=4, ge=2, le=10, description="选项数量")
    platform: str = Field(default="weibo", description="平台")


class PollGenerateResponse(BaseModel):
    """投票响应"""
    success: bool
    topic: str
    platform: str
    question: str
    options: List[str]
    duration_days: int
    add_poll_note: str


@router.post("/poll/generate", response_model=PollGenerateResponse)
async def generate_poll(request: PollGenerateRequest):
    """生成投票"""
    try:
        from backend.services.poll_generator import poll_generator_service
        result = await poll_generator_service.generate_poll(
            request.topic, request.num_options, request.platform
        )
        return PollGenerateResponse(
            success=True,
            topic=result["topic"],
            platform=result["platform"],
            question=result.get("question", ""),
            options=result.get("options", []),
            duration_days=result.get("duration_days", 7),
            add_poll_note=result.get("add_poll_note", ""),
        )
    except Exception as e:
        logger.error(f"生成投票失败: {e}")
        return PollGenerateResponse(
            success=False, topic=request.topic, platform=request.platform,
            question="", options=[], duration_days=7, add_poll_note=""
        )


# Quote Card Generator Models
class QuoteGenerateRequest(BaseModel):
    """金句请求"""
    topic: str = Field(..., description="主题")
    num: int = Field(default=3, ge=1, le=10, description="数量")
    platform: str = Field(default="xiaohongshu", description="平台")


class QuoteGenerateResponse(BaseModel):
    """金句响应"""
    success: bool
    quotes: List[Dict[str, Any]]


@router.post("/quote/generate", response_model=QuoteGenerateResponse)
async def generate_quote(request: QuoteGenerateRequest):
    """生成金句"""
    try:
        from backend.services.quote_card_generator import quote_card_generator_service
        quotes = await quote_card_generator_service.generate_quote(
            request.topic, request.num, request.platform
        )
        return QuoteGenerateResponse(success=True, quotes=quotes)
    except Exception as e:
        logger.error(f"生成金句失败: {e}")
        return QuoteGenerateResponse(success=False, quotes=[])


# Seasonal Content Generator Models
class FestivalContentRequest(BaseModel):
    """节日内容请求"""
    festival: str = Field(..., description="节日")
    product_info: Dict[str, Any] = Field(..., description="产品信息")
    platform: str = Field(default="xiaohongshu", description="平台")


class FestivalContentResponse(BaseModel):
    """节日内容响应"""
    success: bool
    festival: str
    product_name: str
    platform: str
    content_idea: str
    title: str
    key_points: List[str]
    hashtag_suggestions: List[str]


@router.post("/seasonal/festival", response_model=FestivalContentResponse)
async def generate_festival_content(request: FestivalContentRequest):
    """生成节日内容"""
    try:
        from backend.services.seasonal_content_generator import seasonal_content_generator_service
        result = await seasonal_content_generator_service.generate_festival_content(
            request.festival, request.product_info, request.platform
        )
        return FestivalContentResponse(
            success=True,
            festival=result["festival"],
            product_name=result["product_name"],
            platform=result["platform"],
            content_idea=result.get("content_idea", ""),
            title=result.get("title", ""),
            key_points=result.get("key_points", []),
            hashtag_suggestions=result.get("hashtag_suggestions", []),
        )
    except Exception as e:
        logger.error(f"生成节日内容失败: {e}")
        return FestivalContentResponse(
            success=False, festival=request.festival, product_name="",
            platform=request.platform, content_idea="", title="", key_points=[], hashtag_suggestions=[]
        )


# Team Introduction Generator Models
class TeamIntroductionRequest(BaseModel):
    """团队介绍请求"""
    team_name: str = Field(..., description="团队名称")
    company_name: str = Field(..., description="公司名称")
    team_size: int = Field(default=5, ge=1, description="团队规模")


class TeamIntroductionResponse(BaseModel):
    """团队介绍响应"""
    success: bool
    team_name: str
    company_name: str
    team_size: int
    tagline: str
    description: str
    core_values: List[str]
    key_strengths: List[str]
    fun_facts: List[str]


@router.post("/team/introduction", response_model=TeamIntroductionResponse)
async def generate_team_introduction(request: TeamIntroductionRequest):
    """生成团队介绍"""
    try:
        from backend.services.team_introduction_generator import team_introduction_generator_service
        result = await team_introduction_generator_service.generate_team_introduction(
            request.team_name, request.company_name, request.team_size
        )
        return TeamIntroductionResponse(
            success=True,
            team_name=result["team_name"],
            company_name=result["company_name"],
            team_size=result["team_size"],
            tagline=result.get("tagline", ""),
            description=result.get("description", ""),
            core_values=result.get("core_values", []),
            key_strengths=result.get("key_strengths", []),
            fun_facts=result.get("fun_facts", []),
        )
    except Exception as e:
        logger.error(f"生成团队介绍失败: {e}")
        return TeamIntroductionResponse(
            success=False, team_name=request.team_name, company_name=request.company_name,
            team_size=request.team_size, tagline="", description="", core_values=[], key_strengths=[], fun_facts=[]
        )


# Brand Story Generator Models
class BrandStoryRequest(BaseModel):
    """品牌故事请求"""
    brand_name: str = Field(..., description="品牌名称")
    industry: str = Field(..., description="行业")
    founding_year: int = Field(default=2020, description="成立年份")


class BrandStoryResponse(BaseModel):
    """品牌故事响应"""
    success: bool
    brand_name: str
    industry: str
    founding_year: int
    origin_story: str
    mission: str
    vision: str
    values: List[str]
    founder_message: str


@router.post("/brand/story", response_model=BrandStoryResponse)
async def generate_brand_story(request: BrandStoryRequest):
    """生成品牌故事"""
    try:
        from backend.services.brand_story_generator import brand_story_generator_service
        result = await brand_story_generator_service.generate_brand_story(
            request.brand_name, request.industry, request.founding_year
        )
        return BrandStoryResponse(
            success=True,
            brand_name=result["brand_name"],
            industry=result["industry"],
            founding_year=result["founding_year"],
            origin_story=result.get("origin_story", ""),
            mission=result.get("mission", ""),
            vision=result.get("vision", ""),
            values=result.get("values", []),
            founder_message=result.get("founder_message", ""),
        )
    except Exception as e:
        logger.error(f"生成品牌故事失败: {e}")
        return BrandStoryResponse(
            success=False, brand_name=request.brand_name, industry=request.industry,
            founding_year=request.founding_year, origin_story="", mission="", vision="", values=[], founder_message=""
        )


# Product Description Generator Models
class ProductDescriptionRequest(BaseModel):
    """产品描述请求"""
    product_name: str = Field(..., description="产品名称")
    category: str = Field(..., description="产品类别")
    target_audience: str = Field(..., description="目标受众")


class ProductDescriptionResponse(BaseModel):
    """产品描述响应"""
    success: bool
    product_name: str
    category: str
    target_audience: str
    short_description: str
    key_features: List[str]
    specifications: List[str]
    use_cases: List[str]
    benefits: List[str]
    packaging_info: str


@router.post("/product/description", response_model=ProductDescriptionResponse)
async def generate_product_description(request: ProductDescriptionRequest):
    """生成产品描述"""
    try:
        from backend.services.product_description_generator import product_description_generator_service
        result = await product_description_generator_service.generate_product_description(
            request.product_name, request.category, request.target_audience
        )
        return ProductDescriptionResponse(
            success=True,
            product_name=result["product_name"],
            category=result["category"],
            target_audience=result["target_audience"],
            short_description=result.get("short_description", ""),
            key_features=result.get("key_features", []),
            specifications=result.get("specifications", []),
            use_cases=result.get("use_cases", []),
            benefits=result.get("benefits", []),
            packaging_info=result.get("packaging_info", ""),
        )
    except Exception as e:
        logger.error(f"生成产品描述失败: {e}")
        return ProductDescriptionResponse(
            success=False, product_name=request.product_name, category=request.category,
            target_audience=request.target_audience, short_description="", key_features=[],
            specifications=[], use_cases=[], benefits=[], packaging_info=""
        )


# Career Opportunity Generator Models
class CareerOpportunityRequest(BaseModel):
    """职位招聘请求"""
    job_title: str = Field(..., description="职位名称")
    department: str = Field(..., description="部门")
    location: str = Field(..., description="工作地点")
    employment_type: str = Field(default="full-time", description="雇佣类型")


class CareerOpportunityResponse(BaseModel):
    """职位招聘响应"""
    success: bool
    job_title: str
    department: str
    location: str
    employment_type: str
    job_summary: str
    responsibilities: List[str]
    requirements: List[str]
    nice_to_have: List[str]
    benefits: List[str]
    growth_opportunities: str


@router.post("/career/opportunity", response_model=CareerOpportunityResponse)
async def generate_career_opportunity(request: CareerOpportunityRequest):
    """生成职位招聘"""
    try:
        from backend.services.career_opportunity_generator import career_opportunity_generator_service
        result = await career_opportunity_generator_service.generate_career_opportunity(
            request.job_title, request.department, request.location, request.employment_type
        )
        return CareerOpportunityResponse(
            success=True,
            job_title=result["job_title"],
            department=result["department"],
            location=result["location"],
            employment_type=result["employment_type"],
            job_summary=result.get("job_summary", ""),
            responsibilities=result.get("responsibilities", []),
            requirements=result.get("requirements", []),
            nice_to_have=result.get("nice_to_have", []),
            benefits=result.get("benefits", []),
            growth_opportunities=result.get("growth_opportunities", ""),
        )
    except Exception as e:
        logger.error(f"生成职位招聘失败: {e}")
        return CareerOpportunityResponse(
            success=False, job_title=request.job_title, department=request.department,
            location=request.location, employment_type=request.employment_type,
            job_summary="", responsibilities=[], requirements=[], nice_to_have=[], benefits=[], growth_opportunities=""
        )


# Event Agenda Generator Models
class EventAgendaRequest(BaseModel):
    """活动议程请求"""
    event_name: str = Field(..., description="活动名称")
    event_type: str = Field(..., description="活动类型")
    duration_hours: float = Field(default=2.0, description="活动时长")
    num_participants: int = Field(default=50, description="参与人数")


class EventAgendaResponse(BaseModel):
    """活动议程响应"""
    success: bool
    event_name: str
    event_type: str
    duration_hours: float
    num_participants: int
    agenda_items: List[Dict[str, Any]]
    logistics: List[str]
    materials_needed: List[str]
    success_metrics: str


@router.post("/event/agenda", response_model=EventAgendaResponse)
async def generate_event_agenda(request: EventAgendaRequest):
    """生成活动议程"""
    try:
        from backend.services.event_agenda_generator import event_agenda_generator_service
        result = await event_agenda_generator_service.generate_event_agenda(
            request.event_name, request.event_type, request.duration_hours, request.num_participants
        )
        return EventAgendaResponse(
            success=True,
            event_name=result["event_name"],
            event_type=result["event_type"],
            duration_hours=result["duration_hours"],
            num_participants=result["num_participants"],
            agenda_items=result.get("agenda_items", []),
            logistics=result.get("logistics", []),
            materials_needed=result.get("materials_needed", []),
            success_metrics=result.get("success_metrics", ""),
        )
    except Exception as e:
        logger.error(f"生成活动议程失败: {e}")
        return EventAgendaResponse(
            success=False, event_name=request.event_name, event_type=request.event_type,
            duration_hours=request.duration_hours, num_participants=request.num_participants,
            agenda_items=[], logistics=[], materials_needed=[], success_metrics=""
        )


# Workshop Outline Generator Models
class WorkshopOutlineRequest(BaseModel):
    """工作坊大纲请求"""
    workshop_title: str = Field(..., description="工作坊标题")
    target_audience: str = Field(..., description="目标受众")
    duration_hours: float = Field(default=3.0, description="时长")
    difficulty_level: str = Field(default="intermediate", description="难度级别")


class WorkshopOutlineResponse(BaseModel):
    """工作坊大纲响应"""
    success: bool
    workshop_title: str
    target_audience: str
    duration_hours: float
    difficulty_level: str
    learning_objectives: List[str]
    modules: List[Dict[str, Any]]
    materials_required: List[str]
    assessment_methods: List[str]
    follow_up_resources: List[str]


@router.post("/workshop/outline", response_model=WorkshopOutlineResponse)
async def generate_workshop_outline(request: WorkshopOutlineRequest):
    """生成工作坊大纲"""
    try:
        from backend.services.workshop_outline_generator import workshop_outline_generator_service
        result = await workshop_outline_generator_service.generate_workshop_outline(
            request.workshop_title, request.target_audience, request.duration_hours, request.difficulty_level
        )
        return WorkshopOutlineResponse(
            success=True,
            workshop_title=result["workshop_title"],
            target_audience=result["target_audience"],
            duration_hours=result["duration_hours"],
            difficulty_level=result["difficulty_level"],
            learning_objectives=result.get("learning_objectives", []),
            modules=result.get("modules", []),
            materials_required=result.get("materials_required", []),
            assessment_methods=result.get("assessment_methods", []),
            follow_up_resources=result.get("follow_up_resources", []),
        )
    except Exception as e:
        logger.error(f"生成工作坊大纲失败: {e}")
        return WorkshopOutlineResponse(
            success=False, workshop_title=request.workshop_title, target_audience=request.target_audience,
            duration_hours=request.duration_hours, difficulty_level=request.difficulty_level,
            learning_objectives=[], modules=[], materials_required=[], assessment_methods=[], follow_up_resources=[]
        )


# Book Summary Generator Models
class BookSummaryRequest(BaseModel):
    """书籍摘要请求"""
    book_title: str = Field(..., description="书名")
    author: str = Field(..., description="作者")
    genre: str = Field(default="non-fiction", description="类型")


class BookSummaryResponse(BaseModel):
    """书籍摘要响应"""
    success: bool
    book_title: str
    author: str
    genre: str
    book_overview: str
    key_themes: List[str]
    chapter_summaries: List[Dict[str, str]]
    main_takeaways: List[str]
    notable_quotes: List[str]
    reading_recommendations: str
    who_should_read: str


@router.post("/book/summary", response_model=BookSummaryResponse)
async def generate_book_summary(request: BookSummaryRequest):
    """生成书籍摘要"""
    try:
        from backend.services.book_summary_generator import book_summary_generator_service
        result = await book_summary_generator_service.generate_book_summary(
            request.book_title, request.author, request.genre
        )
        return BookSummaryResponse(
            success=True,
            book_title=result["book_title"],
            author=result["author"],
            genre=result["genre"],
            book_overview=result.get("book_overview", ""),
            key_themes=result.get("key_themes", []),
            chapter_summaries=result.get("chapter_summaries", []),
            main_takeaways=result.get("main_takeaways", []),
            notable_quotes=result.get("notable_quotes", []),
            reading_recommendations=result.get("reading_recommendations", ""),
            who_should_read=result.get("who_should_read", ""),
        )
    except Exception as e:
        logger.error(f"生成书籍摘要失败: {e}")
        return BookSummaryResponse(
            success=False, book_title=request.book_title, author=request.author, genre=request.genre,
            book_overview="", key_themes=[], chapter_summaries=[], main_takeaways=[],
            notable_quotes=[], reading_recommendations="", who_should_read=""
        )


# Podcast Episode Generator Models
class PodcastEpisodeRequest(BaseModel):
    """播客剧集请求"""
    episode_title: str = Field(..., description="剧集标题")
    topic: str = Field(..., description="主题")
    duration_minutes: int = Field(default=30, description="时长")
    episode_type: str = Field(default="solo", description="剧集类型")


class PodcastEpisodeResponse(BaseModel):
    """播客剧集响应"""
    success: bool
    episode_title: str
    topic: str
    duration_minutes: int
    episode_type: str
    episode_description: str
    key_talking_points: List[str]
    timestamps: List[Dict[str, str]]
    guest_bio: str
    resources_mentioned: List[str]
    call_to_action: str
    outro_message: str


@router.post("/podcast/episode", response_model=PodcastEpisodeResponse)
async def generate_podcast_episode(request: PodcastEpisodeRequest):
    """生成播客剧集"""
    try:
        from backend.services.podcast_episode_generator import podcast_episode_generator_service
        result = await podcast_episode_generator_service.generate_podcast_episode(
            request.episode_title, request.topic, request.duration_minutes, request.episode_type
        )
        return PodcastEpisodeResponse(
            success=True,
            episode_title=result["episode_title"],
            topic=result["topic"],
            duration_minutes=result["duration_minutes"],
            episode_type=result["episode_type"],
            episode_description=result.get("episode_description", ""),
            key_talking_points=result.get("key_talking_points", []),
            timestamps=result.get("timestamps", []),
            guest_bio=result.get("guest_bio", ""),
            resources_mentioned=result.get("resources_mentioned", []),
            call_to_action=result.get("call_to_action", ""),
            outro_message=result.get("outro_message", ""),
        )
    except Exception as e:
        logger.error(f"生成播客剧集失败: {e}")
        return PodcastEpisodeResponse(
            success=False, episode_title=request.episode_title, topic=request.topic,
            duration_minutes=request.duration_minutes, episode_type=request.episode_type,
            episode_description="", key_talking_points=[], timestamps=[], guest_bio="",
            resources_mentioned=[], call_to_action="", outro_message=""
        )


# Video Tutorial Generator Models
class VideoTutorialRequest(BaseModel):
    """视频教程请求"""
    tutorial_topic: str = Field(..., description="教程主题")
    skill_level: str = Field(default="beginner", description="技能级别")
    estimated_duration: int = Field(default=10, description="预计时长")
    platform: str = Field(default="youtube", description="平台")


class VideoTutorialResponse(BaseModel):
    """视频教程响应"""
    success: bool
    tutorial_topic: str
    skill_level: str
    estimated_duration: int
    platform: str
    tutorial_title: str
    video_description: str
    key_steps: List[Dict[str, Any]]
    required_materials: List[str]
    tips_and_warnings: List[str]
    related_tutorials: List[str]
    chapters: List[str]


@router.post("/video/tutorial", response_model=VideoTutorialResponse)
async def generate_video_tutorial(request: VideoTutorialRequest):
    """生成视频教程"""
    try:
        from backend.services.video_tutorial_generator import video_tutorial_generator_service
        result = await video_tutorial_generator_service.generate_video_tutorial(
            request.tutorial_topic, request.skill_level, request.estimated_duration, request.platform
        )
        return VideoTutorialResponse(
            success=True,
            tutorial_topic=result["tutorial_topic"],
            skill_level=result["skill_level"],
            estimated_duration=result["estimated_duration"],
            platform=result["platform"],
            tutorial_title=result.get("tutorial_title", ""),
            video_description=result.get("video_description", ""),
            key_steps=result.get("key_steps", []),
            required_materials=result.get("required_materials", []),
            tips_and_warnings=result.get("tips_and_warnings", []),
            related_tutorials=result.get("related_tutorials", []),
            chapters=result.get("chapters", []),
        )
    except Exception as e:
        logger.error(f"生成视频教程失败: {e}")
        return VideoTutorialResponse(
            success=False, tutorial_topic=request.tutorial_topic, skill_level=request.skill_level,
            estimated_duration=request.estimated_duration, platform=request.platform,
            tutorial_title="", video_description="", key_steps=[], required_materials=[],
            tips_and_warnings=[], related_tutorials=[], chapters=[]
        )


# Meeting Agenda Generator Models
class MeetingAgendaRequest(BaseModel):
    """会议议程请求"""
    meeting_title: str = Field(..., description="会议标题")
    meeting_type: str = Field(default="team-meeting", description="会议类型")
    duration_minutes: int = Field(default=60, description="会议时长")


class MeetingAgendaResponse(BaseModel):
    """会议议程响应"""
    success: bool
    meeting_title: str
    meeting_type: str
    duration_minutes: int
    meeting_objectives: List[str]
    agenda_items: List[Dict[str, Any]]
    pre_materials: List[str]
    action_items: List[str]
    meeting_etiquette: str


@router.post("/meeting/agenda", response_model=MeetingAgendaResponse)
async def generate_meeting_agenda(request: MeetingAgendaRequest):
    """生成会议议程"""
    try:
        from backend.services.meeting_agenda_generator import meeting_agenda_generator_service
        result = await meeting_agenda_generator_service.generate_meeting_agenda(
            request.meeting_title, request.meeting_type, request.duration_minutes
        )
        return MeetingAgendaResponse(
            success=True,
            meeting_title=result["meeting_title"],
            meeting_type=result["meeting_type"],
            duration_minutes=result["duration_minutes"],
            meeting_objectives=result.get("meeting_objectives", []),
            agenda_items=result.get("agenda_items", []),
            pre_materials=result.get("pre_materials", []),
            action_items=result.get("action_items", []),
            meeting_etiquette=result.get("meeting_etiquette", ""),
        )
    except Exception as e:
        logger.error(f"生成会议议程失败: {e}")
        return MeetingAgendaResponse(
            success=False, meeting_title=request.meeting_title, meeting_type=request.meeting_type,
            duration_minutes=request.duration_minutes, meeting_objectives=[], agenda_items=[],
            pre_materials=[], action_items=[], meeting_etiquette=""
        )


# Project Brief Generator Models
class ProjectBriefRequest(BaseModel):
    """项目简介请求"""
    project_name: str = Field(..., description="项目名称")
    project_type: str = Field(..., description="项目类型")
    team_size: int = Field(default=5, description="团队规模")
    deadline: str = Field(default="4 weeks", description="截止日期")


class ProjectBriefResponse(BaseModel):
    """项目简介响应"""
    success: bool
    project_name: str
    project_type: str
    team_size: int
    deadline: str
    executive_summary: str
    project_goals: List[str]
    scope: Dict[str, List[str]]
    key_deliverables: List[str]
    resource_requirements: List[str]
    risk_factors: List[str]
    success_criteria: str


@router.post("/project/brief", response_model=ProjectBriefResponse)
async def generate_project_brief(request: ProjectBriefRequest):
    """生成项目简介"""
    try:
        from backend.services.project_brief_generator import project_brief_generator_service
        result = await project_brief_generator_service.generate_project_brief(
            request.project_name, request.project_type, request.team_size, request.deadline
        )
        return ProjectBriefResponse(
            success=True,
            project_name=result["project_name"],
            project_type=result["project_type"],
            team_size=result["team_size"],
            deadline=result["deadline"],
            executive_summary=result.get("executive_summary", ""),
            project_goals=result.get("project_goals", []),
            scope=result.get("scope", {"in_scope": [], "out_of_scope": []}),
            key_deliverables=result.get("key_deliverables", []),
            resource_requirements=result.get("resource_requirements", []),
            risk_factors=result.get("risk_factors", []),
            success_criteria=result.get("success_criteria", ""),
        )
    except Exception as e:
        logger.error(f"生成项目简介失败: {e}")
        return ProjectBriefResponse(
            success=False, project_name=request.project_name, project_type=request.project_type,
            team_size=request.team_size, deadline=request.deadline, executive_summary="",
            project_goals=[], scope={"in_scope": [], "out_of_scope": []}, key_deliverables=[],
            resource_requirements=[], risk_factors=[], success_criteria=""
        )


# Client Proposal Generator Models
class ClientProposalRequest(BaseModel):
    """客户提案请求"""
    client_name: str = Field(..., description="客户名称")
    service_type: str = Field(..., description="服务类型")
    project_scale: str = Field(default="medium", description="项目规模")


class ClientProposalResponse(BaseModel):
    """客户提案响应"""
    success: bool
    client_name: str
    service_type: str
    project_scale: str
    proposal_title: str
    executive_summary: str
    proposed_solution: str
    scope_of_work: List[str]
    timeline: str
    pricing_breakdown: List[Dict[str, Any]]
    payment_terms: str
    terms_and_conditions: List[str]
    next_steps: List[str]


@router.post("/proposal/client", response_model=ClientProposalResponse)
async def generate_client_proposal(request: ClientProposalRequest):
    """生成客户提案"""
    try:
        from backend.services.client_proposal_generator import client_proposal_generator_service
        result = await client_proposal_generator_service.generate_client_proposal(
            request.client_name, request.service_type, request.project_scale
        )
        return ClientProposalResponse(
            success=True,
            client_name=result["client_name"],
            service_type=result["service_type"],
            project_scale=result["project_scale"],
            proposal_title=result.get("proposal_title", ""),
            executive_summary=result.get("executive_summary", ""),
            proposed_solution=result.get("proposed_solution", ""),
            scope_of_work=result.get("scope_of_work", []),
            timeline=result.get("timeline", ""),
            pricing_breakdown=result.get("pricing_breakdown", []),
            payment_terms=result.get("payment_terms", ""),
            terms_and_conditions=result.get("terms_and_conditions", []),
            next_steps=result.get("next_steps", []),
        )
    except Exception as e:
        logger.error(f"生成客户提案失败: {e}")
        return ClientProposalResponse(
            success=False, client_name=request.client_name, service_type=request.service_type,
            project_scale=request.project_scale, proposal_title="", executive_summary="",
            proposed_solution="", scope_of_work=[], timeline="", pricing_breakdown=[],
            payment_terms="", terms_and_conditions=[], next_steps=[]
        )


# Performance Review Generator Models
class PerformanceReviewRequest(BaseModel):
    """绩效评估请求"""
    employee_name: str = Field(..., description="员工姓名")
    department: str = Field(..., description="部门")
    review_period: str = Field(default="2025 Annual", description="评估周期")
    position: str = Field(default="Staff", description="职位")


class PerformanceReviewResponse(BaseModel):
    """绩效评估响应"""
    success: bool
    employee_name: str
    department: str
    review_period: str
    position: str
    overall_rating: str
    achievements: List[str]
    areas_for_improvement: List[str]
    goal_progress: List[Dict[str, str]]
    competency_ratings: List[str]
    development_plan: str
    manager_feedback: str
    next_period_goals: List[str]


@router.post("/performance/review", response_model=PerformanceReviewResponse)
async def generate_performance_review(request: PerformanceReviewRequest):
    """生成绩效评估"""
    try:
        from backend.services.performance_review_generator import performance_review_generator_service
        result = await performance_review_generator_service.generate_performance_review(
            request.employee_name, request.department, request.review_period, request.position
        )
        return PerformanceReviewResponse(
            success=True,
            employee_name=result["employee_name"],
            department=result["department"],
            review_period=result["review_period"],
            position=result["position"],
            overall_rating=result.get("overall_rating", ""),
            achievements=result.get("achievements", []),
            areas_for_improvement=result.get("areas_for_improvement", []),
            goal_progress=result.get("goal_progress", []),
            competency_ratings=result.get("competency_ratings", []),
            development_plan=result.get("development_plan", ""),
            manager_feedback=result.get("manager_feedback", ""),
            next_period_goals=result.get("next_period_goals", []),
        )
    except Exception as e:
        logger.error(f"生成绩效评估失败: {e}")
        return PerformanceReviewResponse(
            success=False, employee_name=request.employee_name, department=request.department,
            review_period=request.review_period, position=request.position, overall_rating="",
            achievements=[], areas_for_improvement=[], goal_progress=[], competency_ratings=[],
            development_plan="", manager_feedback="", next_period_goals=[]
        )


# Business Plan Generator Models
class BusinessPlanRequest(BaseModel):
    """商业计划请求"""
    company_name: str = Field(..., description="公司名称")
    industry: str = Field(..., description="行业")
    stage: str = Field(default="startup", description="阶段")


class BusinessPlanResponse(BaseModel):
    """商业计划响应"""
    success: bool
    company_name: str
    industry: str
    stage: str
    executive_summary: str
    problem_statement: str
    solution: str
    market_analysis: str
    business_model: str
    competitive_advantage: str
    target_customers: List[str]
    marketing_strategy: str
    team_overview: str
    financial_projections: str
    funding_requirements: str
    use_of_funds: str


@router.post("/business/plan", response_model=BusinessPlanResponse)
async def generate_business_plan(request: BusinessPlanRequest):
    """生成商业计划"""
    try:
        from backend.services.business_plan_generator import business_plan_generator_service
        result = await business_plan_generator_service.generate_business_plan(
            request.company_name, request.industry, request.stage
        )
        return BusinessPlanResponse(
            success=True,
            company_name=result["company_name"],
            industry=result["industry"],
            stage=result["stage"],
            executive_summary=result.get("executive_summary", ""),
            problem_statement=result.get("problem_statement", ""),
            solution=result.get("solution", ""),
            market_analysis=result.get("market_analysis", ""),
            business_model=result.get("business_model", ""),
            competitive_advantage=result.get("competitive_advantage", ""),
            target_customers=result.get("target_customers", []),
            marketing_strategy=result.get("marketing_strategy", ""),
            team_overview=result.get("team_overview", ""),
            financial_projections=result.get("financial_projections", ""),
            funding_requirements=result.get("funding_requirements", ""),
            use_of_funds=result.get("use_of_funds", ""),
        )
    except Exception as e:
        logger.error(f"生成商业计划失败: {e}")
        return BusinessPlanResponse(
            success=False, company_name=request.company_name, industry=request.industry,
            stage=request.stage, executive_summary="", problem_statement="", solution="",
            market_analysis="", business_model="", competitive_advantage="", target_customers=[],
            marketing_strategy="", team_overview="", financial_projections="", funding_requirements="", use_of_funds=""
        )


# Grant Proposal Generator Models
class GrantProposalRequest(BaseModel):
    """资助提案请求"""
    project_title: str = Field(..., description="项目标题")
    funding_organization: str = Field(..., description="资助机构")
    grant_amount: str = Field(default="¥100,000", description="资助金额")


class GrantProposalResponse(BaseModel):
    """资助提案响应"""
    success: bool
    project_title: str
    funding_organization: str
    grant_amount: str
    project_summary: str
    problem_and_need: str
    project_goals: List[str]
    methodology: str
    timeline: str
    budget_justification: str
    budget_breakdown: List[Dict[str, Any]]
    expected_outcomes: List[str]
    evaluation_plan: str
    sustainability: str
    team_qualifications: str


@router.post("/grant/proposal", response_model=GrantProposalResponse)
async def generate_grant_proposal(request: GrantProposalRequest):
    """生成资助提案"""
    try:
        from backend.services.grant_proposal_generator import grant_proposal_generator_service
        result = await grant_proposal_generator_service.generate_grant_proposal(
            request.project_title, request.funding_organization, request.grant_amount
        )
        return GrantProposalResponse(
            success=True,
            project_title=result["project_title"],
            funding_organization=result["funding_organization"],
            grant_amount=result["grant_amount"],
            project_summary=result.get("project_summary", ""),
            problem_and_need=result.get("problem_and_need", ""),
            project_goals=result.get("project_goals", []),
            methodology=result.get("methodology", ""),
            timeline=result.get("timeline", ""),
            budget_justification=result.get("budget_justification", ""),
            budget_breakdown=result.get("budget_breakdown", []),
            expected_outcomes=result.get("expected_outcomes", []),
            evaluation_plan=result.get("evaluation_plan", ""),
            sustainability=result.get("sustainability", ""),
            team_qualifications=result.get("team_qualifications", ""),
        )
    except Exception as e:
        logger.error(f"生成资助提案失败: {e}")
        return GrantProposalResponse(
            success=False, project_title=request.project_title, funding_organization=request.funding_organization,
            grant_amount=request.grant_amount, project_summary="", problem_and_need="", project_goals=[],
            methodology="", timeline="", budget_justification="", budget_breakdown=[], expected_outcomes=[],
            evaluation_plan="", sustainability="", team_qualifications=""
        )


# Impact Report Generator Models
class ImpactReportRequest(BaseModel):
    """影响报告请求"""
    organization_name: str = Field(..., description="组织名称")
    project_name: str = Field(..., description="项目名称")
    report_period: str = Field(default="2025", description="报告周期")


class ImpactReportResponse(BaseModel):
    """影响报告响应"""
    success: bool
    organization_name: str
    project_name: str
    report_period: str
    executive_summary: str
    key_achievements: List[str]
    impact_metrics: List[Dict[str, str]]
    beneficiary_stories: List[str]
    challenges_faced: List[str]
    lessons_learned: List[str]
    partnerships: List[str]
    financial_summary: str
    future_plans: str
    testimonials: List[str]


@router.post("/impact/report", response_model=ImpactReportResponse)
async def generate_impact_report(request: ImpactReportRequest):
    """生成影响报告"""
    try:
        from backend.services.impact_report_generator import impact_report_generator_service
        result = await impact_report_generator_service.generate_impact_report(
            request.organization_name, request.project_name, request.report_period
        )
        return ImpactReportResponse(
            success=True,
            organization_name=result["organization_name"],
            project_name=result["project_name"],
            report_period=result["report_period"],
            executive_summary=result.get("executive_summary", ""),
            key_achievements=result.get("key_achievements", []),
            impact_metrics=result.get("impact_metrics", []),
            beneficiary_stories=result.get("beneficiary_stories", []),
            challenges_faced=result.get("challenges_faced", []),
            lessons_learned=result.get("lessons_learned", []),
            partnerships=result.get("partnerships", []),
            financial_summary=result.get("financial_summary", ""),
            future_plans=result.get("future_plans", ""),
            testimonials=result.get("testimonials", []),
        )
    except Exception as e:
        logger.error(f"生成影响报告失败: {e}")
        return ImpactReportResponse(
            success=False, organization_name=request.organization_name, project_name=request.project_name,
            report_period=request.report_period, executive_summary="", key_achievements=[], impact_metrics=[],
            beneficiary_stories=[], challenges_faced=[], lessons_learned=[], partnerships=[],
            financial_summary="", future_plans="", testimonials=[]
        )


# Partnership Proposal Generator Models
class PartnershipProposalRequest(BaseModel):
    """合作关系提案请求"""
    your_brand: str = Field(..., description="你的品牌")
    potential_partner: str = Field(..., description="潜在合作伙伴")
    partnership_type: str = Field(default="cross-promotion", description="合作类型")


class PartnershipProposalResponse(BaseModel):
    """合作关系提案响应"""
    success: bool
    your_brand: str
    potential_partner: str
    partnership_type: str
    proposal_title: str
    partnership_summary: str
    mutual_benefits: List[str]
    collaboration_areas: List[str]
    proposed_activities: List[str]
    timeline: str
    resource_commitment: str
    expected_outcomes: List[str]
    success_metrics: List[str]
    terms_and_conditions: List[str]
    next_steps: List[str]


@router.post("/partnership/proposal", response_model=PartnershipProposalResponse)
async def generate_partnership_proposal(request: PartnershipProposalRequest):
    """生成合作关系提案"""
    try:
        from backend.services.partnership_proposal_generator import partnership_proposal_generator_service
        result = await partnership_proposal_generator_service.generate_partnership_proposal(
            request.your_brand, request.potential_partner, request.partnership_type
        )
        return PartnershipProposalResponse(
            success=True,
            your_brand=result["your_brand"],
            potential_partner=result["potential_partner"],
            partnership_type=result["partnership_type"],
            proposal_title=result.get("proposal_title", ""),
            partnership_summary=result.get("partnership_summary", ""),
            mutual_benefits=result.get("mutual_benefits", []),
            collaboration_areas=result.get("collaboration_areas", []),
            proposed_activities=result.get("proposed_activities", []),
            timeline=result.get("timeline", ""),
            resource_commitment=result.get("resource_commitment", ""),
            expected_outcomes=result.get("expected_outcomes", []),
            success_metrics=result.get("success_metrics", []),
            terms_and_conditions=result.get("terms_and_conditions", []),
            next_steps=result.get("next_steps", []),
        )
    except Exception as e:
        logger.error(f"生成合作关系提案失败: {e}")
        return PartnershipProposalResponse(
            success=False, your_brand=request.your_brand, potential_partner=request.potential_partner,
            partnership_type=request.partnership_type, proposal_title="", partnership_summary="",
            mutual_benefits=[], collaboration_areas=[], proposed_activities=[], timeline="",
            resource_commitment="", expected_outcomes=[], success_metrics=[], terms_and_conditions=[], next_steps=[]
        )


# Press Kit Generator Models
class PressKitRequest(BaseModel):
    """媒体资料包请求"""
    company_name: str = Field(..., description="公司名称")
    industry: str = Field(..., description="行业")
    launch_date: str = Field(default="TBD", description="发布日期")


class PressKitResponse(BaseModel):
    """媒体资料包响应"""
    success: bool
    company_name: str
    industry: str
    launch_date: str
    press_release: str
    company_backgrounder: str
    key_messages: List[str]
    leadership_bios: List[str]
    product_service_descriptions: List[str]
    media_assets: List[str]
    awards_and_recognition: List[str]
    contact_information: Dict[str, str]
    social_media_handles: List[str]


@router.post("/press/kit", response_model=PressKitResponse)
async def generate_press_kit(request: PressKitRequest):
    """生成媒体资料包"""
    try:
        from backend.services.press_kit_generator import press_kit_generator_service
        result = await press_kit_generator_service.generate_press_kit(
            request.company_name, request.industry, request.launch_date
        )
        return PressKitResponse(
            success=True,
            company_name=result["company_name"],
            industry=result["industry"],
            launch_date=result["launch_date"],
            press_release=result.get("press_release", ""),
            company_backgrounder=result.get("company_backgrounder", ""),
            key_messages=result.get("key_messages", []),
            leadership_bios=result.get("leadership_bios", []),
            product_service_descriptions=result.get("product_service_descriptions", []),
            media_assets=result.get("mediaAssets", []),
            awards_and_recognition=result.get("awards_and_recognition", []),
            contact_information=result.get("contact_information", {}),
            social_media_handles=result.get("social_media_handles", []),
        )
    except Exception as e:
        logger.error(f"生成媒体资料包失败: {e}")
        return PressKitResponse(
            success=False, company_name=request.company_name, industry=request.industry,
            launch_date=request.launch_date, press_release="", company_backgrounder="", key_messages=[],
            leadership_bios=[], product_service_descriptions=[], media_assets=[], awards_and_recognition=[],
            contact_information={}, social_media_handles=[]
        )


# Investor Deck Generator Models
class InvestorDeckRequest(BaseModel):
    """投资人演示文稿请求"""
    company_name: str = Field(..., description="公司名称")
    industry: str = Field(..., description="行业")
    funding_round: str = Field(default="Series A", description="融资轮次")
    amount_raising: str = Field(default="¥10M", description="融资金额")


class InvestorDeckResponse(BaseModel):
    """投资人演示文稿响应"""
    success: bool
    company_name: str
    industry: str
    funding_round: str
    amount_raising: str
    pitch_title: str
    problem: str
    solution: str
    market_opportunity: str
    product_description: str
    business_model: str
    traction: str
    competition_analysis: str
    team: str
    financials: str
    use_of_funds: str
    contact_information: str


@router.post("/investor/deck", response_model=InvestorDeckResponse)
async def generate_investor_deck(request: InvestorDeckRequest):
    """生成投资人演示文稿"""
    try:
        from backend.services.investor_deck_generator import investor_deck_generator_service
        result = await investor_deck_generator_service.generate_investor_deck(
            request.company_name, request.industry, request.funding_round, request.amount_raising
        )
        return InvestorDeckResponse(
            success=True,
            company_name=result["company_name"],
            industry=result["industry"],
            funding_round=result["funding_round"],
            amount_raising=result["amount_raising"],
            pitch_title=result.get("pitch_title", ""),
            problem=result.get("problem", ""),
            solution=result.get("solution", ""),
            market_opportunity=result.get("market_opportunity", ""),
            product_description=result.get("product_description", ""),
            business_model=result.get("business_model", ""),
            traction=result.get("traction", ""),
            competition_analysis=result.get("competition_analysis", ""),
            team=result.get("team", ""),
            financials=result.get("financials", ""),
            use_of_funds=result.get("use_of_funds", ""),
            contact_information=result.get("contact_information", ""),
        )
    except Exception as e:
        logger.error(f"生成投资人演示文稿失败: {e}")
        return InvestorDeckResponse(
            success=False, company_name=request.company_name, industry=request.industry,
            funding_round=request.funding_round, amount_raising=request.amount_raising,
            pitch_title="", problem="", solution="", market_opportunity="", product_description="",
            business_model="", traction="", competition_analysis="", team="", financials="",
            use_of_funds="", contact_information=""
        )


# One Pager Generator Models
class OnePagerRequest(BaseModel):
    """单页介绍请求"""
    product_name: str = Field(..., description="产品名称")
    product_type: str = Field(default="SaaS", description="产品类型")
    target_customer: str = Field(default="中小企业", description="目标客户")


class OnePagerResponse(BaseModel):
    """单页介绍响应"""
    success: bool
    product_name: str
    product_type: str
    target_customer: str
    tagline: str
    problem: str
    solution: str
    key_features: List[str]
    benefits: List[str]
    use_cases: List[str]
    testimonial: str
    pricing_overview: str
    call_to_action: str


@router.post("/onepager/generate", response_model=OnePagerResponse)
async def generate_one_pager(request: OnePagerRequest):
    """生成单页介绍"""
    try:
        from backend.services.one_pager_generator import one_pager_generator_service
        result = await one_pager_generator_service.generate_one_pager(
            request.product_name, request.product_type, request.target_customer
        )
        return OnePagerResponse(
            success=True,
            product_name=result["product_name"],
            product_type=result["product_type"],
            target_customer=result["target_customer"],
            tagline=result.get("tagline", ""),
            problem=result.get("problem", ""),
            solution=result.get("solution", ""),
            key_features=result.get("key_features", []),
            benefits=result.get("benefits", []),
            use_cases=result.get("use_cases", []),
            testimonial=result.get("testimonial", ""),
            pricing_overview=result.get("pricing_overview", ""),
            call_to_action=result.get("call_to_action", ""),
        )
    except Exception as e:
        logger.error(f"生成单页介绍失败: {e}")
        return OnePagerResponse(
            success=False, product_name=request.product_name, product_type=request.product_type,
            target_customer=request.target_customer, tagline="", problem="", solution="",
            key_features=[], benefits=[], use_cases=[], testimonial="", pricing_overview="", call_to_action=""
        )


# Brand Guidelines Generator Models
class BrandGuidelinesRequest(BaseModel):
    """品牌指南请求"""
    brand_name: str = Field(..., description="品牌名称")
    industry: str = Field(..., description="行业")
    brand_personality: str = Field(default="专业、创新", description="品牌个性")


class BrandGuidelinesResponse(BaseModel):
    """品牌指南响应"""
    success: bool
    brand_name: str
    industry: str
    brand_personality: str
    brand_mission: str
    brand_vision: str
    core_values: List[str]
    brand_voice: Dict[str, Any]
    logo_usage: str
    color_palette: List[str]
    typography: str
    imagery_style: str
    do_and_donts: Dict[str, List[str]]


@router.post("/brand/guidelines", response_model=BrandGuidelinesResponse)
async def generate_brand_guidelines(request: BrandGuidelinesRequest):
    """生成品牌指南"""
    try:
        from backend.services.brand_guidelines_generator import brand_guidelines_generator_service
        result = await brand_guidelines_generator_service.generate_brand_guidelines(
            request.brand_name, request.industry, request.brand_personality
        )
        return BrandGuidelinesResponse(
            success=True,
            brand_name=result["brand_name"],
            industry=result["industry"],
            brand_personality=result["brand_personality"],
            brand_mission=result.get("brand_mission", ""),
            brand_vision=result.get("brand_vision", ""),
            core_values=result.get("core_values", []),
            brand_voice=result.get("brand_voice", {}),
            logo_usage=result.get("logo_usage", ""),
            color_palette=result.get("color_palette", []),
            typography=result.get("typography", ""),
            imagery_style=result.get("imagery_style", ""),
            do_and_donts=result.get("do_and_donts", {"do": [], "donts": []}),
        )
    except Exception as e:
        logger.error(f"生成品牌指南失败: {e}")
        return BrandGuidelinesResponse(
            success=False, brand_name=request.brand_name, industry=request.industry,
            brand_personality=request.brand_personality, brand_mission="", brand_vision="",
            core_values=[], brand_voice={}, logo_usage="", color_palette=[], typography="",
            imagery_style="", do_and_donts={"do": [], "donts": []}
        )


# Crisis Communication Generator Models
class CrisisCommunicationRequest(BaseModel):
    """危机公关请求"""
    company_name: str = Field(..., description="公司名称")
    crisis_type: str = Field(..., description="危机类型")
    severity: str = Field(default="medium", description="严重程度")


class CrisisCommunicationResponse(BaseModel):
    """危机公关响应"""
    success: bool
    company_name: str
    crisis_type: str
    severity: str
    initial_statement: str
    key_messages: List[str]
    response_timeline: str
    media_response: str
    social_media_response: str
    internal_communication: str
    corrective_actions: List[str]
    monitoring_plan: str
    recovery_strategy: str


@router.post("/crisis/communication", response_model=CrisisCommunicationResponse)
async def generate_crisis_communication(request: CrisisCommunicationRequest):
    """生成危机公关"""
    try:
        from backend.services.crisis_communication_generator import crisis_communication_generator_service
        result = await crisis_communication_generator_service.generate_crisis_communication(
            request.company_name, request.crisis_type, request.severity
        )
        return CrisisCommunicationResponse(
            success=True,
            company_name=result["company_name"],
            crisis_type=result["crisis_type"],
            severity=result["severity"],
            initial_statement=result.get("initial_statement", ""),
            key_messages=result.get("key_messages", []),
            response_timeline=result.get("response_timeline", ""),
            media_response=result.get("media_response", ""),
            social_media_response=result.get("social_media_response", ""),
            internal_communication=result.get("internal_communication", ""),
            corrective_actions=result.get("corrective_actions", []),
            monitoring_plan=result.get("monitoring_plan", ""),
            recovery_strategy=result.get("recovery_strategy", ""),
        )
    except Exception as e:
        logger.error(f"生成危机公关失败: {e}")
        return CrisisCommunicationResponse(
            success=False, company_name=request.company_name, crisis_type=request.crisis_type,
            severity=request.severity, initial_statement="", key_messages=[], response_timeline="",
            media_response="", social_media_response="", internal_communication="", corrective_actions=[],
            monitoring_plan="", recovery_strategy=""
        )


# Thought Leadership Generator Models
class ThoughtLeadershipRequest(BaseModel):
    """思想领袖内容请求"""
    author_name: str = Field(..., description="作者姓名")
    industry: str = Field(..., description="行业")
    topic: str = Field(..., description="主题")
    article_type: str = Field(default="opinion", description="文章类型")


class ThoughtLeadershipResponse(BaseModel):
    """思想领袖内容响应"""
    success: bool
    author_name: str
    industry: str
    topic: str
    article_type: str
    title: str
    hook: str
    main_thesis: str
    key_points: List[str]
    supporting_evidence: List[str]
    counter_arguments: List[str]
    call_to_action: str
    author_bio: str
    suggested_hashtags: List[str]


@router.post("/thought/leadership", response_model=ThoughtLeadershipResponse)
async def generate_thought_leadership(request: ThoughtLeadershipRequest):
    """生成思想领袖内容"""
    try:
        from backend.services.thought_leadership_generator import thought_leadership_generator_service
        result = await thought_leadership_generator_service.generate_thought_leadership(
            request.author_name, request.industry, request.topic, request.article_type
        )
        return ThoughtLeadershipResponse(
            success=True,
            author_name=result["author_name"],
            industry=result["industry"],
            topic=result["topic"],
            article_type=result["article_type"],
            title=result.get("title", ""),
            hook=result.get("hook", ""),
            main_thesis=result.get("main_thesis", ""),
            key_points=result.get("key_points", []),
            supporting_evidence=result.get("supporting_evidence", []),
            counter_arguments=result.get("counter_arguments", []),
            call_to_action=result.get("call_to_action", ""),
            author_bio=result.get("author_bio", ""),
            suggested_hashtags=result.get("suggested_hashtags", []),
        )
    except Exception as e:
        logger.error(f"生成思想领袖内容失败: {e}")
        return ThoughtLeadershipResponse(
            success=False, author_name=request.author_name, industry=request.industry,
            topic=request.topic, article_type=request.article_type, title="", hook="",
            main_thesis="", key_points=[], supporting_evidence=[], counter_arguments=[],
            call_to_action="", author_bio="", suggested_hashtags=[]
        )


# Research Summary Generator Models
class ResearchSummaryRequest(BaseModel):
    """研究报告摘要请求"""
    research_title: str = Field(..., description="研究标题")
    research_field: str = Field(..., description="研究领域")
    methodology: str = Field(default="quantitative", description="研究方法")


class ResearchSummaryResponse(BaseModel):
    """研究报告摘要响应"""
    success: bool
    research_title: str
    research_field: str
    methodology: str
    executive_summary: str
    research_objectives: List[str]
    key_findings: List[str]
    data_sources: List[str]
    sample_size: str
    limitations: List[str]
    implications: List[str]
    recommendations: List[str]
    future_research: str


@router.post("/research/summary", response_model=ResearchSummaryResponse)
async def generate_research_summary(request: ResearchSummaryRequest):
    """生成研究报告摘要"""
    try:
        from backend.services.research_summary_generator import research_summary_generator_service
        result = await research_summary_generator_service.generate_research_summary(
            request.research_title, request.research_field, request.methodology
        )
        return ResearchSummaryResponse(
            success=True,
            research_title=result["research_title"],
            research_field=result["research_field"],
            methodology=result["methodology"],
            executive_summary=result.get("executive_summary", ""),
            research_objectives=result.get("research_objectives", []),
            key_findings=result.get("key_findings", []),
            data_sources=result.get("data_sources", []),
            sample_size=result.get("sample_size", ""),
            limitations=result.get("limitations", []),
            implications=result.get("implications", []),
            recommendations=result.get("recommendations", []),
            future_research=result.get("future_research", ""),
        )
    except Exception as e:
        logger.error(f"生成研究报告摘要失败: {e}")
        return ResearchSummaryResponse(
            success=False, research_title=request.research_title, research_field=request.research_field,
            methodology=request.methodology, executive_summary="", research_objectives=[], key_findings=[],
            data_sources=[], sample_size="", limitations=[], implications=[], recommendations=[], future_research=""
        )


# User Story Generator Models
class UserStoryRequest(BaseModel):
    """用户故事请求"""
    persona: str = Field(..., description="用户画像")
    goal: str = Field(..., description="用户目标")
    product_name: str = Field(default="产品", description="产品名称")


class UserStoryResponse(BaseModel):
    """用户故事响应"""
    success: bool
    persona: str
    goal: str
    product_name: str
    story_title: str
    story: str
    acceptance_criteria: List[str]
    user_flow: List[str]
    pain_points: List[str]
    success_metrics: str
    priority: str
    notes: str


@router.post("/user/story", response_model=UserStoryResponse)
async def generate_user_story(request: UserStoryRequest):
    """生成用户故事"""
    try:
        from backend.services.user_story_generator import user_story_generator_service
        result = await user_story_generator_service.generate_user_story(
            request.persona, request.goal, request.product_name
        )
        return UserStoryResponse(
            success=True,
            persona=result["persona"],
            goal=result["goal"],
            product_name=result["product_name"],
            story_title=result.get("story_title", ""),
            story=result.get("story", ""),
            acceptance_criteria=result.get("acceptance_criteria", []),
            user_flow=result.get("user_flow", []),
            pain_points=result.get("pain_points", []),
            success_metrics=result.get("success_metrics", ""),
            priority=result.get("priority", ""),
            notes=result.get("notes", ""),
        )
    except Exception as e:
        logger.error(f"生成用户故事失败: {e}")
        return UserStoryResponse(
            success=False, persona=request.persona, goal=request.goal, product_name=request.product_name,
            story_title="", story="", acceptance_criteria=[], user_flow=[], pain_points=[],
            success_metrics="", priority="", notes=""
        )


# Milestone Celebration Generator Models
class MilestoneCelebrationRequest(BaseModel):
    """里程碑庆祝请求"""
    milestone: str = Field(..., description="里程碑")
    team_name: str = Field(default="团队", description="团队名称")
    achievement_type: str = Field(default="performance", description="成就类型")


class MilestoneCelebrationResponse(BaseModel):
    """里程碑庆祝响应"""
    success: bool
    milestone: str
    team_name: str
    achievement_type: str
    celebration_title: str
    achievement_highlights: List[str]
    team_shoutouts: List[str]
    key_contributors: List[str]
    memorable_moments: List[str]
    social_media_post: str
    internal_communication: str
    next_goals: List[str]
    celebration_ideas: List[str]


@router.post("/milestone/celebration", response_model=MilestoneCelebrationResponse)
async def generate_milestone_celebration(request: MilestoneCelebrationRequest):
    """生成里程碑庆祝"""
    try:
        from backend.services.milestone_celebration_generator import milestone_celebration_generator_service
        result = await milestone_celebration_generator_service.generate_milestone_celebration(
            request.milestone, request.team_name, request.achievement_type
        )
        return MilestoneCelebrationResponse(
            success=True,
            milestone=result["milestone"],
            team_name=result["team_name"],
            achievement_type=result["achievement_type"],
            celebration_title=result.get("celebration_title", ""),
            achievement_highlights=result.get("achievement_highlights", []),
            team_shoutouts=result.get("team_shoutouts", []),
            key_contributors=result.get("key_contributors", []),
            memorable_moments=result.get("memorable_moments", []),
            social_media_post=result.get("social_media_post", ""),
            internal_communication=result.get("internal_communication", ""),
            next_goals=result.get("next_goals", []),
            celebration_ideas=result.get("celebration_ideas", []),
        )
    except Exception as e:
        logger.error(f"生成里程碑庆祝失败: {e}")
        return MilestoneCelebrationResponse(
            success=False, milestone=request.milestone, team_name=request.team_name,
            achievement_type=request.achievement_type, celebration_title="", achievement_highlights=[],
            team_shoutouts=[], key_contributors=[], memorable_moments=[], social_media_post="",
            internal_communication="", next_goals=[], celebration_ideas=[]
        )


# Checklist Generator Models
class ChecklistRequest(BaseModel):
    """清单生成请求"""
    checklist_type: str = Field(..., description="清单类型")
    context: str = Field(..., description="使用场景")
    num_items: int = Field(default=10, description="项目数量")


class ChecklistResponse(BaseModel):
    """清单响应"""
    success: bool
    checklist_type: str
    context: str
    num_items: int
    title: str
    items: List[Dict[str, Any]]
    tips: List[str]
    common_mistakes: List[str]


@router.post("/checklist/generate", response_model=ChecklistResponse)
async def generate_checklist(request: ChecklistRequest):
    """生成清单"""
    try:
        from backend.services.checklist_generator import checklist_generator_service
        result = await checklist_generator_service.generate_checklist(
            request.checklist_type, request.context, request.num_items
        )
        return ChecklistResponse(
            success=True,
            checklist_type=result["checklist_type"],
            context=result["context"],
            num_items=result["num_items"],
            title=result.get("title", ""),
            items=result.get("items", []),
            tips=result.get("tips", []),
            common_mistakes=result.get("common_mistakes", []),
        )
    except Exception as e:
        logger.error(f"生成清单失败: {e}")
        return ChecklistResponse(
            success=False, checklist_type=request.checklist_type, context=request.context,
            num_items=request.num_items, title="", items=[], tips=[], common_mistakes=[]
        )


# FAQ Document Generator Models
class FAQDocumentRequest(BaseModel):
    """FAQ文档请求"""
    topic: str = Field(..., description="主题")
    product_name: str = Field(..., description="产品名称")
    num_questions: int = Field(default=10, description="问题数量")


class FAQDocumentResponse(BaseModel):
    """FAQ文档响应"""
    success: bool
    topic: str
    product_name: str
    num_questions: int
    title: str
    categories: List[Dict[str, Any]]
    contact_support: str
    additional_resources: List[str]


@router.post("/faq/document", response_model=FAQDocumentResponse)
async def generate_faq_document(request: FAQDocumentRequest):
    """生成FAQ文档"""
    try:
        from backend.services.faq_document_generator import faq_document_generator_service
        result = await faq_document_generator_service.generate_faq_document(
            request.topic, request.product_name, request.num_questions
        )
        return FAQDocumentResponse(
            success=True,
            topic=result["topic"],
            product_name=result["product_name"],
            num_questions=result["num_questions"],
            title=result.get("title", ""),
            categories=result.get("categories", []),
            contact_support=result.get("contact_support", ""),
            additional_resources=result.get("additional_resources", []),
        )
    except Exception as e:
        logger.error(f"生成FAQ文档失败: {e}")
        return FAQDocumentResponse(
            success=False, topic=request.topic, product_name=request.product_name,
            num_questions=request.num_questions, title="", categories=[], contact_support="", additional_resources=[]
        )


# Quick Guide Generator Models
class QuickGuideRequest(BaseModel):
    """快速入门指南请求"""
    product_name: str = Field(..., description="产品名称")
    audience: str = Field(default="beginner", description="目标受众")
    guide_length: str = Field(default="short", description="指南长度")


class QuickGuideResponse(BaseModel):
    """快速入门指南响应"""
    success: bool
    product_name: str
    audience: str
    guide_length: str
    title: str
    overview: str
    prerequisites: List[str]
    steps: List[Dict[str, Any]]
    common_first_steps: List[str]
    pitfalls_to_avoid: List[str]
    next_steps: List[str]
    help_resources: List[str]


@router.post("/guide/quick", response_model=QuickGuideResponse)
async def generate_quick_guide(request: QuickGuideRequest):
    """生成快速入门指南"""
    try:
        from backend.services.quick_guide_generator import quick_guide_generator_service
        result = await quick_guide_generator_service.generate_quick_guide(
            request.product_name, request.audience, request.guide_length
        )
        return QuickGuideResponse(
            success=True,
            product_name=result["product_name"],
            audience=result["audience"],
            guide_length=result["guide_length"],
            title=result.get("title", ""),
            overview=result.get("overview", ""),
            prerequisites=result.get("prerequisites", []),
            steps=result.get("steps", []),
            common_first_steps=result.get("common_first_steps", []),
            pitfalls_to_avoid=result.get("pitfalls_to_avoid", []),
            next_steps=result.get("next_steps", []),
            help_resources=result.get("help_resources", []),
        )
    except Exception as e:
        logger.error(f"生成快速入门指南失败: {e}")
        return QuickGuideResponse(
            success=False, product_name=request.product_name, audience=request.audience,
            guide_length=request.guide_length, title="", overview="", prerequisites=[], steps=[],
            common_first_steps=[], pitfalls_to_avoid=[], next_steps=[], help_resources=[]
        )


# Comparison Article Generator Models
class ComparisonArticleRequest(BaseModel):
    """对比文章请求"""
    item_a: str = Field(..., description="对比项A")
    item_b: str = Field(..., description="对比项B")
    comparison_criteria: List[str] = Field(default=None, description="对比标准")


class ComparisonArticleResponse(BaseModel):
    """对比文章响应"""
    success: bool
    item_a: str
    item_b: str
    comparison_criteria: List[str]
    title: str
    introduction: str
    summary_table: List[Dict[str, str]]
    pros_cons: Dict[str, Dict[str, List[str]]]
    detailed_analysis: str
    recommendation: str
    conclusion: str


@router.post("/comparison/article", response_model=ComparisonArticleResponse)
async def generate_comparison_article(request: ComparisonArticleRequest):
    """生成对比文章"""
    try:
        from backend.services.comparison_article_generator import comparison_article_generator_service
        result = await comparison_article_generator_service.generate_comparison_article(
            request.item_a, request.item_b, request.comparison_criteria
        )
        return ComparisonArticleResponse(
            success=True,
            item_a=result["item_a"],
            item_b=result["item_b"],
            comparison_criteria=result["comparison_criteria"],
            title=result.get("title", ""),
            introduction=result.get("introduction", ""),
            summary_table=result.get("summary_table", []),
            pros_cons=result.get("pros_cons", {}),
            detailed_analysis=result.get("detailed_analysis", ""),
            recommendation=result.get("recommendation", ""),
            conclusion=result.get("conclusion", ""),
        )
    except Exception as e:
        logger.error(f"生成对比文章失败: {e}")
        return ComparisonArticleResponse(
            success=False, item_a=request.item_a, item_b=request.item_b,
            comparison_criteria=request.comparison_criteria or [], title="", introduction="",
            summary_table=[], pros_cons={}, detailed_analysis="", recommendation="", conclusion=""
        )


# Trending Topic Generator Models
class TrendingTopicRequest(BaseModel):
    """趋势话题请求"""
    industry: str = Field(..., description="行业")
    platform: str = Field(default="微博", description="平台")
    num_topics: int = Field(default=10, description="话题数量")


class TrendingTopicResponse(BaseModel):
    """趋势话题响应"""
    success: bool
    industry: str
    platform: str
    num_topics: int
    generated_at: str
    trending_topics: List[Dict[str, Any]]
    industry_insights: List[str]
    content_recommendations: List[str]


@router.post("/trending/topics", response_model=TrendingTopicResponse)
async def generate_trending_topics(request: TrendingTopicRequest):
    """生成趋势话题"""
    try:
        from backend.services.trending_topic_generator import trending_topic_generator_service
        result = await trending_topic_generator_service.generate_trending_topics(
            request.industry, request.platform, request.num_topics
        )
        return TrendingTopicResponse(
            success=True,
            industry=result["industry"],
            platform=result["platform"],
            num_topics=result["num_topics"],
            generated_at=result.get("generated_at", ""),
            trending_topics=result.get("trending_topics", []),
            industry_insights=result.get("industry_insights", []),
            content_recommendations=result.get("content_recommendations", []),
        )
    except Exception as e:
        logger.error(f"生成趋势话题失败: {e}")
        return TrendingTopicResponse(
            success=False, industry=request.industry, platform=request.platform,
            num_topics=request.num_topics, generated_at="", trending_topics=[], industry_insights=[], content_recommendations=[]
        )


# Social Media Calendar Generator Models
class SocialMediaCalendarRequest(BaseModel):
    """社交媒体日历请求"""
    platform: str = Field(..., description="平台")
    month: str = Field(default="2026-04", description="月份")
    num_posts: int = Field(default=20, description="帖子数量")


class SocialMediaCalendarResponse(BaseModel):
    """社交媒体日历响应"""
    success: bool
    platform: str
    month: str
    num_posts: int
    content_themes: List[str]
    posting_schedule: List[Dict[str, Any]]
    campaign_ideas: List[str]
    seasonal_content: List[str]
    best_performing_times: str


@router.post("/social/calendar", response_model=SocialMediaCalendarResponse)
async def generate_social_media_calendar(request: SocialMediaCalendarRequest):
    """生成社交媒体日历"""
    try:
        from backend.services.social_media_calendar_generator import social_media_calendar_generator_service
        result = await social_media_calendar_generator_service.generate_social_media_calendar(
            request.platform, request.month, request.num_posts
        )
        return SocialMediaCalendarResponse(
            success=True,
            platform=result["platform"],
            month=result["month"],
            num_posts=result["num_posts"],
            content_themes=result.get("content_themes", []),
            posting_schedule=result.get("posting_schedule", []),
            campaign_ideas=result.get("campaign_ideas", []),
            seasonal_content=result.get("seasonal_content", []),
            best_performing_times=result.get("best_performing_times", ""),
        )
    except Exception as e:
        logger.error(f"生成社交媒体日历失败: {e}")
        return SocialMediaCalendarResponse(
            success=False, platform=request.platform, month=request.month, num_posts=request.num_posts,
            content_themes=[], posting_schedule=[], campaign_ideas=[], seasonal_content=[], best_performing_times=""
        )


# Email Sequence Generator Models
class EmailSequenceRequest(BaseModel):
    """邮件序列请求"""
    sequence_type: str = Field(..., description="序列类型")
    product_name: str = Field(..., description="产品名称")
    num_emails: int = Field(default=5, description="邮件数量")
    target_audience: str = Field(default="new leads", description="目标受众")


class EmailSequenceResponse(BaseModel):
    """邮件序列响应"""
    success: bool
    sequence_type: str
    product_name: str
    num_emails: int
    target_audience: str
    sequence_overview: str
    emails: List[Dict[str, Any]]
    conversion_goals: List[str]
    performance_metrics: str


@router.post("/email/sequence", response_model=EmailSequenceResponse)
async def generate_email_sequence(request: EmailSequenceRequest):
    """生成邮件序列"""
    try:
        from backend.services.email_sequence_generator import email_sequence_generator_service
        result = await email_sequence_generator_service.generate_email_sequence(
            request.sequence_type, request.product_name, request.num_emails, request.target_audience
        )
        return EmailSequenceResponse(
            success=True,
            sequence_type=result["sequence_type"],
            product_name=result["product_name"],
            num_emails=result["num_emails"],
            target_audience=result["target_audience"],
            sequence_overview=result.get("sequence_overview", ""),
            emails=result.get("emails", []),
            conversion_goals=result.get("conversion_goals", []),
            performance_metrics=result.get("performance_metrics", ""),
        )
    except Exception as e:
        logger.error(f"生成邮件序列失败: {e}")
        return EmailSequenceResponse(
            success=False, sequence_type=request.sequence_type, product_name=request.product_name,
            num_emails=request.num_emails, target_audience=request.target_audience,
            sequence_overview="", emails=[], conversion_goals=[], performance_metrics=""
        )


# Webinar Description Generator Models
class WebinarDescriptionRequest(BaseModel):
    """网络研讨会描述请求"""
    webinar_title: str = Field(..., description="研讨会标题")
    topic: str = Field(..., description="主题")
    duration_minutes: int = Field(default=60, description="时长")
    speaker_info: str = Field(default="", description="演讲者信息")


class WebinarDescriptionResponse(BaseModel):
    """网络研讨会描述响应"""
    success: bool
    webinar_title: str
    topic: str
    duration_minutes: int
    speaker_info: str
    event_description: str
    key_learning_points: List[str]
    agenda: List[Dict[str, str]]
    speaker_profiles: List[str]
    target_audience: str
    benefits: List[str]
    registration_cta: str
    faq: List[str]


@router.post("/webinar/description", response_model=WebinarDescriptionResponse)
async def generate_webinar_description(request: WebinarDescriptionRequest):
    """生成网络研讨会描述"""
    try:
        from backend.services.webinar_description_generator import webinar_description_generator_service
        result = await webinar_description_generator_service.generate_webinar_description(
            request.webinar_title, request.topic, request.duration_minutes, request.speaker_info
        )
        return WebinarDescriptionResponse(
            success=True,
            webinar_title=result["webinar_title"],
            topic=result["topic"],
            duration_minutes=result["duration_minutes"],
            speaker_info=result.get("speaker_info", ""),
            event_description=result.get("event_description", ""),
            key_learning_points=result.get("key_learning_points", []),
            agenda=result.get("agenda", []),
            speaker_profiles=result.get("speaker_profiles", []),
            target_audience=result.get("target_audience", ""),
            benefits=result.get("benefits", []),
            registration_cta=result.get("registration_cta", ""),
            faq=result.get("faq", []),
        )
    except Exception as e:
        logger.error(f"生成网络研讨会描述失败: {e}")
        return WebinarDescriptionResponse(
            success=False, webinar_title=request.webinar_title, topic=request.topic,
            duration_minutes=request.duration_minutes, speaker_info=request.speaker_info,
            event_description="", key_learning_points=[], agenda=[], speaker_profiles=[],
            target_audience="", benefits=[], registration_cta="", faq=[]
        )


# Newsletter Content Generator Models
class NewsletterContentRequest(BaseModel):
    """新闻通讯内容请求"""
    newsletter_name: str = Field(..., description="新闻通讯名称")
    issue_number: int = Field(..., description="期号")
    theme: str = Field(default="monthly update", description="主题")


class NewsletterContentResponse(BaseModel):
    """新闻通讯内容响应"""
    success: bool
    newsletter_name: str
    issue_number: int
    theme: str
    subject_line: str
    header_title: str
    opening_message: str
    featured_articles: List[Dict[str, Any]]
    quick_tips: List[str]
    upcoming_events: List[str]
    reader_poll: str
    closing_message: str
    footer: str
    social_share_text: str


@router.post("/newsletter/content", response_model=NewsletterContentResponse)
async def generate_newsletter_content(request: NewsletterContentRequest):
    """生成新闻通讯内容"""
    try:
        from backend.services.newsletter_content_generator import newsletter_content_generator_service
        result = await newsletter_content_generator_service.generate_newsletter_content(
            request.newsletter_name, request.issue_number, request.theme
        )
        return NewsletterContentResponse(
            success=True,
            newsletter_name=result["newsletter_name"],
            issue_number=result["issue_number"],
            theme=result["theme"],
            subject_line=result.get("subject_line", ""),
            header_title=result.get("header_title", ""),
            opening_message=result.get("opening_message", ""),
            featured_articles=result.get("featured_articles", []),
            quick_tips=result.get("quick_tips", []),
            upcoming_events=result.get("upcoming_events", []),
            reader_poll=result.get("reader_poll", ""),
            closing_message=result.get("closing_message", ""),
            footer=result.get("footer", ""),
            social_share_text=result.get("social_share_text", ""),
        )
    except Exception as e:
        logger.error(f"生成新闻通讯内容失败: {e}")
        return NewsletterContentResponse(
            success=False, newsletter_name=request.newsletter_name, issue_number=request.issue_number,
            theme=request.theme, subject_line="", header_title="", opening_message="", featured_articles=[],
            quick_tips=[], upcoming_events=[], reader_poll="", closing_message="", footer="", social_share_text=""
        )


# Product Announcement Generator Models
class ProductAnnouncementRequest(BaseModel):
    """产品公告请求"""
    product_name: str = Field(..., description="产品名称")
    announcement_type: str = Field(..., description="公告类型")
    version: str = Field(default="1.0", description="版本号")


class ProductAnnouncementResponse(BaseModel):
    """产品公告响应"""
    success: bool
    product_name: str
    announcement_type: str
    version: str
    headline: str
    subheadline: str
    announcement_body: str
    key_highlights: List[str]
    new_features: List[str]
    improvements: List[str]
    bug_fixes: List[str]
    availability: str
    upgrade_notice: str
    screenshots: List[str]
    download_link: str
    contact_info: str


@router.post("/product/announcement", response_model=ProductAnnouncementResponse)
async def generate_product_announcement(request: ProductAnnouncementRequest):
    """生成产品公告"""
    try:
        from backend.services.product_announcement_generator import product_announcement_generator_service
        result = await product_announcement_generator_service.generate_product_announcement(
            request.product_name, request.announcement_type, request.version
        )
        return ProductAnnouncementResponse(
            success=True,
            product_name=result["product_name"],
            announcement_type=result["announcement_type"],
            version=result["version"],
            headline=result.get("headline", ""),
            subheadline=result.get("subheadline", ""),
            announcement_body=result.get("announcement_body", ""),
            key_highlights=result.get("key_highlights", []),
            new_features=result.get("new_features", []),
            improvements=result.get("improvements", []),
            bug_fixes=result.get("bug_fixes", []),
            availability=result.get("availability", ""),
            upgrade_notice=result.get("upgrade_notice", ""),
            screenshots=result.get("screenshots", []),
            download_link=result.get("download_link", ""),
            contact_info=result.get("contact_info", ""),
        )
    except Exception as e:
        logger.error(f"生成产品公告失败: {e}")
        return ProductAnnouncementResponse(
            success=False, product_name=request.product_name, announcement_type=request.announcement_type,
            version=request.version, headline="", subheadline="", announcement_body="", key_highlights=[],
            new_features=[], improvements=[], bug_fixes=[], availability="", upgrade_notice="",
            screenshots=[], download_link="", contact_info=""
        )


# Testimonial Request Generator Models
class TestimonialRequest(BaseModel):
    """推荐信请求"""
    customer_name: str = Field(..., description="客户名称")
    product_name: str = Field(..., description="产品名称")
    relationship: str = Field(default="客户", description="关系")


class TestimonialResponse(BaseModel):
    """推荐信响应"""
    success: bool
    customer_name: str
    product_name: str
    relationship: str
    request_subject: str
    request_message: str
    guidelines: List[str]
    suggested_questions: List[Dict[str, str]]
    testimonial_format_options: List[str]
    permission_text: str
    follow_up_timeline: str
    thank_you_message: str


@router.post("/testimonial/request", response_model=TestimonialResponse)
async def generate_testimonial_request(request: TestimonialRequest):
    """生成推荐信请求"""
    try:
        from backend.services.testimonial_request_generator import testimonial_request_generator_service
        result = await testimonial_request_generator_service.generate_testimonial_request(
            request.customer_name, request.product_name, request.relationship
        )
        return TestimonialResponse(
            success=True,
            customer_name=result["customer_name"],
            product_name=result["product_name"],
            relationship=result["relationship"],
            request_subject=result.get("request_subject", ""),
            request_message=result.get("request_message", ""),
            guidelines=result.get("guidelines", []),
            suggested_questions=result.get("suggested_questions", []),
            testimonial_format_options=result.get("testimonial_format_options", []),
            permission_text=result.get("permission_text", ""),
            follow_up_timeline=result.get("follow_up_timeline", ""),
            thank_you_message=result.get("thank_you_message", ""),
        )
    except Exception as e:
        logger.error(f"生成推荐信请求失败: {e}")
        return TestimonialResponse(
            success=False, customer_name=request.customer_name, product_name=request.product_name,
            relationship=request.relationship, request_subject="", request_message="", guidelines=[],
            suggested_questions=[], testimonial_format_options=[], permission_text="",
            follow_up_timeline="", thank_you_message=""
        )


# Award Nomination Generator Models
class AwardNominationRequest(BaseModel):
    """奖项提名请求"""
    nominee_name: str = Field(..., description="被提名者名称")
    award_name: str = Field(..., description="奖项名称")
    category: str = Field(..., description="类别")


class AwardNominationResponse(BaseModel):
    """奖项提名响应"""
    success: bool
    nominee_name: str
    award_name: str
    category: str
    nomination_letter: str
    achievement_summary: str
    key_accomplishments: List[str]
    impact_statement: str
    supporting_evidence: List[str]
    nominee_bio: str
    recommendations: List[str]
    media_kit: List[str]


@router.post("/award/nomination", response_model=AwardNominationResponse)
async def generate_award_nomination(request: AwardNominationRequest):
    """生成奖项提名"""
    try:
        from backend.services.award_nomination_generator import award_nomination_generator_service
        result = await award_nomination_generator_service.generate_award_nomination(
            request.nominee_name, request.award_name, request.category
        )
        return AwardNominationResponse(
            success=True,
            nominee_name=result["nominee_name"],
            award_name=result["award_name"],
            category=result["category"],
            nomination_letter=result.get("nomination_letter", ""),
            achievement_summary=result.get("achievement_summary", ""),
            key_accomplishments=result.get("key_accomplishments", []),
            impact_statement=result.get("impact_statement", ""),
            supporting_evidence=result.get("supporting_evidence", []),
            nominee_bio=result.get("nominee_bio", ""),
            recommendations=result.get("recommendations", []),
            media_kit=result.get("media_kit", []),
        )
    except Exception as e:
        logger.error(f"生成奖项提名失败: {e}")
        return AwardNominationResponse(
            success=False, nominee_name=request.nominee_name, award_name=request.award_name,
            category=request.category, nomination_letter="", achievement_summary="", key_accomplishments=[],
            impact_statement="", supporting_evidence=[], nominee_bio="", recommendations=[], media_kit=[]
        )


# Client Success Story Generator Models
class ClientSuccessStoryRequest(BaseModel):
    """客户成功故事请求"""
    client_name: str = Field(..., description="客户名称")
    industry: str = Field(..., description="行业")
    problem_brief: str = Field(..., description="问题简述")
    solution_brief: str = Field(..., description="解决方案简述")


class ClientSuccessStoryResponse(BaseModel):
    """客户成功故事响应"""
    success: bool
    client_name: str
    industry: str
    problem_brief: str
    solution_brief: str
    story_title: str
    executive_summary: str
    client_background: str
    challenge: str
    solution: str
    implementation: str
    results: List[Dict[str, str]]
    testimonial: str
    lessons_learned: str
    about_company: str


@router.post("/client/success-story", response_model=ClientSuccessStoryResponse)
async def generate_client_success_story(request: ClientSuccessStoryRequest):
    """生成客户成功故事"""
    try:
        from backend.services.client_success_story_generator import client_success_story_generator_service
        result = await client_success_story_generator_service.generate_success_story(
            request.client_name, request.industry, request.problem_brief, request.solution_brief
        )
        return ClientSuccessStoryResponse(
            success=True,
            client_name=result["client_name"],
            industry=result["industry"],
            problem_brief=result["problem_brief"],
            solution_brief=result["solution_brief"],
            story_title=result.get("story_title", ""),
            executive_summary=result.get("executive_summary", ""),
            client_background=result.get("client_background", ""),
            challenge=result.get("challenge", ""),
            solution=result.get("solution", ""),
            implementation=result.get("implementation", ""),
            results=result.get("results", []),
            testimonial=result.get("testimonial", ""),
            lessons_learned=result.get("lessons_learned", ""),
            about_company=result.get("about_company", ""),
        )
    except Exception as e:
        logger.error(f"生成客户成功故事失败: {e}")
        return ClientSuccessStoryResponse(
            success=False, client_name=request.client_name, industry=request.industry,
            problem_brief=request.problem_brief, solution_brief=request.solution_brief,
            story_title="", executive_summary="", client_background="", challenge="", solution="",
            implementation="", results=[], testimonial="", lessons_learned="", about_company=""
        )


# Partnership Announcement Generator Models
class PartnershipAnnouncementRequest(BaseModel):
    """合作公告请求"""
    company_a: str = Field(..., description="公司A")
    company_b: str = Field(..., description="公司B")
    partnership_type: str = Field(..., description="合作类型")


class PartnershipAnnouncementResponse(BaseModel):
    """合作公告响应"""
    success: bool
    company_a: str
    company_b: str
    partnership_type: str
    headline: str
    subheadline: str
    announcement_body: str
    partnership_details: str
    mutual_benefits: List[str]
    joint_initiatives: List[str]
    quote_company_a: str
    quote_company_b: str
    timeline: str
    contact_information: str


@router.post("/partnership/announcement", response_model=PartnershipAnnouncementResponse)
async def generate_partnership_announcement(request: PartnershipAnnouncementRequest):
    """生成合作公告"""
    try:
        from backend.services.partnership_announcement_generator import partnership_announcement_generator_service
        result = await partnership_announcement_generator_service.generate_partnership_announcement(
            request.company_a, request.company_b, request.partnership_type
        )
        return PartnershipAnnouncementResponse(
            success=True,
            company_a=result["company_a"],
            company_b=result["company_b"],
            partnership_type=result["partnership_type"],
            headline=result.get("headline", ""),
            subheadline=result.get("subheadline", ""),
            announcement_body=result.get("announcement_body", ""),
            partnership_details=result.get("partnership_details", ""),
            mutual_benefits=result.get("mutual_benefits", []),
            joint_initiatives=result.get("joint_initiatives", []),
            quote_company_a=result.get("quote_company_a", ""),
            quote_company_b=result.get("quote_company_b", ""),
            timeline=result.get("timeline", ""),
            contact_information=result.get("contact_information", ""),
        )
    except Exception as e:
        logger.error(f"生成合作公告失败: {e}")
        return PartnershipAnnouncementResponse(
            success=False, company_a=request.company_a, company_b=request.company_b,
            partnership_type=request.partnership_type, headline="", subheadline="", announcement_body="",
            partnership_details="", mutual_benefits=[], joint_initiatives=[], quote_company_a="",
            quote_company_b="", timeline="", contact_information=""
        )


# Community Post Generator Models
class CommunityPostRequest(BaseModel):
    """社区帖子请求"""
    platform: str = Field(..., description="平台")
    topic: str = Field(..., description="主题")
    post_type: str = Field(default="discussion", description="帖子类型")


class CommunityPostResponse(BaseModel):
    """社区帖子响应"""
    success: bool
    platform: str
    topic: str
    post_type: str
    title: str
    body: str
    discussion_questions: List[str]
    engagement_tips: List[str]
    hashtags: List[str]
    optimal_posting_time: str
    moderation_notes: str


@router.post("/community/post", response_model=CommunityPostResponse)
async def generate_community_post(request: CommunityPostRequest):
    """生成社区帖子"""
    try:
        from backend.services.community_post_generator import community_post_generator_service
        result = await community_post_generator_service.generate_community_post(
            request.platform, request.topic, request.post_type
        )
        return CommunityPostResponse(
            success=True,
            platform=result["platform"],
            topic=result["topic"],
            post_type=result["post_type"],
            title=result.get("title", ""),
            body=result.get("body", ""),
            discussion_questions=result.get("discussion_questions", []),
            engagement_tips=result.get("engagement_tips", []),
            hashtags=result.get("hashtags", []),
            optimal_posting_time=result.get("optimal_posting_time", ""),
            moderation_notes=result.get("moderation_notes", ""),
        )
    except Exception as e:
        logger.error(f"生成社区帖子失败: {e}")
        return CommunityPostResponse(
            success=False, platform=request.platform, topic=request.topic, post_type=request.post_type,
            title="", body="", discussion_questions=[], engagement_tips=[], hashtags=[],
            optimal_posting_time="", moderation_notes=""
        )


# Service Catalog Generator Models
class ServiceCatalogRequest(BaseModel):
    """服务目录请求"""
    company_name: str = Field(..., description="公司名称")
    industry: str = Field(..., description="行业")
    num_services: int = Field(default=8, description="服务数量")


class ServiceCatalogResponse(BaseModel):
    """服务目录响应"""
    success: bool
    company_name: str
    industry: str
    num_services: int
    catalog_title: str
    introduction: str
    services: List[Dict[str, Any]]
    process_overview: str
    why_choose_us: str
    contact_information: str


@router.post("/service/catalog", response_model=ServiceCatalogResponse)
async def generate_service_catalog(request: ServiceCatalogRequest):
    """生成服务目录"""
    try:
        from backend.services.service_catalog_generator import service_catalog_generator_service
        result = await service_catalog_generator_service.generate_service_catalog(
            request.company_name, request.industry, request.num_services
        )
        return ServiceCatalogResponse(
            success=True,
            company_name=result["company_name"],
            industry=result["industry"],
            num_services=result["num_services"],
            catalog_title=result.get("catalog_title", ""),
            introduction=result.get("introduction", ""),
            services=result.get("services", []),
            process_overview=result.get("process_overview", ""),
            why_choose_us=result.get("why_choose_us", ""),
            contact_information=result.get("contact_information", ""),
        )
    except Exception as e:
        logger.error(f"生成服务目录失败: {e}")
        return ServiceCatalogResponse(
            success=False, company_name=request.company_name, industry=request.industry,
            num_services=request.num_services, catalog_title="", introduction="", services=[],
            process_overview="", why_choose_us="", contact_information=""
        )


# Process Documentation Generator Models
class ProcessDocumentationRequest(BaseModel):
    """流程文档请求"""
    process_name: str = Field(..., description="流程名称")
    department: str = Field(..., description="部门")
    complexity: str = Field(default="medium", description="复杂程度")


class ProcessDocumentationResponse(BaseModel):
    """流程文档响应"""
    success: bool
    process_name: str
    department: str
    complexity: str
    overview: str
    purpose: str
    scope: str
    stakeholders: List[str]
    prerequisites: List[str]
    steps: List[Dict[str, Any]]
    decision_points: List[str]
    error_handling: str
    metrics: List[str]
    related_processes: List[str]
    version: str


@router.post("/process/documentation", response_model=ProcessDocumentationResponse)
async def generate_process_documentation(request: ProcessDocumentationRequest):
    """生成流程文档"""
    try:
        from backend.services.process_documentation_generator import process_documentation_generator_service
        result = await process_documentation_generator_service.generate_process_documentation(
            request.process_name, request.department, request.complexity
        )
        return ProcessDocumentationResponse(
            success=True,
            process_name=result["process_name"],
            department=result["department"],
            complexity=result["complexity"],
            overview=result.get("overview", ""),
            purpose=result.get("purpose", ""),
            scope=result.get("scope", ""),
            stakeholders=result.get("stakeholders", []),
            prerequisites=result.get("prerequisites", []),
            steps=result.get("steps", []),
            decision_points=result.get("decision_points", []),
            error_handling=result.get("error_handling", ""),
            metrics=result.get("metrics", []),
            related_processes=result.get("related_processes", []),
            version=result.get("version", ""),
        )
    except Exception as e:
        logger.error(f"生成流程文档失败: {e}")
        return ProcessDocumentationResponse(
            success=False, process_name=request.process_name, department=request.department,
            complexity=request.complexity, overview="", purpose="", scope="", stakeholders=[],
            prerequisites=[], steps=[], decision_points=[], error_handling="", metrics=[],
            related_processes=[], version=""
        )


# SWOT Analysis Generator Models
class SWOTAnalysisRequest(BaseModel):
    """SWOT分析请求"""
    subject_name: str = Field(..., description="分析对象名称")
    subject_type: str = Field(default="company", description="分析对象类型")
    industry: str = Field(default="", description="行业")


class SWOTAnalysisResponse(BaseModel):
    """SWOT分析响应"""
    success: bool
    subject_name: str
    subject_type: str
    industry: str
    strengths: List[Dict[str, str]]
    weaknesses: List[Dict[str, str]]
    opportunities: List[Dict[str, str]]
    threats: List[Dict[str, str]]
    strategic_recommendations: List[str]
    overall_assessment: str


@router.post("/analysis/swot", response_model=SWOTAnalysisResponse)
async def generate_swot_analysis(request: SWOTAnalysisRequest):
    """生成SWOT分析"""
    try:
        from backend.services.swot_analysis_generator import swot_analysis_generator_service
        result = await swot_analysis_generator_service.generate_swot_analysis(
            request.subject_name, request.subject_type, request.industry
        )
        return SWOTAnalysisResponse(
            success=True,
            subject_name=result["subject_name"],
            subject_type=result["subject_type"],
            industry=result["industry"],
            strengths=result.get("strengths", []),
            weaknesses=result.get("weaknesses", []),
            opportunities=result.get("opportunities", []),
            threats=result.get("threats", []),
            strategic_recommendations=result.get("strategic_recommendations", []),
            overall_assessment=result.get("overall_assessment", ""),
        )
    except Exception as e:
        logger.error(f"生成SWOT分析失败: {e}")
        return SWOTAnalysisResponse(
            success=False, subject_name=request.subject_name, subject_type=request.subject_type,
            industry=request.industry, strengths=[], weaknesses=[], opportunities=[], threats=[],
            strategic_recommendations=[], overall_assessment=""
        )


# Competitive Landscape Generator Models
class CompetitiveLandscapeRequest(BaseModel):
    """竞争格局分析请求"""
    company_name: str = Field(..., description="公司名称")
    industry: str = Field(..., description="行业")
    main_competitors: List[str] = Field(default=None, description="主要竞争对手")


class CompetitiveLandscapeResponse(BaseModel):
    """竞争格局分析响应"""
    success: bool
    company_name: str
    industry: str
    main_competitors: List[str]
    market_overview: str
    competitor_analysis: List[Dict[str, Any]]
    competitive_advantages: List[str]
    market_gaps: List[str]
    threats: List[str]
    recommendations: List[str]


@router.post("/analysis/competitive", response_model=CompetitiveLandscapeResponse)
async def generate_competitive_landscape(request: CompetitiveLandscapeRequest):
    """生成竞争格局分析"""
    try:
        from backend.services.competitive_landscape_generator import competitive_landscape_generator_service
        result = await competitive_landscape_generator_service.generate_competitive_landscape(
            request.company_name, request.industry, request.main_competitors
        )
        return CompetitiveLandscapeResponse(
            success=True,
            company_name=result["company_name"],
            industry=result["industry"],
            main_competitors=result["main_competitors"],
            market_overview=result.get("market_overview", ""),
            competitor_analysis=result.get("competitor_analysis", []),
            competitive_advantages=result.get("competitive_advantages", []),
            market_gaps=result.get("market_gaps", []),
            threats=result.get("threats", []),
            recommendations=result.get("recommendations", []),
        )
    except Exception as e:
        logger.error(f"生成竞争格局分析失败: {e}")
        return CompetitiveLandscapeResponse(
            success=False, company_name=request.company_name, industry=request.industry,
            main_competitors=request.main_competitors or [], market_overview="", competitor_analysis=[],
            competitive_advantages=[], market_gaps=[], threats=[], recommendations=[]
        )


# Mindmap Content Generator Models
class MindmapContentRequest(BaseModel):
    """思维导图内容请求"""
    central_topic: str = Field(..., description="中心主题")
    depth: int = Field(default=3, description="深度")
    branch_count: int = Field(default=5, description="分支数量")


class MindmapContentResponse(BaseModel):
    """思维导图内容响应"""
    success: bool
    central_topic: str
    depth: int
    branch_count: int
    mindmap_structure: Dict[str, Any]
    key_concepts: List[str]
    relationships: List[str]
    visualization_tips: List[str]
    color_coding_suggestions: str


@router.post("/mindmap/content", response_model=MindmapContentResponse)
async def generate_mindmap_content(request: MindmapContentRequest):
    """生成思维导图内容"""
    try:
        from backend.services.mindmap_content_generator import mindmap_content_generator_service
        result = await mindmap_content_generator_service.generate_mindmap_content(
            request.central_topic, request.depth, request.branch_count
        )
        return MindmapContentResponse(
            success=True,
            central_topic=result["central_topic"],
            depth=result["depth"],
            branch_count=result["branch_count"],
            mindmap_structure=result.get("mindmap_structure", {}),
            key_concepts=result.get("key_concepts", []),
            relationships=result.get("relationships", []),
            visualization_tips=result.get("visualization_tips", []),
            color_coding_suggestions=result.get("color_coding_suggestions", ""),
        )
    except Exception as e:
        logger.error(f"生成思维导图内容失败: {e}")
        return MindmapContentResponse(
            success=False, central_topic=request.central_topic, depth=request.depth,
            branch_count=request.branch_count, mindmap_structure={}, key_concepts=[],
            relationships=[], visualization_tips=[], color_coding_suggestions=""
        )


# Market Trend Report Generator Models
class MarketTrendReportRequest(BaseModel):
    """市场趋势报告请求"""
    industry: str = Field(..., description="行业")
    region: str = Field(default="全球", description="地区")
    time_horizon: str = Field(default="2026", description="时间范围")


class MarketTrendReportResponse(BaseModel):
    """市场趋势报告响应"""
    success: bool
    industry: str
    region: str
    time_horizon: str
    executive_summary: str
    market_size: str
    growth_rate: str
    key_trends: List[str]
    driving_factors: List[str]
    challenges: List[str]
    emerging_technologies: List[str]
    consumer_behavior_changes: List[str]
    competitive_landscape: str
    investment_opportunities: List[str]
    forecast: str
    recommendations: List[str]


@router.post("/report/market-trend", response_model=MarketTrendReportResponse)
async def generate_market_trend_report(request: MarketTrendReportRequest):
    """生成市场趋势报告"""
    try:
        from backend.services.market_trend_report_generator import market_trend_report_generator_service
        result = await market_trend_report_generator_service.generate_market_trend_report(
            request.industry, request.region, request.time_horizon
        )
        return MarketTrendReportResponse(
            success=True,
            industry=result["industry"],
            region=result["region"],
            time_horizon=result["time_horizon"],
            executive_summary=result.get("executive_summary", ""),
            market_size=result.get("market_size", ""),
            growth_rate=result.get("growth_rate", ""),
            key_trends=result.get("key_trends", []),
            driving_factors=result.get("driving_factors", []),
            challenges=result.get("challenges", []),
            emerging_technologies=result.get("emerging_technologies", []),
            consumer_behavior_changes=result.get("consumer_behavior_changes", []),
            competitive_landscape=result.get("competitive_landscape", ""),
            investment_opportunities=result.get("investment_opportunities", []),
            forecast=result.get("forecast", ""),
            recommendations=result.get("recommendations", []),
        )
    except Exception as e:
        logger.error(f"生成市场趋势报告失败: {e}")
        return MarketTrendReportResponse(
            success=False, industry=request.industry, region=request.region,
            time_horizon=request.time_horizon, executive_summary="", market_size="", growth_rate="",
            key_trends=[], driving_factors=[], challenges=[], emerging_technologies=[],
            consumer_behavior_changes=[], competitive_landscape="", investment_opportunities=[],
            forecast="", recommendations=[]
        )


# Product Roadmap Generator Models
class ProductRoadmapRequest(BaseModel):
    """产品路线图请求"""
    product_name: str = Field(..., description="产品名称")
    planning_period: str = Field(default="12 months", description="规划周期")
    num_versions: int = Field(default=4, description="版本数量")


class ProductRoadmapResponse(BaseModel):
    """产品路线图响应"""
    success: bool
    product_name: str
    planning_period: str
    num_versions: int
    overview: str
    versions: List[Dict[str, Any]]
    technical_requirements: List[str]
    resource_needs: str
    risks_and_mitigations: List[str]
    success_metrics: str


@router.post("/product/roadmap", response_model=ProductRoadmapResponse)
async def generate_product_roadmap(request: ProductRoadmapRequest):
    """生成产品路线图"""
    try:
        from backend.services.product_roadmap_generator import product_roadmap_generator_service
        result = await product_roadmap_generator_service.generate_product_roadmap(
            request.product_name, request.planning_period, request.num_versions
        )
        return ProductRoadmapResponse(
            success=True,
            product_name=result["product_name"],
            planning_period=result["planning_period"],
            num_versions=result["num_versions"],
            overview=result.get("overview", ""),
            versions=result.get("versions", []),
            technical_requirements=result.get("technical_requirements", []),
            resource_needs=result.get("resource_needs", ""),
            risks_and_mitigations=result.get("risks_and_mitigations", []),
            success_metrics=result.get("success_metrics", ""),
        )
    except Exception as e:
        logger.error(f"生成产品路线图失败: {e}")
        return ProductRoadmapResponse(
            success=False, product_name=request.product_name, planning_period=request.planning_period,
            num_versions=request.num_versions, overview="", versions=[], technical_requirements=[],
            resource_needs="", risks_and_mitigations=[], success_metrics=""
        )


# UX Flow Generator Models
class UXFlowRequest(BaseModel):
    """用户体验流程请求"""
    product_name: str = Field(..., description="产品名称")
    flow_type: str = Field(default="onboarding", description="流程类型")
    num_steps: int = Field(default=7, description="步骤数量")


class UXFlowResponse(BaseModel):
    """用户体验流程响应"""
    success: bool
    product_name: str
    flow_type: str
    num_steps: int
    flow_title: str
    overview: str
    user_persona: str
    steps: List[Dict[str, Any]]
    key_metrics: List[str]
    optimization_suggestions: List[str]
    friction_points: List[str]


@router.post("/ux/flow", response_model=UXFlowResponse)
async def generate_ux_flow(request: UXFlowRequest):
    """生成UX流程"""
    try:
        from backend.services.ux_flow_generator import ux_flow_generator_service
        result = await ux_flow_generator_service.generate_ux_flow(
            request.product_name, request.flow_type, request.num_steps
        )
        return UXFlowResponse(
            success=True,
            product_name=result["product_name"],
            flow_type=result["flow_type"],
            num_steps=result["num_steps"],
            flow_title=result.get("flow_title", ""),
            overview=result.get("overview", ""),
            user_persona=result.get("user_persona", ""),
            steps=result.get("steps", []),
            key_metrics=result.get("key_metrics", []),
            optimization_suggestions=result.get("optimization_suggestions", []),
            friction_points=result.get("friction_points", []),
        )
    except Exception as e:
        logger.error(f"生成UX流程失败: {e}")
        return UXFlowResponse(
            success=False, product_name=request.product_name, flow_type=request.flow_type,
            num_steps=request.num_steps, flow_title="", overview="", user_persona="", steps=[],
            key_metrics=[], optimization_suggestions=[], friction_points=[]
        )


# Campaign Analytics Generator Models
class CampaignAnalyticsRequest(BaseModel):
    """营销活动分析请求"""
    campaign_name: str = Field(..., description="活动名称")
    campaign_type: str = Field(default="social_media", description="活动类型")
    duration_weeks: int = Field(default=4, description="持续周数")


class CampaignAnalyticsResponse(BaseModel):
    """营销活动分析响应"""
    success: bool
    campaign_name: str
    campaign_type: str
    duration_weeks: int
    executive_summary: str
    performance_metrics: Dict[str, Any]
    audience_insights: List[str]
    top_performing_content: List[str]
    underperforming_content: List[str]
    a_b_test_results: List[str]
    channel_performance: List[str]
    key_learnings: List[str]
    optimization_recommendations: List[str]
    next_campaign_suggestions: List[str]


@router.post("/analytics/campaign", response_model=CampaignAnalyticsResponse)
async def generate_campaign_analytics(request: CampaignAnalyticsRequest):
    """生成营销活动分析"""
    try:
        from backend.services.campaign_analytics_generator import campaign_analytics_generator_service
        result = await campaign_analytics_generator_service.generate_campaign_analytics(
            request.campaign_name, request.campaign_type, request.duration_weeks
        )
        return CampaignAnalyticsResponse(
            success=True,
            campaign_name=result["campaign_name"],
            campaign_type=result["campaign_type"],
            duration_weeks=result["duration_weeks"],
            executive_summary=result.get("executive_summary", ""),
            performance_metrics=result.get("performance_metrics", {}),
            audience_insights=result.get("audience_insights", []),
            top_performing_content=result.get("top_performing_content", []),
            underperforming_content=result.get("underperforming_content", []),
            a_b_test_results=result.get("a_b_test_results", []),
            channel_performance=result.get("channel_performance", []),
            key_learnings=result.get("key_learnings", []),
            optimization_recommendations=result.get("optimization_recommendations", []),
            next_campaign_suggestions=result.get("next_campaign_suggestions", []),
        )
    except Exception as e:
        logger.error(f"生成营销活动分析失败: {e}")
        return CampaignAnalyticsResponse(
            success=False, campaign_name=request.campaign_name, campaign_type=request.campaign_type,
            duration_weeks=request.duration_weeks, executive_summary="", performance_metrics={},
            audience_insights=[], top_performing_content=[], underperforming_content=[],
            a_b_test_results=[], channel_performance=[], key_learnings=[], optimization_recommendations=[],
            next_campaign_suggestions=[]
        )


# Customer Persona Generator Models
class CustomerPersonaRequest(BaseModel):
    """客户画像请求"""
    persona_name: str = Field(..., description="画像名称")
    demographic_info: str = Field(..., description="人口统计信息")
    industry: str = Field(default="", description="行业")


class CustomerPersonaResponse(BaseModel):
    """客户画像响应"""
    success: bool
    persona_name: str
    demographic_info: str
    industry: str
    avatar: str
    background: str
    goals: List[str]
    pain_points: List[str]
    motivations: List[str]
    behaviors: List[str]
    preferred_channels: List[str]
    content_preferences: List[str]
    buying_patterns: str
    technology_usage: str
    quotes: List[str]
    success_metrics: str


@router.post("/customer/persona", response_model=CustomerPersonaResponse)
async def generate_customer_persona(request: CustomerPersonaRequest):
    """生成客户画像"""
    try:
        from backend.services.customer_persona_generator import customer_persona_generator_service
        result = await customer_persona_generator_service.generate_customer_persona(
            request.persona_name, request.demographic_info, request.industry
        )
        return CustomerPersonaResponse(
            success=True,
            persona_name=result["persona_name"],
            demographic_info=result["demographic_info"],
            industry=result["industry"],
            avatar=result.get("avatar", ""),
            background=result.get("background", ""),
            goals=result.get("goals", []),
            pain_points=result.get("pain_points", []),
            motivations=result.get("motivations", []),
            behaviors=result.get("behaviors", []),
            preferred_channels=result.get("preferred_channels", []),
            content_preferences=result.get("content_preferences", []),
            buying_patterns=result.get("buying_patterns", ""),
            technology_usage=result.get("technology_usage", ""),
            quotes=result.get("quotes", []),
            success_metrics=result.get("success_metrics", ""),
        )
    except Exception as e:
        logger.error(f"生成客户画像失败: {e}")
        return CustomerPersonaResponse(
            success=False, persona_name=request.persona_name, demographic_info=request.demographic_info,
            industry=request.industry, avatar="", background="", goals=[], pain_points=[],
            motivations=[], behaviors=[], preferred_channels=[], content_preferences=[],
            buying_patterns="", technology_usage="", quotes=[], success_metrics=""
        )


# Value Proposition Generator Models
class ValuePropositionRequest(BaseModel):
    """价值主张请求"""
    product_name: str = Field(..., description="产品名称")
    target_audience: str = Field(..., description="目标受众")
    main_benefit: str = Field(..., description="主要利益")


class ValuePropositionResponse(BaseModel):
    """价值主张响应"""
    success: bool
    product_name: str
    target_audience: str
    main_benefit: str
    headline: str
    subheadline: str
    value_statement: str
    key_benefits: List[str]
    differentiators: List[str]
    proof_points: List[str]
    emotional_benefits: List[str]
    rational_benefits: List[str]
    brand_promise: str
    supporting_evidence: List[str]


@router.post("/value/proposition", response_model=ValuePropositionResponse)
async def generate_value_proposition(request: ValuePropositionRequest):
    """生成价值主张"""
    try:
        from backend.services.value_proposition_generator import value_proposition_generator_service
        result = await value_proposition_generator_service.generate_value_proposition(
            request.product_name, request.target_audience, request.main_benefit
        )
        return ValuePropositionResponse(
            success=True,
            product_name=result["product_name"],
            target_audience=result["target_audience"],
            main_benefit=result["main_benefit"],
            headline=result.get("headline", ""),
            subheadline=result.get("subheadline", ""),
            value_statement=result.get("value_statement", ""),
            key_benefits=result.get("key_benefits", []),
            differentiators=result.get("differentiators", []),
            proof_points=result.get("proof_points", []),
            emotional_benefits=result.get("emotional_benefits", []),
            rational_benefits=result.get("rational_benefits", []),
            brand_promise=result.get("brand_promise", ""),
            supporting_evidence=result.get("supporting_evidence", []),
        )
    except Exception as e:
        logger.error(f"生成价值主张失败: {e}")
        return ValuePropositionResponse(
            success=False, product_name=request.product_name, target_audience=request.target_audience,
            main_benefit=request.main_benefit, headline="", subheadline="", value_statement="",
            key_benefits=[], differentiators=[], proof_points=[], emotional_benefits=[], rational_benefits=[],
            brand_promise="", supporting_evidence=[]
        )


# Brand Messaging Generator Models
class BrandMessagingRequest(BaseModel):
    """品牌话术请求"""
    brand_name: str = Field(..., description="品牌名称")
    industry: str = Field(..., description="行业")
    communication_context: str = Field(default="general", description="沟通场景")


class BrandMessagingResponse(BaseModel):
    """品牌话术响应"""
    success: bool
    brand_name: str
    industry: str
    communication_context: str
    tone_of_voice: str
    messaging_framework: str
    key_messages: List[str]
    sample_copy: Dict[str, str]
    do_and_donts: Dict[str, List[str]]
    platform_specific_messaging: List[str]
    industry_terms: List[str]
    forbidden_words: List[str]


@router.post("/brand/messaging", response_model=BrandMessagingResponse)
async def generate_brand_messaging(request: BrandMessagingRequest):
    """生成品牌话术"""
    try:
        from backend.services.brand_messaging_generator import brand_messaging_generator_service
        result = await brand_messaging_generator_service.generate_brand_messaging(
            request.brand_name, request.industry, request.communication_context
        )
        return BrandMessagingResponse(
            success=True,
            brand_name=result["brand_name"],
            industry=result["industry"],
            communication_context=result["communication_context"],
            tone_of_voice=result.get("tone_of_voice", ""),
            messaging_framework=result.get("messaging_framework", ""),
            key_messages=result.get("key_messages", []),
            sample_copy=result.get("sample_copy", {}),
            do_and_donts=result.get("do_and_donts", {"do": [], "donts": []}),
            platform_specific_messaging=result.get("platform_specific_messaging", []),
            industry_terms=result.get("industry_terms", []),
            forbidden_words=result.get("forbidden_words", []),
        )
    except Exception as e:
        logger.error(f"生成品牌话术失败: {e}")
        return BrandMessagingResponse(
            success=False, brand_name=request.brand_name, industry=request.industry,
            communication_context=request.communication_context, tone_of_voice="",
            messaging_framework="", key_messages=[], sample_copy={}, do_and_donts={"do": [], "donts": []},
            platform_specific_messaging=[], industry_terms=[], forbidden_words=[]
        )


# Go-To-Market Generator Models
class GoToMarketRequest(BaseModel):
    """市场推广计划请求"""
    product_name: str = Field(..., description="产品名称")
    launch_date: str = Field(..., description="发布日期")
    target_market: str = Field(..., description="目标市场")


class GoToMarketResponse(BaseModel):
    """市场推广计划响应"""
    success: bool
    product_name: str
    launch_date: str
    target_market: str
    executive_summary: str
    market_analysis: str
    target_customer: str
    competitive_positioning: str
    pricing_strategy: str
    launch_phases: List[Dict[str, Any]]
    marketing_channels: List[str]
    promotional_tactics: List[str]
    sales_enablement: str
    budget_allocation: str
    risk_assessment: str
    success_metrics: str


@router.post("/go-to-market", response_model=GoToMarketResponse)
async def generate_go_to_market(request: GoToMarketRequest):
    """生成市场推广计划"""
    try:
        from backend.services.go_to_market_generator import go_to_market_generator_service
        result = await go_to_market_generator_service.generate_go_to_market(
            request.product_name, request.launch_date, request.target_market
        )
        return GoToMarketResponse(
            success=True,
            product_name=result["product_name"],
            launch_date=result["launch_date"],
            target_market=result["target_market"],
            executive_summary=result.get("executive_summary", ""),
            market_analysis=result.get("market_analysis", ""),
            target_customer=result.get("target_customer", ""),
            competitive_positioning=result.get("competitive_positioning", ""),
            pricing_strategy=result.get("pricing_strategy", ""),
            launch_phases=result.get("launch_phases", []),
            marketing_channels=result.get("marketing_channels", []),
            promotional_tactics=result.get("promotional_tactics", []),
            sales_enablement=result.get("sales_enablement", ""),
            budget_allocation=result.get("budget_allocation", ""),
            risk_assessment=result.get("risk_assessment", ""),
            success_metrics=result.get("success_metrics", ""),
        )
    except Exception as e:
        logger.error(f"生成市场推广计划失败: {e}")
        return GoToMarketResponse(
            success=False, product_name=request.product_name, launch_date=request.launch_date,
            target_market=request.target_market, executive_summary="", market_analysis="",
            target_customer="", competitive_positioning="", pricing_strategy="", launch_phases=[],
            marketing_channels=[], promotional_tactics=[], sales_enablement="", budget_allocation="",
            risk_assessment="", success_metrics=""
        )


# Channel Strategy Generator Models
class ChannelStrategyRequest(BaseModel):
    """渠道策略请求"""
    product_name: str = Field(..., description="产品名称")
    industry: str = Field(..., description="行业")
    num_channels: int = Field(default=5, description="渠道数量")


class ChannelStrategyResponse(BaseModel):
    """渠道策略响应"""
    success: bool
    product_name: str
    industry: str
    num_channels: int
    overview: str
    channel_analysis: List[Dict[str, Any]]
    channel_mix_recommendation: str
    budget_allocation: str
    timeline: str
    success_metrics: str
    risks: List[str]
    mitigation_strategies: List[str]


@router.post("/strategy/channel", response_model=ChannelStrategyResponse)
async def generate_channel_strategy(request: ChannelStrategyRequest):
    """生成渠道策略"""
    try:
        from backend.services.channel_strategy_generator import channel_strategy_generator_service
        result = await channel_strategy_generator_service.generate_channel_strategy(
            request.product_name, request.industry, request.num_channels
        )
        return ChannelStrategyResponse(
            success=True,
            product_name=result["product_name"],
            industry=result["industry"],
            num_channels=result["num_channels"],
            overview=result.get("overview", ""),
            channel_analysis=result.get("channel_analysis", []),
            channel_mix_recommendation=result.get("channel_mix_recommendation", ""),
            budget_allocation=result.get("budget_allocation", ""),
            timeline=result.get("timeline", ""),
            success_metrics=result.get("success_metrics", ""),
            risks=result.get("risks", []),
            mitigation_strategies=result.get("mitigation_strategies", []),
        )
    except Exception as e:
        logger.error(f"生成渠道策略失败: {e}")
        return ChannelStrategyResponse(
            success=False, product_name=request.product_name, industry=request.industry,
            num_channels=request.num_channels, overview="", channel_analysis=[],
            channel_mix_recommendation="", budget_allocation="", timeline="", success_metrics="",
            risks=[], mitigation_strategies=[]
        )


# Pricing Strategy Generator Models
class PricingStrategyRequest(BaseModel):
    """定价策略请求"""
    product_name: str = Field(..., description="产品名称")
    product_category: str = Field(..., description="产品类别")
    target_segment: str = Field(..., description="目标细分市场")


class PricingStrategyResponse(BaseModel):
    """定价策略响应"""
    success: bool
    product_name: str
    product_category: str
    target_segment: str
    executive_summary: str
    pricing_objectives: List[str]
    pricing_model: str
    price_tiers: List[Dict[str, Any]]
    competitive_pricing_analysis: str
    psychological_pricing: str
    discount_strategy: str
    promotional_pricing: str
    revenue_projections: str
    price_testing_plan: str
    implementation_timeline: str


@router.post("/strategy/pricing", response_model=PricingStrategyResponse)
async def generate_pricing_strategy(request: PricingStrategyRequest):
    """生成定价策略"""
    try:
        from backend.services.pricing_strategy_generator import pricing_strategy_generator_service
        result = await pricing_strategy_generator_service.generate_pricing_strategy(
            request.product_name, request.product_category, request.target_segment
        )
        return PricingStrategyResponse(
            success=True,
            product_name=result["product_name"],
            product_category=result["product_category"],
            target_segment=result["target_segment"],
            executive_summary=result.get("executive_summary", ""),
            pricing_objectives=result.get("pricing_objectives", []),
            pricing_model=result.get("pricing_model", ""),
            price_tiers=result.get("price_tiers", []),
            competitive_pricing_analysis=result.get("competitive_pricing_analysis", ""),
            psychological_pricing=result.get("psychological_pricing", ""),
            discount_strategy=result.get("discount_strategy", ""),
            promotional_pricing=result.get("promotional_pricing", ""),
            revenue_projections=result.get("revenue_projections", ""),
            price_testing_plan=result.get("price_testing_plan", ""),
            implementation_timeline=result.get("implementation_timeline", ""),
        )
    except Exception as e:
        logger.error(f"生成定价策略失败: {e}")
        return PricingStrategyResponse(
            success=False, product_name=request.product_name, product_category=request.product_category,
            target_segment=request.target_segment, executive_summary="", pricing_objectives=[],
            pricing_model="", price_tiers=[], competitive_pricing_analysis="", psychological_pricing="",
            discount_strategy="", promotional_pricing="", revenue_projections="", price_testing_plan="",
            implementation_timeline=""
        )


# Product Launch Checklist Generator Models
class ProductLaunchChecklistRequest(BaseModel):
    """产品发布清单请求"""
    product_name: str = Field(..., description="产品名称")
    launch_date: str = Field(..., description="发布日期")
    launch_type: str = Field(default="new product", description="发布类型")


class ProductLaunchChecklistResponse(BaseModel):
    """产品发布清单响应"""
    success: bool
    product_name: str
    launch_date: str
    launch_type: str
    overview: str
    pre_launch_checklist: List[Dict[str, Any]]
    launch_day_checklist: List[str]
    post_launch_checklist: List[str]
    risk_items: List[str]
    escalation_plan: str
    success_criteria: str


@router.post("/product/launch-checklist", response_model=ProductLaunchChecklistResponse)
async def generate_launch_checklist(request: ProductLaunchChecklistRequest):
    """生成产品发布清单"""
    try:
        from backend.services.product_launch_checklist_generator import product_launch_checklist_generator_service
        result = await product_launch_checklist_generator_service.generate_launch_checklist(
            request.product_name, request.launch_date, request.launch_type
        )
        return ProductLaunchChecklistResponse(
            success=True,
            product_name=result["product_name"],
            launch_date=result["launch_date"],
            launch_type=result["launch_type"],
            overview=result.get("overview", ""),
            pre_launch_checklist=result.get("pre_launch_checklist", []),
            launch_day_checklist=result.get("launch_day_checklist", []),
            post_launch_checklist=result.get("post_launch_checklist", []),
            risk_items=result.get("risk_items", []),
            escalation_plan=result.get("escalation_plan", ""),
            success_criteria=result.get("success_criteria", ""),
        )
    except Exception as e:
        logger.error(f"生成产品发布清单失败: {e}")
        return ProductLaunchChecklistResponse(
            success=False, product_name=request.product_name, launch_date=request.launch_date,
            launch_type=request.launch_type, overview="", pre_launch_checklist=[], launch_day_checklist=[],
            post_launch_checklist=[], risk_items=[], escalation_plan="", success_criteria=""
        )


# Customer Journey Map Generator Models
class CustomerJourneyMapRequest(BaseModel):
    """客户旅程地图请求"""
    product_name: str = Field(..., description="产品名称")
    target_audience: str = Field(..., description="目标受众")
    num_stages: int = Field(default=5, description="阶段数量")


class CustomerJourneyMapResponse(BaseModel):
    """客户旅程地图响应"""
    success: bool
    product_name: str
    target_audience: str
    num_stages: int
    overview: str
    persona: str
    stages: List[Dict[str, Any]]
    key_insights: List[str]
    improvement_areas: List[str]
    quick_wins: List[str]
    strategic_initiatives: List[str]


@router.post("/customer/journey-map", response_model=CustomerJourneyMapResponse)
async def generate_journey_map(request: CustomerJourneyMapRequest):
    """生成客户旅程地图"""
    try:
        from backend.services.customer_journey_map_generator import customer_journey_map_generator_service
        result = await customer_journey_map_generator_service.generate_journey_map(
            request.product_name, request.target_audience, request.num_stages
        )
        return CustomerJourneyMapResponse(
            success=True,
            product_name=result["product_name"],
            target_audience=result["target_audience"],
            num_stages=result["num_stages"],
            overview=result.get("overview", ""),
            persona=result.get("persona", ""),
            stages=result.get("stages", []),
            key_insights=result.get("key_insights", []),
            improvement_areas=result.get("improvement_areas", []),
            quick_wins=result.get("quick_wins", []),
            strategic_initiatives=result.get("strategic_initiatives", []),
        )
    except Exception as e:
        logger.error(f"生成客户旅程地图失败: {e}")
        return CustomerJourneyMapResponse(
            success=False, product_name=request.product_name, target_audience=request.target_audience,
            num_stages=request.num_stages, overview="", persona="", stages=[], key_insights=[],
            improvement_areas=[], quick_wins=[], strategic_initiatives=[]
        )


# Competitor Analysis Generator Models
class CompetitorAnalysisRequest(BaseModel):
    """竞争对手分析请求"""
    your_product: str = Field(..., description="你的产品")
    competitor_name: str = Field(..., description="竞争对手名称")
    industry: str = Field(..., description="行业")


class CompetitorAnalysisResponse(BaseModel):
    """竞争对手分析响应"""
    success: bool
    your_product: str
    competitor_name: str
    industry: str
    overview: str
    competitor_profile: Dict[str, str]
    product_comparison: List[Dict[str, Any]]
    pricing_comparison: str
    strengths: List[str]
    weaknesses: List[str]
    market_share: str
    swot_analysis: Dict[str, List[str]]
    competitive_advantages_to_emphasize: List[str]
    potential_threats: List[str]
    strategic_recommendations: List[str]


@router.post("/analysis/competitor", response_model=CompetitorAnalysisResponse)
async def generate_competitor_analysis(request: CompetitorAnalysisRequest):
    """生成竞争对手分析"""
    try:
        from backend.services.competitor_analysis_generator import competitor_analysis_generator_service
        result = await competitor_analysis_generator_service.generate_competitor_analysis(
            request.your_product, request.competitor_name, request.industry
        )
        return CompetitorAnalysisResponse(
            success=True,
            your_product=result["your_product"],
            competitor_name=result["competitor_name"],
            industry=result["industry"],
            overview=result.get("overview", ""),
            competitor_profile=result.get("competitor_profile", {}),
            product_comparison=result.get("product_comparison", []),
            pricing_comparison=result.get("pricing_comparison", ""),
            strengths=result.get("strengths", []),
            weaknesses=result.get("weaknesses", []),
            market_share=result.get("market_share", ""),
            swot_analysis=result.get("swot_analysis", {}),
            competitive_advantages_to_emphasize=result.get("competitive_advantages_to_emphasize", []),
            potential_threats=result.get("potential_threats", []),
            strategic_recommendations=result.get("strategic_recommendations", []),
        )
    except Exception as e:
        logger.error(f"生成竞争对手分析失败: {e}")
        return CompetitorAnalysisResponse(
            success=False, your_product=request.your_product, competitor_name=request.competitor_name,
            industry=request.industry, overview="", competitor_profile={}, product_comparison=[],
            pricing_comparison="", strengths=[], weaknesses=[], market_share="", swot_analysis={},
            competitive_advantages_to_emphasize=[], potential_threats=[], strategic_recommendations=[]
        )


# Feature Specification Generator Models
class FeatureSpecRequest(BaseModel):
    """功能规格说明书请求"""
    feature_name: str = Field(..., description="功能名称")
    product_name: str = Field(..., description="产品名称")
    feature_type: str = Field(default="new feature", description="功能类型")


class FeatureSpecResponse(BaseModel):
    """功能规格说明书响应"""
    success: bool
    feature_name: str
    product_name: str
    feature_type: str
    overview: str
    user_story: str
    functional_requirements: List[Dict[str, Any]]
    non_functional_requirements: List[str]
    user_interface: Dict[str, Any]
    data_requirements: List[str]
    technical_specifications: List[str]
    dependencies: List[str]
    constraints: List[str]
    edge_cases: List[str]
    error_handling: str
    testing_requirements: List[str]
    success_metrics: str


@router.post("/feature/specification", response_model=FeatureSpecResponse)
async def generate_feature_spec(request: FeatureSpecRequest):
    """生成功能规格说明书"""
    try:
        from backend.services.feature_specification_generator import feature_specification_generator_service
        result = await feature_specification_generator_service.generate_feature_spec(
            request.feature_name, request.product_name, request.feature_type
        )
        return FeatureSpecResponse(
            success=True,
            feature_name=result["feature_name"],
            product_name=result["product_name"],
            feature_type=result["feature_type"],
            overview=result.get("overview", ""),
            user_story=result.get("user_story", ""),
            functional_requirements=result.get("functional_requirements", []),
            non_functional_requirements=result.get("non_functional_requirements", []),
            user_interface=result.get("user_interface", {}),
            data_requirements=result.get("data_requirements", []),
            technical_specifications=result.get("technical_specifications", []),
            dependencies=result.get("dependencies", []),
            constraints=result.get("constraints", []),
            edge_cases=result.get("edge_cases", []),
            error_handling=result.get("error_handling", ""),
            testing_requirements=result.get("testing_requirements", []),
            success_metrics=result.get("success_metrics", ""),
        )
    except Exception as e:
        logger.error(f"生成功能规格说明书失败: {e}")
        return FeatureSpecResponse(
            success=False, feature_name=request.feature_name, product_name=request.product_name,
            feature_type=request.feature_type, overview="", user_story="", functional_requirements=[],
            non_functional_requirements=[], user_interface={}, data_requirements=[], technical_specifications=[],
            dependencies=[], constraints=[], edge_cases=[], error_handling="", testing_requirements=[], success_metrics=""
        )


# API Specification Generator Models
class APISpecRequest(BaseModel):
    """API规格请求"""
    api_name: str = Field(..., description="API名称")
    api_version: str = Field(default="1.0", description="API版本")
    num_endpoints: int = Field(default=5, description="端点数量")


class APISpecResponse(BaseModel):
    """API规格响应"""
    success: bool
    api_name: str
    api_version: str
    num_endpoints: int
    base_url: str
    overview: str
    authentication: str
    endpoints: List[Dict[str, Any]]
    rate_limiting: str
    pagination: str
    webhooks: List[str]
    sdks: List[str]
    changelog: str


@router.post("/api/specification", response_model=APISpecResponse)
async def generate_api_spec(request: APISpecRequest):
    """生成API规格"""
    try:
        from backend.services.api_specification_generator import api_specification_generator_service
        result = await api_specification_generator_service.generate_api_spec(
            request.api_name, request.api_version, request.num_endpoints
        )
        return APISpecResponse(
            success=True,
            api_name=result["api_name"],
            api_version=result["api_version"],
            num_endpoints=result["num_endpoints"],
            base_url=result.get("base_url", ""),
            overview=result.get("overview", ""),
            authentication=result.get("authentication", ""),
            endpoints=result.get("endpoints", []),
            rate_limiting=result.get("rate_limiting", ""),
            pagination=result.get("pagination", ""),
            webhooks=result.get("webhooks", []),
            sdks=result.get("sdks", []),
            changelog=result.get("changelog", ""),
        )
    except Exception as e:
        logger.error(f"生成API规格失败: {e}")
        return APISpecResponse(
            success=False, api_name=request.api_name, api_version=request.api_version,
            num_endpoints=request.num_endpoints, base_url="", overview="", authentication="",
            endpoints=[], rate_limiting="", pagination="", webhooks=[], sdks=[], changelog=""
        )


# Data Dictionary Generator Models
class DataDictionaryRequest(BaseModel):
    """数据字典请求"""
    database_name: str = Field(..., description="数据库名称")
    num_tables: int = Field(default=5, description="表数量")


class DataDictionaryResponse(BaseModel):
    """数据字典响应"""
    success: bool
    database_name: str
    num_tables: int
    overview: str
    tables: List[Dict[str, Any]]
    relationships: List[str]
    assumptions: List[str]
    version: str


@router.post("/data/dictionary", response_model=DataDictionaryResponse)
async def generate_data_dictionary(request: DataDictionaryRequest):
    """生成数据字典"""
    try:
        from backend.services.data_dictionary_generator import data_dictionary_generator_service
        result = await data_dictionary_generator_service.generate_data_dictionary(
            request.database_name, request.num_tables
        )
        return DataDictionaryResponse(
            success=True,
            database_name=result["database_name"],
            num_tables=result["num_tables"],
            overview=result.get("overview", ""),
            tables=result.get("tables", []),
            relationships=result.get("relationships", []),
            assumptions=result.get("assumptions", []),
            version=result.get("version", ""),
        )
    except Exception as e:
        logger.error(f"生成数据字典失败: {e}")
        return DataDictionaryResponse(
            success=False, database_name=request.database_name, num_tables=request.num_tables,
            overview="", tables=[], relationships=[], assumptions=[], version=""
        )


# Architecture Document Generator Models
class ArchitectureDocumentRequest(BaseModel):
    """架构文档请求"""
    system_name: str = Field(..., description="系统名称")
    system_type: str = Field(default="web application", description="系统类型")
    num_components: int = Field(default=6, description="组件数量")


class ArchitectureDocumentResponse(BaseModel):
    """架构文档响应"""
    success: bool
    system_name: str
    system_type: str
    num_components: int
    overview: str
    architecture_diagram_description: str
    components: List[Dict[str, Any]]
    data_flow: str
    security_considerations: List[str]
    scalability: str
    monitoring_and_logging: str
    disaster_recovery: str
    deployment_architecture: str
    technology_decisions: List[str]


@router.post("/architecture/document", response_model=ArchitectureDocumentResponse)
async def generate_architecture_document(request: ArchitectureDocumentRequest):
    """生成架构文档"""
    try:
        from backend.services.architecture_document_generator import architecture_document_generator_service
        result = await architecture_document_generator_service.generate_architecture_document(
            request.system_name, request.system_type, request.num_components
        )
        return ArchitectureDocumentResponse(
            success=True,
            system_name=result["system_name"],
            system_type=result["system_type"],
            num_components=result["num_components"],
            overview=result.get("overview", ""),
            architecture_diagram_description=result.get("architecture_diagram_description", ""),
            components=result.get("components", []),
            data_flow=result.get("data_flow", ""),
            security_considerations=result.get("security_considerations", []),
            scalability=result.get("scalability", ""),
            monitoring_and_logging=result.get("monitoring_and_logging", ""),
            disaster_recovery=result.get("disaster_recovery", ""),
            deployment_architecture=result.get("deployment_architecture", ""),
            technology_decisions=result.get("technology_decisions", []),
        )
    except Exception as e:
        logger.error(f"生成架构文档失败: {e}")
        return ArchitectureDocumentResponse(
            success=False, system_name=request.system_name, system_type=request.system_type,
            num_components=request.num_components, overview="", architecture_diagram_description="",
            components=[], data_flow="", security_considerations=[], scalability="",
            monitoring_and_logging="", disaster_recovery="", deployment_architecture="", technology_decisions=[]
        )


# Incident Report Generator Models
class IncidentReportRequest(BaseModel):
    """事件报告请求"""
    incident_title: str = Field(..., description="事件标题")
    severity: str = Field(default="medium", description="严重程度")
    system_name: str = Field(default="", description="系统名称")


class IncidentReportResponse(BaseModel):
    """事件报告响应"""
    success: bool
    incident_title: str
    severity: str
    system_name: str
    incident_id: str
    detected_time: str
    resolved_time: str
    duration: str
    summary: str
    impact: str
    timeline: List[Dict[str, str]]
    root_cause: str
    contributing_factors: List[str]
    resolution_steps: List[str]
    lessons_learned: List[str]
    preventive_measures: List[str]
    action_items: List[Dict[str, str]]
    resources_affected: List[str]
    customer_impact: str


@router.post("/incident/report", response_model=IncidentReportResponse)
async def generate_incident_report(request: IncidentReportRequest):
    """生成事件报告"""
    try:
        from backend.services.incident_report_generator import incident_report_generator_service
        result = await incident_report_generator_service.generate_incident_report(
            request.incident_title, request.severity, request.system_name
        )
        return IncidentReportResponse(
            success=True,
            incident_title=result["incident_title"],
            severity=result["severity"],
            system_name=result["system_name"],
            incident_id=result.get("incident_id", ""),
            detected_time=result.get("detected_time", ""),
            resolved_time=result.get("resolved_time", ""),
            duration=result.get("duration", ""),
            summary=result.get("summary", ""),
            impact=result.get("impact", ""),
            timeline=result.get("timeline", []),
            root_cause=result.get("root_cause", ""),
            contributing_factors=result.get("contributing_factors", []),
            resolution_steps=result.get("resolution_steps", []),
            lessons_learned=result.get("lessons_learned", []),
            preventive_measures=result.get("preventive_measures", []),
            action_items=result.get("action_items", []),
            resources_affected=result.get("resources_affected", []),
            customer_impact=result.get("customer_impact", ""),
        )
    except Exception as e:
        logger.error(f"生成事件报告失败: {e}")
        return IncidentReportResponse(
            success=False, incident_title=request.incident_title, severity=request.severity,
            system_name=request.system_name, incident_id="", detected_time="", resolved_time="",
            duration="", summary="", impact="", timeline=[], root_cause="", contributing_factors=[],
            resolution_steps=[], lessons_learned=[], preventive_measures=[], action_items=[],
            resources_affected=[], customer_impact=""
        )


# Sprint Planning Generator Models
class SprintPlanningRequest(BaseModel):
    """冲刺计划请求"""
    sprint_name: str = Field(..., description="冲刺名称")
    sprint_number: int = Field(..., description="冲刺编号")
    duration_weeks: int = Field(default=2, description="持续周数")
    num_stories: int = Field(default=8, description="用户故事数量")


class SprintPlanningResponse(BaseModel):
    """冲刺计划响应"""
    success: bool
    sprint_name: str
    sprint_number: int
    duration_weeks: int
    num_stories: int
    sprint_goal: str
    start_date: str
    end_date: str
    user_stories: List[Dict[str, Any]]
    capacity_planning: Dict[str, Any]
    risks: List[str]
    dependencies: List[str]
    retrospective_actions: List[str]
    daily_standup_notes: str


@router.post("/sprint/planning", response_model=SprintPlanningResponse)
async def generate_sprint_planning(request: SprintPlanningRequest):
    """生成冲刺计划"""
    try:
        from backend.services.sprint_planning_generator import sprint_planning_generator_service
        result = await sprint_planning_generator_service.generate_sprint_planning(
            request.sprint_name, request.sprint_number, request.duration_weeks, request.num_stories
        )
        return SprintPlanningResponse(
            success=True,
            sprint_name=result["sprint_name"],
            sprint_number=result["sprint_number"],
            duration_weeks=result["duration_weeks"],
            num_stories=result["num_stories"],
            sprint_goal=result.get("sprint_goal", ""),
            start_date=result.get("start_date", ""),
            end_date=result.get("end_date", ""),
            user_stories=result.get("user_stories", []),
            capacity_planning=result.get("capacity_planning", {}),
            risks=result.get("risks", []),
            dependencies=result.get("dependencies", []),
            retrospective_actions=result.get("retrospective_actions", []),
            daily_standup_notes=result.get("daily_standup_notes", ""),
        )
    except Exception as e:
        logger.error(f"生成冲刺计划失败: {e}")
        return SprintPlanningResponse(
            success=False, sprint_name=request.sprint_name, sprint_number=request.sprint_number,
            duration_weeks=request.duration_weeks, num_stories=request.num_stories,
            sprint_goal="", start_date="", end_date="", user_stories=[], capacity_planning={},
            risks=[], dependencies=[], retrospective_actions=[], daily_standup_notes=""
        )


# Release Notes Generator Models
class ReleaseNotesRequest(BaseModel):
    """发布说明请求"""
    product_name: str = Field(..., description="产品名称")
    version: str = Field(..., description="版本号")
    release_date: str = Field(..., description="发布日期")


class ReleaseNotesResponse(BaseModel):
    """发布说明响应"""
    success: bool
    product_name: str
    version: str
    release_date: str
    release_type: str
    overview: str
    new_features: List[Dict[str, str]]
    improvements: List[Dict[str, str]]
    bug_fixes: List[str]
    known_issues: List[str]
    deprecations: List[str]
    breaking_changes: List[str]
    migration_guide: str
    upgrade_notice: str
    download_links: List[str]
    support_information: str


@router.post("/release/notes", response_model=ReleaseNotesResponse)
async def generate_release_notes(request: ReleaseNotesRequest):
    """生成发布说明"""
    try:
        from backend.services.release_notes_generator import release_notes_generator_service
        result = await release_notes_generator_service.generate_release_notes(
            request.product_name, request.version, request.release_date
        )
        return ReleaseNotesResponse(
            success=True,
            product_name=result["product_name"],
            version=result["version"],
            release_date=result["release_date"],
            release_type=result.get("release_type", ""),
            overview=result.get("overview", ""),
            new_features=result.get("new_features", []),
            improvements=result.get("improvements", []),
            bug_fixes=result.get("bug_fixes", []),
            known_issues=result.get("known_issues", []),
            deprecations=result.get("deprecations", []),
            breaking_changes=result.get("breaking_changes", []),
            migration_guide=result.get("migration_guide", ""),
            upgrade_notice=result.get("upgrade_notice", ""),
            download_links=result.get("download_links", []),
            support_information=result.get("support_information", ""),
        )
    except Exception as e:
        logger.error(f"生成发布说明失败: {e}")
        return ReleaseNotesResponse(
            success=False, product_name=request.product_name, version=request.version,
            release_date=request.release_date, release_type="", overview="", new_features=[],
            improvements=[], bug_fixes=[], known_issues=[], deprecations=[], breaking_changes=[],
            migration_guide="", upgrade_notice="", download_links=[], support_information=""
        )


# Service Level Agreement Generator Models
class SLARequest(BaseModel):
    """服务水平协议请求"""
    service_name: str = Field(..., description="服务名称")
    service_type: str = Field(default="SaaS", description="服务类型")
    tier: str = Field(default="standard", description="服务等级")


class SLAResponse(BaseModel):
    """服务水平协议响应"""
    success: bool
    service_name: str
    service_type: str
    tier: str
    effective_date: str
    overview: str
    service_availability: Dict[str, str]
    performance_metrics: List[Dict[str, str]]
    response_times: Dict[str, str]
    support_availability: str
    maintenance_windows: str
    incident_management: str
    credits_and_refunds: str
    limitations_and_exclusions: List[str]
    reporting_and_monitoring: str
    customer_responsibilities: str
    term_and_termination: str


@router.post("/sla/generate", response_model=SLAResponse)
async def generate_sla(request: SLARequest):
    """生成服务水平协议"""
    try:
        from backend.services.service_level_agreement_generator import service_level_agreement_generator_service
        result = await service_level_agreement_generator_service.generate_sla(
            request.service_name, request.service_type, request.tier
        )
        return SLAResponse(
            success=True,
            service_name=result["service_name"],
            service_type=result["service_type"],
            tier=result["tier"],
            effective_date=result.get("effective_date", ""),
            overview=result.get("overview", ""),
            service_availability=result.get("service_availability", {}),
            performance_metrics=result.get("performance_metrics", []),
            response_times=result.get("response_times", {}),
            support_availability=result.get("support_availability", ""),
            maintenance_windows=result.get("maintenance_windows", ""),
            incident_management=result.get("incident_management", ""),
            credits_and_refunds=result.get("credits_and_refunds", ""),
            limitations_and_exclusions=result.get("limitations_and_exclusions", []),
            reporting_and_monitoring=result.get("reporting_and_monitoring", ""),
            customer_responsibilities=result.get("customer_responsibilities", ""),
            term_and_termination=result.get("term_and_termination", ""),
        )
    except Exception as e:
        logger.error(f"生成服务水平协议失败: {e}")
        return SLAResponse(
            success=False, service_name=request.service_name, service_type=request.service_type,
            tier=request.tier, effective_date="", overview="", service_availability={},
            performance_metrics=[], response_times={}, support_availability="", maintenance_windows="",
            incident_management="", credits_and_refunds="", limitations_and_exclusions=[],
            reporting_and_monitoring="", customer_responsibilities="", term_and_termination=""
        )


# Privacy Policy Generator Models
class PrivacyPolicyRequest(BaseModel):
    """隐私政策请求"""
    company_name: str = Field(..., description="公司名称")
    product_name: str = Field(..., description="产品名称")
    jurisdiction: str = Field(default="中国", description="管辖区域")


class PrivacyPolicyResponse(BaseModel):
    """隐私政策响应"""
    success: bool
    company_name: str
    product_name: str
    jurisdiction: str
    effective_date: str
    last_updated: str
    overview: str
    information_collected: List[str]
    how_information_is_used: List[str]
    information_sharing: str
    data_protection: str
    cookies_and_tracking: str
    user_rights: List[str]
    data_retention: str
    children_privacy: str
    international_transfers: str
    policy_changes: str
    contact_information: str
    consent_text: str


@router.post("/policy/privacy", response_model=PrivacyPolicyResponse)
async def generate_privacy_policy(request: PrivacyPolicyRequest):
    """生成隐私政策"""
    try:
        from backend.services.privacy_policy_generator import privacy_policy_generator_service
        result = await privacy_policy_generator_service.generate_privacy_policy(
            request.company_name, request.product_name, request.jurisdiction
        )
        return PrivacyPolicyResponse(
            success=True,
            company_name=result["company_name"],
            product_name=result["product_name"],
            jurisdiction=result["jurisdiction"],
            effective_date=result.get("effective_date", ""),
            last_updated=result.get("last_updated", ""),
            overview=result.get("overview", ""),
            information_collected=result.get("information_collected", []),
            how_information_is_used=result.get("how_information_is_used", []),
            information_sharing=result.get("information_sharing", ""),
            data_protection=result.get("data_protection", ""),
            cookies_and_tracking=result.get("cookies_and_tracking", ""),
            user_rights=result.get("user_rights", []),
            data_retention=result.get("data_retention", ""),
            children_privacy=result.get("children_privacy", ""),
            international_transfers=result.get("international_transfers", ""),
            policy_changes=result.get("policy_changes", ""),
            contact_information=result.get("contact_information", ""),
            consent_text=result.get("consent_text", ""),
        )
    except Exception as e:
        logger.error(f"生成隐私政策失败: {e}")
        return PrivacyPolicyResponse(
            success=False, company_name=request.company_name, product_name=request.product_name,
            jurisdiction=request.jurisdiction, effective_date="", last_updated="", overview="",
            information_collected=[], how_information_is_used=[], information_sharing="", data_protection="",
            cookies_and_tracking="", user_rights=[], data_retention="", children_privacy="",
            international_transfers="", policy_changes="", contact_information="", consent_text=""
        )


# Terms of Service Generator Models
class TermsOfServiceRequest(BaseModel):
    """服务条款请求"""
    company_name: str = Field(..., description="公司名称")
    product_name: str = Field(..., description="产品名称")
    effective_date: str = Field(..., description="生效日期")


class TermsOfServiceResponse(BaseModel):
    """服务条款响应"""
    success: bool
    company_name: str
    product_name: str
    effective_date: str
    overview: str
    acceptance_of_terms: str
    description_of_service: str
    user_obligations: List[str]
    account_terms: str
    payment_terms: str
    intellectual_property: str
    user_content: str
    prohibited_uses: List[str]
    warranties_and_disclaimers: str
    limitation_of_liability: str
    indemnification: str
    termination: str
    governing_law: str
    dispute_resolution: str
    amendments: str
    contact_information: str
    entire_agreement: str


@router.post("/terms/service", response_model=TermsOfServiceResponse)
async def generate_terms_of_service(request: TermsOfServiceRequest):
    """生成服务条款"""
    try:
        from backend.services.terms_of_service_generator import terms_of_service_generator_service
        result = await terms_of_service_generator_service.generate_terms_of_service(
            request.company_name, request.product_name, request.effective_date
        )
        return TermsOfServiceResponse(
            success=True,
            company_name=result["company_name"],
            product_name=result["product_name"],
            effective_date=result["effective_date"],
            overview=result.get("overview", ""),
            acceptance_of_terms=result.get("acceptance_of_terms", ""),
            description_of_service=result.get("description_of_service", ""),
            user_obligations=result.get("user_obligations", []),
            account_terms=result.get("account_terms", ""),
            payment_terms=result.get("payment_terms", ""),
            intellectual_property=result.get("intellectual_property", ""),
            user_content=result.get("user_content", ""),
            prohibited_uses=result.get("prohibited_uses", []),
            warranties_and_disclaimers=result.get("warranties_and_disclaimers", ""),
            limitation_of_liability=result.get("limitation_of_liability", ""),
            indemnification=result.get("indemnification", ""),
            termination=result.get("termination", ""),
            governing_law=result.get("governing_law", ""),
            dispute_resolution=result.get("dispute_resolution", ""),
            amendments=result.get("amendments", ""),
            contact_information=result.get("contact_information", ""),
            entire_agreement=result.get("entire_agreement", ""),
        )
    except Exception as e:
        logger.error(f"生成服务条款失败: {e}")
        return TermsOfServiceResponse(
            success=False, company_name=request.company_name, product_name=request.product_name,
            effective_date=request.effective_date, overview="", acceptance_of_terms="",
            description_of_service="", user_obligations=[], account_terms="", payment_terms="",
            intellectual_property="", user_content="", prohibited_uses=[], warranties_and_disclaimers="",
            limitation_of_liability="", indemnification="", termination="", governing_law="",
            dispute_resolution="", amendments="", contact_information="", entire_agreement=""
        )


# Cookie Policy Generator Models
class CookiePolicyRequest(BaseModel):
    """Cookie政策请求"""
    website_name: str = Field(..., description="网站名称")
    company_name: str = Field(..., description="公司名称")


class CookiePolicyResponse(BaseModel):
    """Cookie政策响应"""
    success: bool
    website_name: str
    company_name: str
    effective_date: str
    overview: str
    what_are_cookies: str
    how_we_use_cookies: List[str]
    types_of_cookies: List[Dict[str, str]]
    third_party_cookies: List[str]
    cookie_purposes: List[str]
    managing_cookies: str
    browser_settings: str
    impact_of_disabling: str
    updates_to_policy: str
    contact_information: str


@router.post("/policy/cookie", response_model=CookiePolicyResponse)
async def generate_cookie_policy(request: CookiePolicyRequest):
    """生成Cookie政策"""
    try:
        from backend.services.cookie_policy_generator import cookie_policy_generator_service
        result = await cookie_policy_generator_service.generate_cookie_policy(
            request.website_name, request.company_name
        )
        return CookiePolicyResponse(
            success=True,
            website_name=result["website_name"],
            company_name=result["company_name"],
            effective_date=result.get("effective_date", ""),
            overview=result.get("overview", ""),
            what_are_cookies=result.get("what_are_cookies", ""),
            how_we_use_cookies=result.get("how_we_use_cookies", []),
            types_of_cookies=result.get("types_of_cookies", []),
            third_party_cookies=result.get("third_party_cookies", []),
            cookie_purposes=result.get("cookie_purposes", []),
            managing_cookies=result.get("managing_cookies", ""),
            browser_settings=result.get("browser_settings", ""),
            impact_of_disabling=result.get("impact_of_disabling", ""),
            updates_to_policy=result.get("updates_to_policy", ""),
            contact_information=result.get("contact_information", ""),
        )
    except Exception as e:
        logger.error(f"生成Cookie政策失败: {e}")
        return CookiePolicyResponse(
            success=False, website_name=request.website_name, company_name=request.company_name,
            effective_date="", overview="", what_are_cookies="", how_we_use_cookies=[],
            types_of_cookies=[], third_party_cookies=[], cookie_purposes=[], managing_cookies="",
            browser_settings="", impact_of_disabling="", updates_to_policy="", contact_information=""
        )


# Accessibility Statement Generator Models
class AccessibilityStatementRequest(BaseModel):
    """无障碍声明请求"""
    website_name: str = Field(..., description="网站名称")
    organization_name: str = Field(..., description="组织名称")
    compliance_level: str = Field(default="WCAG 2.1 AA", description="合规级别")


class AccessibilityStatementResponse(BaseModel):
    """无障碍声明响应"""
    success: bool
    website_name: str
    organization_name: str
    compliance_level: str
    effective_date: str
    commitment_statement: str
    accessibility_features: List[str]
    accessibility_partial_conformance: List[str]
    non_accessible_content: List[str]
    assessment_approach: str
    feedback_mechanism: str
    contact_information: str
    enforcement_procedure: str
    technical_information: str
    compatible_browsers: str
    assistive_technologies: str
    training_materials: str


@router.post("/statement/accessibility", response_model=AccessibilityStatementResponse)
async def generate_accessibility_statement(request: AccessibilityStatementRequest):
    """生成无障碍声明"""
    try:
        from backend.services.accessibility_statement_generator import accessibility_statement_generator_service
        result = await accessibility_statement_generator_service.generate_accessibility_statement(
            request.website_name, request.organization_name, request.compliance_level
        )
        return AccessibilityStatementResponse(
            success=True,
            website_name=result["website_name"],
            organization_name=result["organization_name"],
            compliance_level=result["compliance_level"],
            effective_date=result.get("effective_date", ""),
            commitment_statement=result.get("commitment_statement", ""),
            accessibility_features=result.get("accessibility_features", []),
            accessibility_partial_conformance=result.get("accessibility_partial_conformance", []),
            non_accessible_content=result.get("non_accessible_content", []),
            assessment_approach=result.get("assessment_approach", ""),
            feedback_mechanism=result.get("feedback_mechanism", ""),
            contact_information=result.get("contact_information", ""),
            enforcement_procedure=result.get("enforcement_procedure", ""),
            technical_information=result.get("technical_information", ""),
            compatible_browsers=result.get("compatible_browsers", ""),
            assistive_technologies=result.get("assistive_technologies", ""),
            training_materials=result.get("training_materials", ""),
        )
    except Exception as e:
        logger.error(f"生成无障碍声明失败: {e}")
        return AccessibilityStatementResponse(
            success=False, website_name=request.website_name, organization_name=request.organization_name,
            compliance_level=request.compliance_level, effective_date="", commitment_statement="",
            accessibility_features=[], accessibility_partial_conformance=[], non_accessible_content=[],
            assessment_approach="", feedback_mechanism="", contact_information="", enforcement_procedure="",
            technical_information="", compatible_browsers="", assistive_technologies="", training_materials=""
        )


# Disclaimer Generator Models
class DisclaimerRequest(BaseModel):
    """免责声明请求"""
    content_type: str = Field(..., description="内容类型")
    company_name: str = Field(..., description="公司名称")
    product_name: str = Field(..., description="产品名称")


class DisclaimerResponse(BaseModel):
    """免责声明响应"""
    success: bool
    content_type: str
    company_name: str
    product_name: str
    effective_date: str
    general_disclaimer: str
    accuracy_disclaimer: str
    medical_disclaimer: str
    financial_disclaimer: str
    legal_disclaimer: str
    professional_advice_disclaimer: str
    third_party_links: str
    user_responsibility: str
    limitation_of_liability: str
    indemnification: str
    changes_to_disclaimer: str
    contact_information: str


@router.post("/disclaimer/generate", response_model=DisclaimerResponse)
async def generate_disclaimer(request: DisclaimerRequest):
    """生成免责声明"""
    try:
        from backend.services.disclaimer_generator import disclaimer_generator_service
        result = await disclaimer_generator_service.generate_disclaimer(
            request.content_type, request.company_name, request.product_name
        )
        return DisclaimerResponse(
            success=True,
            content_type=result["content_type"],
            company_name=result["company_name"],
            product_name=result["product_name"],
            effective_date=result.get("effective_date", ""),
            general_disclaimer=result.get("general_disclaimer", ""),
            accuracy_disclaimer=result.get("accuracy_disclaimer", ""),
            medical_disclaimer=result.get("medical_disclaimer", ""),
            financial_disclaimer=result.get("financial_disclaimer", ""),
            legal_disclaimer=result.get("legal_disclaimer", ""),
            professional_advice_disclaimer=result.get("professional_advice_disclaimer", ""),
            third_party_links=result.get("third_party_links", ""),
            user_responsibility=result.get("user_responsibility", ""),
            limitation_of_liability=result.get("limitation_of_liability", ""),
            indemnification=result.get("indemnification", ""),
            changes_to_disclaimer=result.get("changes_to_disclaimer", ""),
            contact_information=result.get("contact_information", ""),
        )
    except Exception as e:
        logger.error(f"生成免责声明失败: {e}")
        return DisclaimerResponse(
            success=False, content_type=request.content_type, company_name=request.company_name,
            product_name=request.product_name, effective_date="", general_disclaimer="",
            accuracy_disclaimer="", medical_disclaimer="", financial_disclaimer="", legal_disclaimer="",
            professional_advice_disclaimer="", third_party_links="", user_responsibility="",
            limitation_of_liability="", indemnification="", changes_to_disclaimer="", contact_information=""
        )


# Human Resources Policy Generator Models
class HRPolicyRequest(BaseModel):
    """人力资源政策请求"""
    company_name: str = Field(..., description="公司名称")
    policy_type: str = Field(..., description="政策类型")
    num_sections: int = Field(default=8, description="章节数量")


class HRPolicyResponse(BaseModel):
    """人力资源政策响应"""
    success: bool
    company_name: str
    policy_type: str
    num_sections: int
    effective_date: str
    purpose: str
    scope: str
    policy_statements: List[Dict[str, Any]]
    procedures: List[str]
    employee_responsibilities: List[str]
    management_responsibilities: str
    compliance_requirements: List[str]
    violation_consequences: str
    review_process: str
    contact_information: str


@router.post("/hr/policy", response_model=HRPolicyResponse)
async def generate_hr_policy(request: HRPolicyRequest):
    """生成人力资源政策"""
    try:
        from backend.services.human_resources_policy_generator import human_resources_policy_generator_service
        result = await human_resources_policy_generator_service.generate_hr_policy(
            request.company_name, request.policy_type, request.num_sections
        )
        return HRPolicyResponse(
            success=True,
            company_name=result["company_name"],
            policy_type=result["policy_type"],
            num_sections=result["num_sections"],
            effective_date=result.get("effective_date", ""),
            purpose=result.get("purpose", ""),
            scope=result.get("scope", ""),
            policy_statements=result.get("policy_statements", []),
            procedures=result.get("procedures", []),
            employee_responsibilities=result.get("employee_responsibilities", []),
            management_responsibilities=result.get("management_responsibilities", ""),
            compliance_requirements=result.get("compliance_requirements", []),
            violation_consequences=result.get("violation_consequences", ""),
            review_process=result.get("review_process", ""),
            contact_information=result.get("contact_information", ""),
        )
    except Exception as e:
        logger.error(f"生成人力资源政策失败: {e}")
        return HRPolicyResponse(
            success=False, company_name=request.company_name, policy_type=request.policy_type,
            num_sections=request.num_sections, effective_date="", purpose="", scope="",
            policy_statements=[], procedures=[], employee_responsibilities=[], management_responsibilities="",
            compliance_requirements=[], violation_consequences="", review_process="", contact_information=""
        )


# Onboarding Checklist Generator Models
class OnboardingChecklistRequest(BaseModel):
    """入职清单请求"""
    job_title: str = Field(..., description="职位名称")
    department: str = Field(..., description="部门")
    employment_type: str = Field(default="full-time", description="雇佣类型")


class OnboardingChecklistResponse(BaseModel):
    """入职清单响应"""
    success: bool
    job_title: str
    department: str
    employment_type: str
    overview: str
    pre_day_one: List[Dict[str, str]]
    day_one: List[str]
    first_week: List[Dict[str, str]]
    first_month: List[Dict[str, str]]
    training_requirements: List[str]
    required_documents: List[str]
    equipment_and_access: List[str]
    key_contacts: List[str]
    team_introductions: List[str]
    goals_for_first_30_days: List[str]
    success_metrics: str


@router.post("/onboarding/checklist", response_model=OnboardingChecklistResponse)
async def generate_onboarding_checklist(request: OnboardingChecklistRequest):
    """生成入职清单"""
    try:
        from backend.services.onboarding_checklist_generator import onboarding_checklist_generator_service
        result = await onboarding_checklist_generator_service.generate_onboarding_checklist(
            request.job_title, request.department, request.employment_type
        )
        return OnboardingChecklistResponse(
            success=True,
            job_title=result["job_title"],
            department=result["department"],
            employment_type=result["employment_type"],
            overview=result.get("overview", ""),
            pre_day_one=result.get("pre_day_one", []),
            day_one=result.get("day_one", []),
            first_week=result.get("first_week", []),
            first_month=result.get("first_month", []),
            training_requirements=result.get("training_requirements", []),
            required_documents=result.get("required_documents", []),
            equipment_and_access=result.get("equipment_and_access", []),
            key_contacts=result.get("key_contacts", []),
            team_introductions=result.get("team_introductions", []),
            goals_for_first_30_days=result.get("goals_for_first_30_days", []),
            success_metrics=result.get("success_metrics", ""),
        )
    except Exception as e:
        logger.error(f"生成入职清单失败: {e}")
        return OnboardingChecklistResponse(
            success=False, job_title=request.job_title, department=request.department,
            employment_type=request.employment_type, overview="", pre_day_one=[], day_one=[],
            first_week=[], first_month=[], training_requirements=[], required_documents=[],
            equipment_and_access=[], key_contacts=[], team_introductions=[], goals_for_first_30_days=[],
            success_metrics=""
        )


# Exit Interview Template Generator Models
class ExitInterviewTemplateRequest(BaseModel):
    """离职面谈模板请求"""
    employee_name: str = Field(..., description="员工姓名")
    department: str = Field(..., description="部门")
    tenure: str = Field(..., description="任职时间")


class ExitInterviewTemplateResponse(BaseModel):
    """离职面谈模板响应"""
    success: bool
    employee_name: str
    department: str
    tenure: str
    interview_date: str
    interviewer: str
    sections: List[Dict[str, Any]]
    opening_questions: List[str]
    reason_for_leaving_questions: List[str]
    job_satisfaction_questions: List[str]
    management_feedback_questions: List[str]
    work_environment_questions: List[str]
    compensation_benefits_questions: List[str]
    career_development_questions: List[str]
    training_questions: List[str]
    recommendations_questions: List[str]
    closing_questions: List[str]
    confidentiality_statement: str
    next_steps: str


@router.post("/hr/exit-interview", response_model=ExitInterviewTemplateResponse)
async def generate_exit_interview_template(request: ExitInterviewTemplateRequest):
    """生成离职面谈模板"""
    try:
        from backend.services.exit_interview_template_generator import exit_interview_template_generator_service
        result = await exit_interview_template_generator_service.generate_exit_interview_template(
            request.employee_name, request.department, request.tenure
        )
        return ExitInterviewTemplateResponse(
            success=True,
            employee_name=result["employee_name"],
            department=result["department"],
            tenure=result["tenure"],
            interview_date=result.get("interview_date", ""),
            interviewer=result.get("interviewer", ""),
            sections=result.get("sections", []),
            opening_questions=result.get("opening_questions", []),
            reason_for_leaving_questions=result.get("reason_for_leaving_questions", []),
            job_satisfaction_questions=result.get("job_satisfaction_questions", []),
            management_feedback_questions=result.get("management_feedback_questions", []),
            work_environment_questions=result.get("work_environment_questions", []),
            compensation_benefits_questions=result.get("compensation_benefits_questions", []),
            career_development_questions=result.get("career_development_questions", []),
            training_questions=result.get("training_questions", []),
            recommendations_questions=result.get("recommendations_questions", []),
            closing_questions=result.get("closing_questions", []),
            confidentiality_statement=result.get("confidentiality_statement", ""),
            next_steps=result.get("next_steps", ""),
        )
    except Exception as e:
        logger.error(f"生成离职面谈模板失败: {e}")
        return ExitInterviewTemplateResponse(
            success=False, employee_name=request.employee_name, department=request.department,
            tenure=request.tenure, interview_date="", interviewer="", sections=[],
            opening_questions=[], reason_for_leaving_questions=[], job_satisfaction_questions=[],
            management_feedback_questions=[], work_environment_questions=[],
            compensation_benefits_questions=[], career_development_questions=[], training_questions=[],
            recommendations_questions=[], closing_questions=[], confidentiality_statement="", next_steps=""
        )


# Job Description Generator Models
class JobDescriptionRequest(BaseModel):
    """职位描述请求"""
    job_title: str = Field(..., description="职位名称")
    department: str = Field(..., description="部门")
    location: str = Field(..., description="工作地点")
    employment_type: str = Field(default="full-time", description="雇佣类型")


class JobDescriptionResponse(BaseModel):
    """职位描述响应"""
    success: bool
    job_title: str
    department: str
    location: str
    employment_type: str
    job_summary: str
    about_company: str
    key_responsibilities: List[str]
    daily_activities: List[str]
    qualifications: Dict[str, Any]
    required_experience: List[str]
    preferred_qualifications: List[str]
    technical_requirements: List[str]
    soft_skills: List[str]
    language_requirements: List[str]
    certifications: List[str]
    compensation_benefits: List[str]
    career_growth: str
    work_environment: str
    diversity_statement: str


@router.post("/hr/job-description", response_model=JobDescriptionResponse)
async def generate_job_description(request: JobDescriptionRequest):
    """生成职位描述"""
    try:
        from backend.services.job_description_generator import job_description_generator_service
        result = await job_description_generator_service.generate_job_description(
            request.job_title, request.department, request.location, request.employment_type
        )
        return JobDescriptionResponse(
            success=True,
            job_title=result["job_title"],
            department=result["department"],
            location=result["location"],
            employment_type=result["employment_type"],
            job_summary=result.get("job_summary", ""),
            about_company=result.get("about_company", ""),
            key_responsibilities=result.get("key_responsibilities", []),
            daily_activities=result.get("daily_activities", []),
            qualifications=result.get("qualifications", {}),
            required_experience=result.get("required_experience", []),
            preferred_qualifications=result.get("preferred_qualifications", []),
            technical_requirements=result.get("technical_requirements", []),
            soft_skills=result.get("soft_skills", []),
            language_requirements=result.get("language_requirements", []),
            certifications=result.get("certifications", []),
            compensation_benefits=result.get("compensation_benefits", []),
            career_growth=result.get("career_growth", ""),
            work_environment=result.get("work_environment", ""),
            diversity_statement=result.get("diversity_statement", ""),
        )
    except Exception as e:
        logger.error(f"生成职位描述失败: {e}")
        return JobDescriptionResponse(
            success=False, job_title=request.job_title, department=request.department,
            location=request.location, employment_type=request.employment_type, job_summary="",
            about_company="", key_responsibilities=[], daily_activities=[], qualifications={},
            required_experience=[], preferred_qualifications=[], technical_requirements=[], soft_skills=[],
            language_requirements=[], certifications=[], compensation_benefits=[], career_growth="",
            work_environment="", diversity_statement=""
        )


# Training Plan Generator Models
class TrainingPlanRequest(BaseModel):
    """培训计划请求"""
    training_title: str = Field(..., description="培训标题")
    target_audience: str = Field(..., description="目标受众")
    duration_hours: int = Field(default=8, description="培训时长")
    num_sessions: int = Field(default=4, description="场次数量")


class TrainingPlanResponse(BaseModel):
    """培训计划响应"""
    success: bool
    training_title: str
    target_audience: str
    duration_hours: int
    num_sessions: int
    overview: str
    objectives: List[str]
    prerequisites: List[str]
    sessions: List[Dict[str, Any]]
    methodology: str
    assessment_methods: List[str]
    resources_required: List[str]
    post_training_support: str
    evaluation_criteria: str
    certification: str
    follow_up_plan: str


@router.post("/training/plan", response_model=TrainingPlanResponse)
async def generate_training_plan(request: TrainingPlanRequest):
    """生成培训计划"""
    try:
        from backend.services.training_plan_generator import training_plan_generator_service
        result = await training_plan_generator_service.generate_training_plan(
            request.training_title, request.target_audience, request.duration_hours, request.num_sessions
        )
        return TrainingPlanResponse(
            success=True,
            training_title=result["training_title"],
            target_audience=result["target_audience"],
            duration_hours=result["duration_hours"],
            num_sessions=result["num_sessions"],
            overview=result.get("overview", ""),
            objectives=result.get("objectives", []),
            prerequisites=result.get("prerequisites", []),
            sessions=result.get("sessions", []),
            methodology=result.get("methodology", ""),
            assessment_methods=result.get("assessment_methods", []),
            resources_required=result.get("resources_required", []),
            post_training_support=result.get("post_training_support", ""),
            evaluation_criteria=result.get("evaluation_criteria", ""),
            certification=result.get("certification", ""),
            follow_up_plan=result.get("follow_up_plan", ""),
        )
    except Exception as e:
        logger.error(f"生成培训计划失败: {e}")
        return TrainingPlanResponse(
            success=False, training_title=request.training_title, target_audience=request.target_audience,
            duration_hours=request.duration_hours, num_sessions=request.num_sessions, overview="",
            objectives=[], prerequisites=[], sessions=[], methodology="", assessment_methods=[],
            resources_required=[], post_training_support="", evaluation_criteria="", certification="", follow_up_plan=""
        )


# Employee Handbook Generator Models
class EmployeeHandbookRequest(BaseModel):
    """员工手册请求"""
    company_name: str = Field(..., description="公司名称")
    industry: str = Field(..., description="行业")
    num_chapters: int = Field(default=10, description="章节数量")


class EmployeeHandbookResponse(BaseModel):
    """员工手册响应"""
    success: bool
    company_name: str
    industry: str
    num_chapters: int
    version: str
    effective_date: str
    introduction: str
    about_company: str
    chapters: List[Dict[str, Any]]
    code_of_conduct: str
    benefits_overview: str
    leave_policies: str
    performance_management: str
    training_development: str
    workplace_safety: str
    it_security: str
    emergency_procedures: str
    contact_directory: str
    acknowledgment_form: str


@router.post("/hr/employee-handbook", response_model=EmployeeHandbookResponse)
async def generate_employee_handbook(request: EmployeeHandbookRequest):
    """生成员工手册"""
    try:
        from backend.services.employee_handbook_generator import employee_handbook_generator_service
        result = await employee_handbook_generator_service.generate_employee_handbook(
            request.company_name, request.industry, request.num_chapters
        )
        return EmployeeHandbookResponse(
            success=True,
            company_name=result["company_name"],
            industry=result["industry"],
            num_chapters=result["num_chapters"],
            version=result.get("version", ""),
            effective_date=result.get("effective_date", ""),
            introduction=result.get("introduction", ""),
            about_company=result.get("about_company", ""),
            chapters=result.get("chapters", []),
            code_of_conduct=result.get("code_of_conduct", ""),
            benefits_overview=result.get("benefits_overview", ""),
            leave_policies=result.get("leave_policies", ""),
            performance_management=result.get("performance_management", ""),
            training_development=result.get("training_development", ""),
            workplace_safety=result.get("workplace_safety", ""),
            it_security=result.get("it_security", ""),
            emergency_procedures=result.get("emergency_procedures", ""),
            contact_directory=result.get("contact_directory", ""),
            acknowledgment_form=result.get("acknowledgment_form", ""),
        )
    except Exception as e:
        logger.error(f"生成员工手册失败: {e}")
        return EmployeeHandbookResponse(
            success=False, company_name=request.company_name, industry=request.industry,
            num_chapters=request.num_chapters, version="", effective_date="", introduction="",
            about_company="", chapters=[], code_of_conduct="", benefits_overview="", leave_policies="",
            performance_management="", training_development="", workplace_safety="", it_security="",
            emergency_procedures="", contact_directory="", acknowledgment_form=""
        )


# Corporate Video Script Generator Models
class CorporateVideoScriptRequest(BaseModel):
    """企业视频脚本请求"""
    video_title: str = Field(..., description="视频标题")
    video_type: str = Field(default="promotional", description="视频类型")
    duration_minutes: int = Field(default=3, description="时长")


class CorporateVideoScriptResponse(BaseModel):
    """企业视频脚本响应"""
    success: bool
    video_title: str
    video_type: str
    duration_minutes: int
    target_audience: str
    key_message: str
    script: List[Dict[str, Any]]
    voiceover_script: str
    music_and_sound_effects: str
    on_screen_text: str
    call_to_action: str
    production_notes: str
    technical_requirements: str


@router.post("/video/corporate-script", response_model=CorporateVideoScriptResponse)
async def generate_corporate_video_script(request: CorporateVideoScriptRequest):
    """生成企业视频脚本"""
    try:
        from backend.services.corporate_video_script_generator import corporate_video_script_generator_service
        result = await corporate_video_script_generator_service.generate_corporate_video_script(
            request.video_title, request.video_type, request.duration_minutes
        )
        return CorporateVideoScriptResponse(
            success=True,
            video_title=result["video_title"],
            video_type=result["video_type"],
            duration_minutes=result["duration_minutes"],
            target_audience=result.get("target_audience", ""),
            key_message=result.get("key_message", ""),
            script=result.get("script", []),
            voiceover_script=result.get("voiceover_script", ""),
            music_and_sound_effects=result.get("music_and_sound_effects", ""),
            on_screen_text=result.get("on_screen_text", ""),
            call_to_action=result.get("call_to_action", ""),
            production_notes=result.get("production_notes", ""),
            technical_requirements=result.get("technical_requirements", ""),
        )
    except Exception as e:
        logger.error(f"生成企业视频脚本失败: {e}")
        return CorporateVideoScriptResponse(
            success=False, video_title=request.video_title, video_type=request.video_type,
            duration_minutes=request.duration_minutes, target_audience="", key_message="", script=[],
            voiceover_script="", music_and_sound_effects="", on_screen_text="", call_to_action="",
            production_notes="", technical_requirements=""
        )


# Social Media Policy Generator Models
class SocialMediaPolicyRequest(BaseModel):
    """社交媒体政策请求"""
    company_name: str = Field(..., description="公司名称")
    num_sections: int = Field(default=8, description="章节数量")


class SocialMediaPolicyResponse(BaseModel):
    """社交媒体政策响应"""
    success: bool
    company_name: str
    num_sections: int
    effective_date: str
    purpose: str
    scope: str
    sections: List[Dict[str, Any]]
    brand_voice_guidelines: str
    content_guidelines: str
    dos_and_donts: Dict[str, List[str]]
    disclosure_requirements: str
    confidentiality: str
    legal_compliance: str
    crisis_management: str
    employee_guidelines: str
    approval_process: str
    monitoring: str
    enforcement: str
    training_requirements: str
    contact_information: str


@router.post("/policy/social-media", response_model=SocialMediaPolicyResponse)
async def generate_social_media_policy(request: SocialMediaPolicyRequest):
    """生成社交媒体政策"""
    try:
        from backend.services.social_media_policy_generator import social_media_policy_generator_service
        result = await social_media_policy_generator_service.generate_social_media_policy(
            request.company_name, request.num_sections
        )
        return SocialMediaPolicyResponse(
            success=True,
            company_name=result["company_name"],
            num_sections=result["num_sections"],
            effective_date=result.get("effective_date", ""),
            purpose=result.get("purpose", ""),
            scope=result.get("scope", ""),
            sections=result.get("sections", []),
            brand_voice_guidelines=result.get("brand_voice_guidelines", ""),
            content_guidelines=result.get("content_guidelines", ""),
            dos_and_donts=result.get("dos_and_donts", {"do": [], "dont": []}),
            disclosure_requirements=result.get("disclosure_requirements", ""),
            confidentiality=result.get("confidentiality", ""),
            legal_compliance=result.get("legal_compliance", ""),
            crisis_management=result.get("crisis_management", ""),
            employee_guidelines=result.get("employee_guidelines", ""),
            approval_process=result.get("approval_process", ""),
            monitoring=result.get("monitoring", ""),
            enforcement=result.get("enforcement", ""),
            training_requirements=result.get("training_requirements", ""),
            contact_information=result.get("contact_information", ""),
        )
    except Exception as e:
        logger.error(f"生成社交媒体政策失败: {e}")
        return SocialMediaPolicyResponse(
            success=False, company_name=request.company_name, num_sections=request.num_sections,
            effective_date="", purpose="", scope="", sections=[], brand_voice_guidelines="",
            content_guidelines="", dos_and_donts={"do": [], "dont": []}, disclosure_requirements="",
            confidentiality="", legal_compliance="", crisis_management="", employee_guidelines="",
            approval_process="", monitoring="", enforcement="", training_requirements="", contact_information=""
        )


# Corporate Communications Template Generator Models
class CorporateCommsTemplateRequest(BaseModel):
    """企业通讯模板请求"""
    comms_type: str = Field(..., description="通讯类型")
    company_name: str = Field(..., description="公司名称")
    urgency: str = Field(default="normal", description="紧急程度")


class CorporateCommsTemplateResponse(BaseModel):
    """企业通讯模板响应"""
    success: bool
    comms_type: str
    company_name: str
    urgency: str
    template_structure: str
    subject_line: str
    header: str
    body_sections: List[Dict[str, str]]
    call_to_action: str
    signature_block: str
    attachments: List[str]
    distribution_list: str
    timing_recommendations: str
    tone_guidance: str
    branding_guidelines: str
    legal_disclaimer: str


@router.post("/comms/corporate-template", response_model=CorporateCommsTemplateResponse)
async def generate_corporate_comms_template(request: CorporateCommsTemplateRequest):
    """生成企业通讯模板"""
    try:
        from backend.services.corporate_comms_template_generator import corporate_comms_template_generator_service
        result = await corporate_comms_template_generator_service.generate_corporate_comms_template(
            request.comms_type, request.company_name, request.urgency
        )
        return CorporateCommsTemplateResponse(
            success=True,
            comms_type=result["comms_type"],
            company_name=result["company_name"],
            urgency=result["urgency"],
            template_structure=result.get("template_structure", ""),
            subject_line=result.get("subject_line", ""),
            header=result.get("header", ""),
            body_sections=result.get("body_sections", []),
            call_to_action=result.get("call_to_action", ""),
            signature_block=result.get("signature_block", ""),
            attachments=result.get("attachments", []),
            distribution_list=result.get("distribution_list", ""),
            timing_recommendations=result.get("timing_recommendations", ""),
            tone_guidance=result.get("tone_guidance", ""),
            branding_guidelines=result.get("branding_guidelines", ""),
            legal_disclaimer=result.get("legal_disclaimer", ""),
        )
    except Exception as e:
        logger.error(f"生成企业通讯模板失败: {e}")
        return CorporateCommsTemplateResponse(
            success=False, comms_type=request.comms_type, company_name=request.company_name,
            urgency=request.urgency, template_structure="", subject_line="", header="",
            body_sections=[], call_to_action="", signature_block="", attachments=[],
            distribution_list="", timing_recommendations="", tone_guidance="", branding_guidelines="",
            legal_disclaimer=""
        )


# Meeting Minutes Template Generator Models
class MeetingMinutesTemplateRequest(BaseModel):
    """会议纪要模板请求"""
    meeting_type: str = Field(..., description="会议类型")
    num_agenda_items: int = Field(default=6, description="议程项数量")


class MeetingMinutesTemplateResponse(BaseModel):
    """会议纪要模板响应"""
    success: bool
    meeting_type: str
    num_agenda_items: int
    document_header: str
    meeting_information: Dict[str, Any]
    agenda_items: List[Dict[str, Any]]
    action_items_summary: List[Dict[str, str]]
    decisions_log: List[str]
    next_meeting: str
    attachments: List[str]
    distribution: str


@router.post("/meeting/minutes-template", response_model=MeetingMinutesTemplateResponse)
async def generate_meeting_minutes_template(request: MeetingMinutesTemplateRequest):
    """生成会议纪要模板"""
    try:
        from backend.services.meeting_minutes_template_generator import meeting_minutes_template_generator_service
        result = await meeting_minutes_template_generator_service.generate_meeting_minutes_template(
            request.meeting_type, request.num_agenda_items
        )
        return MeetingMinutesTemplateResponse(
            success=True,
            meeting_type=result["meeting_type"],
            num_agenda_items=result["num_agenda_items"],
            document_header=result.get("document_header", ""),
            meeting_information=result.get("meeting_information", {}),
            agenda_items=result.get("agenda_items", []),
            action_items_summary=result.get("action_items_summary", []),
            decisions_log=result.get("decisions_log", []),
            next_meeting=result.get("next_meeting", ""),
            attachments=result.get("attachments", []),
            distribution=result.get("distribution", ""),
        )
    except Exception as e:
        logger.error(f"生成会议纪要模板失败: {e}")
        return MeetingMinutesTemplateResponse(
            success=False, meeting_type=request.meeting_type, num_agenda_items=request.num_agenda_items,
            document_header="", meeting_information={}, agenda_items=[], action_items_summary=[],
            decisions_log=[], next_meeting="", attachments=[], distribution=""
        )


# Project Charter Generator Models
class ProjectCharterRequest(BaseModel):
    """项目章程请求"""
    project_name: str = Field(..., description="项目名称")
    project_sponsor: str = Field(..., description="项目发起人")
    project_manager: str = Field(..., description="项目经理")


class ProjectCharterResponse(BaseModel):
    """项目章程响应"""
    success: bool
    project_name: str
    project_sponsor: str
    project_manager: str
    document_version: str
    date: str
    executive_summary: str
    project_background: str
    project_objectives: List[str]
    scope: Dict[str, List[str]]
    deliverables: List[str]
    milestones: List[Dict[str, Any]]
    budget: str
    resources: str
    stakeholders: List[Dict[str, str]]
    constraints: List[str]
    assumptions: List[str]
    risks: List[str]
    governance_structure: str
    communication_plan: str
    approval_requirements: str
    signed_by: List[str]


@router.post("/project/charter", response_model=ProjectCharterResponse)
async def generate_project_charter(request: ProjectCharterRequest):
    """生成项目章程"""
    try:
        from backend.services.project_charter_generator import project_charter_generator_service
        result = await project_charter_generator_service.generate_project_charter(
            request.project_name, request.project_sponsor, request.project_manager
        )
        return ProjectCharterResponse(
            success=True,
            project_name=result["project_name"],
            project_sponsor=result["project_sponsor"],
            project_manager=result["project_manager"],
            document_version=result.get("document_version", ""),
            date=result.get("date", ""),
            executive_summary=result.get("executive_summary", ""),
            project_background=result.get("project_background", ""),
            project_objectives=result.get("project_objectives", []),
            scope=result.get("scope", {"in_scope": [], "out_of_scope": []}),
            deliverables=result.get("deliverables", []),
            milestones=result.get("milestones", []),
            budget=result.get("budget", ""),
            resources=result.get("resources", ""),
            stakeholders=result.get("stakeholders", []),
            constraints=result.get("constraints", []),
            assumptions=result.get("assumptions", []),
            risks=result.get("risks", []),
            governance_structure=result.get("governance_structure", ""),
            communication_plan=result.get("communication_plan", ""),
            approval_requirements=result.get("approval_requirements", ""),
            signed_by=result.get("signed_by", []),
        )
    except Exception as e:
        logger.error(f"生成项目章程失败: {e}")
        return ProjectCharterResponse(
            success=False, project_name=request.project_name, project_sponsor=request.project_sponsor,
            project_manager=request.project_manager, document_version="", date="", executive_summary="",
            project_background="", project_objectives=[], scope={"in_scope": [], "out_of_scope": []},
            deliverables=[], milestones=[], budget="", resources="", stakeholders=[], constraints=[],
            assumptions=[], risks=[], governance_structure="", communication_plan="", approval_requirements="", signed_by=[]
        )


# Status Report Template Generator Models
class StatusReportTemplateRequest(BaseModel):
    """状态报告模板请求"""
    project_name: str = Field(..., description="项目名称")
    report_type: str = Field(default="project status", description="报告类型")
    reporting_period: str = Field(default="weekly", description="报告周期")


class StatusReportTemplateResponse(BaseModel):
    """状态报告模板响应"""
    success: bool
    project_name: str
    report_type: str
    reporting_period: str
    report_date: str
    prepared_by: str
    executive_summary: str
    overall_status: str
    progress_summary: str
    accomplishments_this_period: List[str]
    planned_for_next_period: List[str]
    metrics: List[Dict[str, str]]
    budget_status: str
    timeline_status: str
    resource_status: str
    issues_and_blockers: List[str]
    risks: List[Dict[str, str]]
    changes: List[str]
    stakeholder_engagement: str
    quality_metrics: str
    next_steps: str
    attachments: List[str]


@router.post("/report/status-template", response_model=StatusReportTemplateResponse)
async def generate_status_report_template(request: StatusReportTemplateRequest):
    """生成状态报告模板"""
    try:
        from backend.services.status_report_template_generator import status_report_template_generator_service
        result = await status_report_template_generator_service.generate_status_report_template(
            request.project_name, request.report_type, request.reporting_period
        )
        return StatusReportTemplateResponse(
            success=True,
            project_name=result["project_name"],
            report_type=result["report_type"],
            reporting_period=result["reporting_period"],
            report_date=result.get("report_date", ""),
            prepared_by=result.get("prepared_by", ""),
            executive_summary=result.get("executive_summary", ""),
            overall_status=result.get("overall_status", ""),
            progress_summary=result.get("progress_summary", ""),
            accomplishments_this_period=result.get("accomplishments_this_period", []),
            planned_for_next_period=result.get("planned_for_next_period", []),
            metrics=result.get("metrics", []),
            budget_status=result.get("budget_status", ""),
            timeline_status=result.get("timeline_status", ""),
            resource_status=result.get("resource_status", ""),
            issues_and_blockers=result.get("issues_and_blockers", []),
            risks=result.get("risks", []),
            changes=result.get("changes", []),
            stakeholder_engagement=result.get("stakeholder_engagement", ""),
            quality_metrics=result.get("quality_metrics", ""),
            next_steps=result.get("next_steps", ""),
            attachments=result.get("attachments", []),
        )
    except Exception as e:
        logger.error(f"生成状态报告模板失败: {e}")
        return StatusReportTemplateResponse(
            success=False, project_name=request.project_name, report_type=request.report_type,
            reporting_period=request.reporting_period, report_date="", prepared_by="", executive_summary="",
            overall_status="", progress_summary="", accomplishments_this_period=[], planned_for_next_period=[],
            metrics=[], budget_status="", timeline_status="", resource_status="", issues_and_blockers=[],
            risks=[], changes=[], stakeholder_engagement="", quality_metrics="", next_steps="", attachments=[]
        )
