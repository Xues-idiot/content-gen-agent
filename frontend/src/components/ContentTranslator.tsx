"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Languages, ArrowRight, Copy, Check, Loader2 } from "lucide-react";
import { useToast } from "@/components/Toast";
import { API_BASE_URL } from "@/lib/api";

interface ContentTranslatorProps {
  defaultContent?: string;
  onTranslated?: (translated: string) => void;
}

const LANGUAGES = [
  { id: "en", name: "英语", emoji: "🇺🇸", flag: "EN" },
  { id: "ja", name: "日语", emoji: "🇯🇵", flag: "JA" },
  { id: "ko", name: "韩语", emoji: "🇰🇷", flag: "KO" },
  { id: "es", name: "西班牙语", emoji: "🇪🇸", flag: "ES" },
  { id: "fr", name: "法语", emoji: "🇫🇷", flag: "FR" },
  { id: "de", name: "德语", emoji: "🇩🇪", flag: "DE" },
];

export default function ContentTranslator({
  defaultContent = "",
  onTranslated,
}: ContentTranslatorProps) {
  const [content, setContent] = useState(defaultContent);
  const [targetLang, setTargetLang] = useState("en");
  const [sourceLang, setSourceLang] = useState("auto");
  const [isTranslating, setIsTranslating] = useState(false);
  const [translated, setTranslated] = useState("");
  const [copied, setCopied] = useState(false);
  const { showToast } = useToast();
  const isMountedRef = React.useRef(true);

  React.useEffect(() => {
    isMountedRef.current = true;
    return () => { isMountedRef.current = false; };
  }, []);

  const handleTranslate = async () => {
    if (!content.trim()) {
      showToast("请输入要翻译的内容", "warning");
      return;
    }

    setIsTranslating(true);
    setTranslated("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/translate`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            content,
            target_lang: targetLang,
            source_lang: sourceLang,
          }),
        }
      );

      if (!isMountedRef.current) return;
      if (!response.ok) throw new Error("API error");
      const data = await response.json();

      if (!isMountedRef.current) return;
      if (data.success) {
        setTranslated(data.translated);
        showToast("翻译成功！", "success");
        onTranslated?.(data.translated);
      } else {
        showToast("翻译失败，请重试", "error");
      }
    } catch {
      if (!isMountedRef.current) return;
      showToast("网络错误，请检查后端服务", "error");
    } finally {
      if (isMountedRef.current) setIsTranslating(false);
    }
  };

  const copyTranslation = async () => {
    if (translated) {
      await navigator.clipboard.writeText(translated);
      setCopied(true);
      showToast("已复制翻译结果", "success");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const swapContent = () => {
    if (translated) {
      setContent(translated);
      setTranslated("");
      // Swap languages
      if (sourceLang !== "auto") {
        setTargetLang(sourceLang);
        setSourceLang("auto");
      }
    }
  };

  const getTargetLangInfo = () => {
    return LANGUAGES.find((l) => l.id === targetLang) || LANGUAGES[0];
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-cyan-50 to-blue-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center">
            <Languages className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">多语言翻译</h3>
            <p className="text-xs text-gray-500">一键翻译内容到多种语言</p>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Language Selection */}
        <div className="flex items-center gap-3">
          {/* Source Language */}
          <div className="flex-1">
            <label className="block text-xs text-gray-500 mb-1">源语言</label>
            <select
              value={sourceLang}
              onChange={(e) => setSourceLang(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-gray-200 bg-white text-sm"
            >
              <option value="auto">自动检测</option>
              <option value="zh">中文</option>
              <option value="en">英语</option>
              <option value="ja">日语</option>
              <option value="ko">韩语</option>
            </select>
          </div>

          {/* Swap Button */}
          <div className="pt-5">
            <button
              onClick={swapContent}
              disabled={!translated}
              className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ArrowRight className="w-4 h-4 text-gray-600" />
            </button>
          </div>

          {/* Target Language */}
          <div className="flex-1">
            <label className="block text-xs text-gray-500 mb-1">目标语言</label>
            <select
              value={targetLang}
              onChange={(e) => setTargetLang(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-gray-200 bg-white text-sm"
            >
              {LANGUAGES.map((lang) => (
                <option key={lang.id} value={lang.id}>
                  {lang.emoji} {lang.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Content Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            {sourceLang === "auto" ? "输入内容" : LANGUAGES.find((l) => l.id === sourceLang)?.name || "源语言"}
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="输入要翻译的内容..."
            rows={4}
            className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-cyan-300 focus:ring-2 focus:ring-cyan-100 outline-none transition-all resize-none"
          />
        </div>

        {/* Translate Button */}
        <button
          onClick={handleTranslate}
          disabled={isTranslating || !content.trim()}
          className="w-full px-4 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-medium rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center justify-center gap-2"
        >
          {isTranslating ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              翻译中...
            </>
          ) : (
            <>
              <Languages className="w-4 h-4" />
              翻译为 {getTargetLangInfo().name}
            </>
          )}
        </button>

        {/* Translation Result */}
        <AnimatePresence mode="wait">
          {translated && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="space-y-3"
            >
              <div className="p-4 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-xl border border-cyan-100">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-cyan-600 font-medium">
                    {getTargetLangInfo().emoji} {getTargetLangInfo().name} 翻译结果
                  </span>
                  <button
                    onClick={copyTranslation}
                    className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {copied ? (
                      <Check className="w-4 h-4 text-green-500" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>
                <p className="text-gray-800 whitespace-pre-wrap">{translated}</p>
              </div>

              {/* Quick Actions */}
              <div className="flex flex-wrap gap-2">
                <span className="text-xs text-gray-500">快速复制到：</span>
                {LANGUAGES.filter((l) => l.id !== targetLang)
                  .slice(0, 3)
                  .map((lang) => (
                    <button
                      key={lang.id}
                      onClick={async () => {
                        // 复制并提示用户可以切换语言
                        await navigator.clipboard.writeText(translated);
                        showToast(`已复制，可切换到${lang.name}进行二次翻译`, "info");
                      }}
                      className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded hover:bg-gray-200 transition-colors"
                    >
                      {lang.emoji} {lang.flag}
                    </button>
                  ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty State */}
        {!isTranslating && !translated && (
          <div className="text-center py-6">
            <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-gray-100 flex items-center justify-center">
              <Languages className="w-6 h-6 text-gray-400" />
            </div>
            <p className="text-sm text-gray-500">输入内容并选择目标语言</p>
            <p className="text-xs text-gray-400 mt-1">支持中、英、日、韩等6种语言</p>
          </div>
        )}
      </div>
    </div>
  );
}