"""
Vox LLM Client 模块测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLLMClient:
    """LLM 客户端测试"""

    def setup_method(self):
        """每个测试方法前执行"""
        from backend.services.llm import LLMClient
        self.client = LLMClient()

    def test_client_initialization(self):
        """测试客户端初始化"""
        assert self.client is not None
        assert self.client.model is not None
        assert self.client.max_retries == 3

    def test_validate_config(self):
        """测试配置验证"""
        # 这个测试可能因为没有配置而返回 False
        result = self.client.validate_config()
        assert isinstance(result, bool)

    def test_parse_structured_output_json(self):
        """测试 JSON 解析"""
        text = '{"title": "测试标题", "content": "测试内容"}'
        result = self.client.parse_structured_output(text)

        assert isinstance(result, dict)
        assert result.get("title") == "测试标题"

    def test_parse_structured_output_markdown(self):
        """测试 Markdown 代码块解析"""
        text = '''
        下面是 JSON：
        ```json
        {"title": "标题", "value": 123}
        ```
        '''
        result = self.client.parse_structured_output(text)

        assert isinstance(result, dict)
        assert result.get("title") == "标题"
        assert result.get("value") == 123

    def test_parse_structured_output_invalid(self):
        """测试无效 JSON 解析"""
        text = "这不是 JSON 格式"
        result = self.client.parse_structured_output(text)

        assert isinstance(result, dict)
        assert "raw" in result

    def test_generate_returns_string_or_error(self):
        """测试 generate 方法返回类型"""
        # 注意：这个测试可能因为没有配置 API key 而失败
        response = self.client.generate("你好")

        # 应该返回字符串（成功或错误）
        assert isinstance(response, str)


class TestRetryDecorator:
    """重试装饰器测试"""

    def test_retry_on_error_success(self):
        """测试重试成功情况"""
        from backend.services.llm import retry_on_error

        call_count = 0

        @retry_on_error(max_retries=3, delay=0.1)
        def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = success_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_on_error_failure_then_success(self):
        """测试失败后重试成功"""
        from backend.services.llm import retry_on_error

        call_count = 0

        @retry_on_error(max_retries=3, delay=0.1)
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return "success"

        result = flaky_func()
        assert result == "success"
        assert call_count == 2

    def test_retry_on_error_all_fail(self):
        """测试全部失败"""
        from backend.services.llm import retry_on_error

        @retry_on_error(max_retries=3, delay=0.1)
        def always_fail():
            raise ValueError("Always fails")

        try:
            always_fail()
            assert False, "Should have raised"
        except ValueError as e:
            assert str(e) == "Always fails"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
