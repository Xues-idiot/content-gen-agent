"""
Vox LLM 模块 - MiniMax API 客户端

参考 MoneyPrinterTurbo 的多 Provider 模式
支持重试机制和错误处理
"""

import os
import re
import time
from typing import Optional, List, Dict, Any
from functools import wraps

import anthropic
from loguru import logger

from backend.config import config


def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """重试装饰器 - 指数退避"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed: {e}")

            raise last_exception
        return wrapper
    return decorator


class LLMClient:
    """
    LLM 客户端

    支持 MiniMax API（兼容 Anthropic 格式）
    特性：
    - 自动重试（指数退避）
    - 连接池管理
    - 结构化输出解析
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3,
    ):
        self.api_key = api_key or config.minimax_api_key
        self.base_url = base_url or config.minimax_base_url
        self.model = model or config.minimax_model
        self.max_retries = max_retries

        self._client: Optional[anthropic.Anthropic] = None

    @property
    def client(self) -> anthropic.Anthropic:
        """获取或创建 Anthropic 客户端"""
        if self._client is None:
            self._client = anthropic.Anthropic(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=60.0,  # 60秒超时
                max_retries=self.max_retries,
            )
        return self._client

    @retry_on_error(max_retries=3, delay=1.0, backoff=2.0)
    def generate(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: Optional[str] = None,
    ) -> str:
        """
        生成文本

        Args:
            prompt: 用户提示
            max_tokens: 最大 token 数
            temperature: 温度参数
            system: 系统提示

        Returns:
            str: 生成的文本
        """
        messages = [{"role": "user", "content": prompt}]

        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        if system:
            params["system"] = system

        try:
            response = self.client.messages.create(**params)
            content = response.content[0].text
            logger.debug(f"LLM response: {content[:200]}...")
            return content
        except anthropic.RateLimitError as e:
            logger.warning(f"Rate limit hit: {e}")
            raise  # 让装饰器处理重试
        except anthropic.APIError as e:
            logger.error(f"API error: {e}")
            raise  # 让装饰器处理重试
        except Exception as e:
            logger.error(f"LLM generate error: {e}")
            return f"Error: {str(e)}"

    @retry_on_error(max_retries=3, delay=1.0, backoff=2.0)
    def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: Optional[str] = None,
    ) -> str:
        """
        使用消息列表生成文本

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            max_tokens: 最大 token 数
            temperature: 温度参数
            system: 系统提示

        Returns:
            str: 生成的文本
        """
        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        if system:
            params["system"] = system

        try:
            response = self.client.messages.create(**params)
            content = response.content[0].text
            logger.debug(f"LLM response: {content[:200]}...")
            return content
        except anthropic.RateLimitError as e:
            logger.warning(f"Rate limit hit: {e}")
            raise
        except anthropic.APIError as e:
            logger.error(f"API error: {e}")
            raise
        except Exception as e:
            logger.error(f"LLM generate error: {e}")
            return f"Error: {str(e)}"

    def parse_structured_output(self, text: str, format_hint: str = "json") -> Dict[str, Any]:
        """
        解析结构化输出

        Args:
            text: LLM 返回的文本
            format_hint: 格式提示（json/markdown）

        Returns:
            dict: 解析后的字典
        """
        import json

        # 尝试提取 JSON
        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 尝试解析 Markdown 代码块
        code_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if code_match:
            try:
                return json.loads(code_match.group(1))
            except json.JSONDecodeError:
                pass

        logger.warning(f"Failed to parse structured output: {text[:200]}")
        return {"raw": text}

    def validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.api_key:
            logger.error("MINIMAX_API_KEY is not set")
            return False
        if not self.model:
            logger.error("Model not configured")
            return False
        return True


# 全局 LLM 客户端实例
llm_client = LLMClient()


if __name__ == "__main__":
    # 测试
    client = LLMClient()

    if not client.validate_config():
        print("Warning: LLM configuration is incomplete")

    response = client.generate(
        prompt="请用一句话介绍你自己",
        system="你是一个有帮助的AI助手"
    )
    print(f"Response: {response}")
