"use client";

import React from "react";
import { motion } from "motion/react";
import SidebarNav from "@/components/SidebarNav";
import { ToastProvider } from "@/components/Toast";
import AnalyticsDashboard from "@/components/AnalyticsDashboard";
import { BarChart3 } from "lucide-react";

function AnalyticsPageContent() {
  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-400 to-blue-500 flex items-center justify-center">
            <BarChart3 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">数据分析</h1>
            <p className="text-gray-500 text-sm">追踪内容质量和表现趋势</p>
          </div>
        </div>
      </motion.div>

      {/* Analytics Dashboard Component */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <AnalyticsDashboard />
      </motion.div>
    </div>
  );
}

export default function AnalyticsPage() {
  return (
    <SidebarNav>
      <ToastProvider>
        <AnalyticsPageContent />
      </ToastProvider>
    </SidebarNav>
  );
}
