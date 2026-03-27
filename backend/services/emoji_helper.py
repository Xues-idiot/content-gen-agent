"""
Vox Emoji Helper Service 模块

Emoji表情服务
- 平台emoji推荐
- emoji使用建议
- emoji效果分析
"""

from typing import Dict, Any, List
from dataclasses import dataclass

from loguru import logger


class EmojiHelperService:
    """
    Emoji表情助手

    提供emoji相关的辅助功能
    """

    # 平台emoji偏好
    PLATFORM_EMOJI = {
        "xiaohongshu": {
            "style": "温暖亲切",
            "commonly_used": ["😀", "😍", "👍", "✨", "📌", "💄", "🏷️", "🌸", "✅", "💖"],
            "avoid": ["太多连续emoji", "与内容无关的emoji"],
        },
        "tiktok": {
            "style": "年轻活力",
            "commonly_used": ["😂", "🔥", "❤️", "💯", "🙄", "😮", "🤯", "💀", "😭", "🤣"],
            "avoid": ["太正式", "过于可爱"],
        },
        "weibo": {
            "style": "观点鲜明",
            "commonly_used": ["[吃瓜]", "[doge]", "[笑哭]", "[太开心]", "[给心心]", "[星星眼]"],
            "avoid": ["纯图片emoji"],
        },
        "official": {
            "style": "专业克制",
            "commonly_used": ["📊", "📈", "✅", "❌", "📌", "💡", "⚠️"],
            "avoid": ["过多emoji", "表情包"],
        },
    }

    # 情绪emoji映射
    EMOTION_EMOJI = {
        "开心": ["😀", "😄", "🥰", "😘", "😍", "🤩", "🥳", "🎉"],
        "惊讶": ["😮", "😱", "🤯", "😳", "🙀"],
        "满意": ["👍", "✅", "💯", "✨", "🏆"],
        "喜爱": ["❤️", "💖", "💕", "🥰", "😘"],
        "思考": ["🤔", "💡", "📝", "🤓"],
        "无语": ["😂", "🤣", "🙄", "😑"],
        "悲伤": ["😭", "💔", "😢", "🥺"],
    }

    def get_platform_emojis(
        self,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        获取平台emoji偏好

        Args:
            platform: 平台

        Returns:
            Dict: emoji信息
        """
        info = self.PLATFORM_EMOJI.get(platform, self.PLATFORM_EMOJI["xiaohongshu"])
        return {
            "platform": platform,
            "style": info["style"],
            "commonly_used": info["commonly_used"],
            "avoid": info["avoid"],
        }

    def suggest_emojis_for_content(
        self,
        content_type: str,
        platform: str = "xiaohongshu",
        num: int = 5,
    ) -> List[str]:
        """
        为内容推荐emoji

        Args:
            content_type: 内容类型
            platform: 平台
            num: 返回数量

        Returns:
            List[str]: 推荐的emoji
        """
        content_emojis = {
            "种草": ["💖", "✨", "👍", "📌", "💄"],
            "测评": ["📊", "💯", "👍", "✅", "🤔"],
            "教程": ["📝", "💡", "✅", "👍", "📌"],
            "日常": ["😀", "✨", "🌸", "💕", "🥰"],
            "好物推荐": ["❤️", "😍", "👍", "✨", "💖"],
            "分享": ["😀", "✨", "💕", "🌸", "👍"],
        }

        emojis = content_emojis.get(content_type, ["✨", "👍", "💖", "😀", "😍"])
        platform_preferred = self.PLATFORM_EMOJI.get(platform, {}).get("commonly_used", [])

        # 优先使用平台偏好的emoji
        result = []
        for e in emojis:
            if len(result) >= num:
                break
            if e in platform_preferred or e not in result:
                result.append(e)

        return result[:num]

    def analyze_emoji_usage(
        self,
        content: str,
    ) -> Dict[str, Any]:
        """
        分析内容中emoji使用情况

        Args:
            content: 内容

        Returns:
            Dict: 分析结果
        """
        emoji_count = sum(1 for c in content if ord(c) > 127000)
        emoji_list = [c for c in content if ord(c) > 127000]

        # 简单分析
        analysis = {
            "emoji_count": emoji_count,
            "emoji_list": list(set(emoji_list))[:10],
            "usage_level": "高" if emoji_count > 10 else ("中" if emoji_count > 3 else "低"),
            "suggestions": [],
        }

        if emoji_count > 15:
            analysis["suggestions"].append("emoji使用过多，可能影响阅读")
        elif emoji_count == 0:
            analysis["suggestions"].append("建议添加适量emoji增加亲和力")

        return analysis


# 全局实例
emoji_helper_service = EmojiHelperService()


if __name__ == "__main__":
    service = EmojiHelperService()

    print("=== 小红书 Emoji ===")
    info = service.get_platform_emojis("xiaohongshu")
    print(f"风格: {info['style']}")
    print(f"常用: {''.join(info['commonly_used'][:5])}")

    print("\n=== 内容推荐 Emoji ===")
    emojis = service.suggest_emojis_for_content("种草", "xiaohongshu")
    print(f"种草类内容: {''.join(emojis)}")

    print("\n=== Emoji 使用分析 ===")
    result = service.analyze_emoji_usage("这款面霜太好用了😀😍✨推荐给大家！")
    print(f"emoji数量: {result['emoji_count']}")
    print(f"使用水平: {result['usage_level']}")
