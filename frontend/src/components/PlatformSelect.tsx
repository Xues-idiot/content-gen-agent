"use client";

import React from "react";
import { motion } from "motion/react";

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
    color: "bg-red-50 border-red-200",
    selectedColor: "#FEE2E2",
  },
  {
    id: "tiktok",
    name: "抖音",
    icon: "📺",
    description: "短视频口播脚本",
    color: "bg-pink-50 border-pink-200",
    selectedColor: "#FCE7F3",
  },
  {
    id: "official",
    name: "公众号",
    icon: "📰",
    description: "长文、排版建议",
    color: "bg-blue-50 border-blue-200",
    selectedColor: "#DBEAFE",
  },
  {
    id: "friend_circle",
    name: "朋友圈",
    icon: "👥",
    description: "简短分享",
    color: "bg-green-50 border-green-200",
    selectedColor: "#DCFCE7",
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
      className="bg-white rounded-xl shadow-md p-6"
    >
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.15 }}
        className="flex justify-between items-center mb-4"
      >
        <h2 className="text-xl font-bold" style={{ color: "#FF6B35" }}>
          目标平台
        </h2>
        <div className="text-sm space-x-2">
          <motion.button
            type="button"
            onClick={selectAll}
            disabled={disabled}
            className="text-orange-600 hover:text-orange-800 disabled:text-gray-400 transition-colors"
            whileHover={disabled ? {} : { scale: 1.05 }}
            whileTap={disabled ? {} : { scale: 0.95 }}
          >
            全选
          </motion.button>
          <span className="text-gray-300">|</span>
          <motion.button
            type="button"
            onClick={selectNone}
            disabled={disabled}
            className="text-orange-600 hover:text-orange-800 disabled:text-gray-400 transition-colors"
            whileHover={disabled ? {} : { scale: 1.05 }}
            whileTap={disabled ? {} : { scale: 0.95 }}
          >
            取消
          </motion.button>
        </div>
      </motion.div>

      <div className="grid grid-cols-2 gap-3">
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
              transition={{ delay: 0.2 + index * 0.05 }}
              whileHover={disabled ? {} : { scale: 1.03, y: -2 }}
              whileTap={disabled ? {} : { scale: 0.97 }}
              className={`p-4 rounded-lg border-2 transition-all text-left relative ${
                isSelected
                  ? `${platform.color} ring-2 ring-orange-400 ring-opacity-50`
                  : "bg-gray-50 border-gray-200 hover:border-gray-300"
              } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
              style={{
                borderColor: isSelected ? undefined : "#E5E7EB",
              }}
            >
              <motion.div
                initial={{ backgroundColor: isSelected ? platform.selectedColor : "#F9FAFB" }}
                animate={{ backgroundColor: isSelected ? platform.selectedColor : "#F9FAFB" }}
                className="flex items-center gap-2"
              >
                <motion.span
                  whileHover={disabled ? {} : { scale: 1.2, rotate: 5 }}
                  className="text-2xl"
                >
                  {platform.icon}
                </motion.span>
                <div>
                  <div className="font-medium">{platform.name}</div>
                  <div className="text-xs text-gray-500">{platform.description}</div>
                </div>
              </motion.div>
              {isSelected && (
                <motion.div
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0, opacity: 0 }}
                  className="absolute top-2 right-2 w-5 h-5 bg-orange-500 rounded-full flex items-center justify-center"
                >
                  <span className="text-white text-xs">✓</span>
                </motion.div>
              )}
            </motion.button>
          );
        })}
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.45 }}
        className="mt-4 text-sm text-gray-600"
      >
        已选择:{" "}
        <motion.span
          key={selected.length}
          initial={{ scale: 1.3, color: "#FF6B35" }}
          animate={{ scale: 1, color: "#4B5563" }}
          className="font-bold"
          style={{ color: "#FF6B35" }}
        >
          {selected.length}
        </motion.span>{" "}
        个平台
        {selected.length > 0 && (
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="ml-2"
          >
            ({PLATFORMS.filter((p) => selected.includes(p.id))
              .map((p) => p.name)
              .join(", ")})
          </motion.span>
        )}
      </motion.div>
    </motion.div>
  );
}
