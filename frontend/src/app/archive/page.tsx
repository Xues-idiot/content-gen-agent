"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import SidebarNav from "@/components/SidebarNav";
import { ToastProvider, useToast } from "@/components/Toast";
import {
  Archive,
  Search,
  Trash2,
  Eye,
  Copy,
  Download,
  FolderOpen,
  FileText,
  Clock,
} from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

interface ArchiveItem {
  id: string;
  name: string;
  category: string;
  created_at: string;
  size: number;
}

interface ArchiveDetail {
  id: string;
  name: string;
  category: string;
  created_at: string;
  content: Record<string, any>;
}

function ArchivePageContent() {
  const { showToast } = useToast();
  const [archives, setArchives] = useState<ArchiveItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterCategory, setFilterCategory] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedArchive, setSelectedArchive] = useState<ArchiveDetail | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  useEffect(() => {
    fetchArchives();
  }, [filterCategory]);

  const fetchArchives = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterCategory) params.append("category", filterCategory);
      params.append("limit", "50");

      const response = await fetch(`${API_BASE_URL}/api/v1/archive?${params}`);
      const data = await response.json();
      if (data.archives) {
        setArchives(data.archives);
      }
    } catch (error) {
      console.error("Failed to fetch archives:", error);
    } finally {
      setLoading(false);
    }
  };

  const searchArchives = async (query: string) => {
    if (!query.trim()) {
      fetchArchives();
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/archive/search?keyword=${encodeURIComponent(query)}`
      );
      const data = await response.json();
      if (data.results) {
        setArchives(data.results);
      }
    } catch (error) {
      console.error("Failed to search archives:", error);
    } finally {
      setLoading(false);
    }
  };

  const viewArchive = async (archiveId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/archive/${archiveId}`);
      const data = await response.json();
      if (data.archive) {
        setSelectedArchive(data.archive);
        setShowDetailModal(true);
      }
    } catch (error) {
      showToast("获取详情失败", "error");
    }
  };

  const deleteArchive = async (archiveId: string) => {
    if (!confirm("确定要删除这个归档吗？")) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/archive/${archiveId}`, {
        method: "DELETE",
      });
      if (response.ok) {
        setArchives((prev) => prev.filter((a) => a.id !== archiveId));
        showToast("归档已删除", "success");
      }
    } catch {
      showToast("删除失败", "error");
    }
  };

  const copyArchiveContent = async (archive: ArchiveDetail) => {
    try {
      const content = JSON.stringify(archive.content, null, 2);
      await navigator.clipboard.writeText(content);
      showToast("已复制到剪贴板", "success");
    } catch {
      showToast("复制失败", "error");
    }
  };

  const downloadArchive = (archive: ArchiveDetail) => {
    const blob = new Blob([JSON.stringify(archive.content, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${archive.name || archive.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("下载开始", "success");
  };

  const filteredArchives = archives.filter((a) => {
    const matchesSearch =
      !searchQuery ||
      a.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = !filterCategory || a.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = [...new Set(archives.map((a) => a.category))];

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

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
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-400 to-green-500 flex items-center justify-center">
            <Archive className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">内容归档</h1>
            <p className="text-gray-500 text-sm">管理和复用历史生成的内容</p>
          </div>
        </div>
      </motion.div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="搜索归档..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && searchArchives(searchQuery)}
            className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-green-300 focus:ring-2 focus:ring-green-100 outline-none transition-all"
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFilterCategory(null)}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
              !filterCategory
                ? "bg-green-500 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            全部
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setFilterCategory(cat)}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                filterCategory === cat
                  ? "bg-green-500 text-white"
                  : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Archives Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full" />
        </div>
      ) : filteredArchives.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16 bg-gray-50 rounded-xl"
        >
          <FolderOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg mb-2">暂无归档内容</p>
          <p className="text-gray-400 text-sm">
            在内容生成页面可以将满意的内容保存到归档
          </p>
        </motion.div>
      ) : (
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          {filteredArchives.map((archive) => (
            <motion.div
              key={archive.id}
              variants={item}
              className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <FileText className="w-4 h-4 text-gray-400" />
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                      {archive.category}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-900 truncate">
                    {archive.name || archive.id}
                  </h3>
                </div>
                <span className="text-xs text-gray-400">{formatSize(archive.size)}</span>
              </div>

              <div className="flex items-center gap-2 text-xs text-gray-400 mb-4">
                <Clock className="w-3 h-3" />
                {new Date(archive.created_at).toLocaleDateString("zh-CN")}
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => viewArchive(archive.id)}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-sm font-medium text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                >
                  <Eye className="w-4 h-4" />
                  查看
                </button>
                <button
                  onClick={() => copyArchiveContent(archive as any)}
                  className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                  title="复制内容"
                >
                  <Copy className="w-4 h-4" />
                </button>
                <button
                  onClick={() => downloadArchive(archive as any)}
                  className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                  title="下载"
                >
                  <Download className="w-4 h-4" />
                </button>
                <button
                  onClick={() => deleteArchive(archive.id)}
                  className="p-2 text-gray-500 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  title="删除"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Detail Modal */}
      {showDetailModal && selectedArchive && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
        >
          <div
            className="absolute inset-0 bg-black/30"
            onClick={() => setShowDetailModal(false)}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden"
          >
            <div className="flex items-center justify-between p-5 border-b border-gray-100">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {selectedArchive.name || "归档详情"}
                </h2>
                <p className="text-sm text-gray-500">
                  {selectedArchive.category} |{" "}
                  {new Date(selectedArchive.created_at).toLocaleString("zh-CN")}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => copyArchiveContent(selectedArchive)}
                  className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                  title="复制"
                >
                  <Copy className="w-5 h-5" />
                </button>
                <button
                  onClick={() => downloadArchive(selectedArchive)}
                  className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                  title="下载"
                >
                  <Download className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  ✕
                </button>
              </div>
            </div>
            <div className="p-5 overflow-y-auto max-h-[60vh]">
              <pre className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded-xl overflow-x-auto">
                {JSON.stringify(selectedArchive.content, null, 2)}
              </pre>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}

export default function ArchivePage() {
  return (
    <SidebarNav>
      <ToastProvider>
        <ArchivePageContent />
      </ToastProvider>
    </SidebarNav>
  );
}
