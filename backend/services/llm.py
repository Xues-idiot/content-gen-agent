"""
Vox LLM 模块 - 多 Provider LLM 客户端

参考 MoneyPrinterTurbo 的多 Provider 模式
支持: MiniMax, DeepSeek, Moonshot, OpenAI, Azure, Ollama, Gemini, Pollinations
"""

import json
import re
import time
import requests
from typing import Optional, List, Dict, Any
from functools import wraps

import anthropic
from loguru import logger

from backend.config import config

# 预编译的正则表达式（避免重复编译）
_JSON_PATTERN = re.compile(r"\{[\s\S]*\}")
_MARKDOWN_CODE_PATTERN = re.compile(r"```(?:json)?\s*([\s\S]*?)```")

# 支持的 LLM Provider
LLM_PROVIDERS = [
    "minimax",    # MiniMax (默认，兼容 Anthropic)
    "deepseek",   # DeepSeek
    "moonshot",   # Moonshot
    "openai",     # OpenAI
    "azure",      # Azure OpenAI
    "ollama",     # Ollama 本地
    "gemini",     # Google Gemini
    "pollinations",  # Pollinations (免费)
]


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
                            f"Attempt {attempt + 1}/{max_retries} failed. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed")

            raise last_exception
        return wrapper
    return decorator


class LLMClient:
    """
    LLM 客户端 - 多 Provider 支持

    支持多种 LLM Provider:
    - minimax: MiniMax API (兼容 Anthropic 格式)
    - deepseek: DeepSeek API
    - moonshot: Moonshot API
    - openai: OpenAI API
    - azure: Azure OpenAI
    - ollama: Ollama 本地模型
    - gemini: Google Gemini
    - pollinations: Pollinations (免费)

    特性：
    - 自动重试（指数退避）
    - 结构化输出解析
    - Provider 动态切换
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3,
    ):
        self.provider = provider or config.llm_provider
        self.max_retries = max_retries

        # 根据 provider 设置配置
        self._configure_provider(api_key, base_url, model)

        self._client: Optional[Any] = None

    def _configure_provider(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """根据 provider 类型配置参数"""
        if self.provider == "minimax":
            self.api_key = api_key or config.minimax_api_key
            self.base_url = base_url or config.minimax_base_url
            self.model = model or config.minimax_model
            self._use_anthropic = True

        elif self.provider == "deepseek":
            self.api_key = api_key or config.deepseek_api_key
            self.base_url = base_url or config.deepseek_base_url
            self.model = model or config.deepseek_model
            self._use_anthropic = False

        elif self.provider == "moonshot":
            self.api_key = api_key or config.moonshot_api_key
            self.base_url = base_url or config.moonshot_base_url
            self.model = model or config.moonshot_model
            self._use_anthropic = False

        elif self.provider == "openai":
            self.api_key = api_key or config.openai_api_key
            self.base_url = base_url or config.openai_base_url
            self.model = model or config.openai_model
            self._use_anthropic = False

        elif self.provider == "azure":
            self.api_key = api_key or config.azure_api_key
            self.base_url = base_url or config.azure_base_url
            self.model = model or config.azure_model
            self._use_anthropic = False
            self._is_azure = True

        elif self.provider == "ollama":
            self.api_key = api_key or "ollama"  # Ollama 不需要真实 key
            self.base_url = base_url or config.ollama_base_url
            self.model = model or config.ollama_model
            self._use_anthropic = False

        elif self.provider == "gemini":
            self.api_key = api_key or config.gemini_api_key
            self.base_url = base_url or ""
            self.model = model or config.gemini_model
            self._use_anthropic = False
            self._is_gemini = True

        elif self.provider == "pollinations":
            self.api_key = None  # Pollinations 不需要 API key
            self.base_url = base_url or config.pollinations_base_url
            self.model = model or config.pollinations_model
            self._use_anthropic = False
            self._is_pollinations = True

        else:
            # 默认为 MiniMax
            self.provider = "minimax"
            self.api_key = api_key or config.minimax_api_key
            self.base_url = base_url or config.minimax_base_url
            self.model = model or config.minimax_model
            self._use_anthropic = True

    @property
    def anthropic_client(self) -> anthropic.Anthropic:
        """获取 Anthropic 客户端 (用于 MiniMax)"""
        if self._client is None or not self._use_anthropic:
            self._client = anthropic.Anthropic(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=60.0,
                max_retries=self.max_retries,
            )
        return self._client

    def _get_openai_client(self):
        """获取 OpenAI 格式客户端"""
        try:
            from openai import OpenAI
            return OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=60.0,
                max_retries=self.max_retries,
            )
        except ImportError:
            logger.error("OpenAI package not installed")
            return None

    def _get_azure_client(self):
        """获取 Azure OpenAI 客户端"""
        try:
            from openai import AzureOpenAI
            return AzureOpenAI(
                api_key=self.api_key,
                api_version=config.azure_api_version,
                azure_endpoint=self.base_url,
                timeout=60.0,
                max_retries=self.max_retries,
            )
        except ImportError:
            logger.error("Azure OpenAI not configured properly")
            return None

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
        return self.generate_with_messages(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
        )

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
        # MiniMax 使用 Anthropic 格式
        if self.provider == "minimax":
            return self._generate_minimax(messages, max_tokens, temperature, system)

        # Gemini 特殊处理
        elif self.provider == "gemini":
            return self._generate_gemini(messages, system)

        # Pollinations 特殊处理
        elif self.provider == "pollinations":
            return self._generate_pollinations(messages)

        # Azure 特殊处理
        elif self.provider == "azure":
            return self._generate_azure(messages, max_tokens, temperature)

        # 其他 Provider 使用 OpenAI 格式
        else:
            return self._generate_openai_format(messages, max_tokens, temperature, system)

    def _generate_minimax(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        system: Optional[str] = None,
    ) -> str:
        """使用 MiniMax API 生成"""
        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if system:
            params["system"] = system

        try:
            response = self.anthropic_client.messages.create(**params)
            if not response.content or not response.content[0].text:
                return "Error: Empty response from LLM"
            return response.content[0].text or "Error: Empty response from LLM"
        except Exception as e:
            logger.error(f"MiniMax generation error: {e}")
            return f"Error: {str(e)}"

    def _generate_openai_format(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        system: Optional[str] = None,
    ) -> str:
        """使用 OpenAI 格式 API 生成"""
        client = self._get_openai_client()
        if not client:
            return "Error: OpenAI client not available"

        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if system:
            params["messages"] = [{"role": "system", "content": system}] + messages

        try:
            response = client.chat.completions.create(**params)
            if not response.choices or not response.choices[0].message.content:
                return "Error: Empty response from LLM"
            return response.choices[0].message.content or "Error: Empty response from LLM"
        except Exception as e:
            logger.error(f"OpenAI format generation error: {e}")
            return f"Error: {str(e)}"

    def _generate_azure(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> str:
        """使用 Azure OpenAI API 生成"""
        client = self._get_azure_client()
        if not client:
            return "Error: Azure client not available"

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            if not response.choices or not response.choices[0].message.content:
                return "Error: Empty response from LLM"
            return response.choices[0].message.content or "Error: Empty response from LLM"
        except Exception as e:
            logger.error(f"Azure generation error: {e}")
            return f"Error: {str(e)}"

    def _generate_gemini(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
    ) -> str:
        """使用 Google Gemini API 生成"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)

            model = genai.GenerativeModel(self.model)

            # 合并消息为单个 prompt
            prompt = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    prompt += f"System: {content}\n"
                else:
                    prompt += f"User: {content}\n"

            if system:
                prompt = f"System: {system}\n{prompt}"

            generation_config = {
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }

            response = model.generate_content(prompt, generation_config=generation_config)

            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    return candidate.content.parts[0].text or "Error: Empty response from Gemini"

            return "Error: Empty response from Gemini"
        except ImportError:
            return "Error: Google Generative AI package not installed"
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return f"Error: {str(e)}"

    def _generate_pollinations(
        self,
        messages: List[Dict[str, str]],
    ) -> str:
        """使用 Pollinations API 生成（免费）"""
        # 将消息转换为单个 prompt
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt += f"[System] {content}\n"
            else:
                prompt += f"{content}\n"

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "seed": 101,
        }

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()

            if result and "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return (content or "").replace("\n", "")
            else:
                return "Error: Invalid response from Pollinations"
        except requests.exceptions.RequestException as e:
            return f"Error: Pollinations request failed: {str(e)}"
        except Exception as e:
            logger.error(f"Pollinations generation error: {e}")
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
        # 尝试提取 JSON（使用预编译的正则）
        json_match = _JSON_PATTERN.search(text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 尝试解析 Markdown 代码块（使用预编译的正则）
        code_match = _MARKDOWN_CODE_PATTERN.search(text)
        if code_match:
            try:
                return json.loads(code_match.group(1))
            except json.JSONDecodeError:
                pass

        logger.warning(f"Failed to parse structured output: {text[:200]}")
        return {"raw": text}

    def validate_config(self) -> bool:
        """验证配置是否有效"""
        if self.provider == "pollinations":
            # Pollinations 不需要 API key
            return True

        if self.provider == "ollama":
            # Ollama 本地不需要真实 key
            return True

        if not self.api_key:
            logger.error(f"{self.provider}: API key is not set")
            return False

        if not self.model:
            logger.error(f"{self.provider}: Model not configured")
            return False

        if self.provider not in ["ollama", "pollinations"] and not self.base_url:
            logger.error(f"{self.provider}: Base URL not configured")
            return False

        return True

    def get_provider_info(self) -> Dict[str, Any]:
        """获取当前 Provider 信息"""
        return {
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "configured": self.validate_config(),
        }


# 全局 LLM 客户端实例
llm_client = LLMClient()


if __name__ == "__main__":
    # 测试
    client = LLMClient()

    print(f"Current provider: {client.provider}")
    print(f"Provider info: {client.get_provider_info()}")

    if not client.validate_config():
        print("Warning: LLM configuration is incomplete")

    response = client.generate(
        prompt="请用一句话介绍你自己",
        system="你是一个有帮助的AI助手"
    )
    print(f"Response: {response}")
