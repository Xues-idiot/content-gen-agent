"use client";

import { motion } from "framer-motion";
import { BarChart3, TrendingUp, AlertTriangle, CheckCircle } from "lucide-react";
import { useState, useEffect } from "react";
import { API_BASE_URL } from "@/lib/api";

interface PlatformStats {
  total_contents: number;
  avg_quality_score: number;
  avg_word_count: number;
  total_violations: number;
  violation_rate: number;
}

interface TrendData {
  date: string;
  avg_score: number;
  content_count: number;
  violation_rate: number;
}

interface PlatformComparison {
  platform: string;
  total_contents: number;
  avg_quality: number;
  min_quality: number;
  max_quality: number;
  total_violations: number;
}

const platformColors = {
  xiaohongshu: { bg: "bg-gradient-to-br from-pink-500 to-rose-600", text: "text-pink-600", light: "bg-pink-50" },
  tiktok: { bg: "bg-gradient-to-br from-gray-800 to-black", text: "text-gray-800", light: "bg-gray-100" },
  official: { bg: "bg-gradient-to-br from-blue-500 to-blue-700", text: "text-blue-600", light: "bg-blue-50" },
  friend_circle: { bg: "bg-gradient-to-br from-green-500 to-emerald-600", text: "text-green-600", light: "bg-green-50" },
};

const platformLabels = {
  xiaohongshu: "小红书",
  tiktok: "抖音",
  official: "公众号",
  friend_circle: "朋友圈",
};

export default function AnalyticsDashboard() {
  const [platformStats, setPlatformStats] = useState<PlatformStats | null>(null);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [comparison, setComparison] = useState<PlatformComparison[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "trends" | "compare">("overview");

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const [statsRes, trendsRes, compareRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/analytics/platform`),
        fetch(`${API_BASE_URL}/api/v1/analytics/trends?days=7`),
        fetch(`${API_BASE_URL}/api/v1/analytics/compare`),
      ]);

      if (!statsRes.ok || !trendsRes.ok || !compareRes.ok) {
        throw new Error(`API error: ${statsRes.status || trendsRes.status || compareRes.status}`);
      }

      const statsData = await statsRes.json();
      const trendsData = await trendsRes.json();
      const compareData = await compareRes.json();

      if (statsData.success) {
        setPlatformStats(statsData);
      }
      if (trendsData.success) {
        setTrends(trendsData.trends || []);
      }
      if (compareData.success) {
        const { best_platform, ...rest } = compareData;
        setComparison(Object.entries(rest).map(([platform, data]) => ({
          platform,
          ...(data as object),
        })) as PlatformComparison[]);
      }
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

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

  const renderOverview = () => (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div variants={item} className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 className="w-4 h-4 text-orange-500" />
            <span className="text-xs text-gray-500">总内容数</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{platformStats?.total_contents || 0}</div>
        </motion.div>

        <motion.div variants={item} className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-green-500" />
            <span className="text-xs text-gray-500">平均质量分</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {platformStats?.avg_quality_score?.toFixed(1) || "0.0"}
          </div>
        </motion.div>

        <motion.div variants={item} className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="w-4 h-4 text-blue-500" />
            <span className="text-xs text-gray-500">平均字数</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {platformStats?.avg_word_count?.toFixed(0) || "0"}
          </div>
        </motion.div>

        <motion.div variants={item} className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            <span className="text-xs text-gray-500">违规率</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {platformStats?.violation_rate ? `${(platformStats.violation_rate * 100).toFixed(1)}%` : "0%"}
          </div>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div variants={item} className="bg-gradient-to-r from-orange-50 to-rose-50 rounded-xl p-5 border border-orange-100">
        <h3 className="font-semibold text-gray-900 mb-2">提升建议</h3>
        <ul className="space-y-1.5 text-sm text-gray-600">
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-2" />
            定期检查违规词，确保内容合规
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-2" />
            保持内容长度在平台推荐范围内
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-2" />
            使用适量 emoji 和标签提升互动
          </li>
        </ul>
      </motion.div>
    </motion.div>
  );

  const renderTrends = () => (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-4">
      <h3 className="font-semibold text-gray-900">7日质量趋势</h3>
      {trends.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-xl">
          <TrendingUp className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">暂无趋势数据</p>
        </div>
      ) : (
        <div className="space-y-3">
          {trends.map((trend, idx) => (
            <motion.div
              key={trend.date}
              variants={item}
              className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-gray-700">{trend.date}</span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  trend.avg_score >= 8 ? "bg-green-100 text-green-700" :
                  trend.avg_score >= 6 ? "bg-yellow-100 text-yellow-700" :
                  "bg-red-100 text-red-700"
                }`}>
                  {trend.avg_score.toFixed(1)}分
                </span>
              </div>
              <div className="flex gap-4 text-xs text-gray-500">
                <span>内容数: {trend.content_count}</span>
                <span>违规率: {(trend.violation_rate * 100).toFixed(1)}%</span>
              </div>
              {/* Simple bar visualization */}
              <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-orange-400 to-orange-500 rounded-full transition-all"
                  style={{ width: `${trend.avg_score * 10}%` }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );

  const renderCompare = () => (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-4">
      <h3 className="font-semibold text-gray-900">平台对比</h3>
      {comparison.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-xl">
          <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">暂无对比数据</p>
        </div>
      ) : (
        <div className="space-y-3">
          {comparison.map((item) => {
            const colors = platformColors[item.platform as keyof typeof platformColors] || {
              bg: "bg-gray-500",
              text: "text-gray-600",
              light: "bg-gray-100",
            };
            return (
              <motion.div
                key={item.platform}
                className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className={`w-3 h-3 rounded-full ${colors.bg}`} />
                    <span className="font-medium text-gray-900">
                      {platformLabels[item.platform as keyof typeof platformLabels] || item.platform}
                    </span>
                  </div>
                  <span className="text-lg font-bold text-gray-900">
                    {item.avg_quality.toFixed(1)}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-4 text-xs text-gray-500">
                  <div>
                    <span className="block text-gray-400">内容量</span>
                    <span className="font-medium text-gray-700">{item.total_contents}</span>
                  </div>
                  <div>
                    <span className="block text-gray-400">最高分</span>
                    <span className="font-medium text-gray-700">{item.max_quality.toFixed(1)}</span>
                  </div>
                  <div>
                    <span className="block text-gray-400">违规数</span>
                    <span className="font-medium text-gray-700">{item.total_violations}</span>
                  </div>
                </div>
                <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${colors.bg}`}
                    style={{ width: `${item.avg_quality * 10}%` }}
                  />
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </motion.div>
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">数据分析</h2>
            <p className="text-sm text-gray-500">内容质量追踪与分析</p>
          </div>
        </div>
        <button
          onClick={fetchAnalytics}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium disabled:opacity-50"
        >
          {loading ? "加载中..." : "刷新数据"}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200 pb-2">
        {[
          { id: "overview", label: "总览" },
          { id: "trends", label: "趋势" },
          { id: "compare", label: "对比" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as typeof activeTab)}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              activeTab === tab.id
                ? "bg-blue-50 text-blue-600 border-b-2 border-blue-500"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full" />
        </div>
      ) : (
        <div className="mt-4">
          {activeTab === "overview" && renderOverview()}
          {activeTab === "trends" && renderTrends()}
          {activeTab === "compare" && renderCompare()}
        </div>
      )}
    </motion.div>
  );
}