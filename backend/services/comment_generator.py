"""
Vox Comment Generator Service 模块

评论生成服务
- 为帖子生成互动评论
- 生成回复模板
- 评论策略建议
"""

import json
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from loguru import logger

from backend.services.llm import llm_service


@dataclass
class CommentOption:
    """评论选项"""
    text: str  # 评论内容
    tone: str  # 语气风格: friendly, professional, humorous, empathetic
    engagement_score: int  # 预估互动效果 0-100
    emoji_used: bool  # 是否使用emoji


class CommentGeneratorService:
    """
    评论生成服务

    为社交媒体内容生成有价值的评论
    """

    # 不同平台的评论风格
    PLATFORM_STYLES = {
        "xiaohongshu": {
            "name": "小红书",
            "style": "亲切友好, 喜欢用emoji, 语气温暖",
            "length": "10-50字",
        },
        "tiktok": {
            "name": "抖音",
            "style": "简短有趣, 口语化, 容易引发回复",
            "length": "5-30字",
        },
        "weibo": {
            "name": "微博",
            "style": "观点鲜明, 喜欢带话题, 可以犀利",
            "length": "20-100字",
        },
        "official": {
            "name": "公众号",
            "style": "专业有深度, 喜欢引发讨论",
            "length": "20-100字",
        },
        "friend_circle": {
            "name": "朋友圈",
            "style": "生活化, 亲切自然",
            "length": "10-50字",
        },
    }

    # 常用评论模板
    COMMENT_TEMPLATES = {
        "positive": [
            "这个产品看起来很不错！👍",
            "写得真好，收藏了！",
            "感谢分享，学到了很多",
            "支持！期待更多内容",
            "太有用了，已经在用了",
        ],
        "question": [
            "请问这个在哪里可以买到？",
            "想知道更多细节，能详细说说吗？",
            "这个效果真的那么好吗？",
            "有使用教程吗？",
        ],
        "engagement": [
            "同意！+1",
            "确实是这样，我也遇到过",
            "有同感！",
            "同样的经历，顶一下",
        ],
    }

    def __init__(self):
        self.llm = llm_service

    async def generate_comments(
        self,
        content: str = "",
        content_type: str = "post",
        platform: str = "xiaohongshu",
        num_comments: int = 5,
        tone: str = "auto",
    ) -> List[CommentOption]:
        """
        生成评论选项

        Args:
            content: 目标内容（帖子/视频描述）
            content_type: 内容类型: post/video/product/review
            platform: 目标平台
            num_comments: 生成数量
            tone: 语气风格: auto/friendly/professional/humorous/empathetic

        Returns:
            List[CommentOption]: 评论选项列表
        """
        try:
            platform_info = self.PLATFORM_STYLES.get(platform, {})
            platform_name = platform_info.get("name", platform)
            style_hint = platform_info.get("style", "自然友好")
            length_hint = platform_info.get("length", "10-50字")

            tone_hints = {
                "friendly": "亲切友好，像朋友之间的交流",
                "professional": "专业认真，像行业人士的评价",
                "humorous": "幽默风趣，让人会心一笑",
                "empathetic": "共情理解，表达同理心",
                "auto": f"自然{style_hint}",
            }

            prompt = f"""请为以下{platform_name}内容生成 {num_comments} 条评论。

内容类型：{content_type}
目标平台：{platform_name}
评论风格：{tone_hints.get(tone, tone_hints['auto'])}
字数建议：{length_hint}

{"内容：" if content else ""}{content or "（无具体内容，根据平台风格生成通用评论）"}

要求：
1. 评论要自然真实，避免太明显的营销感
2. 不同评论使用不同的切入角度
3. 有的评论可以提出问题增加互动
4. 有的评论可以表达共情
5. 适当使用emoji增加亲和力

请以JSON格式返回：
{{
    "comments": [
        {{
            "text": "评论内容",
            "tone": "friendly/professional/humorous/empathetic",
            "engagement_score": 85,
            "emoji_used": true/false
        }}
    ]
}}

只返回JSON："""

            response = self.llm.generate(prompt)

            try:
                result = json.loads(response)
                comments = result.get("comments", [])
            except json.JSONDecodeError:
                match = re.search(r'\{.*}', response, re.DOTALL)
                if match:
                    try:
                        result = json.loads(match.group())
                        comments = result.get("comments", [])
                    except:
                        comments = self._get_fallback_comments(num_comments)
                else:
                    comments = self._get_fallback_comments(num_comments)

            return [
                CommentOption(
                    text=c.get("text", ""),
                    tone=c.get("tone", "friendly"),
                    engagement_score=c.get("engagement_score", 70),
                    emoji_used=c.get("emoji_used", False),
                )
                for c in comments[:num_comments]
            ]

        except Exception as e:
            logger.error(f"生成评论失败: {e}")
            return self._get_fallback_comments(num_comments)

    def _get_fallback_comments(self, num: int) -> List[Dict]:
        """获取默认评论"""
        templates = self.COMMENT_TEMPLATES
        all_comments = (
            templates["positive"] +
            templates["question"] +
            templates["engagement"]
        )
        random.shuffle(all_comments)
        return [
            {
                "text": all_comments[i % len(all_comments)],
                "tone": "friendly",
                "engagement_score": 70,
                "emoji_used": True,
            }
            for i in range(min(num, len(all_comments)))
        ]

    async def generate_reply(
        self,
        original_comment: str,
        platform: str = "xiaohongshu",
        tone: str = "friendly",
    ) -> str:
        """
        生成回复评论的模板

        Args:
            original_comment: 原始评论
            platform: 平台
            tone: 回复语气

        Returns:
            str: 回复内容
        """
        try:
            prompt = f"""请为以下评论生成一条得体的回复。

原始评论：{original_comment}
目标平台：{platform}
回复风格：{tone}

要求：
1. 回复要亲切自然，不要太官方
2. 可以表示感谢或认同
3. 如果评论有问题，可以温和指出
4. 适当使用emoji
5. 字数控制在20字以内

直接返回回复内容，不要其他内容："""

            reply = self.llm.generate(prompt)
            return reply.strip()

        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            return "感谢回复！😊"

    def get_comment_strategy(self, platform: str) -> Dict[str, Any]:
        """
        获取评论策略建议

        Args:
            platform: 平台

        Returns:
            Dict: 评论策略
        """
        strategies = {
            "xiaohongshu": {
                "best_times": ["12:00-13:00", "18:00-20:00", "21:00-22:00"],
                "response_rate": "高",
                "tips": [
                    "及时回复评论，增加互动",
                    "用emoji增加亲切感",
                    "回复时可以@用户",
                    "鼓励用户收藏和关注",
                ],
                "avoid": [
                    "太商业化的回复",
                    "忽略负面评论",
                    "回复太慢",
                ],
            },
            "tiktok": {
                "best_times": ["12:00-14:00", "18:00-20:00", "21:00-23:00"],
                "response_rate": "中",
                "tips": [
                    "简短有趣的回复更容易火",
                    "可以用热门梗回应",
                    "多使用疑问句引导回复",
                ],
                "avoid": [
                    "太长段的回复",
                    "过于严肃的话题",
                ],
            },
            "weibo": {
                "best_times": ["08:00-09:00", "12:00-13:00", "20:00-21:00"],
                "response_rate": "中",
                "tips": [
                    "观点鲜明的评论更容易引发讨论",
                    "可以带相关话题",
                    "适当使用热门梗",
                ],
                "avoid": [
                    "太中立的评论",
                    "容易引战的内容",
                ],
            },
        }

        return strategies.get(platform, strategies["xiaohongshu"])


# 全局实例
comment_generator_service = CommentGeneratorService()


if __name__ == "__main__":
    import asyncio

    service = CommentGeneratorService()

    async def test():
        # 测试评论生成
        print("=== 评论生成测试 ===")
        comments = await service.generate_comments(
            content="这款面霜真的太好用了！用了两周皮肤明显变好了",
            platform="xiaohongshu",
            num_comments=5,
        )

        for i, c in enumerate(comments, 1):
            print(f"{i}. [{c.tone}] {c.text} (预估互动: {c.engagement_score})")

        # 测试回复生成
        print("\n=== 回复生成测试 ===")
        reply = await service.generate_reply(
            original_comment="这款产品真的好用吗？有点担心质量问题",
            platform="xiaohongshu",
        )
        print(f"回复: {reply}")

        # 测试策略获取
        print("\n=== 评论策略 ===")
        strategy = service.get_comment_strategy("xiaohongshu")
        print(f"最佳时间: {', '.join(strategy['best_times'])}")
        print(f"回复率: {strategy['response_rate']}")
        print("建议:")
        for tip in strategy["tips"]:
            print(f"  - {tip}")

    asyncio.run(test())
