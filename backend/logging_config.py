"""
Vox 日志配置模块

统一配置应用日志
"""

import sys
import logging
from pathlib import Path
from loguru import logger


def setup_logging(
    level: str = "INFO",
    log_file: str = None,
    rotation: str = "10 MB",
    retention: str = "7 days",
    format_string: str = None,
) -> None:
    """
    配置日志

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，None 则只输出到控制台
        rotation: 日志轮转大小
        retention: 日志保留时间
        format_string: 自定义格式字符串
    """
    # 移除默认的 handler
    logger.remove()

    # 默认格式
    if format_string is None:
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # 添加控制台输出
    logger.add(
        sys.stderr,
        format=format_string,
        level=level,
        colorize=True,
    )

    # 如果指定了日志文件，添加文件输出
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format=format_string,
            level=level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            encoding="utf-8",
        )

    # 设置日志级别
    logger.level(level)


def get_logger(name: str = None):
    """
    获取 logger 实例

    Args:
        name: 模块名称

    Returns:
        logger 实例
    """
    if name:
        return logger.bind(name=name)
    return logger


class LoggerFilter:
    """日志过滤器"""

    def __init__(self, min_level: str = "INFO"):
        self.min_level = min_level
        self.levels = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50,
        }

    def __call__(self, record):
        level = record["level"].name
        return self.levels.get(level, 20) >= self.levels.get(self.min_level, 20)


# 默认配置
def default_logging():
    """应用默认日志配置"""
    setup_logging(
        level="INFO",
        rotation="10 MB",
        retention="7 days",
    )


if __name__ == "__main__":
    # 测试日志配置
    default_logging()
    logger = get_logger("test")
    logger.info("这是一条测试日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
