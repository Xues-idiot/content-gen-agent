"""
Vox Exporter 模块测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.exporter import Exporter, ExportFormat, ExportResult


class TestExporter:
    """Exporter 测试"""

    def setup_method(self):
        """每个测试方法前的 setup"""
        self.exporter = Exporter()
        self.sample_content = {
            "product": {
                "name": "测试产品",
                "description": "测试描述",
                "selling_points": ["卖点1", "卖点2"],
            },
            "copies": {
                "xiaohongshu": {
                    "copy": {
                        "title": "测试标题",
                        "content": "测试内容",
                        "tags": ["#标签1", "#标签2"],
                    },
                    "review": {
                        "passed": True,
                        "quality_score": 8.5,
                    },
                }
            },
        }

    def test_export_json_success(self):
        """测试 JSON 导出成功"""
        result = self.exporter.export_json(self.sample_content)

        assert result.success == True
        assert result.content != ""
        assert '"product"' in result.content
        assert '"name": "测试产品"' in result.content

    def test_export_json_valid_structure(self):
        """测试 JSON 导出结构有效"""
        import json

        result = self.exporter.export_json(self.sample_content)

        assert result.success == True
        data = json.loads(result.content)
        assert data["product"]["name"] == "测试产品"

    def test_export_markdown_success(self):
        """测试 Markdown 导出成功"""
        result = self.exporter.export_markdown(self.sample_content)

        assert result.success == True
        assert "# 内容生成报告" in result.content
        assert "测试产品" in result.content

    def test_export_html_success(self):
        """测试 HTML 导出成功"""
        result = self.exporter.export_html(self.sample_content)

        assert result.success == True
        assert "<html>" in result.content
        assert "<body>" in result.content

    def test_export_text_success(self):
        """测试纯文本导出成功"""
        result = self.exporter.export_text(self.sample_content)

        assert result.success == True
        assert "测试产品" in result.content

    def test_export_by_format_json(self):
        """测试通过 format 参数导出 JSON"""
        result = self.exporter.export(self.sample_content, ExportFormat.JSON)

        assert result.success == True
        assert result.content != ""

    def test_export_by_format_markdown(self):
        """测试通过 format 参数导出 Markdown"""
        result = self.exporter.export(self.sample_content, ExportFormat.MARKDOWN)

        assert result.success == True
        assert "# 内容生成报告" in result.content

    def test_export_empty_content(self):
        """测试空内容导出"""
        result = self.exporter.export({}, ExportFormat.JSON)

        assert result.success == True  # 应该成功，只是内容为空

    def test_export_invalid_format(self):
        """测试无效格式"""
        result = self.exporter.export(self.sample_content, "invalid")

        assert result.success == False
        assert "Unknown format" in result.error


class TestExportResult:
    """ExportResult 测试"""

    def test_export_result_success(self):
        """测试成功结果"""
        result = ExportResult(success=True, content="test content")

        assert result.success == True
        assert result.content == "test content"
        assert result.error == ""

    def test_export_result_failure(self):
        """测试失败结果"""
        result = ExportResult(success=False, error="Some error")

        assert result.success == False
        assert result.error == "Some error"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
