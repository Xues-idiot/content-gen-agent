"use client";

import React from "react";
import Link from "next/link";
import { motion } from "motion/react";

const PLATFORMS = [
  {
    id: "xiaohongshu",
    name: "小红书",
    icon: "📕",
    description: "种草笔记",
    color: "#EF4444",
  },
  {
    id: "tiktok",
    name: "抖音",
    icon: "📺",
    description: "短视频脚本",
    color: "#EC4899",
  },
  {
    id: "official",
    name: "公众号",
    icon: "📰",
    description: "长文",
    color: "#3B82F6",
  },
  {
    id: "friend_circle",
    name: "朋友圈",
    icon: "👥",
    description: "简短分享",
    color: "#10B981",
  },
];

const FEATURES = [
  {
    icon: "✍️",
    title: "智能文案生成",
    description: "AI 驱动的多平台文案，精准匹配平台风格",
  },
  {
    icon: "🔍",
    title: "违规词检测",
    description: "自动检测广告法违规词，避免法律风险",
  },
  {
    icon: "🖼️",
    title: "配图建议",
    description: "AI 生成的配图提示词，支持多种图片工具",
  },
  {
    icon: "📊",
    title: "质量评分",
    description: "多维度评分体系，量化文案质量",
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: "#FFF8F0" }}>
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-50 via-white to-yellow-50" />
        <div className="absolute top-20 right-10 w-64 h-64 bg-orange-200 rounded-full opacity-20 blur-3xl" />
        <div className="absolute bottom-10 left-10 w-48 h-48 bg-yellow-200 rounded-full opacity-20 blur-3xl" />

        <div className="relative max-w-6xl mx-auto px-4 py-20">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring" }}
                className="inline-block text-7xl mb-6"
              >
                📢
              </motion.span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-5xl md:text-6xl font-bold mb-4"
              style={{ color: "#FF6B35" }}
            >
              Vox
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-2xl md:text-3xl text-gray-700 mb-4 font-medium"
            >
              内容生成 Agent
            </motion.p>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="text-gray-500 mb-8 max-w-xl mx-auto"
            >
              专注于多平台营销内容生成
              <br />
              小红书、抖音、公众号、朋友圈 | 文案 + 配图，一键生成
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <Link
                href="/content"
                className="inline-block px-8 py-4 text-lg font-medium rounded-xl text-white shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5"
                style={{ backgroundColor: "#FF6B35" }}
              >
                开始生成内容 →
              </Link>
            </motion.div>
          </div>

          {/* Platforms */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4"
          >
            {PLATFORMS.map((platform, index) => (
              <motion.div
                key={platform.id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.8 + index * 0.1 }}
                whileHover={{ scale: 1.05, y: -4 }}
                className="bg-white rounded-xl shadow-md p-6 text-center cursor-default"
              >
                <motion.div
                  whileHover={{ rotate: 5 }}
                  className="text-4xl mb-3"
                >
                  {platform.icon}
                </motion.div>
                <div
                  className="font-bold text-lg mb-1"
                  style={{ color: platform.color }}
                >
                  {platform.name}
                </div>
                <div className="text-sm text-gray-500">
                  {platform.description}
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold mb-4" style={{ color: "#1F2937" }}>
              核心功能
            </h2>
            <p className="text-gray-500">
              强大的 AI 能力，简化你的内容创作流程
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {FEATURES.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -4 }}
                className="bg-gray-50 rounded-xl p-6 hover:shadow-md transition-shadow"
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="font-bold text-lg mb-2" style={{ color: "#1F2937" }}>
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-500">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="rounded-2xl p-12 shadow-lg"
            style={{ backgroundColor: "#FF6B35" }}
          >
            <h2 className="text-3xl font-bold text-white mb-4">
              准备好提升你的内容创作效率了吗？
            </h2>
            <p className="text-white/80 mb-8 max-w-lg mx-auto">
              告别繁琐的内容创作流程，让 AI 为你代劳
            </p>
            <Link
              href="/content"
              className="inline-block px-8 py-4 bg-white text-orange-500 text-lg font-bold rounded-xl hover:bg-gray-100 transition-colors"
            >
              立即体验 →
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 bg-white border-t border-gray-200">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <p className="text-gray-500 text-sm">
            Vox 内容生成 Agent v0.1.0 | 基于 AI 的多平台营销内容生成工具
          </p>
        </div>
      </footer>
    </div>
  );
}
