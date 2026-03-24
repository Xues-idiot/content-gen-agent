"""
Vox Copywriter 模块 - 多平台文案生成

负责生成小红书、抖音、公众号、朋友圈等平台的文案
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

from loguru import logger

from backend.agents.planner import ProductInfo, ContentPlan
from backend.services.llm import LLMClient
from backend.prompts import (
    XIAOHONGSHU_PROMPT,
    TIKTOK_PROMPT,
    OFFICIAL_PROMPT,
    FRIEND_CIRCLE_PROMPT,
)


class Platform(Enum):
    """目标平台枚举"""
    XIAOHONGSHU = "xiaohongshu"
    TIKTOK = "tiktok"
    OFFICIAL = "official"
    FRIEND_CIRCLE = "friend_circle"

    def __str__(self):
        return self.value


@dataclass
class CopyResult:
    """文案结果"""
    platform: str
    title: str = ""
    content: str = ""
    script: str = ""
    tags: List[str] = field(default_factory=list)
    image_suggestions: List[str] = field(default_factory=list)
    cta: str = ""  # Call-to-Action 行动号召
    analysis: Dict[str, Any] = field(default_factory=dict)
    raw_output: str = ""
    success: bool = True
    error: str = ""


class Copywriter:
    """文案生成 Agent

    支持多平台文案生成：
    - 小红书：种草笔记
    - 抖音：短视频口播脚本
    - 公众号：长文
    - 朋友圈：简短分享
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    def generate(
        self,
        product: ProductInfo,
        plan: ContentPlan,
        platform: Platform,
    ) -> CopyResult:
        """生成指定平台的文案"""
        logger.info(f"Generating copy for platform: {platform}")

        user_profile = self._format_user_profile(plan)

        if platform == Platform.XIAOHONGSHU:
            return self.write_xiaohongshu(product, plan, user_profile)
        elif platform == Platform.TIKTOK:
            return self.write_tiktok(product, plan, user_profile)
        elif platform == Platform.OFFICIAL:
            return self.write_official(product, plan, user_profile)
        elif platform == Platform.FRIEND_CIRCLE:
            return self.write_friend_circle(product, plan, user_profile)
        else:
            return CopyResult(
                platform=str(platform),
                success=False,
                error=f"Unknown platform: {platform}"
            )

    def generate_all(
        self,
        product: ProductInfo,
        plan: ContentPlan,
    ) -> Dict[Platform, CopyResult]:
        """生成所有平台的文案"""
        results = {}
        for platform in plan.recommended_platforms:
            try:
                p = Platform(platform) if isinstance(platform, str) else platform
                results[p] = self.generate(product, plan, p)
            except Exception as e:
                logger.error(f"Failed to generate copy for {platform}: {e}")
                results[platform] = CopyResult(
                    platform=str(platform),
                    success=False,
                    error=str(e)
                )
        return results

    def write_xiaohongshu(
        self,
        product: ProductInfo,
        plan: ContentPlan,
        user_profile: str,
    ) -> CopyResult:
        """生成小红书文案"""
        prompt = XIAOHONGSHU_PROMPT.format(
            product_name=product.name,
            product_description=product.description,
            selling_points=", ".join(product.selling_points),
            category=product.category,
            user_profile=user_profile,
            content_direction=plan.content_direction,
            tone_of_voice=plan.tone_of_voice,
        )

        response = self.llm.generate(prompt)

        if response.startswith("Error:"):
            return CopyResult(platform="xiaohongshu", success=False, error=response)

        return self._parse_xiaohongshu_response(response)

    def write_tiktok(
        self,
        product: ProductInfo,
        plan: ContentPlan,
        user_profile: str,
    ) -> CopyResult:
        """生成抖音文案"""
        prompt = TIKTOK_PROMPT.format(
            product_name=product.name,
            product_description=product.description,
            selling_points=", ".join(product.selling_points),
            user_profile=user_profile,
            duration=30,
        )

        response = self.llm.generate(prompt)

        if response.startswith("Error:"):
            return CopyResult(platform="tiktok", success=False, error=response)

        return self._parse_tiktok_response(response)

    def write_official(
        self,
        product: ProductInfo,
        plan: ContentPlan,
        user_profile: str,
    ) -> CopyResult:
        """生成公众号文案"""
        prompt = OFFICIAL_PROMPT.format(
            product_name=product.name,
            product_description=product.description,
            selling_points=", ".join(product.selling_points),
            category=product.category,
            user_profile=user_profile,
            content_type="种草文",
        )

        response = self.llm.generate(prompt)

        if response.startswith("Error:"):
            return CopyResult(platform="official", success=False, error=response)

        return self._parse_official_response(response)

    def write_friend_circle(
        self,
        product: ProductInfo,
        plan: ContentPlan,
        user_profile: str,
    ) -> CopyResult:
        """生成朋友圈文案"""
        prompt = FRIEND_CIRCLE_PROMPT.format(
            product_name=product.name,
            product_description=product.description,
            selling_points=", ".join(product.selling_points),
            post_type="好物推荐",
        )

        response = self.llm.generate(prompt)

        if response.startswith("Error:"):
            return CopyResult(platform="friend_circle", success=False, error=response)

        return self._parse_friend_circle_response(response)

    def _format_user_profile(self, plan: ContentPlan) -> str:
        """格式化用户画像"""
        profiles = []
        for i, user in enumerate(plan.target_users, 1):
            profile_str = f"{i}. {user.occupation}"
            if user.pain_points:
                profile_str += f"，痛点：{', '.join(user.pain_points[:2])}"
            if user.buying_motivations:
                profile_str += f"，购买动机：{', '.join(user.buying_motivations[:2])}"
            profiles.append(profile_str)
        return "\n".join(profiles)

    def _parse_xiaohongshu_response(self, response: str) -> CopyResult:
        """解析小红书文案响应"""
        import re
        result = CopyResult(platform="xiaohongshu", raw_output=response)

        title_match = re.search(r"标题：(.+)", response)
        if title_match:
            result.title = title_match.group(1).strip()

        tags_match = re.search(r"标签：([\s\S]+?)(?:配图|$)", response)
        if tags_match:
            result.tags = re.findall(r"#\w+", tags_match.group(1))

        img_match = re.search(r"配图建议：([\s\S]+?)$", response)
        if img_match:
            result.image_suggestions = [
                s.strip() for s in img_match.group(1).strip().split("\n") if s.strip()
            ]

        content_match = re.search(r"正文：([\s\S]+?)标签：", response)
        if content_match:
            result.content = content_match.group(1).strip()
        else:
            content_match = re.search(r"正文：([\s\S]+)$", response)
            if content_match:
                result.content = content_match.group(1).strip()

        # 尝试提取 CTA（小红书也有行动号召）
        cta_match = re.search(r"【?(?:行动号召|结尾|引导)[】]?\s*\n?([\s\S]+?)$", response)
        if cta_match and not result.cta:
            result.cta = cta_match.group(1).strip()

        return result

    def _parse_tiktok_response(self, response: str) -> CopyResult:
        """解析抖音文案响应"""
        import re
        result = CopyResult(platform="tiktok", raw_output=response)

        # 提取开头钩子
        hook_match = re.search(r"【开头钩子】[^\n]*\n([\s\S]+?)(?:\n【|完整脚本|$)", response)
        if hook_match:
            result.title = hook_match.group(1).strip()

        # 提取内容主体
        script_match = re.search(r"【内容主体】([\s\S]+?)(?:【结尾|$)", response)
        if script_match:
            result.script = script_match.group(1).strip()

        # 提取 CTA（行动号召）
        cta_match = re.search(r"【结尾行动号召】\s*\n?([\s\S]+?)$", response)
        if cta_match:
            result.cta = cta_match.group(1).strip()
            result.content = result.title + "\n" + result.script + "\n" + result.cta
        elif result.script:
            result.content = result.title + "\n" + result.script
        else:
            result.content = result.title

        return result

    def _parse_official_response(self, response: str) -> CopyResult:
        """解析公众号文案响应"""
        import re
        result = CopyResult(platform="official", raw_output=response)

        title_match = re.search(r"标题：(.+)", response)
        if title_match:
            result.title = title_match.group(1).strip()

        subtitle_match = re.search(r"副标题：(.+)", response)
        if subtitle_match:
            result.analysis["subtitle"] = subtitle_match.group(1).strip()

        layout_match = re.search(r"排版建议：([\s\S]+?)$", response)
        if layout_match:
            result.analysis["layout"] = layout_match.group(1).strip()

        content_match = re.search(r"正文：([\s\S]+?)(?:排版|$)", response)
        if content_match:
            result.content = content_match.group(1).strip()
        else:
            content_match = re.search(r"正文：([\s\S]+)$", response)
            if content_match:
                result.content = content_match.group(1).strip()

        return result

    def _parse_friend_circle_response(self, response: str) -> CopyResult:
        """解析朋友圈文案响应"""
        import re
        result = CopyResult(platform="friend_circle", raw_output=response)

        content_match = re.search(r"文案：([\s\S]+?)(?:配图|$)", response)
        if content_match:
            result.content = content_match.group(1).strip()

        img_match = re.search(r"配图建议：([\s\S]+?)(?:发布|$)", response)
        if img_match:
            result.image_suggestions = [
                s.strip() for s in img_match.group(1).strip().split("\n") if s.strip()
            ]

        time_match = re.search(r"发布时间建议：(.+)", response)
        if time_match:
            result.analysis["posting_time"] = time_match.group(1).strip()

        # 尝试提取 CTA（朋友圈也有行动号召）
        cta_match = re.search(r"【?(?:行动号召|结尾|引导)[】]?\s*\n?([\s\S]+?)$", response)
        if cta_match:
            result.cta = cta_match.group(1).strip()

        return result


if __name__ == "__main__":
    from backend.agents.planner import ContentPlanner

    planner = ContentPlanner()
    copywriter = Copywriter()

    product = ProductInfo(
        name="智能睡眠枕",
        description="一款基于AI技术的智能枕头",
        selling_points=["改善睡眠质量", "AI智能监测", "个性化调节"],
        target_users=["加班族", "失眠人群"],
        category="家居",
    )

    plan = planner.plan_content(product, ["xiaohongshu"])
    result = copywriter.generate(product, plan, Platform.XIAOHONGSHU)

    print(f"Success: {result.success}")
    print(f"Title: {result.title}")
    print(f"Content: {result.content[:200]}...")
    print(f"Tags: {result.tags}")
