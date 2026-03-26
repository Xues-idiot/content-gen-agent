"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Hash, TrendingUp, Sparkles, Copy, Check, Info } from "lucide-react";
import { useToast } from "@/components/Toast";
import { recommendHashtags, getTrendingHashtags, HashtagInfo, HashtagCombination } from "@/lib/api";

interface HashtagRecommenderProps {
  content?: string;
  platform?: string;
  productInfo?: {
    name?: string;
    description?: string;
    selling_points?: string[];
    category?: string;
  };
  onSelectHashtags?: (hashtags: string[]) => void;
}

export default function HashtagRecommender({
  content = "",
  platform = "xiaohongshu",
  productInfo,
  onSelectHashtags,
}: HashtagRecommenderProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [hashtags, setHashtags] = useState<HashtagInfo[]>([]);
  const [combinations, setCombinations] = useState<HashtagCombination[]>([]);
  const [detectedIndustry, setDetectedIndustry] = useState("");
  const [selectedHashtags, setSelectedHashtags] = useState<Set<string>>(new Set());
  const [copiedHashtag, setCopiedHashtag] = useState<string | null>(null);
  const { showToast } = useToast();
  const isMountedRef = React.useRef(true);

  React.useEffect(() => {
    isMountedRef.current = true;
    return () => { isMountedRef.current = false; };
  }, []);

  const handleRecommend = async () => {
    if (!content.trim()) {
      showToast("请输入内容以获取推荐", "warning");
      return;
    }

    setIsLoading(true);
    try {
      const response = await recommendHashtags({
        content,
        platform,
        amount: 12,
        product_info: productInfo,
      });

      if (!isMountedRef.current) return;
      if (response.success) {
        setHashtags(response.hashtags);
        setCombinations(response.combinations || []);
        setDetectedIndustry(response.detected_industry || "");
        // Auto-select high exposure hashtags
        const autoSelected = new Set(
          response.hashtags
            .filter((h) => h.exposure === "高" || h.heat_score >= 70)
            .map((h) => h.tag)
        );
        setSelectedHashtags(autoSelected);
        showToast("Hashtag 推荐生成成功！", "success");
      } else {
        showToast("推荐生成失败，请重试", "error");
      }
    } catch (error) {
      if (!isMountedRef.current) return;
      showToast("网络错误，请检查后端服务", "error");
    } finally {
      if (isMountedRef.current) setIsLoading(false);
    }
  };

  const handleGetTrending = async () => {
    setIsLoading(true);
    try {
      const response = await getTrendingHashtags({
        platform,
        amount: 15,
      });

      if (!isMountedRef.current) return;
      if (response.success) {
        setHashtags(response.hashtags);
        setCombinations([]);
        setDetectedIndustry(response.detected_industry || "");
        showToast("热门 Hashtag 获取成功！", "success");
      } else {
        showToast("获取失败，请重试", "error");
      }
    } catch (error) {
      if (!isMountedRef.current) return;
      showToast("网络错误，请检查后端服务", "error");
    } finally {
      if (isMountedRef.current) setIsLoading(false);
    }
  };

  const toggleHashtag = (tag: string) => {
    const newSelected = new Set(selectedHashtags);
    if (newSelected.has(tag)) {
      newSelected.delete(tag);
    } else {
      newSelected.add(tag);
    }
    setSelectedHashtags(newSelected);
  };

  const selectCombination = (combo: HashtagCombination) => {
    setSelectedHashtags(new Set(combo.hashtags));
    showToast(`已选择「${combo.name}」组合方案`, "success");
  };

  const copyHashtags = async () => {
    const tags = Array.from(selectedHashtags).join(" ");
    await navigator.clipboard.writeText(tags);
    setCopiedHashtags("all");
    showToast("已复制选中的 Hashtag", "success");
    setTimeout(() => setCopiedHashtag(null), 2000);
  };

  const copySingleHashtag = async (tag: string) => {
    await navigator.clipboard.writeText(tag);
    setCopiedHashtag(tag);
    showToast(`已复制 ${tag}`, "success");
    setTimeout(() => setCopiedHashtag(null), 2000);
  };

  const applyHashtags = () => {
    if (onSelectHashtags) {
      onSelectHashtags(Array.from(selectedHashtags));
    }
    showToast(`已应用 ${selectedHashtags.size} 个 Hashtag`, "success");
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "trending":
        return <TrendingUp className="w-3.5 h-3.5" />;
      case "industry":
        return <Hash className="w-3.5 h-3.5" />;
      case "brand":
        return <Sparkles className="w-3.5 h-3.5" />;
      default:
        return <Hash className="w-3.5 h-3.5" />;
    }
  };

  const getExposureColor = (exposure: string) => {
    switch (exposure) {
      case "高":
        return "text-red-500 bg-red-50 border-red-200";
      case "中":
        return "text-orange-500 bg-orange-50 border-orange-200";
      default:
        return "text-gray-500 bg-gray-50 border-gray-200";
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-orange-50 to-pink-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-400 to-pink-500 flex items-center justify-center">
              <Hash className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">智能 Hashtag 推荐</h3>
              <p className="text-xs text-gray-500">基于内容分析推荐最佳标签</p>
            </div>
          </div>
          {detectedIndustry && (
            <div className="px-2.5 py-1 bg-white rounded-full border border-orange-200">
              <span className="text-xs text-orange-600">行业：{detectedIndustry}</span>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="p-4 border-b border-gray-100 bg-gray-50/50">
        <div className="flex gap-2">
          <button
            onClick={handleRecommend}
            disabled={isLoading || !content.trim()}
            className="flex-1 px-3 py-2 bg-gradient-to-r from-orange-500 to-pink-500 text-white text-sm font-medium rounded-lg hover:from-orange-600 hover:to-pink-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            {isLoading ? "分析中..." : "智能推荐"}
          </button>
          <button
            onClick={handleGetTrending}
            disabled={isLoading}
            className="px-3 py-2 bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-all disabled:opacity-50"
          >
            热门标签
          </button>
        </div>
      </div>

      {/* Hashtags List */}
      <AnimatePresence mode="wait">
        {hashtags.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="p-4 space-y-4"
          >
            {/* Combination Suggestions */}
            {combinations.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center gap-1.5 text-xs text-gray-500">
                  <Info className="w-3.5 h-3.5" />
                  <span>推荐组合方案</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {combinations.map((combo, idx) => (
                    <button
                      key={idx}
                      onClick={() => selectCombination(combo)}
                      className="px-3 py-1.5 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-100 rounded-full text-xs text-purple-700 hover:border-purple-300 transition-colors"
                    >
                      {combo.name} ({combo.expected_exposure})
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Hashtag Grid */}
            <div className="grid grid-cols-2 gap-2">
              {hashtags.map((hashtag, idx) => {
                const isSelected = selectedHashtags.has(hashtag.tag);
                const isCopied = copiedHashtag === hashtag.tag;
                return (
                  <motion.div
                    key={hashtag.tag}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.03 }}
                    className={`
                      relative p-3 rounded-xl border cursor-pointer transition-all
                      ${isSelected
                        ? "border-orange-300 bg-orange-50"
                        : "border-gray-100 bg-white hover:border-gray-200"
                      }
                    `}
                    onClick={() => toggleHashtag(hashtag.tag)}
                  >
                    {/* Selection Indicator */}
                    <div className={`
                      absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full border-2 flex items-center justify-center
                      ${isSelected
                        ? "bg-orange-500 border-orange-500"
                        : "bg-white border-gray-200"
                      }
                    `}>
                      {isSelected && (
                        <Check className="w-3 h-3 text-white" />
                      )}
                    </div>

                    {/* Hashtag Tag */}
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-medium text-gray-900 text-sm">{hashtag.tag}</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          copySingleHashtag(hashtag.tag);
                        }}
                        className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        {isCopied ? (
                          <Check className="w-3.5 h-3.5 text-green-500" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>

                    {/* Category & Exposure */}
                    <div className="flex items-center gap-1.5">
                      <span className={`
                        inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs
                        ${hashtag.category === "trending" ? "bg-red-50 text-red-600" :
                          hashtag.category === "industry" ? "bg-blue-50 text-blue-600" :
                          hashtag.category === "brand" ? "bg-purple-50 text-purple-600" :
                          "bg-gray-50 text-gray-600"
                        }
                      `}>
                        {getCategoryIcon(hashtag.category)}
                        {hashtag.category === "trending" ? "热门" :
                         hashtag.category === "industry" ? "行业" :
                         hashtag.category === "brand" ? "品牌" : "情感"}
                      </span>
                      <span className={`
                        px-1.5 py-0.5 rounded text-xs border
                        ${getExposureColor(hashtag.exposure)}
                      `}>
                        {hashtag.exposure}曝光
                      </span>
                    </div>

                    {/* Reason */}
                    {hashtag.reason && (
                      <p className="mt-1.5 text-xs text-gray-500 line-clamp-2">{hashtag.reason}</p>
                    )}
                  </motion.div>
                );
              })}
            </div>

            {/* Selected Count & Actions */}
            <div className="flex items-center justify-between pt-3 border-t border-gray-100">
              <div className="text-sm text-gray-500">
                已选择 <span className="font-semibold text-orange-500">{selectedHashtags.size}</span> / {hashtags.length} 个标签
              </div>
              <div className="flex gap-2">
                <button
                  onClick={copyHashtags}
                  disabled={selectedHashtags.size === 0}
                  className="px-3 py-1.5 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  复制
                </button>
                <button
                  onClick={applyHashtags}
                  disabled={selectedHashtags.size === 0}
                  className="px-3 py-1.5 text-sm text-white bg-gradient-to-r from-orange-500 to-pink-500 rounded-lg hover:from-orange-600 hover:to-pink-600 transition-all disabled:opacity-50"
                >
                  应用到内容
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty State */}
      {!isLoading && hashtags.length === 0 && (
        <div className="p-8 text-center">
          <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-gray-100 flex items-center justify-center">
            <Hash className="w-6 h-6 text-gray-400" />
          </div>
          <p className="text-sm text-gray-500">点击「智能推荐」获取 Hashtag 建议</p>
          <p className="text-xs text-gray-400 mt-1">或点击「热门标签」查看平台热门内容</p>
        </div>
      )}
    </div>
  );
}