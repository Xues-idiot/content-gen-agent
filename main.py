"""
Vox - 内容生成 Agent
主入口文件
"""

import uvicorn
from contextlib import asynccontextmanager

from backend.logging_config import default_logging, get_logger
from backend.constants import VERSION, APP_NAME, APP_DESCRIPTION

# 初始化日志
default_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app):
    """应用生命周期"""
    logger.info(f"{APP_NAME} v{VERSION} 启动中...")
    logger.info(f"描述: {APP_DESCRIPTION}")
    logger.info("后端 API 服务地址: http://localhost:8003")
    logger.info("API 文档地址: http://localhost:8003/docs")
    yield
    logger.info(f"{APP_NAME} 服务关闭")


def create_app() -> uvicorn:
    """创建并配置应用"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from backend.api.content import router as content_router

    app = FastAPI(
        title=f"{APP_NAME} - {APP_DESCRIPTION}",
        version=VERSION,
        description="多平台营销内容生成 API，支持小红书、抖音、公众号、朋友圈",
        lifespan=lifespan,
    )

    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册 API 路由
    app.include_router(content_router)

    @app.get("/")
    async def root():
        return {
            "name": APP_NAME,
            "version": VERSION,
            "description": APP_DESCRIPTION,
        }

    @app.get("/health")
    async def health():
        return {"status": "healthy", "version": VERSION}

    return app


app = create_app()


if __name__ == "__main__":
    logger.info(f"启动 {APP_NAME} v{VERSION}...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info",
    )
