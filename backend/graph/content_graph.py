"""
Vox Content Graph - LangGraph 编排

内容生成管道的状态管理和流程编排
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal
from enum import Enum

from loguru import logger


class WorkflowState(str, Enum):
    """工作流状态"""
    IDLE = "idle"
    PLANNING = "planning"
    WRITING = "writing"
    REVIEWING = "reviewing"
    GENERATING_IMAGES = "generating_images"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ContentState:
    """内容生成状态"""
    # 输入
    product_name: str = ""
    product_description: str = ""
    selling_points: List[str] = field(default_factory=list)
    target_users: List[str] = field(default_factory=list)
    category: str = ""
    platforms: List[str] = field(default_factory=list)

    # 中间状态
    state: WorkflowState = WorkflowState.IDLE
    progress: float = 0.0  # 0-100

    # 规划结果
    content_plan: Optional[Dict] = None

    # 文案结果
    copy_results: Dict[str, Any] = field(default_factory=dict)

    # 审核结果
    review_results: Dict[str, Any] = field(default_factory=dict)

    # 图片建议
    image_suggestions: Dict[str, List[str]] = field(default_factory=dict)

    # 最终结果
    final_content: Dict[str, Any] = field(default_factory=dict)

    # 错误
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value if isinstance(self.state, Enum) else self.state,
            "progress": self.progress,
            "product_name": self.product_name,
            "copy_results": self.copy_results,
            "review_results": self.review_results,
            "final_content": self.final_content,
            "errors": self.errors,
        }


class ContentGraph:
    """
    内容生成图

    编排以下流程：
    1. 规划 (Planner) - 分析产品和用户，确定内容方向
    2. 写作 (Copywriter) - 生成各平台文案
    3. 审核 (Reviewer) - 检查文案质量和违规词
    4. 图片 (ImageGenerator) - 生成/推荐配图
    5. 导出 (Exporter) - 导出最终结果
    """

    def __init__(self):
        self.state = ContentState()

    def reset(self):
        """重置状态"""
        self.state = ContentState()

    def run(self, product_info: Dict) -> ContentState:
        """
        运行完整的内容生成流程

        Args:
            product_info: 产品信息字典

        Returns:
            ContentState: 最终状态
        """
        logger.info("Starting content generation workflow")

        # 初始化输入
        self.state.product_name = product_info.get("name", "")
        self.state.product_description = product_info.get("description", "")
        self.state.selling_points = product_info.get("selling_points", [])
        self.state.target_users = product_info.get("target_users", [])
        self.state.category = product_info.get("category", "")
        self.state.platforms = product_info.get("platforms", ["xiaohongshu"])

        try:
            # Step 1: 规划
            self._planning_step()
            if self.state.errors:
                self.state.state = WorkflowState.FAILED
                return self.state

            # Step 2: 写作
            self._writing_step()
            if self.state.errors:
                self.state.state = WorkflowState.FAILED
                return self.state

            # Step 3: 审核
            self._reviewing_step()

            # Step 4: 图片
            self._image_step()

            # Step 5: 导出
            self._export_step()

            self.state.state = WorkflowState.COMPLETED
            self.state.progress = 100.0
            logger.info("Content generation workflow completed")

        except Exception as e:
            logger.error(f"Workflow error: {e}")
            self.state.errors.append(str(e))
            self.state.state = WorkflowState.FAILED

        return self.state

    def _planning_step(self):
        """规划步骤"""
        logger.info("Step 1: Planning content")
        self.state.state = WorkflowState.PLANNING
        self.state.progress = 10.0

        from backend.agents.planner import ContentPlanner, ProductInfo

        planner = ContentPlanner()

        product = ProductInfo(
            name=self.state.product_name,
            description=self.state.product_description,
            selling_points=self.state.selling_points,
            target_users=self.state.target_users,
            category=self.state.category,
        )

        plan = planner.plan_content(product, self.state.platforms)

        self.state.content_plan = {
            "content_direction": plan.content_direction,
            "key_themes": plan.key_themes,
            "tone_of_voice": plan.tone_of_voice,
            "recommended_platforms": plan.recommended_platforms,
            "content_ratio": plan.content_ratio,
        }

        logger.info(f"Planning completed: {plan.content_direction}")

    def _writing_step(self):
        """写作步骤"""
        logger.info("Step 2: Writing copy")
        self.state.state = WorkflowState.WRITING
        self.state.progress = 40.0

        from backend.agents.planner import ProductInfo, ContentPlan
        from backend.agents.copywriter import Copywriter, Platform

        planner = Copywriter()

        product = ProductInfo(
            name=self.state.product_name,
            description=self.state.product_description,
            selling_points=self.state.selling_points,
            target_users=self.state.target_users,
            category=self.state.category,
        )

        # 临时创建 plan
        plan = ContentPlan(
            product=product,
            target_users=[],
            content_direction=self.state.content_plan.get("content_direction", ""),
            key_themes=self.state.content_plan.get("key_themes", []),
            tone_of_voice=self.state.content_plan.get("tone_of_voice", ""),
            recommended_platforms=self.state.platforms,
        )

        results = planner.generate_all(product, plan)

        self.state.copy_results = {}
        for platform, result in results.items():
            platform_key = str(platform)
            self.state.copy_results[platform_key] = {
                "title": result.title,
                "content": result.content,
                "script": result.script,
                "tags": result.tags,
                "image_suggestions": result.image_suggestions,
                "success": result.success,
            }

        logger.info(f"Writing completed for {len(self.state.copy_results)} platforms")

    def _reviewing_step(self):
        """审核步骤"""
        logger.info("Step 3: Reviewing content")
        self.state.state = WorkflowState.REVIEWING
        self.state.progress = 60.0

        from backend.agents.reviewer import Reviewer

        reviewer = Reviewer()

        self.state.review_results = {}
        for platform, copy_data in self.state.copy_results.items():
            content = copy_data.get("content", "")
            if content:
                review = reviewer.review_quality(content)
                self.state.review_results[platform] = {
                    "passed": review.passed,
                    "quality_score": review.quality_score,
                    "violations": [
                        {"word": v.word, "suggestion": v.suggestion}
                        for v in review.violations
                    ],
                    "suggestions": review.suggestions,
                }

        logger.info("Reviewing completed")

    def _image_step(self):
        """图片步骤"""
        logger.info("Step 4: Generating image suggestions")
        self.state.state = WorkflowState.GENERATING_IMAGES
        self.state.progress = 80.0

        from backend.tools.image_gen import ImageGenerator

        generator = ImageGenerator()

        self.state.image_suggestions = {}
        for platform in self.state.platforms:
            suggestions = generator.suggest_images(
                product_name=self.state.product_name,
                product_category=self.state.category,
                platform=platform,
            )
            self.state.image_suggestions[platform] = [
                {"type": s.type, "description": s.description, "prompt": s.prompt}
                for s in suggestions
            ]

        logger.info("Image suggestions generated")

    def _export_step(self):
        """导出步骤"""
        logger.info("Step 5: Exporting content")
        self.state.state = WorkflowState.EXPORTING

        self.state.final_content = {
            "product": {
                "name": self.state.product_name,
                "description": self.state.product_description,
                "selling_points": self.state.selling_points,
            },
            "content_plan": self.state.content_plan,
            "copies": {},
        }

        for platform, copy_data in self.state.copy_results.items():
            review = self.state.review_results.get(platform, {})
            images = self.state.image_suggestions.get(platform, [])

            self.state.final_content["copies"][platform] = {
                "copy": copy_data,
                "review": review,
                "images": images,
            }

        logger.info("Export completed")


if __name__ == "__main__":
    # 测试
    graph = ContentGraph()

    product_info = {
        "name": "智能睡眠枕",
        "description": "一款基于AI技术的智能枕头",
        "selling_points": ["改善睡眠质量", "AI智能监测", "个性化调节"],
        "target_users": ["加班族", "失眠人群"],
        "category": "家居",
        "platforms": ["xiaohongshu", "tiktok"],
    }

    result = graph.run(product_info)

    print(f"State: {result.state}")
    print(f"Progress: {result.progress}")
    print(f"Errors: {result.errors}")
    print(f"Final content keys: {list(result.final_content.keys())}")
