"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import SidebarNav from "@/components/SidebarNav";
import { ToastProvider, useToast } from "@/components/Toast";
import {
  Megaphone,
  Plus,
  X,
  Calendar,
  FileText,
  Clock,
  Trash2,
  Eye,
  Edit2,
  CheckCircle,
  Circle,
  AlertCircle,
} from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

interface Campaign {
  id: string;
  name: string;
  description: string;
  campaign_type: string;
  status: string;
  start_date: string | null;
  end_date: string | null;
  tags: string[];
  created_at: string;
}

interface CampaignContent {
  id: string;
  platform: string;
  title: string;
  content: string;
  scheduled_time: string | null;
  status: string;
}

function CampaignsPageContent() {
  const { showToast } = useToast();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [campaignContents, setCampaignContents] = useState<CampaignContent[]>([]);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);
  const isMountedRef = useRef(true);

  // Form state
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    campaign_type: "product_launch",
    start_date: "",
    end_date: "",
    tags: "",
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    isMountedRef.current = true;
    fetchCampaigns();
    return () => { isMountedRef.current = false; };
  }, [filterStatus]);

  useEffect(() => {
    if (selectedCampaign) {
      fetchCampaignContents(selectedCampaign.id);
    }
  }, [selectedCampaign]);

  const fetchCampaigns = async () => {
    if (!isMountedRef.current) return;
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterStatus) params.append("status", filterStatus);

      const response = await fetch(`${API_BASE_URL}/api/v1/campaigns?${params}`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      if (isMountedRef.current && data.campaigns) {
        setCampaigns(data.campaigns);
      }
    } catch (error) {
      console.error("Failed to fetch campaigns:", error);
      if (isMountedRef.current) {
        showToast("获取营销活动列表失败", "error");
      }
    } finally {
      if (isMountedRef.current) setLoading(false);
    }
  };

  const fetchCampaignContents = async (campaignId: string) => {
    if (!isMountedRef.current) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/campaigns/${campaignId}`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      if (isMountedRef.current && data.contents) {
        setCampaignContents(data.contents);
      }
    } catch (error) {
      console.error("Failed to fetch campaign contents:", error);
      if (isMountedRef.current) {
        showToast("获取活动内容失败", "error");
      }
    }
  };

  const createCampaign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name) {
      showToast("请填写活动名称", "error");
      return;
    }
    if (!isMountedRef.current) return;

    setSubmitting(true);
    try {
      const params = new URLSearchParams({
        name: formData.name,
        description: formData.description,
        campaign_type: formData.campaign_type,
      });
      // Append tags individually for proper array handling (backend expects tags=tag1&tags=tag2)
      if (formData.tags) {
        formData.tags.split(",").forEach(tag => params.append("tags", tag.trim()));
      }
      if (formData.start_date) params.append("start_date", formData.start_date);
      if (formData.end_date) params.append("end_date", formData.end_date);

      const response = await fetch(`${API_BASE_URL}/api/v1/campaigns?${params}`, {
        method: "POST",
      });

      if (response.ok) {
        if (isMountedRef.current) {
          showToast("活动创建成功", "success");
          setShowCreateModal(false);
          setFormData({
            name: "",
            description: "",
            campaign_type: "product_launch",
            start_date: "",
            end_date: "",
            tags: "",
          });
          fetchCampaigns();
        }
      } else {
        if (isMountedRef.current) {
          showToast("创建失败", "error");
        }
      }
    } catch {
      if (isMountedRef.current) {
        showToast("网络错误", "error");
      }
    } finally {
      if (isMountedRef.current) setSubmitting(false);
    }
  };

  const deleteCampaign = async (campaignId: string) => {
    if (!confirm("确定要删除这个活动吗？")) return;
    if (!isMountedRef.current) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/campaigns/${campaignId}`, {
        method: "DELETE",
      });
      if (response.ok) {
        if (isMountedRef.current) {
          setCampaigns((prev) => prev.filter((c) => c.id !== campaignId));
          if (selectedCampaign?.id === campaignId) {
            setSelectedCampaign(null);
          }
          showToast("活动已删除", "success");
        }
      }
    } catch {
      if (isMountedRef.current) {
        showToast("删除失败", "error");
      }
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "paused":
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case "completed":
        return <Circle className="w-4 h-4 text-gray-400" />;
      default:
        return <Circle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "active":
        return "进行中";
      case "paused":
        return "已暂停";
      case "completed":
        return "已完成";
      case "draft":
        return "草稿";
      default:
        return status;
    }
  };

  const campaignTypes: Record<string, string> = {
    product_launch: "产品发布",
    promotion: "促销活动",
    seasonal: "季节性营销",
    brand: "品牌推广",
  };

  const filteredCampaigns = filterStatus
    ? campaigns.filter((c) => c.status === filterStatus)
    : campaigns;

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
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-pink-400 to-pink-500 flex items-center justify-center">
              <Megaphone className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">营销活动</h1>
              <p className="text-gray-500 text-sm">管理和追踪营销活动进度</p>
            </div>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 bg-pink-500 text-white rounded-xl hover:bg-pink-600 transition-colors font-medium shadow-md hover:shadow-lg"
          >
            <Plus className="w-5 h-5" />
            新建活动
          </button>
        </div>
      </motion.div>

      {/* Filter */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setFilterStatus(null)}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
            !filterStatus
              ? "bg-pink-500 text-white"
              : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
          }`}
        >
          全部
        </button>
        {["active", "paused", "completed", "draft"].map((status) => (
          <button
            key={status}
            onClick={() => setFilterStatus(status)}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
              filterStatus === status
                ? "bg-pink-500 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            {getStatusLabel(status)}
          </button>
        ))}
      </div>

      {/* Campaigns List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin w-8 h-8 border-2 border-pink-500 border-t-transparent rounded-full" />
        </div>
      ) : filteredCampaigns.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16 bg-gray-50 rounded-xl"
        >
          <Megaphone className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg mb-2">暂无营销活动</p>
          <p className="text-gray-400 text-sm">点击"新建活动"创建一个营销活动</p>
        </motion.div>
      ) : (
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 lg:grid-cols-2 gap-4"
        >
          {filteredCampaigns.map((campaign) => (
            <motion.div
              key={campaign.id}
              variants={item}
              className={`bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-all cursor-pointer ${
                selectedCampaign?.id === campaign.id ? "ring-2 ring-pink-300" : ""
              }`}
              onClick={() => setSelectedCampaign(campaign)}
            >
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 bg-pink-100 text-pink-700 rounded text-xs">
                      {campaignTypes[campaign.campaign_type] || campaign.campaign_type}
                    </span>
                    <span className="flex items-center gap-1 text-xs text-gray-500">
                      {getStatusIcon(campaign.status)}
                      {getStatusLabel(campaign.status)}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-900">{campaign.name}</h3>
                  {campaign.description && (
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                      {campaign.description}
                    </p>
                  )}
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteCampaign(campaign.id);
                  }}
                  className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div className="flex items-center gap-4 text-xs text-gray-400">
                {campaign.start_date && (
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {new Date(campaign.start_date).toLocaleDateString("zh-CN")}
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {new Date(campaign.created_at).toLocaleDateString("zh-CN")}
                </span>
              </div>

              {campaign.tags && campaign.tags.length > 0 && (
                <div className="flex gap-1.5 mt-3 flex-wrap">
                  {campaign.tags.map((tag, idx) => (
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
      )}

      {/* Campaign Detail Panel */}
      <AnimatePresence>
        {selectedCampaign && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="mt-8 bg-white rounded-xl p-6 border border-gray-100 shadow-sm"
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {selectedCampaign.name}
                </h2>
                <p className="text-sm text-gray-500">{selectedCampaign.description}</p>
              </div>
              <button
                onClick={() => setSelectedCampaign(null)}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Campaign Contents */}
            <div className="mb-4">
              <h3 className="font-medium text-gray-900 mb-3">活动内容</h3>
              {campaignContents.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-4 bg-gray-50 rounded-lg">
                  暂无内容
                </p>
              ) : (
                <div className="space-y-3">
                  {campaignContents.map((content) => (
                    <div
                      key={content.id}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <span className="px-2 py-0.5 bg-pink-100 text-pink-700 rounded text-xs">
                          {content.platform}
                        </span>
                        <span className="text-sm text-gray-700">{content.title}</span>
                      </div>
                      <span className="text-xs text-gray-400">
                        {content.status === "published" ? "已发布" : "待发布"}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Create Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div
              className="absolute inset-0 bg-black/30"
              onClick={() => setShowCreateModal(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between p-5 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">新建营销活动</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={createCampaign} className="p-5 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    活动名称 *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="例如：618大促活动"
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-pink-300 focus:ring-2 focus:ring-pink-100 outline-none transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    活动描述
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                    placeholder="描述活动目标和内容..."
                    rows={3}
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-pink-300 focus:ring-2 focus:ring-pink-100 outline-none transition-all resize-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    活动类型
                  </label>
                  <select
                    value={formData.campaign_type}
                    onChange={(e) =>
                      setFormData({ ...formData, campaign_type: e.target.value })
                    }
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-pink-300 focus:ring-2 focus:ring-pink-100 outline-none transition-all"
                  >
                    <option value="product_launch">产品发布</option>
                    <option value="promotion">促销活动</option>
                    <option value="seasonal">季节性营销</option>
                    <option value="brand">品牌推广</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      开始日期
                    </label>
                    <input
                      type="date"
                      value={formData.start_date}
                      onChange={(e) =>
                        setFormData({ ...formData, start_date: e.target.value })
                      }
                      className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-pink-300 focus:ring-2 focus:ring-pink-100 outline-none transition-all"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      结束日期
                    </label>
                    <input
                      type="date"
                      value={formData.end_date}
                      onChange={(e) =>
                        setFormData({ ...formData, end_date: e.target.value })
                      }
                      className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-pink-300 focus:ring-2 focus:ring-pink-100 outline-none transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    标签（逗号分隔）
                  </label>
                  <input
                    type="text"
                    value={formData.tags}
                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                    placeholder="例如：618, 大促, 优惠"
                    className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-pink-300 focus:ring-2 focus:ring-pink-100 outline-none transition-all"
                  />
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 px-4 py-2.5 border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors font-medium"
                  >
                    取消
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="flex-1 px-4 py-2.5 bg-pink-500 text-white rounded-xl hover:bg-pink-600 transition-colors font-medium disabled:opacity-50"
                  >
                    {submitting ? "创建中..." : "创建活动"}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function CampaignsPage() {
  return (
    <SidebarNav>
      <ToastProvider>
        <CampaignsPageContent />
      </ToastProvider>
    </SidebarNav>
  );
}
