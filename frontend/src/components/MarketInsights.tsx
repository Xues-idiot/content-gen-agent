"use client";

import React from "react";
import { motion, AnimatePresence } from "motion/react";
import { useContentStore } from "@/store/content-store";

export default function MarketInsights() {
  const { marketResearch, copyResults } = useContentStore();

  const hasData =
    marketResearch.insights.length > 0 ||
    marketResearch.trends.length > 0 ||
    marketResearch.competitors.length > 0;

  if (!hasData || copyResults.length === 0) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="bg-white rounded-xl shadow-md p-6"
    >
      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
        <span className="text-2xl">🔍</span>
        <span style={{ color: "#FF6B35" }}>市场调研洞察</span>
      </h3>

      <div className="space-y-4">
        {/* Trend Topics */}
        {marketResearch.trends.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-1">
              <span>📈</span> 趋势话题
            </h4>
            <div className="flex flex-wrap gap-2">
              {marketResearch.trends.slice(0, 5).map((trend, idx) => (
                <motion.span
                  key={idx}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.4 + idx * 0.05 }}
                  className="px-3 py-1 rounded-full text-sm font-medium"
                  style={{
                    backgroundColor: "#FF6B3515",
                    color: "#FF6B35",
                  }}
                >
                  {trend.length > 50 ? trend.substring(0, 50) + "..." : trend}
                </motion.span>
              ))}
            </div>
          </div>
        )}

        {/* Market Insights */}
        {marketResearch.insights.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-1">
              <span>💡</span> 市场洞察
            </h4>
            <ul className="space-y-2">
              {marketResearch.insights.slice(0, 3).map((insight, idx) => (
                <motion.li
                  key={idx}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + idx * 0.1 }}
                  className="text-sm text-gray-700 flex items-start gap-2 bg-gray-50 p-2 rounded"
                >
                  <span className="text-FF6B35">•</span>
                  <span>
                    {insight.length > 100 ? insight.substring(0, 100) + "..." : insight}
                  </span>
                </motion.li>
              ))}
            </ul>
          </div>
        )}

        {/* Competitor Content */}
        {marketResearch.competitors.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-1">
              <span>🏢</span> 竞品动态
            </h4>
            <div className="space-y-2">
              {marketResearch.competitors.slice(0, 3).map((comp, idx) => (
                <motion.a
                  key={idx}
                  href={comp.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.6 + idx * 0.1 }}
                  className="block p-3 rounded-lg border border-gray-200 hover:border-orange-300 hover:bg-orange-50 transition-colors"
                >
                  <p className="text-sm font-medium text-gray-800">{comp.title}</p>
                  <p className="text-xs text-gray-500 mt-1">{comp.name}</p>
                </motion.a>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
