"use client";

import React from "react";
import { motion } from "motion/react";
import { Check, Layers } from "lucide-react";

interface PlatformSelectProps {
  selected: string[];
  onChange: (platforms: string[]) => void;
  disabled?: boolean;
}

const PLATFORMS = [
  {
    id: "xiaohongshu",
    name: "小红书",
    icon: "📕",
    description: "种草笔记、长文案",
    color: "#EF4444",
    gradient: "from-red-500 to-rose-600",
    bgLight: "bg-red-50",
    borderLight: "border-red-200",
    selectedBg: "bg-red-50",
    selectedBorder: "border-red-400",
    checkBg: "bg-red-500",
    tagBg: "bg-red-100",
    tagText: "text-red-700",
  },
  {
    id: "tiktok",
    name: "抖音",
    icon: "📺",
    description: "短视频口播脚本",
    color: "#EC4899",
    gradient: "from-pink-500 to-fuchsia-600",
    bgLight: "bg-pink-50",
    borderLight: "border-pink-200",
    selectedBg: "bg-pink-50",
    selectedBorder: "border-pink-400",
    checkBg: "bg-pink-500",
    tagBg: "bg-pink-100",
    tagText: "text-pink-700",
  },
  {
    id: "official",
    name: "公众号",
    icon: "📰",
    description: "长文、排版建议",
    color: "#3B82F6",
    gradient: "from-blue-500 to-indigo-600",
    bgLight: "bg-blue-50",
    borderLight: "border-blue-200",
    selectedBg: "bg-blue-50",
    selectedBorder: "border-blue-400",
    checkBg: "bg-blue-500",
    tagBg: "bg-blue-100",
    tagText: "text-blue-700",
  },
  {
    id: "friend_circle",
    name: "朋友圈",
    icon: "👥",
    description: "简短分享",
    color: "#10B981",
    gradient: "from-emerald-500 to-teal-600",
    bgLight: "bg-emerald-50",
    borderLight: "border-emerald-200",
    selectedBg: "bg-emerald-50",
    selectedBorder: "border-emerald-400",
    checkBg: "bg-emerald-500",
    tagBg: "bg-emerald-100",
    tagText: "text-emerald-700",
  },
];

export default function PlatformSelect({
  selected,
  onChange,
  disabled = false,
}: PlatformSelectProps) {
  const togglePlatform = (id: string) => {
    if (disabled) return;

    if (selected.includes(id)) {
      onChange(selected.filter((p) => p !== id));
    } else {
      onChange([...selected, id]);
    }
  };

  const selectAll = () => {
    if (disabled) return;
    onChange(PLATFORMS.map((p) => p.id));
  };

  const selectNone = () => {
    if (disabled) return;
    onChange([]);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="card card-elevated overflow-hidden"
    >
      {/* Header */}
      <div className="px-6 py-5 border-b border-neutral-200/50 bg-gradient-to-r from-neutral-50 to-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-md shadow-violet-500/20">
              <Layers className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-display text-lg font-bold text-neutral-900">
                目标平台
              </h2>
              <p className="text-xs text-neutral-500">选择要生成的平台</p>
            </div>
          </div>

          {/* Quick Actions */}
          {!disabled && (
            <div className="flex items-center gap-2">
              <motion.button
                type="button"
                onClick={selectAll}
                className="text-xs font-medium text-violet-600 hover:text-violet-800 px-2 py-1 rounded-lg hover:bg-violet-50 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                全选
              </motion.button>
              <span className="text-neutral-300">|</span>
              <motion.button
                type="button"
                onClick={selectNone}
                className="text-xs font-medium text-neutral-500 hover:text-neutral-700 px-2 py-1 rounded-lg hover:bg-neutral-100 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                取消
              </motion.button>
            </div>
          )}
        </div>
      </div>

      {/* Platform Grid */}
      <div className="p-6">
        <div className="grid grid-cols-2 gap-4">
          {PLATFORMS.map((platform, index) => {
            const isSelected = selected.includes(platform.id);
            return (
              <motion.button
                key={platform.id}
                type="button"
                onClick={() => togglePlatform(platform.id)}
                disabled={disabled}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.15 + index * 0.05 }}
                whileHover={disabled ? {} : { scale: 1.02, y: -2 }}
                whileTap={disabled ? {} : { scale: 0.98 }}
                className={`
                  relative p-4 rounded-xl border-2 transition-all duration-300 text-left
                  ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
                  ${isSelected
                    ? `${platform.selectedBg} ${platform.selectedBorder} shadow-lg`
                    : `${platform.bgLight} ${platform.borderLight} hover:${platform.borderLight}`
                  }
                `}
              >
                {/* Selection Indicator */}
                {isSelected && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className={`absolute top-2 right-2 w-5 h-5 ${platform.checkBg} rounded-full flex items-center justify-center shadow-md`}
                  >
                    <Check className="w-3 h-3 text-white" strokeWidth={3} />
                  </motion.div>
                )}

                {/* Platform Icon */}
                <motion.div
                  whileHover={disabled ? {} : { scale: 1.1, rotate: 3 }}
                  className={`
                    w-12 h-12 rounded-xl flex items-center justify-center text-xl mb-3
                    ${isSelected
                      ? `bg-gradient-to-br ${platform.gradient} shadow-lg`
                      : "bg-white shadow-sm"
                    }
                  `}
                >
                  {platform.icon}
                </motion.div>

                {/* Platform Name */}
                <div
                  className={`font-semibold text-base mb-1 ${
                    isSelected ? platform.tagText : "text-neutral-700"
                  }`}
                >
                  {platform.name}
                </div>

                {/* Platform Description */}
                <div className="text-xs text-neutral-500">
                  {platform.description}
                </div>

                {/* Hover Gradient Overlay */}
                {!isSelected && !disabled && (
                  <div
                    className={`absolute inset-0 rounded-xl bg-gradient-to-br ${platform.gradient} opacity-0 hover:opacity-5 transition-opacity duration-300`}
                  />
                )}
              </motion.button>
            );
          })}
        </div>

        {/* Selection Summary */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-5 p-4 rounded-xl bg-gradient-to-br from-neutral-50 to-neutral-100/50 border border-neutral-200/50"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-neutral-600">
              已选择平台
            </span>
            <motion.span
              key={selected.length}
              initial={{ scale: 1.3, color: "#5B21B6" }}
              animate={{ scale: 1, color: "#5B21B6" }}
              className="text-display-sm font-bold text-violet-600"
            >
              {selected.length}
            </motion.span>
          </div>

          {selected.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="mt-3 flex flex-wrap gap-2"
            >
              {PLATFORMS.filter((p) => selected.includes(p.id)).map((platform) => (
                <motion.span
                  key={platform.id}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className={`
                    inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium
                    ${platform.tagBg} ${platform.tagText}
                  `}
                >
                  {platform.icon}
                  {platform.name}
                </motion.span>
              ))}
            </motion.div>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
}
