"use client";

import { motion } from "framer-motion";
import { Lightbulb, Clock, Hash, MessageSquare } from "lucide-react";
import { useState } from "react";
import { API_BASE_URL } from "@/lib/api";

interface PlatformPractices {
  name: string;
  optimal_length: string;
  hashtag_format: string;
  emoji_usage: string;
  best_posting_times: string[];
  tips: string[];
}

interface PlatformBestPracticesProps {
  initialPlatform?: string;
}

const platformColors = {
  xiaohongshu: {
    bg: "bg-gradient-to-br from-pink-500 to-rose-600",
    light: "bg-pink-50 border-pink-200",
    text: "text-pink-700",
  },
  tiktok: {
    bg: "bg-gradient-to-br from-gray-900 to-black",
    light: "bg-gray-100 border-gray-200",
    text: "text-gray-700",
  },
  official: {
    bg: "bg-gradient-to-br from-blue-500 to-blue-700",
    light: "bg-blue-50 border-blue-200",
    text: "text-blue-700",
  },
  friend_circle: {
    bg: "bg-gradient-to-br from-green-500 to-emerald-600",
    light: "bg-green-50 border-green-200",
    text: "text-green-700",
  },
};

const platformLabels = {
  xiaohongshu: "小红书",
  tiktok: "抖音",
  official: "公众号",
  friend_circle: "朋友圈",
};

export default function PlatformBestPractices({ initialPlatform = "xiaohongshu" }: PlatformBestPracticesProps) {
  const [selectedPlatform, setSelectedPlatform] = useState(initialPlatform);
  const [practices, setPractices] = useState<PlatformPractices | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchPractices = async (platform: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/best-practices/${platform}`);
      const data = await response.json();
      if (data.success) {
        setPractices(data.practices);
      }
    } catch (error) {
      console.error("Failed to fetch practices:", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePlatformChange = (platform: string) => {
    setSelectedPlatform(platform);
    fetchPractices(platform);
  };

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
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center">
          <Lightbulb className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-gray-900">平台最佳实践</h2>
          <p className="text-sm text-gray-500">各平台内容创作建议</p>
        </div>
      </div>

      {/* Platform Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {Object.entries(platformLabels).map(([key, label]) => (
          <button
            key={key}
            onClick={() => handlePlatformChange(key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
              selectedPlatform === key
                ? `${platformColors[key as keyof typeof platformColors].bg} text-white shadow-lg`
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full" />
        </div>
      ) : practices ? (
        <motion.div
          key={selectedPlatform}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Platform Name */}
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl ${platformColors[selectedPlatform as keyof typeof platformColors].light} ${platformColors[selectedPlatform as keyof typeof platformColors].text}`}>
            <span className="font-semibold">{practices.name}</span>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <motion.div
              variants={item}
              className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm"
            >
              <div className="text-xs text-gray-500 mb-1">最佳内容长度</div>
              <div className="font-medium text-gray-900">{practices.optimal_length}</div>
            </motion.div>
            <motion.div
              variants={item}
              className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm"
            >
              <div className="text-xs text-gray-500 mb-1">标签格式</div>
              <div className="font-medium text-gray-900">{practices.hashtag_format || "无"}</div>
            </motion.div>
            <motion.div
              variants={item}
              className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm"
            >
              <div className="text-xs text-gray-500 mb-1">Emoji使用</div>
              <div className="font-medium text-gray-900">{practices.emoji_usage}</div>
            </motion.div>
            <motion.div
              variants={item}
              className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm"
            >
              <div className="text-xs text-gray-500 mb-1">最佳发布时段</div>
              <div className="font-medium text-gray-900">{practices.best_posting_times.length}个</div>
            </motion.div>
          </div>

          {/* Best Posting Times */}
          <motion.div variants={item} className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <Clock className="w-4 h-4 text-orange-500" />
              <h3 className="font-semibold text-gray-900">最佳发布时间</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {practices.best_posting_times.map((time, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1.5 bg-orange-50 text-orange-700 rounded-lg text-sm font-medium"
                >
                  {time}
                </span>
              ))}
            </div>
          </motion.div>

          {/* Tips */}
          <motion.div variants={item} className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <Hash className="w-4 h-4 text-orange-500" />
              <h3 className="font-semibold text-gray-900">创作建议</h3>
            </div>
            <motion.ul
              variants={container}
              initial="hidden"
              animate="show"
              className="space-y-2"
            >
              {practices.tips.map((tip, idx) => (
                <motion.li
                  key={idx}
                  variants={item}
                  className="flex items-start gap-2 text-sm text-gray-600"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-2 flex-shrink-0" />
                  {tip}
                </motion.li>
              ))}
            </motion.ul>
          </motion.div>
        </motion.div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-xl">
          <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">选择平台查看最佳实践</p>
        </div>
      )}
    </motion.div>
  );
}