"""
Vox Generators API

统一调用所有内容生成服务的 REST API 接口
支持动态服务发现和调用
"""

import os
import glob
import importlib
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.logging_config import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/api/generators", tags=["generators"])


class GeneratorRequest(BaseModel):
    """通用生成器请求"""
    service_name: str = Field(..., description="服务名称（不含 Generator 后缀）")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="服务参数")


class GeneratorResponse(BaseModel):
    """通用生成器响应"""
    success: bool
    service_name: str
    result: Dict[str, Any]
    error: str = ""


class ServiceInfo(BaseModel):
    """服务信息"""
    name: str
    description: str
    module: str
    parameters: List[Dict[str, Any]] = []


class ServiceListResponse(BaseModel):
    """服务列表响应"""
    services: List[ServiceInfo]
    total: int


def generate_service_registry() -> Dict[str, str]:
    """自动扫描backend/services/目录下所有生成器服务"""
    registry = {}
    pattern = os.path.join("backend", "services", "*_generator.py")
    for filepath in glob.glob(pattern):
        # 从文件路径提取服务名称
        filename = os.path.basename(filepath)
        # filename 格式: xxx_generator.py
        # base_name 格式: xxx_generator
        base_name = filename.replace("_generator.py", "")
        # service_name 格式: xxx (去掉 _generator 后缀)
        # 文件名可能是 xxx_generator.py 或 xxx_yyy_generator.py
        # 需要去掉最后的 _generator 得到服务名
        if base_name.endswith("_generator"):
            service_name = base_name[:-10]  # 去掉 "_generator" (9个字符)
        else:
            service_name = base_name
        # 模块路径应该是 backend.services.xxx_generator
        module_path = f"backend.services.{base_name}"
        registry[service_name] = module_path
    return registry


# 自动生成服务注册表
SERVICE_REGISTRY = generate_service_registry()


def get_service_instance(service_name: str):
    """动态获取服务实例"""
    if service_name not in SERVICE_REGISTRY:
        raise ValueError(f"Service '{service_name}' not found in registry")

    module_path = SERVICE_REGISTRY[service_name]
    try:
        module = importlib.import_module(module_path)
        # 查找 module-level 的服务实例 (xxx_generator_service)
        for attr_name in dir(module):
            if attr_name.endswith('_generator_service'):
                return getattr(module, attr_name)
        raise ValueError(f"Service instance not found in {module_path}")
    except ImportError as e:
        raise ValueError(f"Failed to import service module: {e}")


@router.get("/", response_model=ServiceListResponse)
async def list_services():
    """列出所有可用的生成服务"""
    services = []
    for name in sorted(SERVICE_REGISTRY.keys()):
        services.append(ServiceInfo(
            name=name,
            description=name.replace('_', ' ').title(),
            module=SERVICE_REGISTRY[name]
        ))
    return ServiceListResponse(services=services, total=len(services))


@router.post("/generate", response_model=GeneratorResponse)
async def generate(request: GeneratorRequest):
    """调用指定的生成服务"""
    try:
        service_name = request.service_name
        parameters = request.parameters

        # 获取服务实例
        service = get_service_instance(service_name)

        # 动态调用生成方法
        # 假设所有服务都有 generate_xxx 方法
        method_name = f"generate_{service_name.replace('-', '_')}"
        if hasattr(service, method_name):
            method = getattr(service, method_name)
            result = await method(**parameters)
        else:
            # 尝试通用 generate 方法
            if hasattr(service, 'generate'):
                result = await service.generate(**parameters)
            else:
                raise ValueError(f"Service {service_name} has no generate method")

        return GeneratorResponse(
            success=True,
            service_name=service_name,
            result=result
        )

    except ValueError as e:
        logger.warning(f"Service not found: {request.service_name}")
        return GeneratorResponse(
            success=False,
            service_name=request.service_name,
            result={},
            error=str(e)
        )
    except Exception as e:
        logger.error(f"Generator error: {e}")
        return GeneratorResponse(
            success=False,
            service_name=request.service_name,
            result={},
            error=f"Internal error: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "total_services": len(SERVICE_REGISTRY),
        "services": list(SERVICE_REGISTRY.keys())[:10] + ["..."]
    }


@router.get("/{service_name}")
async def get_service_info(service_name: str):
    """获取指定服务的信息"""
    if service_name not in SERVICE_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    return {
        "name": service_name,
        "module": SERVICE_REGISTRY[service_name],
        "description": service_name.replace('_', ' ').title()
    }
