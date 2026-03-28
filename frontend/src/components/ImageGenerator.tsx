"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Image, Download, Copy, Check, Loader2, Wand2 } from "lucide-react";
import { useToast } from "@/components/Toast";
import { API_BASE_URL } from "@/lib/api";

interface ImageGeneratorProps {
  defaultPrompt?: string;
  platform?: string;
  onImageGenerated?: (imageUrl: string, localPath?: string) => void;
}

const IMAGE_STYLES = [
  { id: "modern", name: "现代简约", emoji: "✨", description: "简洁、专业" },
  { id: "minimal", name: "极简", emoji: "◻️", description: "白色背景、纯净" },
  { id: "lifestyle", name: "生活方式", emoji: "🏠", description: "温馨、真实" },
  { id: "product", name: "产品展示", emoji: "📦", description: "专业摄影" },
  { id: "natural", name: "自然", emoji: "🌿", description: "真实、鲜活" },
  { id: "vivid", name: "鲜艳", emoji: "🎨", description: "高饱和度" },
];

const IMAGE_SIZES = [
  { id: "square", name: "方形", emoji: "◻️", ratio: "1:1" },
  { id: "portrait", name: "竖屏", emoji: "📱", ratio: "3:4" },
  { id: "landscape", name: "横屏", emoji: "🖼️", ratio: "4:3" },
  { id: "wide", name: "宽屏", emoji: "🎬", ratio: "16:9" },
];

export default function ImageGenerator({
  defaultPrompt = "",
  platform = "xiaohongshu",
  onImageGenerated,
}: ImageGeneratorProps) {
  const [prompt, setPrompt] = useState(defaultPrompt);
  const [style, setStyle] = useState("modern");
  const [size, setSize] = useState("square");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<{
    url: string;
    local_path: string;
    width: number;
    height: number;
  } | null>(null);
  const [copied, setCopied] = useState(false);
  const { showToast } = useToast();
  const isMountedRef = React.useRef(true);

  React.useEffect(() => {
    isMountedRef.current = true;
    return () => { isMountedRef.current = false; };
  }, []);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      showToast("请输入图片描述", "warning");
      return;
    }

    setIsGenerating(true);
    setGeneratedImage(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/image/generate`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt,
            style,
            size,
            save_local: false,
          }),
        }
      );

      if (!isMountedRef.current) return;
      if (!response.ok) throw new Error("API error");
      const data = await response.json();

      if (!isMountedRef.current) return;
      if (data.success) {
        setGeneratedImage({
          url: data.url,
          local_path: data.local_path || "",
          width: data.width,
          height: data.height,
        });
        showToast("图片生成成功！", "success");
        onImageGenerated?.(data.url, data.local_path);
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

  const copyUrl = async () => {
    if (generatedImage?.url) {
      await navigator.clipboard.writeText(generatedImage.url);
      setCopied(true);
      showToast("图片链接已复制", "success");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getSizeDescription = () => {
    const s = IMAGE_SIZES.find((s) => s.id === size);
    return s ? `${s.name} (${s.ratio})` : size;
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-purple-50 to-pink-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center">
            <Image className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">AI 图片生成</h3>
            <p className="text-xs text-gray-500">使用 Pollinations AI 生成图片</p>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Prompt Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            图片描述
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="描述你想要生成的图片..."
            rows={3}
            className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-purple-300 focus:ring-2 focus:ring-purple-100 outline-none transition-all resize-none"
          />
        </div>

        {/* Style Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            图片风格
          </label>
          <div className="grid grid-cols-3 gap-2">
            {IMAGE_STYLES.map((s) => (
              <button
                key={s.id}
                onClick={() => setStyle(s.id)}
                className={`p-2 rounded-xl border text-left transition-all ${
                  style === s.id
                    ? "border-purple-300 bg-purple-50"
                    : "border-gray-100 bg-white hover:border-gray-200"
                }`}
              >
                <div className="flex items-center gap-1.5">
                  <span>{s.emoji}</span>
                  <span className="text-sm font-medium text-gray-900">{s.name}</span>
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{s.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Size Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            图片尺寸
          </label>
          <div className="flex gap-2">
            {IMAGE_SIZES.map((s) => (
              <button
                key={s.id}
                onClick={() => setSize(s.id)}
                className={`flex-1 p-2 rounded-xl border text-center transition-all ${
                  size === s.id
                    ? "border-purple-300 bg-purple-50"
                    : "border-gray-100 bg-white hover:border-gray-200"
                }`}
              >
                <div className="text-lg">{s.emoji}</div>
                <div className="text-xs font-medium text-gray-900">{s.name}</div>
                <div className="text-xs text-gray-500">{s.ratio}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={isGenerating || !prompt.trim()}
          className="w-full px-4 py-2.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center justify-center gap-2"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              生成中...
            </>
          ) : (
            <>
              <Wand2 className="w-4 h-4" />
              生成图片
            </>
          )}
        </button>

        {/* Generated Image */}
        <AnimatePresence mode="wait">
          {generatedImage && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="space-y-3"
            >
              <div className="relative rounded-xl overflow-hidden bg-gray-100">
                <img
                  src={generatedImage.url}
                  alt="Generated"
                  className="w-full h-auto"
                  style={{
                    aspectRatio:
                      generatedImage.width / generatedImage.height,
                  }}
                />
              </div>

              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>
                  {generatedImage.width} × {generatedImage.height} · {getSizeDescription()}
                </span>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={copyUrl}
                  className="flex-1 px-3 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center gap-1.5"
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4 text-green-500" />
                      已复制
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      复制链接
                    </>
                  )}
                </button>
                <a
                  href={generatedImage.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 px-3 py-2 bg-purple-100 text-purple-700 text-sm rounded-lg hover:bg-purple-200 transition-colors flex items-center justify-center gap-1.5"
                >
                  <Download className="w-4 h-4" />
                  下载
                </a>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty State */}
        {!isGenerating && !generatedImage && (
          <div className="text-center py-8">
            <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-gray-100 flex items-center justify-center">
              <Image className="w-6 h-6 text-gray-400" />
            </div>
            <p className="text-sm text-gray-500">输入描述并选择风格即可生成图片</p>
            <p className="text-xs text-gray-400 mt-1">免费使用 Pollinations AI</p>
          </div>
        )}
      </div>
    </div>
  );
}