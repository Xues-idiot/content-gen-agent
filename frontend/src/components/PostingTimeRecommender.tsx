"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Clock, TrendingUp, Calendar, AlertCircle, CheckCircle2 } from "lucide-react";
import { useToast } from "@/components/Toast";
import { API_BASE_URL } from "@/lib/api";

interface TimeSlot {
  time: string;
  day_of_week: string;
  score: number;
  exposure: "低" | "中" | "高";
  engagement: "低" | "中" | "高";
  reason: string;
}

interface WeeklyData {
  best_hour: string;
  best_hour_name: string;
  score: number;
  is_weekend: boolean;
}

interface PostingTimeRecommenderProps {
  platform?: string;
  industry?: string;
  onSelectTime?: (day: string, time: string) => void;
}

export default function PostingTimeRecommender({
  platform = "xiaohongshu",
  industry = "通用",
  onSelectTime,
}: PostingTimeRecommenderProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [bestTimes, setBestTimes] = useState<TimeSlot[]>([]);
  const [worstTimes, setWorstTimes] = useState<TimeSlot[]>([]);
  const [tips, setTips] = useState<string[]>([]);
  const [weeklyData, setWeeklyData] = useState<Record<string, WeeklyData>>({});
  const [activeTab, setActiveTab] = useState<"daily" | "weekly">("daily");
  const { showToast } = useToast();
  const isMountedRef = React.useRef(true);

  React.useEffect(() => {
    isMountedRef.current = true;
    return () => { isMountedRef.current = false; };
  }, []);

  const fetchPostingTime = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/posting-time/suggest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ platform, industry, days_ahead: 7 }),
      });

      if (!isMountedRef.current) return;
      if (!response.ok) throw new Error("API error");
      const data = await response.json();

      if (!isMountedRef.current) return;
      if (data.success) {
        setBestTimes(data.best_times || []);
        setWorstTimes(data.worst_times || []);
        setTips(data.tips || []);
        showToast("发布时间建议获取成功！", "success");
      } else {
        showToast("获取失败，请重试", "error");
      }
    } catch {
      if (!isMountedRef.current) return;
      showToast("网络错误，请检查后端服务", "error");
    } finally {
      if (isMountedRef.current) setIsLoading(false);
    }
  };

  const fetchWeeklySummary = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/posting-time/weekly`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ platform, industry }),
      });

      if (!isMountedRef.current) return;
      if (!response.ok) throw new Error("API error");
      const data = await response.json();

      if (!isMountedRef.current) return;
      if (data.success) {
        setWeeklyData(data.weekly_data || {});
        showToast("每周汇总获取成功！", "success");
      } else {
        showToast("获取失败，请重试", "error");
      }
    } catch {
      if (!isMountedRef.current) return;
      showToast("网络错误，请检查后端服务", "error");
    } finally {
      setIsLoading(false);
    }
  };

  const handleTabChange = (tab: "daily" | "weekly") => {
    setActiveTab(tab);
    if (tab === "daily" && bestTimes.length === 0) {
      fetchPostingTime();
    } else if (tab === "weekly" && Object.keys(weeklyData).length === 0) {
      fetchWeeklySummary();
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return "text-red-500 bg-red-50";
    if (score >= 50) return "text-orange-500 bg-orange-50";
    return "text-gray-500 bg-gray-50";
  };

  const getExposureIcon = (exposure: string) => {
    if (exposure === "高") return <TrendingUp className="w-4 h-4 text-red-500" />;
    if (exposure === "中") return <TrendingUp className="w-4 h-4 text-orange-500" />;
    return <TrendingUp className="w-4 h-4 text-gray-400" />;
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
              <Clock className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">最佳发布时间建议</h3>
              <p className="text-xs text-gray-500">
                {platform === "xiaohongshu" ? "小红书" : platform === "tiktok" ? "抖音" : platform} · {industry}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex border-b border-gray-100">
        <button
          onClick={() => handleTabChange("daily")}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === "daily"
              ? "text-blue-600 border-b-2 border-blue-600 bg-blue-50/50"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          <Calendar className="w-4 h-4 inline mr-1.5" />
          每日详情
        </button>
        <button
          onClick={() => handleTabChange("weekly")}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === "weekly"
              ? "text-blue-600 border-b-2 border-blue-600 bg-blue-50/50"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          <Clock className="w-4 h-4 inline mr-1.5" />
          每周概览
        </button>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Daily View */}
        <AnimatePresence mode="wait">
          {activeTab === "daily" && (
            <motion.div
              key="daily"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              {bestTimes.length === 0 && !isLoading ? (
                <div className="text-center py-8">
                  <Clock className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                  <p className="text-sm text-gray-500">点击按钮获取发布时间建议</p>
                </div>
              ) : (
                <>
                  {/* Best Times */}
                  <div>
                    <div className="flex items-center gap-1.5 mb-2">
                      <CheckCircle2 className="w-4 h-4 text-green-500" />
                      <span className="text-sm font-medium text-gray-700">最佳时段</span>
                    </div>
                    <div className="space-y-2">
                      {bestTimes.slice(0, 5).map((slot, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-3 bg-gradient-to-r from-green-50 to-white rounded-xl border border-green-100 cursor-pointer hover:border-green-200 transition-colors"
                          onClick={() => onSelectTime?.(slot.day_of_week, slot.time)}
                        >
                          <div className="flex items-center gap-3">
                            <div className="text-xs text-gray-500 w-12">{slot.day_of_week}</div>
                            <div className="font-medium text-gray-900">{slot.time}</div>
                            <div className="text-xs text-gray-500">{slot.reason}</div>
                          </div>
                          <div className="flex items-center gap-2">
                            {getExposureIcon(slot.exposure)}
                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${getScoreColor(slot.score)}`}>
                              {slot.score}分
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Worst Times */}
                  {worstTimes.length > 0 && (
                    <div>
                      <div className="flex items-center gap-1.5 mb-2">
                        <AlertCircle className="w-4 h-4 text-red-400" />
                        <span className="text-sm font-medium text-gray-700">建议避开</span>
                      </div>
                      <div className="space-y-2">
                        {worstTimes.slice(0, 3).map((slot, idx) => (
                          <div
                            key={idx}
                            className="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-100"
                          >
                            <div className="flex items-center gap-3">
                              <div className="text-xs text-gray-500 w-12">{slot.day_of_week}</div>
                              <div className="font-medium text-gray-900">{slot.time}</div>
                            </div>
                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${getScoreColor(slot.score)}`}>
                              {slot.score}分
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Tips */}
                  {tips.length > 0 && (
                    <div className="p-3 bg-blue-50 rounded-xl border border-blue-100">
                      <div className="text-xs font-medium text-blue-700 mb-2">发布建议</div>
                      <ul className="space-y-1">
                        {tips.map((tip, idx) => (
                          <li key={idx} className="text-xs text-blue-600 flex items-start gap-1.5">
                            <span className="text-blue-400">•</span>
                            {tip}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Weekly View */}
        <AnimatePresence mode="wait">
          {activeTab === "weekly" && (
            <motion.div
              key="weekly"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-3"
            >
              {Object.keys(weeklyData).length === 0 && !isLoading ? (
                <div className="text-center py-8">
                  <Clock className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                  <p className="text-sm text-gray-500">点击按钮获取每周汇总</p>
                </div>
              ) : (
                <>
                  {/* Weekly Grid */}
                  <div className="grid grid-cols-7 gap-2">
                    {["周一", "周二", "周三", "周四", "周五", "周六", "周日"].map((day) => {
                      const data = weeklyData[day];
                      const isWeekend = day === "周六" || day === "周日";

                      return (
                        <div
                          key={day}
                          className={`
                            p-2 rounded-xl border text-center cursor-pointer transition-all
                            ${isWeekend
                              ? "bg-purple-50 border-purple-100 hover:border-purple-200"
                              : "bg-blue-50 border-blue-100 hover:border-blue-200"
                            }
                            ${data ? "" : "opacity-50"}
                          `}
                          onClick={() => data && onSelectTime?.(day, data.best_hour)}
                        >
                          <div className={`text-xs font-medium ${isWeekend ? "text-purple-600" : "text-blue-600"}`}>
                            {day}
                          </div>
                          {data && (
                            <>
                              <div className="text-sm font-semibold text-gray-900 mt-1">
                                {data.best_hour}
                              </div>
                              <div className="text-xs text-gray-500">
                                {data.best_hour_name}
                              </div>
                              <div className={`mt-1 px-1.5 py-0.5 rounded text-xs font-medium ${getScoreColor(data.score)}`}>
                                {data.score}分
                              </div>
                            </>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  {/* Legend */}
                  <div className="flex items-center justify-center gap-4 pt-2 border-t border-gray-100">
                    <div className="flex items-center gap-1.5">
                      <div className="w-3 h-3 rounded bg-blue-100 border border-blue-200" />
                      <span className="text-xs text-gray-500">工作日</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-3 h-3 rounded bg-purple-100 border border-purple-200" />
                      <span className="text-xs text-gray-500">周末</span>
                    </div>
                  </div>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-white/80 flex items-center justify-center">
          <div className="flex items-center gap-2 text-blue-600">
            <Clock className="w-5 h-5 animate-spin" />
            <span className="text-sm">分析中...</span>
          </div>
        </div>
      )}
    </div>
  );
}