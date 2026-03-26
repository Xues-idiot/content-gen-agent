"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { copyToClipboard } from "@/lib/utils";

interface CopyResult {
  platform: string;
  title: string;
  content: string;
  script?: string;
  cta?: string;  // Call-to-Action 行动号召
  tags: string[];
  imageSuggestions: string[];
  review?: {
    passed: boolean;
    qualityScore: number;
    violations: Array<{ word: string; suggestion: string; severity?: string }>;
    suggestions?: string[];
  };
  success: boolean;
  error?: string;
}

interface CopyOutputProps {
  results: CopyResult[];
}

const PLATFORM_INFO: Record<string, { name: string; icon: string; color: string; bgColor: string }> = {
  xiaohongshu: { name: "小红书", icon: "📕", color: "#EF4444", bgColor: "bg-red-50" },
  tiktok: { name: "抖音", icon: "📺", color: "#EC4899", bgColor: "bg-pink-50" },
  official: { name: "公众号", icon: "📰", color: "#3B82F6", bgColor: "bg-blue-50" },
  friend_circle: { name: "朋友圈", icon: "👥", color: "#10B981", bgColor: "bg-green-50" },
};

// Platform-specific preview components
function XiaohongshuPreview({ result }: { result: CopyResult }) {
  return (
    <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200 max-w-sm">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center">
          <span>📕</span>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-900">用户名</p>
          <p className="text-xs text-gray-500">小红书号</p>
        </div>
      </div>
      {result.title && <h3 className="font-bold text-gray-900 mb-2">{result.title}</h3>}
      <div className="text-sm text-gray-700 whitespace-pre-wrap mb-3">
        {result.content ? result.content.slice(0, 200) : ""}{result.content && result.content.length > 200 && "..."}
      </div>
      {result.tags && result.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {result.tags.slice(0, 5).map((tag, idx) => (
            <span key={idx} className="text-xs text-red-500">#{tag.replace("#", "")}</span>
          ))}
        </div>
      )}
      {result.cta && <div className="bg-red-50 rounded-lg p-3 text-sm text-red-600">{result.cta}</div>}
    </div>
  );
}

function TikTokPreview({ result }: { result: CopyResult }) {
  return (
    <div className="bg-black rounded-lg p-4 shadow-lg max-w-sm">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 rounded-full bg-pink-900 flex items-center justify-center">
          <span>📺</span>
        </div>
        <div className="text-white">
          <p className="font-medium">@用户名</p>
          <p className="text-xs text-gray-400">抖音号</p>
        </div>
      </div>
      {result.script && (
        <div className="text-white text-sm mb-3 font-mono whitespace-pre-wrap">
          {result.script.slice(0, 150)}{result.script.length > 150 && "..."}
        </div>
      )}
      {result.cta && <div className="bg-pink-600 text-white rounded-lg p-3 text-sm">{result.cta}</div>}
    </div>
  );
}

function OfficialPreview({ result }: { result: CopyResult }) {
  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 max-w-md overflow-hidden">
      <div className="p-4">
        {result.title && <h2 className="text-xl font-bold text-gray-900 mb-2">{result.title}</h2>}
        <div className="text-sm text-gray-500 mb-3">公众号名称 · 日期</div>
        <div className="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap">
          {result.content ? result.content.slice(0, 300) : ""}{result.content && result.content.length > 300 && "..."}
        </div>
      </div>
      <div className="border-t border-gray-200 p-3 bg-gray-50">
        <span className="text-xs text-gray-500">阅读全文</span>
      </div>
    </div>
  );
}

function FriendCirclePreview({ result }: { result: CopyResult }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 max-w-sm">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
          <span>👤</span>
        </div>
        <div>
          <p className="font-medium text-gray-900">微信用户</p>
          <p className="text-xs text-gray-500">刚刚</p>
        </div>
      </div>
      <div className="text-gray-800 text-sm whitespace-pre-wrap mb-3">{result.content || ""}</div>
      {result.cta && <div className="bg-green-50 rounded-lg p-3 text-sm text-green-700 mb-3">{result.cta}</div>}
      <div className="border-t border-gray-200 pt-2">
        <div className="text-xs text-gray-400 flex gap-4">
          <span>评论</span><span>赞</span><span>收藏</span>
        </div>
      </div>
    </div>
  );
}

export default function CopyOutput({ results }: CopyOutputProps) {
  const [copiedPlatform, setCopiedPlatform] = useState<string | null>(null);
  const [previewPlatform, setPreviewPlatform] = useState<string | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const handleCopy = async (platform: string, text: string) => {
    const success = await copyToClipboard(text);
    if (success) {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      setCopiedPlatform(platform);
      timeoutRef.current = setTimeout(() => setCopiedPlatform(null), 2000);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 8) return "#10B981";
    if (score >= 6) return "#F59E0B";
    return "#EF4444";
  };

  const renderPreview = (result: CopyResult) => {
    switch (result.platform) {
      case "xiaohongshu": return <XiaohongshuPreview result={result} />;
      case "tiktok": return <TikTokPreview result={result} />;
      case "official": return <OfficialPreview result={result} />;
      case "friend_circle": return <FriendCirclePreview result={result} />;
      default: return null;
    }
  };

  if (results.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl shadow-md p-8 text-center"
      >
        <motion.div
          animate={{ scale: [1, 1.1, 1], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="text-4xl mb-4"
        >
          📝
        </motion.div>
        <p className="text-gray-500">填写产品信息并选择平台后，点击"生成内容"按钮</p>
        <p className="text-gray-400 text-sm mt-2">生成的文案将显示在这里</p>
      </motion.div>
    );
  }

  return (
    <div className="space-y-4">
      <AnimatePresence>
        {results.map((result, index) => {
          const info = PLATFORM_INFO[result.platform] || {
            name: result.platform,
            icon: "📄",
            color: "#6B7280",
            bgColor: "bg-gray-50",
          };

          return (
            <motion.div
              key={result.platform}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-md overflow-hidden"
            >
              {/* Header */}
              <div
                className="px-6 py-3 border-b border-gray-200 flex justify-between items-center"
                style={{ backgroundColor: `${info.color}10` }}
              >
                <div className="flex items-center gap-3">
                  <motion.span
                    whileHover={{ scale: 1.2, rotate: 5 }}
                    className="text-2xl"
                  >
                    {info.icon}
                  </motion.span>
                  <h3 className="font-bold text-lg" style={{ color: info.color }}>
                    {info.name}
                  </h3>
                  {result.success && result.review && (
                    <motion.span
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", delay: 0.2 }}
                      className="text-xs px-2 py-1 rounded-full font-medium"
                      style={{
                        backgroundColor: result.review?.passed ? "#DCFCE7" : "#FEE2E2",
                        color: result.review?.passed ? "#166534" : "#DC2626",
                      }}
                    >
                      {result.review?.passed ? "✓ 审核通过" : "⚠ 有问题"}
                    </motion.span>
                  )}
                </div>
                <div className="flex gap-2">
                  {result.success && (
                    <>
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setPreviewPlatform(previewPlatform === result.platform ? null : result.platform)}
                        className="text-sm px-4 py-1.5 rounded-lg font-medium transition-all"
                        style={{
                          backgroundColor: previewPlatform === result.platform ? info.color : "#F3F4F6",
                          color: previewPlatform === result.platform ? "white" : "#374151",
                        }}
                      >
                        {previewPlatform === result.platform ? "📝 返回编辑" : "👁️ 预览"}
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() =>
                          handleCopy(result.platform, `${result.title || ""}\n\n${result.content || ""}`)
                        }
                        className="text-sm px-4 py-1.5 rounded-lg font-medium transition-all"
                        style={{
                          backgroundColor: copiedPlatform === result.platform ? info.color : "#F3F4F6",
                          color: copiedPlatform === result.platform ? "white" : "#374151",
                        }}
                      >
                        {copiedPlatform === result.platform ? "✓ 已复制" : "📋 复制文案"}
                      </motion.button>
                    </>
                  )}
                </div>
              </div>

              {/* Platform Preview */}
              <AnimatePresence>
                {previewPlatform === result.platform && result.success && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="border-t border-gray-200 bg-gray-50 p-6 overflow-hidden"
                  >
                    <h4 className="text-sm font-medium text-gray-500 mb-4 flex items-center gap-2">
                      <span>👁️</span> {info.name} 预览效果
                    </h4>
                    <div className="flex justify-center">{renderPreview(result)}</div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Content */}
              <div className="p-6">
                {!result.success ? (
                  <div className="text-red-500 flex items-center gap-2">
                    <span>✕</span>
                    <span>生成失败: {result.error || "未知错误"}</span>
                  </div>
                ) : (
                  <>
                    {/* Title */}
                    {result.title && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.2 }}
                        className="mb-4"
                      >
                        <h4 className="text-sm font-medium text-gray-500 mb-1">标题</h4>
                        <motion.p
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.3 }}
                          className="text-xl font-bold"
                          style={{ color: info.color }}
                        >
                          {result.title}
                        </motion.p>
                      </motion.div>
                    )}

                    {/* Script (for TikTok) */}
                    {result.script && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                        className="mb-4"
                      >
                        <h4 className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-1">
                          <span>🎤</span> 口播脚本
                        </h4>
                        <div className="bg-gray-50 p-4 rounded-lg whitespace-pre-wrap text-sm border border-gray-200">
                          {result.script}
                        </div>
                      </motion.div>
                    )}

                    {/* CTA (Call-to-Action) */}
                    {result.cta && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.35 }}
                        className="mb-4"
                      >
                        <h4 className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-1">
                          <span>📢</span> 行动号召
                        </h4>
                        <div
                          className="p-4 rounded-lg border-2 border-dashed"
                          style={{
                            backgroundColor: `${info.color}10`,
                            borderColor: info.color,
                          }}
                        >
                          <p className="text-gray-800 font-medium">{result.cta}</p>
                        </div>
                      </motion.div>
                    )}

                    {/* Main Content */}
                    {result.content && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.4 }}
                        className="mb-4"
                      >
                        <h4 className="text-sm font-medium text-gray-500 mb-1">正文</h4>
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.5 }}
                          className="prose prose-sm max-w-none whitespace-pre-wrap text-gray-700"
                        >
                          {result.content}
                        </motion.div>
                      </motion.div>
                    )}

                    {/* Tags */}
                    {result.tags && result.tags.length > 0 && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                        className="mb-4"
                      >
                        <h4 className="text-sm font-medium text-gray-500 mb-2">标签</h4>
                        <div className="flex flex-wrap gap-2">
                          {result.tags.map((tag, idx) => (
                            <motion.span
                              key={idx}
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ delay: 0.6 + idx * 0.05 }}
                              whileHover={{ scale: 1.05, y: -2 }}
                              className="px-3 py-1 rounded-full text-sm font-medium cursor-default"
                              style={{
                                backgroundColor: `${info.color}15`,
                                color: info.color,
                              }}
                            >
                              {tag}
                            </motion.span>
                          ))}
                        </div>
                      </motion.div>
                    )}

                    {/* Review Results */}
                    {result.review && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.6 }}
                        className="border-t border-gray-200 pt-4 mt-4"
                      >
                        <h4 className="text-sm font-medium text-gray-500 mb-3 flex items-center gap-1">
                          <span>🔍</span> 审核结果
                        </h4>
                        <div
                          className="rounded-lg p-4 space-y-3"
                          style={{ backgroundColor: `${info.color}08` }}
                        >
                          {/* Quality Score */}
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600">质量评分</span>
                            <motion.div
                              initial={{ scale: 0 }}
                              animate={{ scale: 1 }}
                              transition={{ delay: 0.7, type: "spring" }}
                              className="flex items-center gap-2"
                            >
                              <div
                                className="w-24 h-2 rounded-full overflow-hidden"
                                style={{ backgroundColor: "#E5E7EB" }}
                              >
                                <motion.div
                                  initial={{ width: 0 }}
                                  animate={{ width: `${(result.review?.qualityScore || 0) * 10}%` }}
                                  transition={{ delay: 0.8, duration: 0.5 }}
                                  className="h-full rounded-full"
                                  style={{ backgroundColor: getScoreColor(result.review?.qualityScore || 0) }}
                                />
                              </div>
                              <span
                                className="font-bold text-sm"
                                style={{ color: getScoreColor(result.review?.qualityScore || 0) }}
                              >
                                {(result.review?.qualityScore || 0).toFixed(1)}/10
                              </span>
                            </motion.div>
                          </div>

                          {/* Violations */}
                          {result.review?.violations &&
                            result.review.violations.length > 0 && (
                              <div className="pt-2 border-t border-gray-200">
                                <div className="text-sm font-medium text-red-600 mb-2 flex items-center gap-1">
                                  <span>⚠️</span> 违规词 ({result.review.violations.length})
                                </div>
                                <ul className="space-y-1">
                                  {result.review.violations.map((v, idx) => (
                                    <li
                                      key={idx}
                                      className="text-sm text-red-600 flex items-center gap-2"
                                    >
                                      <span className="text-red-400">•</span>
                                      <span className="font-medium">{v.word}</span>
                                      <span className="text-gray-400">→</span>
                                      <span className="text-gray-600">{v.suggestion}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                          {/* Suggestions */}
                          {result.review?.suggestions &&
                            result.review.suggestions.length > 0 && (
                              <div className="pt-2 border-t border-gray-200">
                                <div className="text-sm font-medium text-blue-600 mb-2 flex items-center gap-1">
                                  <span>💡</span> 改进建议
                                </div>
                                <ul className="space-y-1">
                                  {result.review.suggestions.slice(0, 3).map((s, idx) => (
                                    <li
                                      key={idx}
                                      className="text-sm text-gray-600 flex items-start gap-2"
                                    >
                                      <span className="text-blue-400">•</span>
                                      {s}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                        </div>
                      </motion.div>
                    )}

                    {/* Image Suggestions */}
                    {result.imageSuggestions &&
                      result.imageSuggestions.length > 0 && (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.7 }}
                          className="border-t border-gray-200 pt-4 mt-4"
                        >
                          <h4 className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-1">
                            <span>🖼️</span> 配图建议
                          </h4>
                          <ul className="space-y-2">
                            {result.imageSuggestions.map((img, idx) => (
                              <motion.li
                                key={idx}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.8 + idx * 0.05 }}
                                className="text-sm text-gray-700 flex items-start gap-2 bg-gray-50 p-2 rounded"
                              >
                                <span style={{ color: info.color }}>•</span>
                                <span>{img}</span>
                              </motion.li>
                            ))}
                          </ul>
                        </motion.div>
                      )}
                  </>
                )}
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
