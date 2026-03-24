"""
Vox Exporter 模块 - 导出功能

负责将内容导出为不同格式
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
import base64


class ExportFormat(Enum):
    """导出格式"""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    TEXT = "text"


@dataclass
class ExportResult:
    """导出结果"""
    success: bool
    content: str = ""
    file_path: str = ""
    error: str = ""


@dataclass
class ContentTemplate:
    """内容模板"""
    id: str
    name: str
    platform: str
    content: str
    tags: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    usage_count: int = 0


class TemplateStorage:
    """模板存储管理器"""

    def __init__(self):
        self._templates: Dict[str, List[ContentTemplate]] = {}

    def save_template(self, template: ContentTemplate) -> bool:
        """保存模板"""
        try:
            if template.platform not in self._templates:
                self._templates[template.platform] = []
            self._templates[template.platform].append(template)
            return True
        except Exception:
            return False

    def get_templates(self, platform: str) -> List[ContentTemplate]:
        """获取平台的所有模板"""
        return self._templates.get(platform, [])

    def get_all_templates(self) -> Dict[str, List[ContentTemplate]]:
        """获取所有模板"""
        return self._templates

    def delete_template(self, platform: str, template_id: str) -> bool:
        """删除模板"""
        if platform in self._templates:
            self._templates[platform] = [
                t for t in self._templates[platform] if t.id != template_id
            ]
            return True
        return False

    def increment_usage(self, platform: str, template_id: str) -> bool:
        """增加模板使用次数"""
        if platform in self._templates:
            for t in self._templates[platform]:
                if t.id == template_id:
                    t.usage_count += 1
                    return True
        return False


# 全局模板存储实例
_template_storage = TemplateStorage()


class Exporter:
    """
    导出 Agent

    支持多种格式导出：
    - JSON: 完整数据结构
    - Markdown: 适合文档展示
    - HTML: 适合网页展示
    - Text: 纯文本格式
    """

    def export_json(self, content: Dict[str, Any]) -> ExportResult:
        """导出为 JSON 格式"""
        try:
            json_str = json.dumps(content, ensure_ascii=False, indent=2)
            return ExportResult(success=True, content=json_str)
        except Exception as e:
            return ExportResult(success=False, error=str(e))

    def export_markdown(self, content: Dict[str, Any]) -> ExportResult:
        """导出为 Markdown 格式"""
        try:
            md_lines = []
            md_lines.append("# 内容生成报告\n")

            # 产品信息
            if "product" in content:
                product = content["product"]
                md_lines.append("## 产品信息\n")
                md_lines.append(f"- **名称**: {product.get('name', '')}\n")
                md_lines.append(f"- **描述**: {product.get('description', '')}\n")
                md_lines.append(f"- **卖点**: {', '.join(product.get('selling_points', []))}\n")
                md_lines.append("")

            # 内容规划
            if "content_plan" in content:
                plan = content["content_plan"]
                md_lines.append("## 内容规划\n")
                md_lines.append(f"- **方向**: {plan.get('content_direction', '')}\n")
                md_lines.append(f"- **语调**: {plan.get('tone_of_voice', '')}\n")
                md_lines.append(f"- **平台**: {', '.join(plan.get('recommended_platforms', []))}\n")
                md_lines.append("")

            # 各平台文案
            if "copies" in content:
                copies = content["copies"]
                md_lines.append("## 生成内容\n")

                platform_names = {
                    "xiaohongshu": "小红书",
                    "tiktok": "抖音",
                    "official": "公众号",
                    "friend_circle": "朋友圈",
                }

                for platform, data in copies.items():
                    platform_name = platform_names.get(platform, platform)
                    copy = data.get("copy", {})
                    review = data.get("review", {})
                    images = data.get("images", [])

                    md_lines.append(f"### {platform_name}\n")

                    # 标题
                    if copy.get("title"):
                        md_lines.append(f"**标题**: {copy['title']}\n")

                    # 文案内容
                    if copy.get("content"):
                        md_lines.append("\n**正文**:\n")
                        md_lines.append(copy["content"])
                        md_lines.append("\n")

                    # 标签
                    if copy.get("tags"):
                        md_lines.append(f"**标签**: {' '.join(copy['tags'])}\n")

                    # 审核结果
                    if review:
                        md_lines.append("\n**审核结果**:\n")
                        md_lines.append(f"- 通过: {'是' if review.get('passed') else '否'}\n")
                        if review.get("quality_score"):
                            md_lines.append(f"- 质量分: {review['quality_score']:.1f}/10\n")
                        if review.get("violations"):
                            md_lines.append("- 违规词:\n")
                            for v in review["violations"]:
                                md_lines.append(f"  - {v['word']}: {v['suggestion']}\n")

                    # 图片建议
                    if images:
                        md_lines.append("\n**配图建议**:\n")
                        for img in images:
                            md_lines.append(f"- [{img['type']}] {img['description']}\n")

                    md_lines.append("\n---\n")

            return ExportResult(success=True, content="\n".join(md_lines))

        except Exception as e:
            return ExportResult(success=False, error=str(e))

    def export_html(self, content: Dict[str, Any]) -> ExportResult:
        """导出为 HTML 格式"""
        try:
            # 首先生成 Markdown
            md_result = self.export_markdown(content)
            if not md_result.success:
                return md_result

            # 简单的 Markdown 到 HTML 转换
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>内容生成报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
        h3 {{ color: #888; }}
        .tag {{ background: #e1f5fe; padding: 2px 8px; border-radius: 4px; margin: 2px; display: inline-block; }}
        .violation {{ color: #d32f2f; }}
        .passed {{ color: #388e3c; }}
        .failed {{ color: #d32f2f; }}
        pre {{ background: #f5f5f5; padding: 15px; border-radius: 8px; overflow-x: auto; }}
    </style>
</head>
<body>
    <pre>{md_result.content}</pre>
</body>
</html>
            """
            return ExportResult(success=True, content=html)

        except Exception as e:
            return ExportResult(success=False, error=str(e))

    def export_text(self, content: Dict[str, Any]) -> ExportResult:
        """导出为纯文本格式"""
        try:
            lines = []
            lines.append("=" * 50)
            lines.append("内容生成报告")
            lines.append("=" * 50)

            # 产品信息
            if "product" in content:
                product = content["product"]
                lines.append("\n【产品信息】")
                lines.append(f"名称: {product.get('name', '')}")
                lines.append(f"描述: {product.get('description', '')}")
                lines.append(f"卖点: {', '.join(product.get('selling_points', []))}")

            # 各平台文案
            if "copies" in content:
                copies = content["copies"]
                lines.append("\n【生成内容】")

                platform_names = {
                    "xiaohongshu": "小红书",
                    "tiktok": "抖音",
                    "official": "公众号",
                    "friend_circle": "朋友圈",
                }

                for platform, data in copies.items():
                    platform_name = platform_names.get(platform, platform)
                    copy = data.get("copy", {})

                    lines.append(f"\n--- {platform_name} ---")
                    if copy.get("title"):
                        lines.append(f"标题: {copy['title']}")
                    if copy.get("content"):
                        lines.append(f"\n{copy['content']}")
                    if copy.get("tags"):
                        lines.append(f"\n标签: {' '.join(copy['tags'])}")

            return ExportResult(success=True, content="\n".join(lines))

        except Exception as e:
            return ExportResult(success=False, error=str(e))

    def export(
        self,
        content: Dict[str, Any],
        format: ExportFormat = ExportFormat.JSON,
    ) -> ExportResult:
        """
        导出内容

        Args:
            content: 内容字典
            format: 导出格式

        Returns:
            ExportResult: 导出结果
        """
        if format == ExportFormat.JSON:
            return self.export_json(content)
        elif format == ExportFormat.MARKDOWN:
            return self.export_markdown(content)
        elif format == ExportFormat.HTML:
            return self.export_html(content)
        elif format == ExportFormat.TEXT:
            return self.export_text(content)
        else:
            return ExportResult(success=False, error=f"Unknown format: {format}")

    # 模板管理方法
    def save_as_template(
        self,
        name: str,
        platform: str,
        content: str,
        tags: Optional[List[str]] = None,
    ) -> ContentTemplate:
        """将内容保存为模板"""
        template = ContentTemplate(
            id=f"tpl_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=name,
            platform=platform,
            content=content,
            tags=tags or [],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            usage_count=0,
        )
        _template_storage.save_template(template)
        return template

    def get_templates(self, platform: str) -> List[ContentTemplate]:
        """获取平台模板"""
        return _template_storage.get_templates(platform)

    def get_all_templates(self) -> Dict[str, List[ContentTemplate]]:
        """获取所有模板"""
        return _template_storage.get_all_templates()

    def delete_template(self, platform: str, template_id: str) -> bool:
        """删除模板"""
        return _template_storage.delete_template(platform, template_id)

    def convert_format(
        self,
        content: str,
        from_platform: str,
        to_platform: str,
    ) -> Dict[str, str]:
        """
        将内容从一种平台格式转换到另一种平台格式

        Args:
            content: 原内容
            from_platform: 原平台
            to_platform: 目标平台

        Returns:
            dict: 包含转换后的内容和调整说明
        """
        import re

        # 移除原平台的标签格式
        if from_platform == "xiaohongshu":
            content = re.sub(r"#[^\s#]+", "", content)
        elif from_platform == "tiktok":
            content = re.sub(r"#\S+", "", content)

        # 根据目标平台调整
        if to_platform == "xiaohongshu":
            # 转换为小红书风格
            lines = content.split("\n")
            if lines and not lines[0].startswith("#"):
                content = f"## {lines[0]}\n" + "\n".join(lines[1:])
            # 添加标签占位符
            content = content.strip() + "\n\n#标签1 #标签2 #标签3"

        elif to_platform == "tiktok":
            # 转换为抖音风格
            lines = content.split("\n")
            if len(lines) > 3:
                content = lines[0] + "\n" + "\n".join(lines[1:4]) + "\n...\n" + lines[-1]
            # 精简内容
            if len(content) > 150:
                content = content[:147] + "..."

        elif to_platform == "official":
            # 转换为公众号风格
            lines = content.split("\n")
            if lines and not lines[0].startswith("#"):
                content = "**" + lines[0] + "**\n\n" + "\n".join(lines[1:])
            # 添加段落分隔
            content = re.sub(r"\n\n+", "\n\n", content)

        elif to_platform == "friend_circle":
            # 转换为朋友圈风格
            # 移除所有标签
            content = re.sub(r"#[^\s#]+", "", content)
            # 精简内容
            if len(content) > 200:
                content = content[:197] + "..."

        adjustments = []
        if from_platform != to_platform:
            adjustments.append(f"从{from_platform}格式转换为{to_platform}格式")
        if from_platform == "xiaohongshu" and to_platform != "xiaohongshu":
            adjustments.append("已移除原标签")
        if to_platform == "friend_circle":
            adjustments.append("已精简为朋友圈风格")

        return {
            "original": content,
            "converted": content,
            "adjustments": adjustments,
        }


if __name__ == "__main__":
    exporter = Exporter()

    # 测试数据
    test_content = {
        "product": {
            "name": "智能睡眠枕",
            "description": "AI智能枕头",
            "selling_points": ["改善睡眠", "AI监测"],
        },
        "content_plan": {
            "content_direction": "家居解决方案",
            "tone_of_voice": "亲切真实",
            "recommended_platforms": ["xiaohongshu"],
        },
        "copies": {
            "xiaohongshu": {
                "copy": {
                    "title": "这个枕头让我睡眠质量翻倍！",
                    "content": "作为一个加班族，睡眠质量一直很差...",
                    "tags": ["#智能家居", "#睡眠好物"],
                },
                "review": {
                    "passed": True,
                    "quality_score": 8.5,
                    "violations": [],
                },
                "images": [
                    {"type": "产品图", "description": "清晰的主图"},
                ],
            }
        },
    }

    # 测试各种格式
    for fmt in ExportFormat:
        result = exporter.export(test_content, fmt)
        print(f"\n{'='*40}")
        print(f"Format: {fmt.value}")
        print(f"Success: {result.success}")
        print(f"Content (first 200 chars): {result.content[:200]}...")
