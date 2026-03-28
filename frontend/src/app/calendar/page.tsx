"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import SidebarNav from "@/components/SidebarNav";
import { ToastProvider, useToast } from "@/components/Toast";
import ContentCalendar from "@/components/ContentCalendar";
import { Calendar, Plus, X } from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

function CalendarPageContent() {
  const { showToast } = useToast();
  const [showScheduleModal, setShowScheduleModal] = useState(false);

  // Form state for new schedule
  const [formData, setFormData] = useState({
    product_name: "",
    platform: "xiaohongshu",
    title: "",
    content: "",
    tags: "",
    scheduled_time: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    return () => { isMountedRef.current = false; };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title || !formData.content) {
      showToast("请填写标题和内容", "error");
      return;
    }

    if (!isMountedRef.current) return;
    setSubmitting(true);
    try {
      const params = new URLSearchParams({
        product_name: formData.product_name,
        platform: formData.platform,
        title: formData.title,
        content: formData.content,
        scheduled_time: formData.scheduled_time || new Date().toISOString(),
      });
      // Append tags individually for proper array handling (backend expects tags=tag1&tags=tag2)
      if (formData.tags) {
        formData.tags.split(",").forEach(tag => params.append("tags", tag.trim()));
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/schedule?${params}`, {
        method: "POST",
      });

      if (response.ok) {
        showToast("计划已添加", "success");
        if (isMountedRef.current) {
          setShowScheduleModal(false);
          setFormData({
            product_name: "",
            platform: "xiaohongshu",
            title: "",
            content: "",
            tags: "",
            scheduled_time: "",
          });
        }
      } else {
        showToast("添加失败", "error");
      }
    } catch {
      showToast("网络错误", "error");
    } finally {
      if (isMountedRef.current) setSubmitting(false);
    }
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
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-400 to-orange-500 flex items-center justify-center">
              <Calendar className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">内容日历</h1>
              <p className="text-gray-500 text-sm">管理计划发布的内容和发布时段</p>
            </div>
          </div>
          <button
            onClick={() => setShowScheduleModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 bg-orange-500 text-white rounded-xl hover:bg-orange-600 transition-colors font-medium shadow-md hover:shadow-lg"
          >
            <Plus className="w-5 h-5" />
            新建计划
          </button>
        </div>
      </motion.div>

      {/* Calendar Component */}
      <ContentCalendar onScheduleNew={() => setShowScheduleModal(true)} />

      {/* Schedule Modal */}
      <AnimatePresence>
        {showScheduleModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div
              className="absolute inset-0 bg-black/30"
              onClick={() => setShowScheduleModal(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between p-5 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">新建发布计划</h2>
                <button
                  onClick={() => setShowScheduleModal(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="p-5 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    产品名称
                  </label>
                  <input
                    type="text"
                    value={formData.product_name}
                    onChange={(e) =>
                      setFormData({ ...formData, product_name: e.target.value })
                    }
                    placeholder="例如：智能睡眠枕"
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-orange-300 focus:ring-2 focus:ring-orange-100 outline-none transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    目标平台
                  </label>
                  <select
                    value={formData.platform}
                    onChange={(e) =>
                      setFormData({ ...formData, platform: e.target.value })
                    }
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-orange-300 focus:ring-2 focus:ring-orange-100 outline-none transition-all"
                  >
                    <option value="xiaohongshu">小红书</option>
                    <option value="tiktok">抖音</option>
                    <option value="official">公众号</option>
                    <option value="friend_circle">朋友圈</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    内容标题
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) =>
                      setFormData({ ...formData, title: e.target.value })
                    }
                    placeholder="输入标题..."
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-orange-300 focus:ring-2 focus:ring-orange-100 outline-none transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    内容正文
                  </label>
                  <textarea
                    value={formData.content}
                    onChange={(e) =>
                      setFormData({ ...formData, content: e.target.value })
                    }
                    placeholder="输入内容..."
                    rows={4}
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-orange-300 focus:ring-2 focus:ring-orange-100 outline-none transition-all resize-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    标签（逗号分隔）
                  </label>
                  <input
                    type="text"
                    value={formData.tags}
                    onChange={(e) =>
                      setFormData({ ...formData, tags: e.target.value })
                    }
                    placeholder="例如：睡眠, 健康, 科技"
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-orange-300 focus:ring-2 focus:ring-orange-100 outline-none transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    计划发布时间
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.scheduled_time}
                    onChange={(e) =>
                      setFormData({ ...formData, scheduled_time: e.target.value })
                    }
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-orange-300 focus:ring-2 focus:ring-orange-100 outline-none transition-all"
                  />
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowScheduleModal(false)}
                    className="flex-1 px-4 py-2.5 border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors font-medium"
                  >
                    取消
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="flex-1 px-4 py-2.5 bg-orange-500 text-white rounded-xl hover:bg-orange-600 transition-colors font-medium disabled:opacity-50"
                  >
                    {submitting ? "提交中..." : "添加计划"}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function CalendarPage() {
  return (
    <SidebarNav>
      <ToastProvider>
        <CalendarPageContent />
      </ToastProvider>
    </SidebarNav>
  );
}
