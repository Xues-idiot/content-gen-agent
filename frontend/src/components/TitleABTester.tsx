"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Sparkles, Copy, Check, ThumbsUp, TrendingUp, AlertTriangle, Lightbulb } from "lucide-react";
import { useToast } from "@/components/Toast";
import { API_BASE_URL } from "@/lib/api";

interface TitleVariation {
  title: string;
  style: string;
  emoji_used: boolean;
  length: number;
  ctr_score: number;
  engagement_score: number;
  strengths: string[];
  weaknesses: string[];
}

interface TitleABTesterProps {
  content?: string;
  platform?: string;
  productInfo?: {
    name?: string;
    description?: string;
    selling_points?: string[];
    category?: string;
  };
  onSelectTitle?: (title: string) => void;
}

export default function TitleABTester({
  content = "",
  platform = "xiaohongshu",
  productInfo,
  onSelectTitle,
}: TitleABTesterProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [variations, setVariations] = useState<TitleVariation[]>([]);
  const [bestTitle, setBestTitle] = useState<TitleVariation | null>(null);
  const [recommendation, setRecommendation] = useState("");
  const [selectedTitle, setSelectedTitle] = useState<string | null>(null);
  const [copiedTitle, setCopiedTitle] = useState<string | null>(null);
  const { showToast } = useToast();
  const isMountedRef = React.useRef(true);

  React.useEffect(() => {
    isMountedRef.current = true;
    return () => { isMountedRef.current = false; };
  }, []);

  const handleGenerate = async () => {
    if (!content.trim()) {
      showToast("请输入内容以生成标题", "warning");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/title/abtest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content, platform, amount: 6, product_info: productInfo }),
      });

      if (!isMountedRef.current) return;
      if (!response.ok) throw new Error("API error");
      const data = await response.json();

      if (!isMountedRef.current) return;
      if (data.success) {
        setVariations(data.variations || []);
        setBestTitle(data.best_title || null);
        setRecommendation(data.recommendation || "");
        showToast("标题变体生成成功！", "success");
      } else {
        showToast("生成失败，请重试", "error");
      }
    } catch {
      if (!isMountedRef.current) return;
      showToast("网络错误，请检查后端服务", "error");
    } finally {
      if (isMountedRef.current) setIsLoading(false);
    }
  };

  const copyTitle = async (title: string) => {
    await navigator.clipboard.writeText(title);
    setCopiedTitle(title);
    showToast("已复制标题", "success");
    setTimeout(() => setCopiedTitle(null), 2000);
  };

  const applyTitle = (title: string) => {
    setSelectedTitle(title);
    if (onSelectTitle) {
      onSelectTitle(title);
    }
    showToast("已应用标题", "success");
  };

  const getStyleColor = (style: string) => {
    const colors: Record<string, string> = {
      "悬念型": "bg-purple-50 border-purple-200 text-purple-700",
      "数字型": "bg-blue-50 border-blue-200 text-blue-700",
      "情感型": "bg-pink-50 border-pink-200 text-pink-700",
      "问题型": "bg-amber-50 border-amber-200 text-amber-700",
      "命令型": "bg-red-50 border-red-200 text-red-700",
      "对比型": "bg-indigo-50 border-indigo-200 text-indigo-700",
      "蹭热点型": "bg-orange-50 border-orange-200 text-orange-700",
    };
    return colors[style] || "bg-gray-50 border-gray-200 text-gray-700";
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return "text-green-600";
    if (score >= 50) return "text-orange-500";
    return "text-gray-400";
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-amber-50 to-orange-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">标题 A/B 测试</h3>
            <p className="text-xs text-gray-500">生成多个标题变体，找到最佳选择</p>
          </div>
        </div>
      </div>

      {/* Action Button */}
      <div className="p-4 border-b border-gray-100 bg-gray-50/50">
        <button
          onClick={handleGenerate}
          disabled={isLoading || !content.trim()}
          className="w-full px-4 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 text-white font-medium rounded-lg hover:from-amber-600 hover:to-orange-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
        >
          {isLoading ? "生成中..." : "生成标题变体"}
        </button>
      </div>

      {/* Results */}
      <AnimatePresence mode="wait">
        {variations.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="p-4 space-y-4"
          >
            {/* Recommendation */}
            {recommendation && (
              <div className="p-3 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl">
                <div className="flex items-center gap-2 text-green-700">
                  <Lightbulb className="w-4 h-4" />
                  <span className="text-sm font-medium">推荐</span>
                </div>
                <p className="text-sm text-green-600 mt-1">{recommendation}</p>
              </div>
            )}

            {/* Best Title Highlight */}
            {bestTitle && (
              <div className="p-4 bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-300 rounded-xl">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-amber-600">🏆 最佳标题</span>
                  <span className={`text-sm font-bold ${getScoreColor(bestTitle.ctr_score)}`}>
                    CTR: {bestTitle.ctr_score}
                  </span>
                </div>
                <p className="text-lg font-semibold text-gray-900 mb-2">{bestTitle.title}</p>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-xs border ${getStyleColor(bestTitle.style)}`}>
                    {bestTitle.style}
                  </span>
                  <button
                    onClick={() => copyTitle(bestTitle.title)}
                    className="p-1 text-gray-400 hover:text-gray-600"
                  >
                    {copiedTitle === bestTitle.title ? (
                      <Check className="w-4 h-4 text-green-500" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* All Variations */}
            <div className="space-y-3">
              <div className="text-sm font-medium text-gray-700">所有变体</div>
              {variations.map((v, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    selectedTitle === v.title
                      ? "border-blue-400 bg-blue-50"
                      : "border-gray-100 hover:border-gray-200 bg-white"
                  } ${bestTitle && v.title === bestTitle.title ? "hidden" : ""}`}
                  onClick={() => applyTitle(v.title)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{v.title}</p>
                      <div className="flex items-center gap-2 mt-1.5">
                        <span className={`px-1.5 py-0.5 rounded text-xs border ${getStyleColor(v.style)}`}>
                          {v.style}
                        </span>
                        {v.emoji_used && <span className="text-xs text-gray-400">😀 含emoji</span>}
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <div className="flex items-center gap-1">
                        <TrendingUp className="w-3.5 h-3.5 text-gray-400" />
                        <span className={`text-sm font-medium ${getScoreColor(v.ctr_score)}`}>
                          {v.ctr_score}
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <ThumbsUp className="w-3.5 h-3.5 text-gray-400" />
                        <span className={`text-sm font-medium ${getScoreColor(v.engagement_score)}`}>
                          {v.engagement_score}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Strengths & Weaknesses */}
                  <div className="mt-2 flex gap-4 text-xs">
                    {v.strengths.length > 0 && (
                      <div className="text-green-600">
                        ✓ {v.strengths[0]}
                      </div>
                    )}
                    {v.weaknesses.length > 0 && (
                      <div className="text-orange-500">
                        ⚠ {v.weaknesses[0]}
                      </div>
                    )}
                  </div>

                  {/* Copy Button */}
                  <div className="mt-2 flex justify-end">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        copyTitle(v.title);
                      }}
                      className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
                    >
                      {copiedTitle === v.title ? (
                        <Check className="w-3.5 h-3.5 text-green-500" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty State */}
      {!isLoading && variations.length === 0 && (
        <div className="p-8 text-center">
          <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-gray-100 flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-gray-400" />
          </div>
          <p className="text-sm text-gray-500">点击按钮生成多个标题变体</p>
          <p className="text-xs text-gray-400 mt-1">AI 将为内容生成不同风格的标题</p>
        </div>
      )}
    </div>
  );
}