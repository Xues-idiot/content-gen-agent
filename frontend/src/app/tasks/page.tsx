"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import SidebarNav from "@/components/SidebarNav";
import { ToastProvider, useToast } from "@/components/Toast";
import {
  ListTodo,
  RefreshCw,
  Trash2,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  PlayCircle,
  PauseCircle,
} from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

interface Task {
  task_id: string;
  state: string;
  progress: number;
  created_at: string;
  updated_at: string;
  result: Record<string, any>;
  error: string;
}

function TasksPageContent() {
  const { showToast } = useToast();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterState, setFilterState] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    fetchTasks();
    return () => { isMountedRef.current = false; };
  }, [filterState, page]);

  const fetchTasks = async () => {
    if (!isMountedRef.current) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });
      if (filterState) params.append("state", filterState);

      const response = await fetch(`${API_BASE_URL}/api/v1/tasks?${params}`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      if (isMountedRef.current && data.tasks) {
        setTasks(data.tasks);
        setTotal(data.total);
      }
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
      if (isMountedRef.current) {
        showToast("获取任务列表失败", "error");
      }
    } finally {
      if (isMountedRef.current) setLoading(false);
    }
  };

  const deleteTask = async (taskId: string) => {
    if (!isMountedRef.current) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/tasks/${taskId}`, {
        method: "DELETE",
      });
      if (isMountedRef.current && response.ok) {
        setTasks((prev) => prev.filter((t) => t.task_id !== taskId));
        showToast("任务已删除", "success");
      }
    } catch {
      if (isMountedRef.current) {
        showToast("删除失败", "error");
      }
    }
  };

  const getStateIcon = (state: string) => {
    switch (state) {
      case "pending":
        return <Clock className="w-4 h-4 text-gray-400" />;
      case "processing":
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case "complete":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "failed":
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStateLabel = (state: string) => {
    switch (state) {
      case "pending":
        return "等待中";
      case "processing":
        return "处理中";
      case "complete":
        return "已完成";
      case "failed":
        return "失败";
      default:
        return state;
    }
  };

  const getStateColor = (state: string) => {
    switch (state) {
      case "pending":
        return "bg-gray-100 text-gray-600";
      case "processing":
        return "bg-blue-100 text-blue-600";
      case "complete":
        return "bg-green-100 text-green-600";
      case "failed":
        return "bg-red-100 text-red-600";
      default:
        return "bg-gray-100 text-gray-600";
    }
  };

  const states = ["pending", "processing", "complete", "failed"];
  const totalPages = Math.ceil(total / pageSize);

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.05 },
    },
  };

  const item = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0 },
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-400 to-violet-500 flex items-center justify-center">
              <ListTodo className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">任务管理</h1>
              <p className="text-gray-500 text-sm">监控异步任务执行状态</p>
            </div>
          </div>
          <button
            onClick={fetchTasks}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2.5 bg-violet-500 text-white rounded-xl hover:bg-violet-600 transition-colors font-medium shadow-md hover:shadow-lg disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? "animate-spin" : ""}`} />
            刷新
          </button>
        </div>
      </motion.div>

      {/* Filter */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => {
            setFilterState(null);
            setPage(1);
          }}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
            !filterState
              ? "bg-violet-500 text-white"
              : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
          }`}
        >
          全部
        </button>
        {states.map((state) => (
          <button
            key={state}
            onClick={() => {
              setFilterState(state);
              setPage(1);
            }}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors flex items-center gap-1.5 ${
              filterState === state
                ? "bg-violet-500 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            {getStateIcon(state)}
            {getStateLabel(state)}
          </button>
        ))}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {states.map((state) => {
          const count = tasks.filter((t) => t.state === state).length;
          return (
            <div
              key={state}
              className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm"
            >
              <div className="flex items-center gap-2 mb-1">
                {getStateIcon(state)}
                <span className="text-sm text-gray-500">{getStateLabel(state)}</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">{count}</div>
            </div>
          );
        })}
      </div>

      {/* Tasks List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full" />
        </div>
      ) : tasks.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16 bg-gray-50 rounded-xl"
        >
          <ListTodo className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg mb-2">暂无任务</p>
          <p className="text-gray-400 text-sm">视频生成等异步任务会显示在这里</p>
        </motion.div>
      ) : (
        <>
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-3"
          >
            {tasks.map((task) => (
              <motion.div
                key={task.task_id}
                variants={item}
                className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-medium ${getStateColor(
                          task.state
                        )}`}
                      >
                        {getStateLabel(task.state)}
                      </span>
                      <span className="text-xs text-gray-400 font-mono">
                        {task.task_id}
                      </span>
                    </div>

                    {/* Progress Bar */}
                    {task.state === "processing" && (
                      <div className="mb-3">
                        <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                          <span>进度</span>
                          <span>{task.progress}%</span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${task.progress}%` }}
                            className="h-full bg-gradient-to-r from-violet-400 to-violet-500 rounded-full"
                          />
                        </div>
                      </div>
                    )}

                    {/* Error Message */}
                    {task.error && (
                      <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
                        {task.error}
                      </div>
                    )}

                    {/* Result Preview */}
                    {task.result && Object.keys(task.result).length > 0 && (
                      <div className="mb-2">
                        <p className="text-xs text-gray-500 mb-1">结果预览：</p>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(task.result)
                            .slice(0, 3)
                            .map(([key, value]) => (
                              <span
                                key={key}
                                className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs"
                              >
                                {key}: {typeof value === "string" ? value.slice(0, 20) : JSON.stringify(value).slice(0, 20)}
                              </span>
                            ))}
                        </div>
                      </div>
                    )}

                    {/* Timestamps */}
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        创建: {new Date(task.created_at).toLocaleString("zh-CN")}
                      </span>
                      <span>更新: {new Date(task.updated_at).toLocaleString("zh-CN")}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => deleteTask(task.task_id)}
                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    title="删除任务"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </motion.div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 rounded-lg font-medium text-sm bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                上一页
              </button>
              <span className="px-4 py-2 text-sm text-gray-500">
                第 {page} / {totalPages} 页
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 rounded-lg font-medium text-sm bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default function TasksPage() {
  return (
    <SidebarNav>
      <ToastProvider>
        <TasksPageContent />
      </ToastProvider>
    </SidebarNav>
  );
}
