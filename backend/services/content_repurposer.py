"""
Vox Content Repurposer Service 模块

内容再利用服务
- 将一篇内容改写成不同格式
- 平台格式转换
- 内容长度适配
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class RepurposedContent:
    """再利用后的内容"""
    platform: str
    content_type: str  # tweet_thread, blog_post, short_video, long_video, etc.
    title: str
    content: str
    key_points: List[str]  # 保留的关键点
    adaptations: List[str]  # 做了哪些改编


class ContentRepurposerService:
    """
    内容再利用服务

    将一篇内容改写成不同格式，在不同平台发布
    """

    PLATFORM_FORMATS = {
        "xiaohongshu": {
            "name": "小红书",
            "content_types": ["笔记", "图文", "短视频"],
            "max_length": 1000,
            "style": "轻松友好，有emoji，有标签",
        },
        "tiktok": {
            "name": "抖音",
            "content_types": ["短视频脚本", "直播话术"],
            "max_length": 150,
            "style": "口语化，节奏快，有悬念",
        },
        "official": {
            "name": "公众号",
            "content_types": ["文章", "图文消息"],
            "max_length": 20000,
            "style": "专业深度，有条理",
        },
        "friend_circle": {
            "name": "朋友圈",
            "content_types": ["图文", "短视频"],
            "max_length": 500,
            "style": "生活化，亲切自然",
        },
        "weibo": {
            "name": "微博",
            "content_types": ["推文", "thread"],
            "max_length": 2000,
            "style": "简洁有观点，可带话题",
        },
    }

    def __init__(self):
        self.llm = llm_service

    async def repurpose_content(
        self,
        content: str,
        source_platform: str,
        target_platforms: List[str],
        content_type: str = "auto",
        preserve_key_points: bool = True,
    ) -> List[RepurposedContent]:
        """
        内容的跨平台再利用

        Args:
            content: 原始内容
            source_platform: 来源平台
            target_platforms: 目标平台列表
            content_type: 内容类型 (auto, thread, article, script, etc.)
            preserve_key_points: 是否保留关键点

        Returns:
            List[RepurposedContent]: 改写后的内容列表
        """
        try:
            # 提取关键点
            key_points = await self._extract_key_points(content) if preserve_key_points else []

            # 生成各平台内容
            results = []
            for platform in target_platforms:
                try:
                    repurposed = await self._repurpose_for_platform(
                        content=content,
                        source_platform=source_platform,
                        target_platform=platform,
                        content_type=content_type,
                        key_points=key_points,
                    )
                    results.append(repurposed)
                except Exception as e:
                    logger.warning(f"平台 {platform} 改写失败: {e}")
                    continue

            return results

        except Exception as e:
            logger.error(f"内容再利用失败: {e}")
            return []

    async def _extract_key_points(self, content: str) -> List[str]:
        """提取内容的关键点"""
        prompt = f"""请从以下内容中提取3-5个关键点，这些关键点需要在新内容中保留。

原文：
{content}

请以JSON格式返回：
{{"key_points": ["关键点1", "关键点2", "关键点3"]}}

只返回JSON，不要其他内容："""

        response = self.llm.generate(prompt)

        try:
            result = json.loads(response)
            return result.get("key_points", [])
        except json.JSONDecodeError:
            match = re.search(r'\{.*}', response, re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group())
                    return result.get("key_points", [])
                except:
                    pass
            return []

    async def _repurpose_for_platform(
        self,
        content: str,
        source_platform: str,
        target_platform: str,
        content_type: str,
        key_points: List[str],
    ) -> RepurposedContent:
        """为特定平台改写内容"""
        platform_info = self.PLATFORM_FORMATS.get(target_platform, {})
        platform_name = platform_info.get("name", target_platform)
        style = platform_info.get("style", "自然流畅")
        max_length = platform_info.get("max_length", 1000)

        content_type_hints = {
            "xiaohongshu": "小红书笔记风格",
            "tiktok": "抖音短视频脚本",
            "official": "公众号文章",
            "friend_circle": "朋友圈图文",
            "weibo": "微博推文",
        }

        content_type_hint = content_type_hints.get(target_platform, "")

        key_points_str = "\n".join([f"- {kp}" for kp in key_points]) if key_points else "保留原文核心信息"

        prompt = f"""请将以下内容改写成适合在{platform_name}发布的版本。

原文平台：{source_platform}
目标平台：{platform_name}
目标内容类型：{content_type_hint}

原文内容：
{content}

需要保留的关键点：
{key_points_str}

平台特点：{style}
字数限制：不超过{max_length}字

请以JSON格式返回：
{{
    "title": "标题（如果没有则留空）",
    "content": "改写后的内容",
    "content_type": "实际采用的内容类型",
    "adaptations": ["改编1", "改编2", "改编3"]
}}

只返回JSON，不要其他内容："""

        response = self.llm.generate(prompt)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            match = re.search(r'\{.*}', response, re.DOTALL)
            if match:
                result = json.loads(match.group())
            else:
                result = {
                    "title": "",
                    "content": content[:max_length] if len(content) > max_length else content,
                    "content_type": content_type,
                    "adaptations": ["长度调整"],
                }

        return RepurposedContent(
            platform=target_platform,
            content_type=result.get("content_type", content_type),
            title=result.get("title", ""),
            content=result.get("content", content[:max_length]),
            key_points=key_points,
            adaptations=result.get("adaptations", []),
        )

    def expand_to_thread(
        self,
        content: str,
        platform: str = "weibo",
    ) -> List[str]:
        """
        将内容扩展为 thread

        Args:
            content: 原始内容
            platform: 目标平台

        Returns:
            List[str]: thread 的各条内容
        """
        try:
            prompt = f"""请将以下内容改写为一个thread，每条不超过150字。

原文：
{content}

目标平台：{platform}

请以JSON格式返回（一个数组，每项是一条推文）：
{{"tweets": ["推文1", "推文2", "推文3", ...]}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
                return result.get("tweets", [])
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                if match:
                    try:
                        result = json.loads(match.group())
                        return result.get("tweets", [])
                    except:
                        pass
                return [content]

        except Exception as e:
            logger.error(f"扩展为thread失败: {e}")
            return [content]

    def condense_to_brief(
        self,
        content: str,
        max_length: int = 150,
    ) -> str:
        """
        将内容压缩为简短版本

        Args:
            content: 原始内容
            max_length: 最大长度

        Returns:
            str: 压缩后的内容
        """
        try:
            prompt = f"""请将以下内容压缩到{max_length}字以内，保留核心信息。

原文：
{content}

请直接返回压缩后的内容，不要解释："""

            result = self.llm.generate(prompt)
            return result.strip()

        except Exception as e:
            logger.error(f"压缩内容失败: {e}")
            return content[:max_length]


# 全局实例
content_repurposer_service = ContentRepurposerService()


if __name__ == "__main__":
    import asyncio

    service = ContentRepurposerService()

    async def test():
        content = """
        今天分享一款超级好用的面霜！

        这款面霜质地清爽不油腻，保湿效果一级棒。用了一个月，皮肤明显变好了，毛孔也细腻了很多。

        强烈推荐给和我一样是干皮的姐妹们！
        """

        # 测试跨平台改写
        results = await service.repurpose_content(
            content=content,
            source_platform="xiaohongshu",
            target_platforms=["weibo", "tiktok", "official"],
            preserve_key_points=True,
        )

        print(f"生成了 {len(results)} 个平台的内容：\n")
        for r in results:
            print(f"平台: {r.platform}")
            print(f"类型: {r.content_type}")
            print(f"标题: {r.title}")
            print(f"内容: {r.content[:100]}...")
            print(f"改编: {', '.join(r.adaptations)}")
            print("-" * 40)

        # 测试扩展为 thread
        print("\n扩展为 Thread：")
        tweets = service.expand_to_thread(content)
        for i, tweet in enumerate(tweets, 1):
            print(f"{i}. {tweet}")

        # 测试压缩
        print("\n压缩内容：")
        brief = service.condense_to_brief(content)
        print(brief)

    asyncio.run(test())
