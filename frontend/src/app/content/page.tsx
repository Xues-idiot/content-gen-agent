"use client";

import React, { useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import ProductInput, { ProductData } from "@/components/ProductInput";
import PlatformSelect from "@/components/PlatformSelect";
import CopyOutput from "@/components/CopyOutput";
import ImagePreview from "@/components/ImagePreview";
import ExportPanel from "@/components/ExportPanel";
import MarketInsights from "@/components/MarketInsights";
import LoadingSpinner from "@/components/LoadingSpinner";
import { useContentStore } from "@/store/content-store";
import { ToastProvider, useToast } from "@/components/Toast";

function ContentPageContent() {
  const {
    product,
    selectedPlatforms,
    copyResults,
    imageSuggestions,
    marketResearch,
    isLoading,
    error,
    progress,
    setProduct,
    setSelectedPlatforms,
    setCopyResults,
    setImageSuggestions,
    setMarketResearch,
    setIsLoading,
    setError,
    setProgress,
  } = useContentStore();

  const { showToast } = useToast();

  // Fetch health status on mount
  const [backendStatus, setBackendStatus] = React.useState<{
    api: boolean;
    tavily: boolean;
  }>({ api: false, tavily: false });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch("http://localhost:8003/health");
        if (response.ok) {
          const data = await response.json();
          setBackendStatus({
            api: data.api_key_configured || false,
            tavily: data.tavily_api_configured || false,
          });
        }
      } catch {
        // Backend not available
      }
    };
    checkHealth();
  }, []);

  const handleGenerate = async (prod: ProductData) => {
    setProduct(prod);
    setIsLoading(true);
    setError(null);
    setMarketResearch({ insights: [], trends: [], competitors: [] }); // Clear previous research
    setProgress(10);

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 10, 90));
      }, 500);

      setProgress(20);

      const response = await fetch("http://localhost:8003/api/v1/content/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          product: {
            name: prod.name,
            description: prod.description,
            selling_points: prod.sellingPoints,
            target_users: prod.targetUsers,
            category: prod.category,
            price_range: prod.priceRange,
          },
          platforms: selectedPlatforms,
        }),
      });

      clearInterval(progressInterval);
      setProgress(70);

      const data = await response.json();

      if (data.success) {
        setProgress(90);
        setCopyResults(data.platform_results);

        const suggestions: Record<string, any[]> = {};
        data.platform_results.forEach((result: any) => {
          if (result.imageSuggestions && result.imageSuggestions.length > 0) {
            suggestions[result.platform] = result.imageSuggestions.map((text: string, idx: number) => ({
              type: `图片${idx + 1}`,
              description: text,
              prompt: text,
            }));
          }
        });
        setImageSuggestions(suggestions);

        // Store market research data
        if (data.market_insights || data.trend_topics || data.competitor_content) {
          setMarketResearch({
            insights: data.market_insights || [],
            trends: data.trend_topics || [],
            competitors: data.competitor_content || [],
          });
        }

        setProgress(100);
        showToast("内容生成成功！", "success");
      } else {
        setError(data.errors?.join(", ") || "生成失败");
        showToast("内容生成失败", "error");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "请求失败，请检查后端服务");
      showToast("网络错误，请检查后端服务是否运行", "error");
    } finally {
      setIsLoading(false);
      setTimeout(() => setProgress(0), 500);
    }
  };

  // 构建导出内容
  const exportContent: Record<string, any> = {
    product: product
      ? {
          name: product.name,
          description: product.description,
          selling_points: product.sellingPoints,
          category: product.category,
        }
      : {},
    copies: {} as Record<string, any>,
  };

  copyResults.forEach((result) => {
    exportContent.copies[result.platform] = {
      copy: {
        title: result.title,
        content: result.content,
        script: result.script,
        tags: result.tags,
      },
      review: result.review,
      images: result.imageSuggestions,
    };
  });

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#FFF8F0" }}>
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="bg-white shadow-sm"
      >
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold" style={{ color: "#FF6B35" }}>
                📢 Vox 内容生成
              </h1>
              <p className="text-gray-600 text-sm mt-1">
                多平台营销内容一键生成 - 小红书、抖音、公众号、朋友圈
              </p>
            </div>
            {/* Status Indicator */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5" title="MiniMax API">
                <span
                  className={`w-2 h-2 rounded-full ${backendStatus.api ? "bg-green-500" : "bg-red-500"}`}
                />
                <span className="text-xs text-gray-500">API</span>
              </div>
              <div className="flex items-center gap-1.5" title="Tavily API">
                <span
                  className={`w-2 h-2 rounded-full ${backendStatus.tavily ? "bg-green-500" : "bg-yellow-500"}`}
                />
                <span className="text-xs text-gray-500">调研</span>
              </div>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Progress Bar */}
      <AnimatePresence>
        {isLoading && progress > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="h-1 bg-gray-200">
              <motion.div
                className="h-full"
                style={{ backgroundColor: "#FF6B35" }}
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Error Message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700"
            >
              <strong>错误:</strong> {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading Overlay */}
        <AnimatePresence>
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="mb-6 flex items-center justify-center gap-3 py-8"
            >
              <LoadingSpinner size="lg" text="AI 正在生成内容..." />
            </motion.div>
          )}
        </AnimatePresence>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Input */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4 }}
            className="lg:col-span-1 space-y-6"
          >
            <ProductInput onGenerate={handleGenerate} isLoading={isLoading} />

            <PlatformSelect
              selected={selectedPlatforms}
              onChange={setSelectedPlatforms}
              disabled={isLoading}
            />
          </motion.div>

          {/* Right Column - Output */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="lg:col-span-2 space-y-6"
          >
            {/* Copy Results */}
            <CopyOutput results={copyResults} />

            {/* Image Suggestions */}
            <ImagePreview suggestions={imageSuggestions} />

            {/* Market Insights */}
            <MarketInsights />

            {/* Export Panel */}
            <ExportPanel content={exportContent} disabled={copyResults.length === 0} />
          </motion.div>
        </div>
      </main>

      {/* Footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="bg-white border-t border-gray-200 mt-8"
      >
        <div className="max-w-6xl mx-auto px-4 py-4 text-center text-gray-500 text-sm">
          Vox 内容生成 Agent v0.1.0 | 基于 AI 的多平台营销内容生成工具
        </div>
      </motion.footer>
    </div>
  );
}

export default function ContentPage() {
  return (
    <ToastProvider>
      <ContentPageContent />
    </ToastProvider>
  );
}
