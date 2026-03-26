"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { copyToClipboard } from "@/lib/utils";

interface ImageSuggestion {
  type: string;
  description: string;
  prompt: string;
}

interface ImagePreviewProps {
  suggestions: Record<string, ImageSuggestion[]>;
}

const PLATFORM_INFO: Record<string, { name: string; icon: string; color: string }> = {
  xiaohongshu: { name: "小红书", icon: "📕", color: "#EF4444" },
  tiktok: { name: "抖音", icon: "📺", color: "#EC4899" },
  official: { name: "公众号", icon: "📰", color: "#3B82F6" },
  friend_circle: { name: "朋友圈", icon: "👥", color: "#10B981" },
};

export default function ImagePreview({ suggestions }: ImagePreviewProps) {
  const hasSuggestions = Object.keys(suggestions).length > 0;
  const [copiedIdx, setCopiedIdx] = useState<string | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const copyPrompt = async (prompt: string, idx: string) => {
    const success = await copyToClipboard(prompt);
    if (success) {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      setCopiedIdx(idx);
      timeoutRef.current = setTimeout(() => setCopiedIdx(null), 2000);
    }
  };

  if (!hasSuggestions) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="bg-white rounded-xl shadow-md p-8 text-center"
      >
        <motion.div
          animate={{ scale: [1, 1.1, 1], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="text-4xl mb-4"
        >
          🖼️
        </motion.div>
        <p className="text-gray-500">生成内容后，AI将提供配图建议</p>
        <p className="text-gray-400 text-sm mt-2">支持 DALL-E、Midjourney 等工具</p>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-xl shadow-md p-6"
    >
      <motion.h2
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.1 }}
        className="text-xl font-bold mb-4 flex items-center gap-2"
        style={{ color: "#FF6B35" }}
      >
        <span>🖼️</span> 配图建议
      </motion.h2>

      <div className="space-y-6">
        <AnimatePresence>
          {Object.entries(suggestions).map(([platform, images], platformIndex) => {
            const info = PLATFORM_INFO[platform] || {
              name: platform,
              icon: "📄",
              color: "#6B7280",
            };

            return (
              <motion.div
                key={platform}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: platformIndex * 0.1 }}
                className="border-b border-gray-200 pb-4 last:border-b-0 last:pb-0"
              >
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: platformIndex * 0.1 + 0.05 }}
                  className="flex items-center gap-2 mb-3"
                >
                  <motion.span
                    whileHover={{ scale: 1.2, rotate: 5 }}
                    className="text-xl"
                  >
                    {info.icon}
                  </motion.span>
                  <h3 className="font-medium" style={{ color: info.color }}>
                    {info.name}
                  </h3>
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: platformIndex * 0.1 + 0.1, type: "spring" }}
                    className="text-xs px-2 py-0.5 rounded-full text-white"
                    style={{ backgroundColor: info.color }}
                  >
                    {images.length} 张
                  </motion.span>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <AnimatePresence>
                    {images.map((img, idx) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        transition={{ delay: platformIndex * 0.1 + idx * 0.05 }}
                        whileHover={{ scale: 1.02, y: -2 }}
                        className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors cursor-default"
                      >
                        <div className="flex items-start gap-3">
                          <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ delay: platformIndex * 0.1 + idx * 0.05 + 0.1, type: "spring" }}
                            className="text-white rounded-lg px-3 py-1 text-sm font-medium shadow-sm"
                            style={{ backgroundColor: info.color }}
                          >
                            {img.type}
                          </motion.div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-gray-700 mb-2 line-clamp-2">
                              {img.description}
                            </p>
                            <motion.button
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              transition={{ delay: platformIndex * 0.1 + idx * 0.05 + 0.2 }}
                              onClick={() => copyPrompt(img.prompt, `${platform}-${idx}`)}
                              whileHover={{ scale: 1.02 }}
                              whileTap={{ scale: 0.98 }}
                              className={`text-xs px-2 py-1 rounded border text-gray-600 hover:text-gray-900 transition-colors flex items-center gap-1 ${
                                copiedIdx === `${platform}-${idx}`
                                  ? "bg-green-50 border-green-200 text-green-600"
                                  : "bg-white border-gray-200"
                              }`}
                            >
                              <span>{copiedIdx === `${platform}-${idx}` ? "✓" : "📋"}</span>
                              {copiedIdx === `${platform}-${idx}` ? "已复制" : "复制提示词"}
                            </motion.button>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="mt-4 p-4 rounded-lg flex items-start gap-2"
        style={{ backgroundColor: "#FFF8F0" }}
      >
        <span className="text-lg">💡</span>
        <p className="text-sm" style={{ color: "#FF6B35" }}>
          提示：这些是AI生成的配图建议，您可以使用 DALL-E、Midjourney
          等工具根据提示词生成实际图片
        </p>
      </motion.div>
    </motion.div>
  );
}
