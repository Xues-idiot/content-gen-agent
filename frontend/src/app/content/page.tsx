"use client";

import React, { useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import ProductInput, { ProductData } from "@/components/ProductInput";
import PlatformSelect from "@/components/PlatformSelect";
import CopyOutput from "@/components/CopyOutput";
import ImagePreview from "@/components/ImagePreview";
import ExportPanel from "@/components/ExportPanel";
import MarketInsights from "@/components/MarketInsights";
import VideoGenerator from "@/components/VideoGenerator";
import HashtagRecommender from "@/components/HashtagRecommender";
import LoadingSpinner from "@/components/LoadingSpinner";
import SidebarNav from "@/components/SidebarNav";
import { useContentStore } from "@/store/content-store";
import { ToastProvider, useToast } from "@/components/Toast";
import { API_BASE_URL } from "@/lib/api";
import { AlertCircle, Zap } from "lucide-react";

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

  const isMountedRef = React.useRef(true);
  const progressResetTimeoutRef = React.useRef<NodeJS.Timeout | null>(null);

  const [backendStatus, setBackendStatus] = React.useState<{
    api: boolean;
    tavily: boolean;
  }>({ api: false, tavily: false });

  React.useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      if (progressResetTimeoutRef.current) {
        clearTimeout(progressResetTimeoutRef.current);
        progressResetTimeoutRef.current = null;
      }
    };
  }, []);

  const loadingSteps = [
    "正在分析产品信息",
    "正在获取市场洞察",
    "正在生成小红书文案",
    "正在生成抖音脚本",
    "正在生成公众号内容",
    "正在生成朋友圈文案",
    "正在进行内容审核",
  ];
  const [currentLoadingStep, setCurrentLoadingStep] = React.useState(0);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`);
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
    setCurrentLoadingStep(0);
    setMarketResearch({ insights: [], trends: [], competitors: [] });
    setProgress(5);

    setProgress(10);
    setCurrentLoadingStep(0);

    const progressInterval = setInterval(() => {
      if (isMountedRef.current) {
        setProgress((prev) => Math.min(prev + 5, 90));
        setCurrentLoadingStep((prev) => Math.min(prev + 1, loadingSteps.length - 1));
      }
    }, 800);

    try {
      setProgress(15);
      setCurrentLoadingStep(1);

      const response = await fetch(`${API_BASE_URL}/api/v1/content/generate`, {
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

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      clearInterval(progressInterval);
      setProgress(80);
      setCurrentLoadingStep(loadingSteps.length - 1);

      const data = await response.json();

      if (data.success) {
        setProgress(95);
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
      clearInterval(progressInterval);
      setError(err instanceof Error ? err.message : "请求失败，请检查后端服务");
      showToast("网络错误，请检查后端服务是否运行", "error");
    } finally {
      setIsLoading(false);
      if (progressResetTimeoutRef.current) {
        clearTimeout(progressResetTimeoutRef.current);
      }
      progressResetTimeoutRef.current = setTimeout(() => {
        if (isMountedRef.current) {
          setProgress(0);
          setCurrentLoadingStep(0);
        }
      }, 500);
    }
  };

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

  const videoScript = React.useMemo(() => {
    const tiktokResult = copyResults.find((r) => r.platform === "tiktok");
    if (tiktokResult?.script) return tiktokResult.script;
    if (copyResults.length > 0 && copyResults[0].content) return copyResults[0].content;
    return "";
  }, [copyResults]);

  const videoTitle = React.useMemo(() => {
    const tiktokResult = copyResults.find((r) => r.platform === "tiktok");
    if (tiktokResult?.title) return tiktokResult.title;
    if (product?.name) return product.name;
    return "";
  }, [copyResults, product]);

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Progress Bar */}
      <AnimatePresence>
        {isLoading && progress > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="h-1 bg-neutral-200">
              <motion.div
                className="h-full gradient-brand"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {/* Error Message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0, y: -10 }}
              animate={{ opacity: 1, height: "auto", y: 0 }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6"
            >
              <div className="card card-bordered p-4 bg-red-50 border-red-200 flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                <div>
                  <strong className="text-red-700">错误:</strong>
                  <span className="text-red-600 ml-2">{error}</span>
                </div>
              </div>
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
              className="mb-6"
            >
              <div className="card card-bordered p-6 bg-gradient-to-r from-violet-50 to-purple-50">
                <LoadingSpinner
                  size="lg"
                  text="AI 正在生成内容..."
                  steps={loadingSteps}
                  currentStep={currentLoadingStep}
                />
              </div>
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

            {/* Backend Status */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="card card-bordered p-4"
            >
              <div className="flex items-center gap-2 mb-3">
                <Zap className="w-4 h-4 text-violet-600" />
                <span className="text-sm font-semibold text-neutral-700">服务状态</span>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-neutral-500">API 服务</span>
                  <span className={`flex items-center gap-1.5 ${backendStatus.api ? "text-emerald-600" : "text-red-500"}`}>
                    <span className={`w-2 h-2 rounded-full ${backendStatus.api ? "bg-emerald-500" : "bg-red-500"}`} />
                    {backendStatus.api ? "已配置" : "未配置"}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-neutral-500">Tavily API</span>
                  <span className={`flex items-center gap-1.5 ${backendStatus.tavily ? "text-emerald-600" : "text-amber-500"}`}>
                    <span className={`w-2 h-2 rounded-full ${backendStatus.tavily ? "bg-emerald-500" : "bg-amber-500"}`} />
                    {backendStatus.tavily ? "已配置" : "未配置"}
                  </span>
                </div>
              </div>
            </motion.div>
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

            {/* Hashtag Recommender */}
            {copyResults.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.2 }}
              >
                <HashtagRecommender
                  content={`${videoTitle} ${copyResults.map(r => r.content).join(' ')}`}
                  platform={selectedPlatforms[0] || "xiaohongshu"}
                  productInfo={product}
                  onSelectHashtags={(hashtags) => {
                    console.log("Selected hashtags:", hashtags);
                  }}
                />
              </motion.div>
            )}

            {/* Export Panel */}
            <ExportPanel content={exportContent} disabled={copyResults.length === 0} />

            {/* Video Generation */}
            {copyResults.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.3 }}
              >
                <VideoGenerator script={videoScript} title={videoTitle} />
              </motion.div>
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
}

export default function ContentPage() {
  return (
    <SidebarNav>
      <ToastProvider>
        <ContentPageContent />
      </ToastProvider>
    </SidebarNav>
  );
}
