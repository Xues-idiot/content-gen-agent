"""
Vox 配置模块
从 config.toml 和环境变量加载配置
"""

import os
from pathlib import Path
from typing import Optional

import toml
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config:
    """Vox 配置类"""
    
    _instance: Optional["Config"] = None
    
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
    
    @property
    def minimax_api_key(self) -> str:
        # Environment variable takes precedence over config file
        key = os.getenv("MINIMAX_API_KEY")
        if key:
            return key
        # Config file value - don't replace placeholders, return as-is
        return self.minimax.get("api_key", "")
    
    @property
    def minimax_base_url(self) -> str:
        return os.getenv("MINIMAX_BASE_URL") or self.minimax.get("base_url", 
            "https://api.minimaxi.com/anthropic")
    
    @property
    def minimax_model(self) -> str:
        return os.getenv("MINIMAX_MODEL") or self.llm.get("model", "MiniMax-M2.2")
    
    @property
    def tavily_api_key(self) -> str:
        return os.getenv("TAVILY_API_KEY") or self._config.get("tavily", {}).get("api_key", "")
    
    @classmethod
    def get_instance(cls) -> "Config":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# 全局配置实例
config = Config.get_instance()
