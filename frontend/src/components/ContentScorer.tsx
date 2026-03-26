"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Star, ThumbsUp, AlertTriangle, Lightbulb, Loader2, CheckCircle2 } from "lucide-react";
import { useToast } from "@/components/Toast";
import { API_BASE_URL } from "@/lib/api";

interface ContentScorerProps {
  content?: string;
  title?: string;
  platform?: string;
  tags?: string[];
  onScoreCalculated?: (score: number) => void;
}

interface ScoreResult {
  overall_score: number;
  engagement_score: number;
  compliance_score: number;
  readability_score: number;
  seo_score: number;
  platform_fit_score: number;
  score_level: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
}

const DIMENSIONS = [
  { key: "engagement_score", name: "吸引力", color: "from-red-400 to-pink-500", icon: "🔥" },
  { key: "compliance_score", name: "合规性", color: "from-green-400 to-emerald-500", icon: "✅" },
  { key: "readability_score", name: "可读性", color: "from-blue-400 to-cyan-500", icon: "📖" },
  { key: "seo_score", name: "SEO友好", color: "from-purple-400 to-violet-500", icon: "🔍" },
  { key: "platform_fit_score", name: "平台适配", color: "from-amber-400 to-orange-500", icon: "📱" },
];

export default function ContentScorer({
  content = "",
  title = "",
  platform = "xiaohongshu",
  tags = [],
  onScoreCalculated,
}: ContentScorerProps) {
  const [isScoring, setIsScoring] = useState(false);
  const [scoreResult, setScoreResult] = useState<ScoreResult | null>(null);
  const { showToast } = useToast();
  const isMountedRef = React.useRef(true);

  React.useEffect(() => {
    isMountedRef.current = true;
    return () => { isMountedRef.current = false; };
  }, []);

  const handleScore = async () => {
    if (!content.trim()) {
      showToast("请输入内容进行评分", "warning");
      return;
    }

    setIsScoring(true);
    setScoreResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/content/score`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content, platform, title, tags }),
      });

      if (!isMountedRef.current) return;
      if (!response.ok) throw new Error("API error");
      const data = await response.json();

      if (!isMountedRef.current) return;
      if (data.success) {
        setScoreResult(data);
        showToast("评分完成！", "success");
        onScoreCalculated?.(data.overall_score);
      } else {
        showToast("评分失败，请重试", "error");
      }
    } catch {
      if (!isMountedRef.current) return;
      showToast("网络错误，请检查后端服务", "error");
    } finally {
      if (isMountedRef.current) setIsScoring(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-orange-500";
    return "text-red-500";
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return "bg-green-50";
    if (score >= 60) return "bg-orange-50";
    return "bg-red-50";
  };

  const getLevelBadgeColor = (level: string) => {
    switch (level) {
      case "优秀":
        return "bg-gradient-to-r from-green-500 to-emerald-500 text-white";
      case "良好":
        return "bg-gradient-to-r from-blue-500 to-cyan-500 text-white";
      case "一般":
        return "bg-gradient-to-r from-orange-500 to-amber-500 text-white";
      default:
        return "bg-gradient-to-r from-red-500 to-pink-500 text-white";
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-indigo-50 to-purple-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center">
            <Star className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">内容质量评分</h3>
            <p className="text-xs text-gray-500">多维度分析内容质量</p>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Score Button */}
        <button
          onClick={handleScore}
          disabled={isScoring || !content.trim()}
          className="w-full px-4 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-medium rounded-lg hover:from-indigo-600 hover:to-purple-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center justify-center gap-2"
        >
          {isScoring ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              评分中...
            </>
          ) : (
            <>
              <Star className="w-4 h-4" />
              开始评分
            </>
          )}
        </button>

        {/* Score Results */}
        <AnimatePresence mode="wait">
          {scoreResult && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="space-y-4"
            >
              {/* Overall Score */}
              <div className="text-center p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl">
                <div className="text-xs text-indigo-600 font-medium mb-1">综合评分</div>
                <div className="flex items-center justify-center gap-3">
                  <span className={`text-4xl font-bold ${getScoreColor(scoreResult.overall_score)}`}>
                    {scoreResult.overall_score}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getLevelBadgeColor(scoreResult.score_level)}`}>
                    {scoreResult.score_level}
                  </span>
                </div>
              </div>

              {/* Dimension Scores */}
              <div className="space-y-2">
                {DIMENSIONS.map((dim) => {
                  const score = scoreResult[dim.key as keyof ScoreResult] as number;
                  return (
                    <div key={dim.key} className="flex items-center gap-3">
                      <span className="text-base">{dim.icon}</span>
                      <span className="text-sm text-gray-600 w-20">{dim.name}</span>
                      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${score}%` }}
                          transition={{ duration: 0.8, ease: "easeOut" }}
                          className={`h-full bg-gradient-to-r ${dim.color}`}
                        />
                      </div>
                      <span className={`text-sm font-medium w-10 ${getScoreColor(score)}`}>
                        {score}
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* Strengths */}
              {scoreResult.strengths.length > 0 && (
                <div className="p-3 bg-green-50 rounded-xl border border-green-100">
                  <div className="flex items-center gap-1.5 mb-2">
                    <ThumbsUp className="w-4 h-4 text-green-600" />
                    <span className="text-sm font-medium text-green-700">优点</span>
                  </div>
                  <ul className="space-y-1">
                    {scoreResult.strengths.map((s, i) => (
                      <li key={i} className="text-xs text-green-600 flex items-start gap-1.5">
                        <CheckCircle2 className="w-3 h-3 mt-0.5 flex-shrink-0" />
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Weaknesses */}
              {scoreResult.weaknesses.length > 0 && (
                <div className="p-3 bg-amber-50 rounded-xl border border-amber-100">
                  <div className="flex items-center gap-1.5 mb-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    <span className="text-sm font-medium text-amber-700">待改进</span>
                  </div>
                  <ul className="space-y-1">
                    {scoreResult.weaknesses.map((w, i) => (
                      <li key={i} className="text-xs text-amber-600 flex items-start gap-1.5">
                        <span className="text-amber-400">•</span>
                        {w}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Suggestions */}
              {scoreResult.suggestions.length > 0 && (
                <div className="p-3 bg-blue-50 rounded-xl border border-blue-100">
                  <div className="flex items-center gap-1.5 mb-2">
                    <Lightbulb className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-700">改进建议</span>
                  </div>
                  <ul className="space-y-1">
                    {scoreResult.suggestions.map((s, i) => (
                      <li key={i} className="text-xs text-blue-600 flex items-start gap-1.5">
                        <span className="text-blue-400">{i + 1}.</span>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty State */}
        {!isScoring && !scoreResult && (
          <div className="text-center py-6">
            <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-gray-100 flex items-center justify-center">
              <Star className="w-6 h-6 text-gray-400" />
            </div>
            <p className="text-sm text-gray-500">点击按钮对内容进行评分</p>
            <p className="text-xs text-gray-400 mt-1">多维度分析：吸引力、合规性、可读性等</p>
          </div>
        )}
      </div>
    </div>
  );
}