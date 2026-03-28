"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Copy,
  Check,
  Eye,
  EyeOff,
  ThumbsUp,
  ThumbsDown,
  AlertTriangle,
  Lightbulb,
  Image,
  MessageSquare,
  Sparkles,
} from "lucide-react";

interface CopyResult {
  platform: string;
  title: string;
  content: string;
  script?: string;
  cta?: string;
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

const PLATFORM_INFO: Record<string, {
  name: string;
  icon: string;
  color: string;
  gradient: string;
  bgLight: string;
  tagBg: string;
  tagText: string;
  checkBg: string;
}> = {
  xiaohongshu: {
    name: "小红书",
    icon: "📕",
    color: "#EF4444",
    gradient: "from-red-500 to-rose-600",
    bgLight: "bg-red-50",
    tagBg: "bg-red-100",
    tagText: "text-red-700",
    checkBg: "bg-red-500",
  },
  tiktok: {
    name: "抖音",
    icon: "📺",
    color: "#EC4899",
    gradient: "from-pink-500 to-fuchsia-600",
    bgLight: "bg-pink-50",
    tagBg: "bg-pink-100",
    tagText: "text-pink-700",
    checkBg: "bg-pink-500",
  },
  official: {
    name: "公众号",
    icon: "📰",
    color: "#3B82F6",
    gradient: "from-blue-500 to-indigo-600",
    bgLight: "bg-blue-50",
    tagBg: "bg-blue-100",
    tagText: "text-blue-700",
    checkBg: "bg-blue-500",
  },
  friend_circle: {
    name: "朋友圈",
    icon: "👥",
    color: "#10B981",
    gradient: "from-emerald-500 to-teal-600",
    bgLight: "bg-emerald-50",
    tagBg: "bg-emerald-100",
    tagText: "text-emerald-700",
    checkBg: "bg-emerald-500",
  },
};

export default function CopyOutput({ results }: CopyOutputProps) {
  const [copiedPlatform, setCopiedPlatform] = useState<string | null>(null);
  const [previewPlatform, setPreviewPlatform] = useState<string | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const handleCopy = async (platform: string, text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      setCopiedPlatform(platform);
      timeoutRef.current = setTimeout(() => setCopiedPlatform(null), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 8) return "#059669";
    if (score >= 6) return "#D97706";
    return "#DC2626";
  };

  if (results.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card card-bordered p-12 text-center"
      >
        <motion.div
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{ duration: 2, repeat: Infinity }}
          className="w-20 h-20 rounded-2xl bg-gradient-to-br from-neutral-100 to-neutral-200 flex items-center justify-center mx-auto mb-6"
        >
          <MessageSquare className="w-10 h-10 text-neutral-400" />
        </motion.div>
        <h3 className="font-display text-lg font-bold text-neutral-900 mb-2">
          等待生成内容
        </h3>
        <p className="text-neutral-500 text-sm max-w-sm mx-auto">
          填写产品信息并选择平台后，点击"开始生成内容"按钮
        </p>
        <div className="mt-6 flex items-center justify-center gap-2">
          <div className="px-3 py-1.5 rounded-full bg-violet-50 text-violet-600 text-xs font-medium">
            智能文案
          </div>
          <div className="px-3 py-1.5 rounded-full bg-orange-50 text-orange-600 text-xs font-medium">
            违规检测
          </div>
          <div className="px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-600 text-xs font-medium">
            质量评分
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="space-y-6">
      <AnimatePresence>
        {results.map((result, index) => {
          const info = PLATFORM_INFO[result.platform] || {
            name: result.platform,
            icon: "📄",
            color: "#78716C",
            gradient: "from-stone-500 to-neutral-600",
            bgLight: "bg-stone-50",
            tagBg: "bg-stone-100",
            tagText: "text-stone-700",
            checkBg: "bg-stone-500",
          };

          return (
            <motion.div
              key={result.platform}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="card card-elevated overflow-hidden"
            >
              {/* Header */}
              <div
                className={`px-6 py-4 border-b border-neutral-200/50 ${
                  info.bgLight
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {/* Platform Icon */}
                    <motion.div
                      whileHover={{ scale: 1.1, rotate: 3 }}
                      className={`w-11 h-11 rounded-xl bg-gradient-to-br ${info.gradient} flex items-center justify-center text-xl shadow-lg`}
                    >
                      {info.icon}
                    </motion.div>

                    {/* Platform Name */}
                    <div>
                      <h3
                        className="font-display text-lg font-bold"
                        style={{ color: info.color }}
                      >
                        {info.name}
                      </h3>
                      <p className="text-xs text-neutral-500">内容已生成</p>
                    </div>

                    {/* Review Badge */}
                    {result.success && result.review && (
                      <motion.span
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: "spring", delay: 0.2 }}
                        className={`
                          ml-2 px-3 py-1 rounded-full text-xs font-semibold
                          flex items-center gap-1
                          ${result.review.passed
                            ? "bg-emerald-100 text-emerald-700"
                            : "bg-amber-100 text-amber-700"
                          }
                        `}
                      >
                        {result.review.passed ? (
                          <>
                            <ThumbsUp className="w-3 h-3" />
                            审核通过
                          </>
                        ) : (
                          <>
                            <AlertTriangle className="w-3 h-3" />
                            需修改
                          </>
                        )}
                      </motion.span>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center gap-2">
                    {result.success && (
                      <>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() =>
                            setPreviewPlatform(
                              previewPlatform === result.platform ? null : result.platform
                            )
                          }
                          className={`
                            btn btn-sm flex items-center gap-1.5
                            ${previewPlatform === result.platform
                              ? "gradient-brand text-white"
                              : "bg-white border border-neutral-200 text-neutral-600 hover:bg-neutral-50"
                            }
                          `}
                        >
                          {previewPlatform === result.platform ? (
                            <>
                              <EyeOff className="w-4 h-4" />
                              隐藏
                            </>
                          ) : (
                            <>
                              <Eye className="w-4 h-4" />
                              预览
                            </>
                          )}
                        </motion.button>

                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() =>
                            handleCopy(
                              result.platform,
                              `${result.title || ""}\n\n${result.content || ""}`
                            )
                          }
                          className={`
                            btn btn-sm flex items-center gap-1.5
                            ${copiedPlatform === result.platform
                              ? `${info.gradient} text-white`
                              : "bg-white border border-neutral-200 text-neutral-600 hover:bg-neutral-50"
                            }
                          `}
                        >
                          {copiedPlatform === result.platform ? (
                            <>
                              <Check className="w-4 h-4" />
                              已复制
                            </>
                          ) : (
                            <>
                              <Copy className="w-4 h-4" />
                              复制
                            </>
                          )}
                        </motion.button>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="p-6">
                {!result.success ? (
                  <div className="flex items-center gap-3 p-4 rounded-xl bg-red-50 border border-red-200">
                    <AlertTriangle className="w-5 h-5 text-red-500" />
                    <span className="text-red-700 font-medium">
                      生成失败: {result.error || "未知错误"}
                    </span>
                  </div>
                ) : (
                  <>
                    {/* Title */}
                    {result.title && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.2 }}
                        className="mb-5"
                      >
                        <label className="text-label text-neutral-400 mb-2 block">
                          标题
                        </label>
                        <p
                          className="text-xl font-bold leading-snug"
                          style={{ color: info.color }}
                        >
                          {result.title}
                        </p>
                      </motion.div>
                    )}

                    {/* Script (for TikTok) */}
                    {result.script && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.25 }}
                        className="mb-5"
                      >
                        <label className="text-label text-neutral-400 mb-2 flex items-center gap-1.5">
                          <span className="w-5 h-5 rounded bg-pink-100 flex items-center justify-center">
                            <span className="text-pink-600 text-xs">🎤</span>
                          </span>
                          口播脚本
                        </label>
                        <div className="p-4 rounded-xl bg-neutral-900 text-neutral-100 font-mono text-sm leading-relaxed whitespace-pre-wrap">
                          {result.script}
                        </div>
                      </motion.div>
                    )}

                    {/* CTA (Call-to-Action) */}
                    {result.cta && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                        className="mb-5"
                      >
                        <label className="text-label text-neutral-400 mb-2 flex items-center gap-1.5">
                          <Sparkles className="w-4 h-4 text-orange-500" />
                          行动号召
                        </label>
                        <div
                          className={`p-4 rounded-xl border-2 border-dashed ${info.tagBg}`}
                          style={{ borderColor: info.color }}
                        >
                          <p className="font-semibold text-neutral-800">
                            {result.cta}
                          </p>
                        </div>
                      </motion.div>
                    )}

                    {/* Main Content */}
                    {result.content && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.35 }}
                        className="mb-5"
                      >
                        <label className="text-label text-neutral-400 mb-2 block">
                          正文内容
                        </label>
                        <div className="prose prose-neutral max-w-none text-neutral-700 leading-relaxed whitespace-pre-wrap">
                          {result.content}
                        </div>
                      </motion.div>
                    )}

                    {/* Tags */}
                    {result.tags && result.tags.length > 0 && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.4 }}
                        className="mb-5"
                      >
                        <label className="text-label text-neutral-400 mb-3 block flex items-center gap-1.5">
                          <span className="text-neutral-400">#</span> 标签
                        </label>
                        <div className="flex flex-wrap gap-2">
                          {result.tags.map((tag, idx) => (
                            <motion.span
                              key={idx}
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ delay: 0.45 + idx * 0.05 }}
                              whileHover={{ scale: 1.05, y: -2 }}
                              className={`
                                px-3 py-1.5 rounded-full text-sm font-medium
                                ${info.tagBg} ${info.tagText}
                              `}
                            >
                              #{tag.replace("#", "")}
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
                        transition={{ delay: 0.5 }}
                        className="border-t border-neutral-200 pt-5 mt-5"
                      >
                        <label className="text-label text-neutral-400 mb-3 block flex items-center gap-1.5">
                          <Lightbulb className="w-4 h-4 text-amber-500" />
                          审核结果
                        </label>

                        <div
                          className={`rounded-xl p-5 space-y-4 ${
                            info.bgLight
                          }`}
                        >
                          {/* Quality Score */}
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-neutral-600">
                              质量评分
                            </span>
                            <div className="flex items-center gap-3">
                              <div className="w-32 h-2 rounded-full bg-white overflow-hidden">
                                <motion.div
                                  initial={{ width: 0 }}
                                  animate={{
                                    width: `${(result.review?.qualityScore || 0) * 10}%`,
                                  }}
                                  transition={{ delay: 0.6, duration: 0.5 }}
                                  className="h-full rounded-full"
                                  style={{
                                    backgroundColor: getScoreColor(result.review?.qualityScore || 0),
                                  }}
                                />
                              </div>
                              <span
                                className="font-bold text-sm w-12 text-right"
                                style={{
                                  color: getScoreColor(result.review?.qualityScore || 0),
                                }}
                              >
                                {(result.review?.qualityScore || 0).toFixed(1)}/10
                              </span>
                            </div>
                          </div>

                          {/* Violations */}
                          {result.review?.violations &&
                            result.review.violations.length > 0 && (
                              <div className="pt-4 border-t border-red-200/50">
                                <div className="flex items-center gap-2 mb-2">
                                  <AlertTriangle className="w-4 h-4 text-red-500" />
                                  <span className="text-sm font-semibold text-red-700">
                                    违规词 ({result.review.violations.length})
                                  </span>
                                </div>
                                <ul className="space-y-2">
                                  {result.review.violations.map((v, idx) => (
                                    <li
                                      key={idx}
                                      className="flex items-center gap-2 text-sm"
                                    >
                                      <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
                                      <span className="font-semibold text-red-600">
                                        {v.word}
                                      </span>
                                      <span className="text-neutral-400">→</span>
                                      <span className="text-neutral-600">
                                        {v.suggestion}
                                      </span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                          {/* Suggestions */}
                          {result.review?.suggestions &&
                            result.review.suggestions.length > 0 && (
                              <div className="pt-4 border-t border-blue-200/50">
                                <div className="flex items-center gap-2 mb-2">
                                  <Lightbulb className="w-4 h-4 text-blue-500" />
                                  <span className="text-sm font-semibold text-blue-700">
                                    改进建议
                                  </span>
                                </div>
                                <ul className="space-y-2">
                                  {result.review.suggestions.slice(0, 3).map((s, idx) => (
                                    <li
                                      key={idx}
                                      className="flex items-start gap-2 text-sm text-neutral-600"
                                    >
                                      <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5" />
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
                          transition={{ delay: 0.55 }}
                          className="border-t border-neutral-200 pt-5 mt-5"
                        >
                          <label className="text-label text-neutral-400 mb-3 block flex items-center gap-1.5">
                            <Image className="w-4 h-4 text-violet-500" />
                            配图建议
                          </label>
                          <ul className="space-y-2">
                            {result.imageSuggestions.map((img, idx) => (
                              <motion.li
                                key={idx}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.6 + idx * 0.05 }}
                                className="flex items-start gap-2 p-3 rounded-lg bg-neutral-50 border border-neutral-200/50"
                              >
                                <span className="w-5 h-5 rounded bg-violet-100 flex items-center justify-center flex-shrink-0">
                                  <span className="text-violet-600 text-xs">{idx + 1}</span>
                                </span>
                                <span className="text-sm text-neutral-700">{img}</span>
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
