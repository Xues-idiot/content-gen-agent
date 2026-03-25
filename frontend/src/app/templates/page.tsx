"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import SidebarNav from "@/components/SidebarNav";
import { ToastProvider, useToast } from "@/components/Toast";
import {
  Sparkles,
  Search,
  Copy,
  Trash2,
  ExternalLink,
  Check,
  FileText,
  MessageSquare,
  BarChart2,
  Users,
} from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

interface Template {
  id: string;
  name: string;
  content: string;
  tags: string[];
  usage_count: number;
  created_at: string;
}

interface TemplateLibrary {
  name: string;
  structure: string[];
  example_title: string;
}

const platformIcons: Record<string, React.ReactNode> = {
  xiaohongshu: <FileText className="w-4 h-4" />,
  tiktok: <MessageSquare className="w-4 h-4" />,
  official: <BarChart2 className="w-4 h-4" />,
  friend_circle: <Users className="w-4 h-4" />,
};

const platformLabels: Record<string, string> = {
  xiaohongshu: "小红书",
  tiktok: "抖音",
  official: "公众号",
  friend_circle: "朋友圈",
};

const platformColors: Record<string, string> = {
  xiaohongshu: "bg-pink-100 text-pink-700 border-pink-200",
  tiktok: "bg-gray-900 text-white border-gray-800",
  official: "bg-blue-100 text-blue-700 border-blue-200",
  friend_circle: "bg-green-100 text-green-700 border-green-200",
};

function TemplatesPageContent() {
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState<string>("xiaohongshu");
  const [libraryTemplates, setLibraryTemplates] = useState<Record<string, TemplateLibrary>>({});
  const [savedTemplates, setSavedTemplates] = useState<Template[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    fetchTemplateLibrary();
    fetchSavedTemplates();
  }, [activeTab]);

  const fetchTemplateLibrary = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/templates/library/${activeTab}`);
      const data = await response.json();
      if (data.success) {
        setLibraryTemplates(data.templates || {});
      }
    } catch (error) {
      console.error("Failed to fetch template library:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSavedTemplates = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/templates/${activeTab}`);
      const data = await response.json();
      if (data.templates) {
        setSavedTemplates(data.templates);
      }
    } catch (error) {
      console.error("Failed to fetch saved templates:", error);
    }
  };

  const deleteTemplate = async (templateId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/templates/${activeTab}/${templateId}`, {
        method: "DELETE",
      });
      if (response.ok) {
        setSavedTemplates((prev) => prev.filter((t) => t.id !== templateId));
        showToast("模板已删除", "success");
      }
    } catch (error) {
      showToast("删除失败", "error");
    }
  };

  const copyToClipboard = async (content: string, templateId: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedId(templateId);
      showToast("已复制到剪贴板", "success");
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      showToast("复制失败", "error");
    }
  };

  const filteredSavedTemplates = savedTemplates.filter((t) =>
    t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.05 },
    },
  };

  const item = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0 },
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-400 to-orange-500 flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">模板库</h1>
            <p className="text-gray-500 text-sm">浏览和使用平台最佳实践模板</p>
          </div>
        </div>
      </motion.div>

      {/* Platform Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {Object.entries(platformLabels).map(([key, label]) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition-all ${
              activeTab === key
                ? "text-white shadow-md"
                : "bg-white text-gray-600 hover:bg-gray-50 border border-gray-200"
            }`}
            style={activeTab === key ? { backgroundColor: "#FF6B35" } : undefined}
          >
            {platformIcons[key]}
            {label}
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="搜索模板..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-orange-300 focus:ring-2 focus:ring-orange-100 outline-none transition-all"
        />
      </div>

      {/* Saved Templates Section */}
      {savedTemplates.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h2 className="text-lg font-semibold text-gray-900 mb-4">我的模板</h2>
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            {filteredSavedTemplates.map((template) => (
              <motion.div
                key={template.id}
                variants={item}
                className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 truncate">{template.name}</h3>
                    <p className="text-xs text-gray-400 mt-1">
                      使用 {template.usage_count} 次 |{" "}
                      {new Date(template.created_at).toLocaleDateString("zh-CN")}
                    </p>
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => copyToClipboard(template.content, template.id)}
                      className="p-2 text-gray-500 hover:text-orange-500 hover:bg-orange-50 rounded-lg transition-colors"
                      title="复制"
                    >
                      {copiedId === template.id ? (
                        <Check className="w-4 h-4 text-green-500" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </button>
                    <button
                      onClick={() => deleteTemplate(template.id)}
                      className="p-2 text-gray-500 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                      title="删除"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <p className="text-sm text-gray-600 line-clamp-3">{template.content}</p>
                {template.tags.length > 0 && (
                  <div className="flex gap-1.5 mt-3 flex-wrap">
                    {template.tags.map((tag, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      )}

      {/* Template Library */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h2 className="text-lg font-semibold text-gray-900 mb-4">平台模板库</h2>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full" />
          </div>
        ) : Object.keys(libraryTemplates).length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-xl">
            <Sparkles className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">暂无模板</p>
          </div>
        ) : (
          <div className="space-y-6">
            {Object.entries(libraryTemplates).map(([key, template]) => (
              <motion.div
                key={key}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm"
              >
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div>
                    <h3 className="font-semibold text-gray-900">{template.name}</h3>
                    <p className="text-sm text-orange-500 mt-1">{template.example_title}</p>
                  </div>
                  <button
                    onClick={() => copyToClipboard(template.structure.join("\n"), key)}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-orange-500 hover:bg-orange-50 rounded-lg transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                    复制结构
                  </button>
                </div>

                {/* Structure Steps */}
                <div className="mb-4">
                  <p className="text-xs text-gray-500 mb-2">内容结构：</p>
                  <div className="flex flex-wrap gap-2">
                    {template.structure.map((step, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-lg text-sm"
                      >
                        <span className="w-5 h-5 rounded-full bg-orange-100 text-orange-600 text-xs font-bold flex items-center justify-center">
                          {idx + 1}
                        </span>
                        <span className="text-gray-700">{step}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
}

export default function TemplatesPage() {
  return (
    <SidebarNav>
      <ToastProvider>
        <TemplatesPageContent />
      </ToastProvider>
    </SidebarNav>
  );
}
