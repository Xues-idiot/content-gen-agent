"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { API_BASE_URL } from "@/lib/api";

interface ServiceInfo {
  name: string;
  description: string;
  module: string;
}

interface GeneratorExplorerProps {
  onGenerate?: (serviceName: string, result: any) => void;
}

export default function GeneratorExplorer({ onGenerate }: GeneratorExplorerProps) {
  const [services, setServices] = useState<ServiceInfo[]>([]);
  const [selectedService, setSelectedService] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  // 常用服务分类
  const categories = {
    marketing: ["email", "campaign", "social_media", "content", "marketing", "advertising", "brand"],
    sales: ["sales", "customer", "lead", "deal", "pipeline", "quote", "roi", "churn"],
    business: ["business", "strategy", "plan", "analysis", "report", "metrics"],
    product: ["product", "feature", "roadmap", "launch"],
    operation: ["process", "workflow", "template", "checklist", "document"],
  };

  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/generators/`);
      if (response.ok) {
        const data = await response.json();
        setServices(data.services);
      }
    } catch (err) {
      setError("Failed to fetch services");
    } finally {
      setIsLoading(false);
    }
  };

  const filteredServices = services.filter((s) =>
    s.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getCategory = (serviceName: string): string => {
    const name = serviceName.toLowerCase();
    for (const [category, keywords] of Object.entries(categories)) {
      if (keywords.some((k) => name.includes(k))) {
        return category;
      }
    }
    return "other";
  };

  const groupedServices = filteredServices.reduce((acc, service) => {
    const category = getCategory(service.name);
    if (!acc[category]) acc[category] = [];
    acc[category].push(service);
    return acc;
  }, {} as Record<string, ServiceInfo[]>);

  const handleGenerate = async (serviceName: string) => {
    setSelectedService(serviceName);
    setIsGenerating(true);
    setResult(null);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/generators/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          service_name: serviceName,
          parameters: {},
        }),
      });

      const data = await response.json();
      if (data.success) {
        setResult(data.result);
        onGenerate?.(serviceName, data.result);
      } else {
        setError(data.error || "Generation failed");
      }
    } catch (err) {
      setError("Network error");
    } finally {
      setIsGenerating(false);
    }
  };

  const getCategoryColor = (category: string): string => {
    const colors: Record<string, string> = {
      marketing: "bg-pink-100 text-pink-800",
      sales: "bg-blue-100 text-blue-800",
      business: "bg-purple-100 text-purple-800",
      product: "bg-green-100 text-green-800",
      operation: "bg-orange-100 text-orange-800",
      other: "bg-gray-100 text-gray-800",
    };
    return colors[category] || colors.other;
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">内容生成器</h2>
        <p className="text-gray-600">浏览并使用 300+ 内容生成服务</p>
      </div>

      {/* 搜索框 */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="搜索服务..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
        />
      </div>

      {/* 服务列表 */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
        </div>
      ) : (
        <div className="space-y-6 max-h-[600px] overflow-y-auto">
          {Object.entries(groupedServices).map(([category, categoryServices]) => (
            <div key={category}>
              <h3 className={`text-sm font-medium px-3 py-1 rounded-full inline-block mb-3 ${getCategoryColor(category)}`}>
                {category.toUpperCase()} ({categoryServices.length})
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                {categoryServices.map((service) => (
                  <motion.button
                    key={service.name}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleGenerate(service.name)}
                    disabled={isGenerating}
                    className={`p-3 text-left rounded-lg border transition-colors ${
                      selectedService === service.name
                        ? "border-orange-500 bg-orange-50"
                        : "border-gray-200 hover:border-orange-300 hover:bg-gray-50"
                    }`}
                  >
                    <div className="text-sm font-medium text-gray-900 truncate">
                      {service.name.replace(/_/g, " ")}
                    </div>
                  </motion.button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 生成结果 */}
      <AnimatePresence>
        {isGenerating && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="mt-6 p-4 bg-gray-50 rounded-lg"
          >
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-orange-500"></div>
              <span className="text-gray-600">正在生成...</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-6"
          >
            <h3 className="text-lg font-medium text-gray-900 mb-3">生成结果</h3>
            <pre className="p-4 bg-gray-900 text-gray-100 rounded-lg overflow-auto max-h-96 text-sm">
              {JSON.stringify(result, null, 2)}
            </pre>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
