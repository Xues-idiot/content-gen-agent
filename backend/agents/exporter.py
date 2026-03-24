"""
Vox Exporter 模块 - 导出功能

负责将内容导出为不同格式
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime


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


class ContentArchive:
    """
    内容归档管理器

    负责内容的备份、归档和恢复
    """

    def __init__(self):
        self._archives: List[Dict[str, Any]] = []
        self._archive_id_counter = 0

    def archive_content(
        self,
        content: Dict[str, Any],
        name: str = "",
        category: str = "general",
    ) -> Dict[str, Any]:
        """
        归档内容

        Args:
            content: 内容数据
            name: 归档名称
            category: 分类

        Returns:
            dict: 归档结果
        """
        self._archive_id_counter += 1
        archive_id = f"arc_{self._archive_id_counter:06d}"

        archive_entry = {
            "id": archive_id,
            "name": name or f"Archive {self._archive_id_counter}",
            "category": category,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "size": len(json.dumps(content)),
        }

        self._archives.append(archive_entry)

        return {
            "success": True,
            "archive_id": archive_id,
            "total_archives": len(self._archives),
        }

    def get_archives(
        self,
        category: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        获取归档列表

        Args:
            category: 可选的分类过滤
            limit: 返回数量限制

        Returns:
            list: 归档列表
        """
        archives = self._archives

        if category:
            archives = [a for a in archives if a["category"] == category]

        return sorted(
            archives,
            key=lambda x: x["created_at"],
            reverse=True
        )[:limit]

    def get_archive(self, archive_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个归档

        Args:
            archive_id: 归档ID

        Returns:
            dict: 归档数据
        """
        for archive in self._archives:
            if archive["id"] == archive_id:
                return archive
        return None

    def delete_archive(self, archive_id: str) -> bool:
        """
        删除归档

        Args:
            archive_id: 归档ID

        Returns:
            bool: 是否成功
        """
        original_count = len(self._archives)
        self._archives = [a for a in self._archives if a["id"] != archive_id]
        return len(self._archives) < original_count

    def search_archives(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索归档

        Args:
            keyword: 搜索关键词

        Returns:
            list: 匹配的归档
        """
        keyword_lower = keyword.lower()
        results = []

        for archive in self._archives:
            # 搜索名称和分类
            if keyword_lower in archive["name"].lower():
                results.append(archive)
                continue

            # 搜索内容
            content_str = json.dumps(archive["content"], ensure_ascii=False)
            if keyword_lower in content_str.lower():
                results.append(archive)

        return results

    def export_archive_summary(self) -> Dict[str, Any]:
        """
        导出归档统计摘要

        Returns:
            dict: 统计摘要
        """
        total_size = sum(a["size"] for a in self._archives)
        categories = {}

        for archive in self._archives:
            cat = archive["category"]
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1

        return {
            "total_archives": len(self._archives),
            "total_size_bytes": total_size,
            "by_category": categories,
            "newest_archive": self._archives[-1]["created_at"] if self._archives else None,
        }


# 全局归档管理器
_content_archive = ContentArchive()


# 新增导出格式
class AdvancedExportFormat(Enum):
    """高级导出格式"""
    CSV = "csv"
    XML = "xml"
    PDF_HTML = "pdf_html"  # HTML格式，适合打印
    EMAIL_HTML = "email_html"  # 邮件格式


class AdvancedExporter(Exporter):
    """
    高级导出器

    扩展 Exporter，支持更多导出格式
    """

    def export_csv(self, content: Dict[str, Any]) -> ExportResult:
        """导出为 CSV 格式"""
        try:
            import csv
            import io

            output = io.StringIO()

            # 准备CSV数据
            rows = []

            # 标题行
            rows.append(["平台", "标题", "内容", "标签", "质量分数", "是否通过"])

            # 内容行
            if "copies" in content:
                for platform, data in content["copies"].items():
                    copy = data.get("copy", {})
                    review = data.get("review", {})

                    rows.append([
                        platform,
                        copy.get("title", ""),
                        copy.get("content", ""),
                        ",".join(copy.get("tags", [])),
                        str(review.get("quality_score", "")),
                        "是" if review.get("passed") else "否",
                    ])

            writer = csv.writer(output)
            writer.writerows(rows)

            return ExportResult(success=True, content=output.getvalue())
        except Exception as e:
            return ExportResult(success=False, error=str(e))

    def export_xml(self, content: Dict[str, Any]) -> ExportResult:
        """导出为 XML 格式"""
        try:
            lines = ['<?xml version="1.0" encoding="UTF-8"?>']
            lines.append("<content_report>")

            # 产品信息
            if "product" in content:
                product = content["product"]
                lines.append("  <product>")
                lines.append(f"    <name>{self._escape_xml(product.get('name', ''))}</name>")
                lines.append(f"    <description>{self._escape_xml(product.get('description', ''))}</description>")
                lines.append("  </product>")

            # 内容
            if "copies" in content:
                lines.append("  <copies>")
                for platform, data in content["copies"].items():
                    lines.append(f"    <{platform}>")
                    copy = data.get("copy", {})
                    if copy.get("title"):
                        lines.append(f"      <title>{self._escape_xml(copy['title'])}</title>")
                    if copy.get("content"):
                        lines.append(f"      <content>{self._escape_xml(copy['content'])}</content>")
                    if copy.get("tags"):
                        lines.append(f"      <tags>{self._escape_xml(','.join(copy['tags']))}</tags>")
                    lines.append(f"    </{platform}>")
                lines.append("  </copies>")

            lines.append("</content_report>")

            return ExportResult(success=True, content="\n".join(lines))
        except Exception as e:
            return ExportResult(success=False, error=str(e))

    def export_pdf_html(self, content: Dict[str, Any]) -> ExportResult:
        """导出为适合打印的HTML格式"""
        try:
            md_result = self.export_markdown(content)
            if not md_result.success:
                return md_result

            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>内容生成报告 - 打印版</title>
    <style>
        @media print {{
            body {{ font-size: 12pt; }}
            h1 {{ page-break-before: always; }}
            .platform-section {{ page-break-inside: avoid; }}
        }}
        body {{ font-family: 'Georgia', serif; max-width: 800px; margin: 0 auto; padding: 40px; }}
        h1 {{ color: #333; border-bottom: 2px solid #FF6B35; padding-bottom: 10px; }}
        h2 {{ color: #666; margin-top: 30px; }}
        .platform-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
        .title {{ font-size: 14pt; font-weight: bold; margin-bottom: 10px; }}
        .content {{ line-height: 1.6; }}
        .tags {{ margin-top: 10px; color: #888; }}
        .review {{ margin-top: 10px; padding: 10px; background: #f9f9f9; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
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

    def export_email_html(self, content: Dict[str, Any]) -> ExportResult:
        """导出为邮件HTML格式"""
        try:
            platform_names = {
                "xiaohongshu": "小红书",
                "tiktok": "抖音",
                "official": "公众号",
                "friend_circle": "朋友圈",
            }

            lines = ['<!DOCTYPE html><html><body style="font-family: Arial, sans-serif;">']

            # 标题
            product_name = content.get("product", {}).get("name", "产品")
            lines.append(f'<h2 style="color: #FF6B35;">{product_name} - 多平台内容方案</h2>')

            if "copies" in content:
                for platform, data in content["copies"].items():
                    copy = data.get("copy", {})
                    pname = platform_names.get(platform, platform)

                    lines.append(f'''
<div style="margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px;">
    <h3 style="color: #333; margin-bottom: 10px;">{pname}</h3>
    <p style="font-weight: bold; font-size: 14px;">{copy.get('title', '')}</p>
    <p style="line-height: 1.6; color: #555;">{copy.get('content', '')}</p>
    <p style="color: #888; font-size: 12px;">
        标签: {' '.join(copy.get('tags', []))}
    </p>
</div>
                    ''')

            lines.append('</body></html>')

            return ExportResult(success=True, content="\n".join(lines))
        except Exception as e:
            return ExportResult(success=False, error=str(e))

    def _escape_xml(self, text: str) -> str:
        """转义XML特殊字符"""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    def advanced_export(
        self,
        content: Dict[str, Any],
        format: str = "csv",
    ) -> ExportResult:
        """
        高级导出

        Args:
            content: 内容数据
            format: 导出格式 (csv/xml/pdf_html/email_html)

        Returns:
            ExportResult: 导出结果
        """
        format_map = {
            "csv": self.export_csv,
            "xml": self.export_xml,
            "pdf_html": self.export_pdf_html,
            "email_html": self.export_email_html,
        }

        exporter = format_map.get(format)
        if not exporter:
            return ExportResult(success=False, error=f"Unknown format: {format}")

        return exporter(content)


# 全局高级导出器
advanced_exporter = AdvancedExporter()


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
