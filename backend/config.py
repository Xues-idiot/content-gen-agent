"""
Vox 配置模块
从 config.toml 和环境变量加载配置
"""

import os
import threading
from pathlib import Path
from typing import Optional

import toml
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config:
    """Vox 配置类"""

    _instance: Optional["Config"] = None
    _lock = threading.Lock()

    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.config_file = self.root_dir / "config.toml"
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        if not self.config_file.exists():
            example_file = self.root_dir / "config.example.toml"
            if example_file.exists():
                import shutil
                shutil.copy(example_file, self.config_file)

        if self.config_file.exists():
            with open(self.config_file, encoding="utf-8") as f:
                self._config = toml.load(f)
        else:
            self._config = {}

    @property
    def app(self) -> dict:
        return self._config.get("app", {})

    @property
    def llm(self) -> dict:
        return self._config.get("llm", {})

    @property
    def minimax(self) -> dict:
        return self._config.get("minimax", {})

    # ==================== MiniMax LLM 配置 ====================
    @property
    def minimax_api_key(self) -> Optional[str]:
        # Environment variable takes precedence over config file
        key = os.getenv("MINIMAX_API_KEY")
        if key:
            return key
        # Config file value
        return self.minimax.get("api_key")

    @property
    def minimax_base_url(self) -> str:
        return os.getenv("MINIMAX_BASE_URL") or self.minimax.get("base_url",
            "https://api.minimax.com/anthropic")

    @property
    def minimax_model(self) -> str:
        return os.getenv("MINIMAX_MODEL") or self.llm.get("model", "MiniMax-M2.7")

    # ==================== LLM Provider 配置 ====================
    @property
    def llm_provider(self) -> str:
        """当前 LLM Provider"""
        return os.getenv("LLM_PROVIDER") or self.llm.get("provider", "minimax")

    # DeepSeek
    @property
    def deepseek_api_key(self) -> Optional[str]:
        return os.getenv("DEEPSEEK_API_KEY") or self.llm.get("deepseek_api_key")

    @property
    def deepseek_model(self) -> str:
        return os.getenv("DEEPSEEK_MODEL") or self.llm.get("deepseek_model", "deepseek-chat")

    @property
    def deepseek_base_url(self) -> str:
        return os.getenv("DEEPSEEK_BASE_URL") or self.llm.get("deepseek_base_url", "https://api.deepseek.com")

    # Moonshot
    @property
    def moonshot_api_key(self) -> Optional[str]:
        return os.getenv("MOONSHOT_API_KEY") or self.llm.get("moonshot_api_key")

    @property
    def moonshot_model(self) -> str:
        return os.getenv("MOONSHOT_MODEL") or self.llm.get("moonshot_model", "moonshot-v1-8k")

    @property
    def moonshot_base_url(self) -> str:
        return os.getenv("MOONSHOT_BASE_URL") or self.llm.get("moonshot_base_url", "https://api.moonshot.cn/v1")

    # OpenAI
    @property
    def openai_api_key(self) -> Optional[str]:
        return os.getenv("OPENAI_API_KEY") or self.llm.get("openai_api_key")

    @property
    def openai_model(self) -> str:
        return os.getenv("OPENAI_MODEL") or self.llm.get("openai_model", "gpt-4o")

    @property
    def openai_base_url(self) -> str:
        return os.getenv("OPENAI_BASE_URL") or self.llm.get("openai_base_url", "https://api.openai.com/v1")

    # Azure
    @property
    def azure_api_key(self) -> Optional[str]:
        return os.getenv("AZURE_API_KEY") or self.llm.get("azure_api_key")

    @property
    def azure_model(self) -> str:
        return os.getenv("AZURE_MODEL") or self.llm.get("azure_model", "")

    @property
    def azure_base_url(self) -> str:
        return os.getenv("AZURE_BASE_URL") or self.llm.get("azure_base_url", "")

    @property
    def azure_api_version(self) -> str:
        return os.getenv("AZURE_API_VERSION") or self.llm.get("azure_api_version", "2024-02-15-preview")

    # Ollama
    @property
    def ollama_api_key(self) -> Optional[str]:
        return os.getenv("OLLAMA_API_KEY") or self.llm.get("ollama_api_key", "ollama")

    @property
    def ollama_model(self) -> str:
        return os.getenv("OLLAMA_MODEL") or self.llm.get("ollama_model", "llama3")

    @property
    def ollama_base_url(self) -> str:
        return os.getenv("OLLAMA_BASE_URL") or self.llm.get("ollama_base_url", "http://localhost:11434/v1")

    # Gemini
    @property
    def gemini_api_key(self) -> Optional[str]:
        return os.getenv("GEMINI_API_KEY") or self.llm.get("gemini_api_key")

    @property
    def gemini_model(self) -> str:
        return os.getenv("GEMINI_MODEL") or self.llm.get("gemini_model", "gemini-1.5-flash")

    # Pollinations
    @property
    def pollinations_model(self) -> str:
        return os.getenv("POLLINATIONS_MODEL") or self.llm.get("pollinations_model", "openai-fast")

    @property
    def pollinations_base_url(self) -> str:
        return os.getenv("POLLINATIONS_BASE_URL") or self.llm.get("pollinations_base_url", "https://text.pollinations.ai/openai")

    @property
    def tavily_api_key(self) -> Optional[str]:
        return os.getenv("TAVILY_API_KEY") or self._config.get("tavily", {}).get("api_key")

    @classmethod
    def get_instance(cls) -> "Config":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance


# 全局配置实例
config = Config.get_instance()
