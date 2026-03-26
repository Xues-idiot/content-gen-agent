"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  History,
  Search,
  Trash2,
  Edit3,
  Loader2,
  Calendar,
  Tag,
  FileText,
  Archive,
  X,
  Check,
} from "lucide-react";
import { useToast } from "@/components/Toast";
import { API_BASE_URL } from "@/lib/api";

interface ContentRecord {
  id: string;
  platform: string;
  title: string;
  content: string;
  tags: string[];
  created_at: string;
  updated_at: string;
  is_draft: boolean;
  product_name: string;
  metadata: Record<string, any>;
}

interface ContentStats {
  total: number;
  drafts: number;
  published: number;
  platforms: string[];
}

interface ContentHistoryProps {
  onLoadRecord?: (record: ContentRecord) => void;
}

export default function ContentHistory({ onLoadRecord }: ContentHistoryProps) {
  const [records, setRecords] = useState<ContentRecord[]>([]);
  const [stats, setStats] = useState<ContentStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [keyword, setKeyword] = useState("");
  const [platformFilter, setPlatformFilter] = useState("");
  const [showDraftsOnly, setShowDraftsOnly] = useState<boolean | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<ContentRecord | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({ title: "", content: "", tags: "" });
  const { showToast } = useToast();
  const isMountedRef = React.useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    return () => { isMountedRef.current = false; };
  }, []);

  const loadRecords = async (searchKeyword = keyword, platform = platformFilter, drafts = showDraftsOnly) => {
    setIsSearching(true);
    try {
      const params = new URLSearchParams();
      if (searchKeyword) params.append("keyword", searchKeyword);
      if (platform) params.append("platform", platform);
      if (drafts !== null) params.append("is_draft", String(drafts));

      const response = await fetch(`${API_BASE_URL}/api/v1/content/history?${params}`);
      if (!isMountedRef.current) return;
      if (!response.ok) throw new Error("API error");

      const data = await response.json();
      if (!isMountedRef.current) return;

      if (data.success) {
        setRecords(data.records || []);
        if (data.stats) setStats(data.stats);
      }
    } catch {
      if (!isMountedRef.current) return;
      showToast("加载历史记录失败", "error");
    } finally {
      if (isMountedRef.current) setIsSearching(false);
    }
  };

  useEffect(() => {
    loadRecords();
  }, []);

  const handleSearch = () => {
    loadRecords(keyword, platformFilter, showDraftsOnly);
  };

  const handleDelete = async (recordId: string) => {
    if (!confirm("确定要删除这条记录吗？")) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/content/history/${recordId}`, {
        method: "DELETE",
      });

      if (!isMountedRef.current) return;
      if (!response.ok) throw new Error("API error");

      const data = await response.json();
      if (!isMountedRef.current) return;

      if (data.success) {
        showToast("删除成功", "success");
        loadRecords();
      } else {
        showToast("删除失败", "error");
      }
    } catch {
      if (!isMountedRef.current) return;
      showToast("网络错误", "error");
    }
  };

  const handleEdit = (record: ContentRecord) => {
    setSelectedRecord(record);
    setEditForm({
      title: record.title,
      content: record.content,
      tags: record.tags.join(", "),
    });
    setIsEditing(true);
  };

  const handleSaveEdit = async () => {
    if (!selectedRecord) return;

    try {
      const tags = editForm.tags.split(",").map(t => t.trim()).filter(Boolean);

      const response = await fetch(`${API_BASE_URL}/api/v1/content/history/${selectedRecord.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: editForm.title,
          content: editForm.content,
          tags: tags,
        }),
      });

      if (!isMountedRef.current) return;
      if (!response.ok) throw new Error("API error");

      const data = await response.json();
      if (!isMountedRef.current) return;

      if (data.success) {
        showToast("更新成功", "success");
        setIsEditing(false);
        setSelectedRecord(null);
        loadRecords();
      } else {
        showToast("更新失败", "error");
      }
    } catch {
      if (!isMountedRef.current) return;
      showToast("网络错误", "error");
    }
  };

  const handleLoadToEditor = (record: ContentRecord) => {
    onLoadRecord?.(record);
    showToast("已加载到编辑器", "success");
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getPlatformLabel = (platform: string) => {
    const labels: Record<string, string> = {
      xiaohongshu: "小红书",
      tiktok: "抖音",
      official: "公众号",
      friend_circle: "朋友圈",
    };
    return labels[platform] || platform;
  };

  const getPlatformColor = (platform: string) => {
    const colors: Record<string, string> = {
      xiaohongshu: "bg-pink-100 text-pink-700",
      tiktok: "bg-black text-white",
      official: "bg-blue-100 text-blue-700",
      friend_circle: "bg-green-100 text-green-700",
    };
    return colors[platform] || "bg-gray-100 text-gray-700";
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-amber-50 to-orange-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
            <History className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">内容历史</h3>
            <p className="text-xs text-gray-500">管理已生成的内容记录</p>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-amber-50 rounded-lg p-2 text-center">
              <div className="text-lg font-bold text-amber-600">{stats.total}</div>
              <div className="text-xs text-amber-500">总计</div>
            </div>
            <div className="bg-orange-50 rounded-lg p-2 text-center">
              <div className="text-lg font-bold text-orange-600">{stats.drafts}</div>
              <div className="text-xs text-orange-500">草稿</div>
            </div>
            <div className="bg-green-50 rounded-lg p-2 text-center">
              <div className="text-lg font-bold text-green-600">{stats.published}</div>
              <div className="text-xs text-green-500">已发布</div>
            </div>
          </div>
        )}

        {/* Search Filters */}
        <div className="space-y-2">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="搜索标题或内容..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-300 focus:border-transparent"
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={isSearching}
              className="px-3 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 disabled:opacity-50 transition-colors"
            >
              {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            </button>
          </div>

          <div className="flex gap-2">
            <select
              value={platformFilter}
              onChange={(e) => setPlatformFilter(e.target.value)}
              className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-300"
            >
              <option value="">全部平台</option>
              <option value="xiaohongshu">小红书</option>
              <option value="tiktok">抖音</option>
              <option value="official">公众号</option>
              <option value="friend_circle">朋友圈</option>
            </select>

            <select
              value={showDraftsOnly === null ? "" : showDraftsOnly ? "true" : "false"}
              onChange={(e) => {
                const val = e.target.value;
                setShowDraftsOnly(val === "" ? null : val === "true");
              }}
              className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-300"
            >
              <option value="">全部状态</option>
              <option value="false">已发布</option>
              <option value="true">草稿</option>
            </select>
          </div>
        </div>

        {/* Records List */}
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {records.length === 0 ? (
            <div className="text-center py-8">
              <Archive className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p className="text-sm text-gray-500">暂无历史记录</p>
            </div>
          ) : (
            records.map((record) => (
              <motion.div
                key={record.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-3 bg-gray-50 rounded-xl border border-gray-100 hover:border-amber-200 transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`px-2 py-0.5 text-xs rounded-full ${getPlatformColor(record.platform)}`}>
                        {getPlatformLabel(record.platform)}
                      </span>
                      {record.is_draft && (
                        <span className="px-2 py-0.5 text-xs rounded-full bg-gray-200 text-gray-600">
                          草稿
                        </span>
                      )}
                    </div>
                    <h4 className="font-medium text-gray-900 truncate">{record.title}</h4>
                    <p className="text-xs text-gray-500 mt-1 line-clamp-2">{record.content}</p>
                    {record.tags.length > 0 && (
                      <div className="flex items-center gap-1 mt-2 flex-wrap">
                        <Tag className="w-3 h-3 text-gray-400" />
                        {record.tags.slice(0, 3).map((tag, i) => (
                          <span key={i} className="text-xs px-1.5 py-0.5 bg-gray-200 text-gray-600 rounded">
                            {tag}
                          </span>
                        ))}
                        {record.tags.length > 3 && (
                          <span className="text-xs text-gray-400">+{record.tags.length - 3}</span>
                        )}
                      </div>
                    )}
                    <div className="flex items-center gap-2 mt-2 text-xs text-gray-400">
                      <Calendar className="w-3 h-3" />
                      {formatDate(record.created_at)}
                      {record.product_name && (
                        <>
                          <span>•</span>
                          <span>{record.product_name}</span>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col gap-1">
                    <button
                      onClick={() => handleLoadToEditor(record)}
                      className="p-1.5 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                      title="加载到编辑器"
                    >
                      <FileText className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleEdit(record)}
                      className="p-1.5 text-amber-500 hover:bg-amber-50 rounded-lg transition-colors"
                      title="编辑"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(record.id)}
                      className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                      title="删除"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>

      {/* Edit Modal */}
      <AnimatePresence>
        {isEditing && selectedRecord && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setIsEditing(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">编辑内容</h3>
                <button
                  onClick={() => setIsEditing(false)}
                  className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>

              <div className="p-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">标题</label>
                  <input
                    type="text"
                    value={editForm.title}
                    onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                    className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-300"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">内容</label>
                  <textarea
                    value={editForm.content}
                    onChange={(e) => setEditForm({ ...editForm, content: e.target.value })}
                    rows={8}
                    className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-300 resize-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">标签（用逗号分隔）</label>
                  <input
                    type="text"
                    value={editForm.tags}
                    onChange={(e) => setEditForm({ ...editForm, tags: e.target.value })}
                    placeholder="标签1, 标签2, 标签3"
                    className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-300"
                  />
                </div>
              </div>

              <div className="p-4 border-t border-gray-100 flex justify-end gap-2">
                <button
                  onClick={() => setIsEditing(false)}
                  className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={handleSaveEdit}
                  className="px-4 py-2 text-sm bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors flex items-center gap-1"
                >
                  <Check className="w-4 h-4" />
                  保存
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}