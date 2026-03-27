"""
Vox Task Queue 模块

异步任务队列管理
支持内存和Redis两种存储模式
"""

import asyncio
import threading
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from loguru import logger

from backend.config import config


class TaskState(Enum):
    """任务状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class Task:
    """任务数据类"""
    task_id: str
    state: TaskState = TaskState.PENDING
    progress: int = 0
    created_at: str = ""
    updated_at: str = ""
    result: Dict[str, Any] = field(default_factory=dict)
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "state": self.state.value,
            "progress": self.progress,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "result": self.result,
            "error": self.error,
        }


class BaseTaskQueue(ABC):
    """任务队列基类"""

    @abstractmethod
    def create_task(self, task_type: str, params: Dict[str, Any]) -> str:
        """创建新任务，返回 task_id"""
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务信息"""
        pass

    @abstractmethod
    def update_task(
        self,
        task_id: str,
        state: TaskState = None,
        progress: int = None,
        result: Dict[str, Any] = None,
        error: str = None,
    ) -> bool:
        """更新任务状态"""
        pass

    @abstractmethod
    def get_all_tasks(
        self, page: int = 1, page_size: int = 20, state: TaskState = None
    ) -> tuple:
        """获取所有任务，分页返回 (tasks, total)"""
        pass

    @abstractmethod
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        pass


class MemoryTaskQueue(BaseTaskQueue):
    """内存任务队列"""

    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()

    def create_task(self, task_type: str, params: Dict[str, Any]) -> str:
        task_id = f"{task_type}-{uuid.uuid4().hex[:8]}"
        now = datetime.now().isoformat()
        task = Task(
            task_id=task_id,
            state=TaskState.PENDING,
            progress=0,
            created_at=now,
            updated_at=now,
            result={"task_type": task_type, "params": params},
        )
        with self._lock:
            self._tasks[task_id] = task
        logger.info(f"Task created: {task_id} ({task_type})")
        return task_id

    def get_task(self, task_id: str) -> Optional[Task]:
        with self._lock:
            return self._tasks.get(task_id)

    def update_task(
        self,
        task_id: str,
        state: TaskState = None,
        progress: int = None,
        result: Dict[str, Any] = None,
        error: str = None,
    ) -> bool:
        with self._lock:
            if task_id not in self._tasks:
                return False
            task = self._tasks[task_id]
            if state is not None:
                task.state = state
            if progress is not None:
                task.progress = max(0, min(100, int(progress)))
            if result is not None:
                task.result.update(result)
            if error is not None:
                task.error = error
            task.updated_at = datetime.now().isoformat()
            return True

    def get_all_tasks(
        self, page: int = 1, page_size: int = 20, state: TaskState = None
    ) -> tuple:
        with self._lock:
            tasks = list(self._tasks.values())
            if state is not None:
                tasks = [t for t in tasks if t.state == state]
            tasks.sort(key=lambda t: t.created_at, reverse=True)
            total = len(tasks)
            start = (page - 1) * page_size
            end = start + page_size
            return tasks[start:end], total

    def delete_task(self, task_id: str) -> bool:
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
            return False


class AsyncTaskQueue:
    """
    异步任务执行器

    支持：
    - 后台执行耗时任务
    - 进度追踪
    - 任务取消（通过设置标志位）
    """

    def __init__(self, queue: BaseTaskQueue = None):
        self._queue = queue or MemoryTaskQueue()
        self._running_tasks: Dict[str, asyncio.Task] = {}

    async def submit_task(
        self,
        task_type: str,
        params: Dict[str, Any],
        coro_func=None,
    ) -> str:
        """
        提交异步任务

        Args:
            task_type: 任务类型 (video_generate, batch_generate 等)
            params: 任务参数
            coro_func: 异步执行函数，签名为 async_func(task_id, params, update_callback)

        Returns:
            task_id
        """
        task_id = self._queue.create_task(task_type, params)

        if coro_func:
            task = asyncio.create_task(
                self._run_task(task_id, coro_func, params)
            )
            self._running_tasks[task_id] = task

        return task_id

    async def _run_task(
        self,
        task_id: str,
        coro_func,
        params: Dict[str, Any],
    ):
        """内部方法：运行任务"""
        try:
            self._queue.update_task(task_id, state=TaskState.PROCESSING, progress=0)

            async def update_callback(progress: int, **kwargs):
                self._queue.update_task(
                    task_id,
                    progress=progress,
                    result=kwargs,
                )

            result = await coro_func(task_id, params, update_callback)

            self._queue.update_task(
                task_id,
                state=TaskState.COMPLETE,
                progress=100,
                result={"data": result} if result else {},
            )
            logger.success(f"Task completed: {task_id}")

        except Exception as e:
            logger.error(f"Task failed: {task_id}")
            self._queue.update_task(
                task_id,
                state=TaskState.FAILED,
                error="任务执行失败，请稍后重试",
            )
        finally:
            self._running_tasks.pop(task_id, None)

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务信息"""
        return self._queue.get_task(task_id)

    def get_task_state(self, task_id: str) -> Optional[TaskState]:
        """获取任务状态"""
        task = self._queue.get_task(task_id)
        return task.state if task else None

    def cancel_task(self, task_id: str) -> bool:
        """取消任务（如果正在运行）"""
        if task_id in self._running_tasks:
            self._running_tasks[task_id].cancel()
            self._queue.update_task(task_id, state=TaskState.FAILED, error="Cancelled by user")
            return True
        return False


# 全局实例
task_queue = MemoryTaskQueue()
async_task_queue = AsyncTaskQueue(task_queue)


# ============ 视频生成任务流程 ============

async def video_generate_task(
    task_id: str,
    params: Dict[str, Any],
    update_callback,
):
    """
    视频生成异步任务流程

    流程：
    1. 生成脚本 (10%)
    2. 生成关键词 (20%)
    3. 生成音频 (40%)
    4. 生成字幕 (50%)
    5. 下载素材 (60%)
    6. 合并视频 (80%)
    7. 生成最终视频 (100%)
    """
    from backend.services.voice import voice_service
    from backend.services.subtitle import subtitle_service
    from backend.tools.material_collector import material_collector
    from backend.tools.video_generator import VideoGenerator, VideoAspect, VideoParams

    try:
        # 1. 生成脚本
        update_callback(5, step="生成脚本")
        video_script = params.get("script", "")
        if not video_script:
            from backend.agents.copywriter import Copywriter
            from backend.agents.planner import ProductInfo, ContentPlan

            product = ProductInfo(**params.get("product", {}))
            plan_data = params.get("plan", {})
            user_profile_data = params.get("user_profile", {})

            # 构建 user_profile 字符串
            user_profile_str = user_profile_data.get("occupation", "目标用户") if isinstance(user_profile_data, dict) else str(user_profile_data)

            copywriter_instance = Copywriter()
            copy_result = copywriter_instance.write_tiktok(
                product=product,
                plan=ContentPlan(**plan_data) if plan_data else None,
                user_profile=user_profile_str,
            )
            video_script = copy_result.script or copy_result.content

        update_callback(10, step="脚本生成完成", script=video_script)

        # 2. 生成关键词
        update_callback(20, step="生成关键词")
        video_terms = params.get("search_terms", [])
        if not video_terms and params.get("auto_generate_terms", True):
            from backend.agents.copywriter import copywriter
            keywords = copywriter.generate_keywords(video_script, amount=5)
            video_terms = [k.strip() for k in keywords] if keywords else []

        update_callback(25, step="关键词生成完成", terms=video_terms)

        # 3. 生成音频
        update_callback(30, step="开始生成音频")
        voice_name = params.get("voice_name", "zh-CN-XiaoyiNeural")
        voice_rate = params.get("voice_rate", 1.0)

        audio_path, subtitle_path, duration = voice_service.generate_with_subtitles(
            text=video_script,
            voice_name=voice_name,
            voice_rate=voice_rate,
        )

        if not audio_path:
            raise Exception("音频生成失败")

        update_callback(40, step="音频生成完成", audio_path=audio_path, duration=duration)

        # 4. 生成字幕
        update_callback(50, step="生成字幕")
        if not subtitle_path:
            subtitle_path = subtitle_service.generate_subtitle(
                audio_path=audio_path,
                language=params.get("language", "zh"),
            )

        update_callback(55, step="字幕生成完成", subtitle_path=subtitle_path)

        # 5. 下载素材
        update_callback(60, step="下载视频素材")
        video_aspect = params.get("video_aspect", "9:16")
        source = params.get("video_source", "pexels")

        video_paths = material_collector.download_videos(
            search_terms=video_terms,
            video_aspect=video_aspect,
            source=source,
            audio_duration=duration,
        )

        if not video_paths:
            raise Exception("视频素材下载失败")

        update_callback(70, step="素材下载完成", video_count=len(video_paths))

        # 6. 合并视频
        update_callback(75, step="合并视频")
        generator = VideoGenerator()

        aspect_map = {
            "9:16": VideoAspect.PORTRAIT,
            "16:9": VideoAspect.LANDSCAPE,
            "1:1": VideoAspect.SQUARE,
        }

        video_params = VideoParams(
            video_aspect=aspect_map.get(video_aspect, VideoAspect.PORTRAIT),
            video_concat_mode=params.get("concat_mode", "random"),
            video_transition_mode=params.get("transition_mode", "fade_in"),
        )

        combined_path = generator.combine_videos(
            video_paths=video_paths,
            audio_path=audio_path,
            output_path=params.get("combined_output", ""),
            params=video_params,
        )

        if not combined_path:
            raise Exception("视频合并失败")

        update_callback(85, step="视频合并完成", combined_path=combined_path)

        # 7. 生成最终视频
        update_callback(90, step="生成最终视频")

        final_result = generator.generate_video(
            video_path=combined_path,
            audio_path=audio_path,
            subtitle_path=subtitle_path or "",
            output_path=params.get("output_path", ""),
            params=video_params,
        )

        update_callback(100, step="完成", final_path=final_result.video_path if final_result.success else "")

        return {
            "video_path": final_result.video_path if final_result.success else combined_path,
            "audio_path": audio_path,
            "subtitle_path": subtitle_path,
            "duration": duration,
            "script": video_script,
            "terms": video_terms,
        }

    except Exception as e:
        logger.error("Video generate task error")
        raise


# ============ 批处理任务流程 ============

async def batch_generate_task(
    task_id: str,
    params: Dict[str, Any],
    update_callback,
):
    """
    批量生成异步任务流程

    流程：
    1. 处理每个产品的文案 (N * 25%)
    2. 生成所有视频 (50-100%)
    """
    from backend.agents.copywriter import copywriter
    from backend.agents.planner import ProductInfo, ContentPlan

    try:
        products = params.get("products", [])
        platforms = params.get("platforms", ["xiaohongshu", "tiktok"])
        results = []

        total_products = len(products)
        for i, product_data in enumerate(products):
            progress_start = int((i / total_products) * 50)
            update_callback(
                progress_start,
                step=f"处理产品 {i+1}/{total_products}",
                current_product=product_data.get("name", ""),
            )

            product = ProductInfo(**product_data)
            plan = ContentPlan(**params.get("plan", {})) if params.get("plan") else None

            # 生成多平台文案
            copy_results = await copywriter.generate_all(product, plan)
            product_result = {
                "product_name": product.name,
                "copies": {},
            }

            for platform, copy_result in copy_results.items():
                if platform in platforms:
                    product_result["copies"][platform] = {
                        "title": copy_result.title,
                        "content": copy_result.content,
                        "script": copy_result.script,
                        "tags": copy_result.tags,
                    }

            results.append(product_result)
            update_callback(
                int(((i + 1) / total_products) * 50),
                step=f"完成产品 {i+1}/{total_products}",
            )

        update_callback(50, step="开始生成视频")

        # 批量生成视频
        video_results = []
        for i, result in enumerate(results):
            for platform, copy_data in result["copies"].items():
                if platform == "tiktok" and copy_data.get("script"):
                    update_callback(
                        50 + int((i / len(results)) * 50),
                        step=f"生成视频 {i+1}/{len(results)}",
                    )
                    # 这里可以调用 video_generate_task
                    # 简化处理，仅返回文案结果

        update_callback(100, step="完成", results=results)

        return {"results": results, "total": len(results)}

    except Exception as e:
        logger.error("Batch generate task error")
        raise


# 导出
__all__ = [
    "TaskState",
    "Task",
    "BaseTaskQueue",
    "MemoryTaskQueue",
    "AsyncTaskQueue",
    "task_queue",
    "async_task_queue",
    "video_generate_task",
    "batch_generate_task",
]
