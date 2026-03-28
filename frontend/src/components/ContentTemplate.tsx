"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { FileText, Copy, Check, Loader2, Sparkles } from "lucide-react";
import { useToast } from "@/components/Toast";
import { API_BASE_URL } from "@/lib/api";

interface ContentTemplateProps {
  platform?: string;
  productInfo?: {
    name?: string;
    description?: string;
    selling_points?: string[];
  };
  onApplyTemplate?: (template: string) => void;
}

const PLATFORMS = [
  { id: "xiaohongshu", name: "小红书", emoji: "📕", color: "red" },
  { id: "tiktok", name: "抖音", emoji: "🎵", color: "pink" },
  { id: "official", name: "公众号", emoji: "📰", color: "blue" },
  { id: "friend_circle", name: "朋友圈", emoji: "📱", color: "green" },
];

const CONTENT_TYPES = [
  { id: "product", name: "产品种草", emoji: "🛍️", description: "推荐产品、分享使用体验" },
  { id: "promotion", name: "促销活动", emoji: "🎉", description: "优惠信息、活动通知" },
  { id: "story", name: "品牌故事", emoji: "📖", description: "品牌历史、用户故事" },
  { id: "tips", name: "干货技巧", emoji: "💡", description: "教程、技巧分享" },
];

const TONES = [
  { id: "friendly", name: "亲切友好", emoji: "😊", description: "像朋友推荐" },
  { id: "professional", name: "专业正式", emoji: "💼", description: "权威可信" },
  { id: "casual", name: "轻松随意", emoji: "😎", description: "生活化" },
  { id: "humorous", name: "幽默风趣", emoji: "😄", description: "有梗有趣" },
];

export default function ContentTemplate({
  platform = "xiaohongshu",
  productInfo,
  onApplyTemplate,
}: ContentTemplateProps) {
  const [selectedPlatform, setSelectedPlatform] = useState(platform);
  const [selectedType, setSelectedType] = useState("product");
  const [selectedTone, setSelectedTone] = useState("friendly");
  const [isGenerating, setIsGenerating] = useState(false);
  const [template, setTemplate] = useState("");
  const [placeholders, setPlaceholders] = useState<string[]>([]);
  const [examples, setExamples] = useState<string[]>([]);
  const [copied, setCopied] = useState(false);
  const { showToast } = useToast();
  const isMountedRef = React.useRef(true);

  React.useEffect(() => {
    isMountedRef.current = true;
    return () => { isMountedRef.current = false; };
  }, []);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setTemplate("");
    setPlaceholders([]);
    setExamples([]);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/content/template`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            platform: selectedPlatform,
            content_type: selectedType,
            tone: selectedTone,
            product_info: productInfo,
          }),
        }
      );

      if (!isMountedRef.current) return;
      if (!response.ok) throw new Error("API error");
      const data = await response.json();

      if (!isMountedRef.current) return;
      if (data.success) {
        setTemplate(data.template || "");
        setPlaceholders(data.placeholders || []);
        setExamples(data.examples || []);
        showToast("模板生成成功！", "success");
      } else {
        showToast("生成失败，请重试", "error");
      }
    } catch {
      if (!isMountedRef.current) return;
      showToast("网络错误，请检查后端服务", "error");
    } finally {
      if (isMountedRef.current) setIsGenerating(false);
    }
  };

  const copyTemplate = async () => {
    if (template) {
      await navigator.clipboard.writeText(template);
      setCopied(true);
      showToast("模板已复制", "success");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const applyTemplate = () => {
    if (template && onApplyTemplate) {
      onApplyTemplate(template);
      showToast("模板已应用", "success");
    }
  };

  const getPlatformColor = (id: string) => {
    const p = PLATFORMS.find((p) => p.id === id);
    switch (p?.color) {
      case "red":
        return "from-red-400 to-pink-500";
      case "pink":
        return "from-pink-400 to-purple-500";
      case "blue":
        return "from-blue-400 to-cyan-500";
      case "green":
        return "from-green-400 to-emerald-500";
      default:
        return "from-gray-400 to-gray-500";
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-violet-50 to-purple-50">
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${getPlatformColor(selectedPlatform)} flex items-center justify-center`}>
            <FileText className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">内容模板</h3>
            <p className="text-xs text-gray-500">快速获取文案模板</p>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Platform Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">目标平台</label>
          <div className="flex flex-wrap gap-2">
            {PLATFORMS.map((p) => (
              <button
                key={p.id}
                onClick={() => setSelectedPlatform(p.id)}
                className={`px-3 py-1.5 rounded-lg border text-sm font-medium transition-all flex items-center gap-1.5 ${
                  selectedPlatform === p.id
                    ? `border-transparent bg-gradient-to-r ${getPlatformColor(p.id)} text-white shadow-sm`
                    : "border-gray-200 bg-white text-gray-700 hover:border-gray-300"
                }`}
              >
                <span>{p.emoji}</span>
                <span>{p.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Content Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">内容类型</label>
          <div className="grid grid-cols-2 gap-2">
            {CONTENT_TYPES.map((t) => (
              <button
                key={t.id}
                onClick={() => setSelectedType(t.id)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  selectedType === t.id
                    ? "border-violet-300 bg-violet-50"
                    : "border-gray-100 bg-white hover:border-gray-200"
                }`}
              >
                <div className="flex items-center gap-1.5">
                  <span>{t.emoji}</span>
                  <span className="text-sm font-medium text-gray-900">{t.name}</span>
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{t.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Tone Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">语气风格</label>
          <div className="flex flex-wrap gap-2">
            {TONES.map((t) => (
              <button
                key={t.id}
                onClick={() => setSelectedTone(t.id)}
                className={`px-3 py-1.5 rounded-lg border text-sm transition-all ${
                  selectedTone === t.id
                    ? "border-violet-300 bg-violet-50 text-violet-700"
                    : "border-gray-200 bg-white text-gray-600 hover:border-gray-300"
                }`}
              >
                <span className="mr-1">{t.emoji}</span>
                {t.name}
              </button>
            ))}
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="w-full px-4 py-2.5 bg-gradient-to-r from-violet-500 to-purple-500 text-white font-medium rounded-lg hover:from-violet-600 hover:to-purple-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center justify-center gap-2"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              生成中...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              生成模板
            </>
          )}
        </button>

        {/* Template Result */}
        <AnimatePresence mode="wait">
          {template && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="space-y-3"
            >
              {/* Template */}
              <div className="p-4 bg-gradient-to-r from-violet-50 to-purple-50 rounded-xl border border-violet-100">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-violet-600 font-medium">生成的模板</span>
                  <button
                    onClick={copyTemplate}
                    className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {copied ? (
                      <Check className="w-4 h-4 text-green-500" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>
                <p className="text-gray-800 text-sm whitespace-pre-wrap">{template}</p>
              </div>

              {/* Placeholders */}
              {placeholders.length > 0 && (
                <div className="p-3 bg-amber-50 rounded-xl border border-amber-100">
                  <div className="text-xs text-amber-700 font-medium mb-1.5">需要填充的内容</div>
                  <div className="flex flex-wrap gap-1.5">
                    {placeholders.map((p, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-white rounded border border-amber-200 text-amber-700 text-xs"
                      >
                        {p}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Examples */}
              {examples.length > 0 && (
                <div className="space-y-2">
                  <div className="text-xs text-gray-500 font-medium">使用示例</div>
                  {examples.map((ex, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-gray-50 rounded-lg border border-gray-100"
                    >
                      <p className="text-xs text-gray-600">{ex}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Apply Button */}
              <button
                onClick={applyTemplate}
                className="w-full px-4 py-2 bg-violet-100 text-violet-700 font-medium rounded-lg hover:bg-violet-200 transition-colors"
              >
                应用此模板
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty State */}
        {!isGenerating && !template && (
          <div className="text-center py-6">
            <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-gray-100 flex items-center justify-center">
              <FileText className="w-6 h-6 text-gray-400" />
            </div>
            <p className="text-sm text-gray-500">选择平台和内容类型生成模板</p>
            <p className="text-xs text-gray-400 mt-1">模板包含占位符，方便快速填充</p>
          </div>
        )}
      </div>
    </div>
  );
}