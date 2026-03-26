"""
Vox LLM 设置 API

提供 LLM Provider 管理和配置接口
"""

from typing import Optional, Dict, Any, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from loguru import logger

from backend.config import config
from backend.services.llm import llm_client, LLM_PROVIDERS

router = APIRouter(prefix="/llm", tags=["LLM设置"])


class LLMProviderInfo(BaseModel):
    """LLM Provider 信息"""
    name: str = Field(..., description="Provider 名称")
    configured: bool = Field(..., description="是否已配置")
    models: List[str] = Field(default_factory=list, description="可用模型")


class LLMConfigResponse(BaseModel):
    """LLM 配置响应"""
    current_provider: str = Field(..., description="当前 Provider")
    available_providers: List[str] = Field(..., description="可用 Provider 列表")
    provider_info: Dict[str, Any] = Field(..., description="当前 Provider 详情")


class LLMProviderUpdateRequest(BaseModel):
    """LLM Provider 更新请求"""
    provider: str = Field(..., description="Provider 名称")
    api_key: Optional[str] = Field(None, description="API Key (可选)")
    base_url: Optional[str] = Field(None, description="Base URL (可选)")
    model: Optional[str] = Field(None, description="模型名称 (可选)")


@router.get("/config", response_model=LLMConfigResponse)
async def get_llm_config():
    """
    获取当前 LLM 配置

    Returns:
        LLMConfigResponse: 当前配置信息
    """
    try:
        current_info = llm_client.get_provider_info()

        return LLMConfigResponse(
            current_provider=llm_client.provider,
            available_providers=LLM_PROVIDERS,
            provider_info=current_info,
        )
    except Exception as e:
        logger.error(f"Failed to get LLM config: {e}")
        raise HTTPException(status_code=500, detail="获取配置失败，请稍后重试")


@router.get("/providers", response_model=List[LLMProviderInfo])
async def get_providers():
    """
    获取所有可用的 LLM Provider 及其状态

    Returns:
        List[LLMProviderInfo]: Provider 列表
    """
    providers_info = []

    for provider_name in LLM_PROVIDERS:
        configured = False
        models = []

        # 检查各 Provider 配置状态
        if provider_name == "minimax":
            configured = bool(config.minimax_api_key)
            models = ["MiniMax-M2.7", "MiniMax-M2"]
        elif provider_name == "deepseek":
            configured = bool(config.deepseek_api_key)
            models = ["deepseek-chat", "deepseek-coder"]
        elif provider_name == "moonshot":
            configured = bool(config.moonshot_api_key)
            models = ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
        elif provider_name == "openai":
            configured = bool(config.openai_api_key)
            models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        elif provider_name == "azure":
            configured = bool(config.azure_api_key and config.azure_base_url)
            models = ["gpt-4o", "gpt-4", "gpt-35-turbo"]
        elif provider_name == "ollama":
            configured = True  # Ollama 本地服务无需 API key
            models = ["llama3", "llama3.1", "mistral", "qwen2.5"]
        elif provider_name == "gemini":
            configured = bool(config.gemini_api_key)
            models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
        elif provider_name == "pollinations":
            configured = True  # 免费服务无需 API key
            models = ["openai-fast", "openai", "mistral"]

        providers_info.append(LLMProviderInfo(
            name=provider_name,
            configured=configured,
            models=models,
        ))

    return providers_info


@router.post("/provider", response_model=Dict[str, Any])
async def update_provider(request: LLMProviderUpdateRequest):
    """
    更新 LLM Provider 配置

    Args:
        request: Provider 更新请求

    Returns:
        更新后的 Provider 信息
    """
    if request.provider not in LLM_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的 Provider: {request.provider}"
        )

    try:
        # 创建新的 LLM 客户端实例
        global llm_client
        from backend.services.llm import LLMClient

        llm_client = LLMClient(
            provider=request.provider,
            api_key=request.api_key,
            base_url=request.base_url,
            model=request.model,
        )

        # 验证配置
        if not llm_client.validate_config():
            raise HTTPException(
                status_code=400,
                detail=f"Provider {request.provider} 配置无效，请检查 API Key 和其他参数"
            )

        return {
            "success": True,
            "provider": llm_client.provider,
            "model": llm_client.model,
            "base_url": llm_client.base_url,
            "message": f"已切换到 {request.provider} Provider"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to switch LLM provider: {e}")
        raise HTTPException(status_code=500, detail="切换 Provider 失败，请稍后重试")


@router.post("/test", response_model=Dict[str, str])
async def test_llm_connection(prompt: str = "请回复'连接成功'"):
    """
    测试 LLM 连接

    Args:
        prompt: 测试提示词

    Returns:
        测试结果
    """
    try:
        response = llm_client.generate(
            prompt=prompt,
            max_tokens=100,
            temperature=0.7,
        )

        if response.startswith("Error:"):
            return {
                "success": False,
                "response": response,
                "provider": llm_client.provider,
                "model": llm_client.model,
            }

        return {
            "success": True,
            "response": response,
            "provider": llm_client.provider,
            "model": llm_client.model,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "provider": llm_client.provider,
        }
