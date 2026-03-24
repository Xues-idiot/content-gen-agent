"""
Vox Copywriter 模块 - 多平台文案生成

负责生成小红书、抖音、公众号、朋友圈等平台的文案
"""

import re
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

# 预编译的正则表达式（避免重复编译）
_RE_TITLE = re.compile(r"标题：(.+)")
_RE_TAGS = re.compile(r"标签：([\s\S]+?)(?:配图|$)")
_RE_IMAGE_SUGGESTION = re.compile(r"配图建议：([\s\S]+?)$")
_RE_CONTENT_XHS = re.compile(r"正文：([\s\S]+?)标签：")
_RE_CONTENT_XHS_FALLBACK = re.compile(r"正文：([\s\S]+)$")
_RE_CTA = re.compile(r"【?(?:行动号召|结尾|引导)[】]?\s*\n?([\s\S]+?)$")
_RE_HOOK = re.compile(r"【开头钩子】[^\n]*\n([\s\S]+?)(?:\n【|完整脚本|$)")
_RE_SCRIPT = re.compile(r"【内容主体】([\s\S]+?)(?:【结尾|$)")
_RE_CTA_TIKTOK = re.compile(r"【结尾行动号召】\s*\n?([\s\S]+?)$")
_RE_SUBTITLE = re.compile(r"副标题：(.+)")
_RE_LAYOUT = re.compile(r"排版建议：([\s\S]+?)$")
_RE_CONTENT_OFFICIAL = re.compile(r"正文：([\s\S]+?)(?:排版|$)")
_RE_CONTENT_OFFICIAL_FALLBACK = re.compile(r"正文：([\s\S]+)$")
_RE_CONTENT_FC = re.compile(r"文案：([\s\S]+?)(?:配图|$)")
_RE_POST_TIME = re.compile(r"发布时间建议：(.+)")


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

    def regenerate(
        self,
        product: ProductInfo,
        plan: ContentPlan,
        platform: Platform,
    ) -> CopyResult:
        """重新生成指定平台的文案（保留其他平台结果）"""
        logger.info(f"Regenerating copy for platform: {platform}")
        try:
            return self.generate(product, plan, platform)
        except Exception as e:
            logger.error(f"Failed to regenerate copy for {platform}: {e}")
            return CopyResult(
                platform=str(platform),
                success=False,
                error=str(e)
            )

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
        result = CopyResult(platform="xiaohongshu", raw_output=response)

        title_match = _RE_TITLE.search(response)
        if title_match:
            result.title = title_match.group(1).strip()

        tags_match = _RE_TAGS.search(response)
        if tags_match:
            result.tags = re.findall(r"#\w+", tags_match.group(1))

        img_match = _RE_IMAGE_SUGGESTION.search(response)
        if img_match:
            result.image_suggestions = [
                s.strip() for s in img_match.group(1).strip().split("\n") if s.strip()
            ]

        content_match = _RE_CONTENT_XHS.search(response)
        if content_match:
            result.content = content_match.group(1).strip()
        else:
            content_match = _RE_CONTENT_XHS_FALLBACK.search(response)
            if content_match:
                result.content = content_match.group(1).strip()

        # 尝试提取 CTA（小红书也有行动号召）
        cta_match = _RE_CTA.search(response)
        if cta_match and not result.cta:
            result.cta = cta_match.group(1).strip()

        return result

    def _parse_tiktok_response(self, response: str) -> CopyResult:
        """解析抖音文案响应"""
        result = CopyResult(platform="tiktok", raw_output=response)

        # 提取开头钩子
        hook_match = _RE_HOOK.search(response)
        if hook_match:
            result.title = hook_match.group(1).strip()

        # 提取内容主体
        script_match = _RE_SCRIPT.search(response)
        if script_match:
            result.script = script_match.group(1).strip()

        # 提取 CTA（行动号召）
        cta_match = _RE_CTA_TIKTOK.search(response)
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
        result = CopyResult(platform="official", raw_output=response)

        title_match = _RE_TITLE.search(response)
        if title_match:
            result.title = title_match.group(1).strip()

        subtitle_match = _RE_SUBTITLE.search(response)
        if subtitle_match:
            result.analysis["subtitle"] = subtitle_match.group(1).strip()

        layout_match = _RE_LAYOUT.search(response)
        if layout_match:
            result.analysis["layout"] = layout_match.group(1).strip()

        content_match = _RE_CONTENT_OFFICIAL.search(response)
        if content_match:
            result.content = content_match.group(1).strip()
        else:
            content_match = _RE_CONTENT_OFFICIAL_FALLBACK.search(response)
            if content_match:
                result.content = content_match.group(1).strip()

        return result

    def _parse_friend_circle_response(self, response: str) -> CopyResult:
        """解析朋友圈文案响应"""
        result = CopyResult(platform="friend_circle", raw_output=response)

        content_match = _RE_CONTENT_FC.search(response)
        if content_match:
            result.content = content_match.group(1).strip()

        img_match = _RE_IMAGE_SUGGESTION.search(response)
        if img_match:
            result.image_suggestions = [
                s.strip() for s in img_match.group(1).strip().split("\n") if s.strip()
            ]

        time_match = _RE_POST_TIME.search(response)
        if time_match:
            result.analysis["posting_time"] = time_match.group(1).strip()

        # 尝试提取 CTA（朋友圈也有行动号召）
        cta_match = _RE_CTA.search(response)
        if cta_match:
            result.cta = cta_match.group(1).strip()

        return result

    def generate_style_variations(
        self,
        product: ProductInfo,
        platform: str,
        base_content: str,
        styles: Optional[List[str]] = None,
    ) -> List[Dict[str, str]]:
        """
        生成多种风格的文案变体

        Args:
            product: 产品信息
            platform: 目标平台
            base_content: 基础文案
            styles: 风格列表

        Returns:
            list: 文案变体列表
        """
        if styles is None:
            styles = ["formal", "casual", "humorous", "professional"]

        variations = []

        style_prompts = {
            "formal": f"将以下文案改写为正式风格：\n{base_content}",
            "casual": f"将以下文案改写为轻松随意风格：\n{base_content}",
            "humorous": f"将以下文案改写为幽默风趣风格：\n{base_content}",
            "professional": f"将以下文案改写为专业严谨风格：\n{base_content}",
            "emotional": f"将以下文案改写为情感化风格：\n{base_content}",
            "storytelling": f"将以下文案改写为故事叙述风格：\n{base_content}",
        }

        for style in styles:
            if style in style_prompts:
                response = self.llm.generate(style_prompts[style])
                variations.append({
                    "style": style,
                    "content": response if not response.startswith("Error:") else base_content,
                })

        return variations

    def generate_ab_copies(
        self,
        product: ProductInfo,
        platform: str,
        num_variants: int = 3,
    ) -> List[CopyResult]:
        """
        生成A/B测试用的多个文案版本

        Args:
            product: 产品信息
            platform: 目标平台
            num_variants: 变体数量

        Returns:
            list: 多个文案结果
        """
        results = []

        # 生成多个不同角度的文案
        angles = [
            ("痛点解决", "从用户痛点出发，强调产品如何解决问题"),
            ("产品测评", "客观介绍产品特点和使用体验"),
            ("好物推荐", "以推荐角度分享产品亮点"),
            ("场景化", "描述具体使用场景，让用户产生代入感"),
            ("对比", "通过对比突显产品优势"),
        ]

        for i in range(min(num_variants, len(angles))):
            angle_name, angle_desc = angles[i]

            prompt = f"""为{platform}平台生成一款{product.name}的文案。

产品信息：
- 名称：{product.name}
- 描述：{product.description}
- 卖点：{', '.join(product.selling_points)}

内容角度：{angle_desc}

请生成包含标题、正文、标签的完整文案。"""

            response = self.llm.generate(prompt)

            if response.startswith("Error:"):
                results.append(CopyResult(
                    platform=platform,
                    success=False,
                    error=response,
                    analysis={"angle": angle_name},
                ))
            else:
                result = self._parse_friend_circle_response(response) if platform == "friend_circle" else \
                         self._parse_xiaohongshu_response(response) if platform == "xiaohongshu" else \
                         self._parse_official_response(response)
                result.analysis["angle"] = angle_name
                results.append(result)

        return results

    def regenerate_with_feedback(
        self,
        original: CopyResult,
        feedback: str,
        product: ProductInfo,
    ) -> CopyResult:
        """
        根据反馈重新生成文案

        Args:
            original: 原始文案结果
            feedback: 改进反馈
            product: 产品信息

        Returns:
            CopyResult: 重新生成的文案
        """
        prompt = f"""请根据以下反馈改进文案。

原始文案：
标题：{original.title}
正文：{original.content}
标签：{', '.join(original.tags)}

改进反馈：
{feedback}

产品信息：
- 名称：{product.name}
- 描述：{product.description}
- 卖点：{', '.join(product.selling_points)}

请生成改进后的完整文案，包含标题、正文、标签。"""

        response = self.llm.generate(prompt)

        if response.startswith("Error:"):
            return CopyResult(
                platform=original.platform,
                success=False,
                error=response,
            )

        result = self._parse_friend_circle_response(response) if original.platform == "friend_circle" else \
                 self._parse_xiaohongshu_response(response) if original.platform == "xiaohongshu" else \
                 self._parse_official_response(response)

        result.analysis["regenerated_from"] = original.raw_output[:100] if original.raw_output else ""
        result.analysis["feedback"] = feedback

        return result


# 季节性文案模板
SEASONAL_TEMPLATES = {
    "spring": {
        "name": "春季",
        "keywords": ["春暖花开", "踏青", "春日", "新品"],
        "themes": ["焕新", "清新", "活力", "生长"],
    },
    "summer": {
        "name": "夏季",
        "keywords": ["清凉", "防晒", "海边", "暑假"],
        "themes": ["解暑", "清爽", "热情", "活力"],
    },
    "autumn": {
        "name": "秋季",
        "keywords": ["秋风", "落叶", "丰收", "中秋"],
        "themes": ["温暖", "收获", "舒适", "慵懒"],
    },
    "winter": {
        "name": "冬季",
        "keywords": ["寒冷", "保暖", "年终", "圣诞", "新年"],
        "themes": ["温暖", "温馨", "年终", "团圆"],
    },
    "festival": {
        "name": "节日通用",
        "keywords": ["优惠", "送礼", "庆祝", "限时"],
        "themes": ["送礼", "优惠", "限定", "庆典"],
    },
}


@dataclass
class SeasonalCopy:
    """季节性文案"""
    season: str
    theme: str
    title: str
    content: str
    hashtags: List[str]


class SeasonalCopywriter:
    """
    季节性文案生成器

    根据不同季节和节日生成应景的营销文案
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.templates = SEASONAL_TEMPLATES
        self.llm = llm_client or LLMClient()

    def generate_seasonal_copy(
        self,
        product: ProductInfo,
        platform: str,
        season: str = "spring",
        festival: str = "",
    ) -> SeasonalCopy:
        """
        生成季节性文案

        Args:
            product: 产品信息
            platform: 目标平台
            season: 季节 (spring/summer/autumn/winter)
            festival: 节日名称 (可选)

        Returns:
            SeasonalCopy: 季节性文案
        """
        template = self.templates.get(season, self.templates["spring"])

        # 构建季节性提示
        seasonal_context = f"""
现在是{template['name']}，推荐使用以下季节性元素：
- 关键词：{', '.join(template['keywords'])}
- 主题：{', '.join(template['themes'])}
{f'- 节日：{festival}' if festival else ''}
"""

        prompt = f"""为{platform}平台生成一款{product.name}的{template['name']}季节性文案。

产品信息：
- 名称：{product.name}
- 描述：{product.description}
- 卖点：{', '.join(product.selling_points)}

{seasonal_context}

请生成包含标题、正文、标签的完整文案，体现季节感。"""

        response = self.llm.generate(prompt)

        # 使用预编译的正则解析
        title_match = _RE_TITLE.search(response)
        title = title_match.group(1).strip() if title_match else f"{product.name} - {template['name']}推荐"

        tags_match = _RE_TAGS.search(response)
        tags = re.findall(r"#\w+", tags_match.group(1)) if tags_match else []

        content_match = re.search(r"正文：([\s\S]+?)(?:标签|$)", response)
        content = content_match.group(1).strip() if content_match else response

        return SeasonalCopy(
            season=season,
            theme=festival or template["name"],
            title=title,
            content=content,
            hashtags=tags,
        )

    def adapt_to_season(
        self,
        original_content: str,
        original_platform: str,
        target_season: str,
    ) -> str:
        """
        将现有文案适配到不同季节

        Args:
            original_content: 原始文案
            original_platform: 原始平台
            target_season: 目标季节

        Returns:
            str: 适配后的文案
        """
        template = self.templates.get(target_season, self.templates["spring"])

        prompt = f"""将以下{template['name']}文案进行季节性改编：

原始文案：
{original_content}

目标季节：{template['name']}
季节关键词：{', '.join(template['keywords'])}

请保持文案核心信息不变，只调整季节性表达。"""

        response = self.llm.generate(prompt)

        return response if not response.startswith("Error:") else original_content


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
