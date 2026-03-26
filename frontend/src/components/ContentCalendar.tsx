"use client";

import { motion } from "framer-motion";
import { Calendar, Clock, Trash2, CheckCircle } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { API_BASE_URL } from "@/lib/api";

interface ScheduledContent {
  id: string;
  product_name: string;
  platform: string;
  title: string;
  content: string;
  tags: string[];
  scheduled_time: string;
  status: string;
  created_at: string;
}

interface ContentCalendarProps {
  onScheduleNew?: () => void;
}

const platformColors = {
  xiaohongshu: "bg-pink-100 text-pink-700 border-pink-200",
  tiktok: "bg-black text-white border-gray-800",
  official: "bg-blue-100 text-blue-700 border-blue-200",
  friend_circle: "bg-green-100 text-green-700 border-green-200",
};

const platformLabels = {
  xiaohongshu: "小红书",
  tiktok: "抖音",
  official: "公众号",
  friend_circle: "朋友圈",
};

export default function ContentCalendar({ onScheduleNew }: ContentCalendarProps) {
  const [scheduledContent, setScheduledContent] = useState<ScheduledContent[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterPlatform, setFilterPlatform] = useState<string | null>(null);
  const isMountedRef = useRef(true);

  const fetchCalendar = async () => {
    if (!isMountedRef.current) return;
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterPlatform) params.append("platform", filterPlatform);

      const response = await fetch(`${API_BASE_URL}/api/v1/calendar?${params}`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      if (isMountedRef.current && data.success) {
        setScheduledContent(data.scheduled_content || []);
      }
    } catch (error) {
      console.error("Failed to fetch calendar:", error);
    } finally {
      if (isMountedRef.current) setLoading(false);
    }
  };

  const deleteSchedule = async (id: string) => {
    if (!isMountedRef.current) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/schedule/${id}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        throw new Error(`删除失败: ${response.status}`);
      }
      if (isMountedRef.current) {
        setScheduledContent((prev) => prev.filter((c) => c.id !== id));
      }
    } catch (error) {
      console.error("Failed to delete schedule:", error);
    }
  };

  const markPublished = async (id: string) => {
    if (!isMountedRef.current) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/schedule/${id}/publish`, {
        method: "PUT",
      });
      if (!response.ok) {
        throw new Error(`标记发布失败: ${response.status}`);
      }
      if (isMountedRef.current) {
        setScheduledContent((prev) =>
          prev.map((c) => (c.id === id ? { ...c, status: "published" } : c))
        );
      }
    } catch (error) {
      console.error("Failed to mark published:", error);
    }
  };

  useEffect(() => {
    isMountedRef.current = true;
    return () => { isMountedRef.current = false; };
  }, []);

  const filteredContent = filterPlatform
    ? scheduledContent.filter((c) => c.platform === filterPlatform)
    : scheduledContent;

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
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
            <Calendar className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">内容日历</h2>
            <p className="text-sm text-gray-500">管理计划发布的内容</p>
          </div>
        </div>
        <button
          onClick={onScheduleNew}
          className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors text-sm font-medium"
        >
          新建计划
        </button>
      </div>

      {/* Filter */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setFilterPlatform(null)}
          className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
            !filterPlatform
              ? "bg-orange-500 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          全部
        </button>
        {Object.entries(platformLabels).map(([key, label]) => (
          <button
            key={key}
            onClick={() => setFilterPlatform(key)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              filterPlatform === key
                ? "bg-orange-500 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Calendar List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full" />
        </div>
      ) : filteredContent.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12 bg-gray-50 rounded-xl"
        >
          <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">暂无计划内容</p>
          <p className="text-sm text-gray-400 mt-1">点击"新建计划"添加内容</p>
        </motion.div>
      ) : (
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="space-y-3"
        >
          {filteredContent.map((content) => (
            <motion.div
              key={content.id}
              variants={item}
              className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium border ${
                        platformColors[content.platform as keyof typeof platformColors]
                      }`}
                    >
                      {platformLabels[content.platform as keyof typeof platformLabels]}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium ${
                        content.status === "published"
                          ? "bg-green-100 text-green-700"
                          : "bg-yellow-100 text-yellow-700"
                      }`}
                    >
                      {content.status === "published" ? "已发布" : "待发布"}
                    </span>
                  </div>
                  <h3 className="font-medium text-gray-900 truncate">{content.title}</h3>
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">{content.content}</p>
                  <div className="flex items-center gap-4 mt-3 text-xs text-gray-400">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(content.scheduled_time).toLocaleString("zh-CN")}
                    </span>
                    <span>{content.product_name}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {content.status !== "published" && (
                    <button
                      onClick={() => markPublished(content.id)}
                      className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                      title="标记已发布"
                    >
                      <CheckCircle className="w-5 h-5" />
                    </button>
                  )}
                  <button
                    onClick={() => deleteSchedule(content.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="删除"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
              {content.tags && content.tags.length > 0 && (
                <div className="flex gap-1.5 mt-3 flex-wrap">
                  {content.tags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Load Button */}
      {!loading && scheduledContent.length === 0 && (
        <button
          onClick={fetchCalendar}
          className="w-full py-3 border-2 border-dashed border-gray-200 rounded-xl text-gray-500 hover:border-orange-300 hover:text-orange-500 transition-colors"
        >
          加载现有计划
        </button>
      )}
    </motion.div>
  );
}