"use client";

import React from "react";
import Link from "next/link";
import { motion } from "motion/react";
import {
  Zap,
  Shield,
  Image,
  BarChart3,
  Sparkles,
  ArrowRight,
  Play,
  CheckCircle2,
  Layers,
  Brain,
  Palette,
} from "lucide-react";

const PLATFORMS = [
  {
    id: "xiaohongshu",
    name: "小红书",
    icon: "📕",
    description: "种草笔记 · 长文案",
    color: "#EF4444",
    gradient: "from-red-500 to-rose-600",
  },
  {
    id: "tiktok",
    name: "抖音",
    icon: "📺",
    description: "短视频口播脚本",
    color: "#EC4899",
    gradient: "from-pink-500 to-fuchsia-600",
  },
  {
    id: "official",
    name: "公众号",
    icon: "📰",
    description: "深度长文 · 排版",
    color: "#3B82F6",
    gradient: "from-blue-500 to-indigo-600",
  },
  {
    id: "friend_circle",
    name: "朋友圈",
    icon: "👥",
    description: "简短分享 · 互动",
    color: "#10B981",
    gradient: "from-emerald-500 to-teal-600",
  },
];

const FEATURES = [
  {
    icon: Brain,
    title: "AI 智能生成",
    description: "基于大语言模型，理解平台特性，生成高转化率内容",
    color: "#5B21B6",
    bg: "bg-violet-50",
    iconColor: "text-violet-600",
  },
  {
    icon: Shield,
    title: "违规词检测",
    description: "内置广告法违规词库，自动检测并提供修改建议",
    color: "#059669",
    bg: "bg-emerald-50",
    iconColor: "text-emerald-600",
  },
  {
    icon: Image,
    title: "配图建议",
    description: "AI 生成配套图片提示词，支持多种图片生成工具",
    color: "#D97706",
    bg: "bg-amber-50",
    iconColor: "text-amber-600",
  },
  {
    icon: BarChart3,
    title: "质量评分",
    description: "多维度评分体系，量化文案质量，指明优化方向",
    color: "#DC2626",
    bg: "bg-red-50",
    iconColor: "text-red-600",
  },
  {
    icon: Layers,
    title: "多平台适配",
    description: "一次输入，多平台内容一键生成，保持风格一致性",
    color: "#7C3AED",
    bg: "bg-purple-50",
    iconColor: "text-purple-600",
  },
  {
    icon: Palette,
    title: "营销工具集",
    description: "标签推荐、发布时间、AB测试等实用工具",
    color: "#DB2777",
    bg: "bg-pink-50",
    iconColor: "text-pink-600",
  },
];

const STATS = [
  { value: "50+", label: "样式系统" },
  { value: "4", label: "主流平台" },
  { value: "10+", label: "营销工具" },
  { value: "毫秒级", label: "生成速度" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background Effects */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 mesh-gradient" />
        <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-gradient-to-br from-violet-200/40 via-transparent to-transparent rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-gradient-to-tr from-orange-200/30 via-transparent to-transparent rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[1000px] bg-gradient-to-r from-violet-100/20 to-orange-100/20 rounded-full blur-3xl" />

        {/* Animated Grid */}
        <div className="absolute inset-0 grid-pattern opacity-30" />

        {/* Floating Orbs */}
        <motion.div
          animate={{
            y: [0, -20, 0],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/4 left-1/4 w-32 h-32 bg-gradient-to-br from-violet-300/20 to-transparent rounded-full blur-xl"
        />
        <motion.div
          animate={{
            y: [0, 20, 0],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
          className="absolute bottom-1/3 right-1/4 w-40 h-40 bg-gradient-to-br from-orange-300/20 to-transparent rounded-full blur-xl"
        />
      </div>

      {/* Navigation */}
      <nav className="relative z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3"
          >
            <div className="relative">
              <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center text-white text-xl shadow-lg shadow-violet-500/25">
                📢
              </div>
              <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-violet-500 to-orange-500 -z-10 blur opacity-30" />
            </div>
            <div>
              <h1 className="font-display text-2xl font-bold text-neutral-900 tracking-tight">
                Vox
              </h1>
              <p className="text-xs text-neutral-500 font-medium tracking-wide">
                AI 内容生成平台
              </p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="flex items-center gap-3"
          >
            <Link
              href="/content"
              className="btn btn-primary btn-md shadow-lg shadow-violet-500/20"
            >
              <Sparkles className="w-4 h-4" />
              开始创作
            </Link>
          </motion.div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative px-6 pt-12 pb-20">
        <div className="max-w-5xl mx-auto text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ delay: 0.1, duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 backdrop-blur-sm border border-violet-200 shadow-sm mb-8"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-violet-500"></span>
            </span>
            <span className="text-sm font-medium text-violet-700">
              基于 AI 的多平台内容生成
            </span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="text-display-xl text-neutral-900 mb-6 leading-tight"
          >
            <span className="gradient-brand bg-clip-text text-transparent">
              一键生成
            </span>
            <br />
            <span className="text-neutral-800">多平台营销内容</span>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35, duration: 0.5 }}
            className="text-body-lg text-neutral-600 max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            输入产品信息，AI 自动为你生成适配
            <span className="font-semibold text-violet-600"> 小红书 </span>
            <span className="font-semibold text-pink-600"> 抖音 </span>
            <span className="font-semibold text-blue-600"> 公众号 </span>
            <span className="font-semibold text-emerald-600"> 朋友圈 </span>
            的营销文案
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
          >
            <Link
              href="/content"
              className="btn btn-secondary btn-xl shadow-xl shadow-orange-500/25 group"
            >
              <Zap className="w-5 h-5 group-hover:scale-110 transition-transform" />
              开始生成内容
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="/generators"
              className="btn btn-outline-primary btn-xl"
            >
              <Play className="w-4 h-4" />
              浏览工具集
            </Link>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto"
          >
            {STATS.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.7 + index * 0.1 }}
                className="card card-bordered p-5 text-center hover:shadow-lg transition-all duration-300"
              >
                <div className="text-display-sm gradient-brand bg-clip-text text-transparent font-bold">
                  {stat.value}
                </div>
                <div className="text-body-xs text-neutral-500 font-medium mt-1">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Platforms Section */}
      <section className="relative px-6 py-16">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-display-md text-neutral-900 mb-4">
              支持的主流平台
            </h2>
            <p className="text-body-md text-neutral-600">
              一次输入，多平台内容同步生成，保持风格一致性
            </p>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {PLATFORMS.map((platform, index) => (
              <motion.div
                key={platform.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -8, scale: 1.02 }}
                className="card card-bordered p-6 cursor-pointer group relative overflow-hidden"
              >
                {/* Gradient Background on Hover */}
                <div
                  className={`absolute inset-0 bg-gradient-to-br ${platform.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}
                />

                {/* Icon */}
                <motion.div
                  whileHover={{ scale: 1.15, rotate: 5 }}
                  className="w-14 h-14 rounded-2xl bg-gradient-to-br from-neutral-100 to-neutral-200 flex items-center justify-center text-2xl mb-4 group-hover:shadow-lg transition-shadow"
                >
                  {platform.icon}
                </motion.div>

                {/* Content */}
                <h3
                  className="font-display text-lg font-bold mb-1"
                  style={{ color: platform.color }}
                >
                  {platform.name}
                </h3>
                <p className="text-body-sm text-neutral-500">
                  {platform.description}
                </p>

                {/* Bottom Accent Line */}
                <div
                  className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r ${platform.gradient} transform origin-left scale-x-0 group-hover:scale-x-100 transition-transform duration-300`}
                />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative px-6 py-20">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-display-md text-neutral-900 mb-4">
              强大的 AI 能力
            </h2>
            <p className="text-body-md text-neutral-600 max-w-2xl mx-auto">
              端到端的营销内容解决方案，让内容创作更高效
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ y: -4 }}
                  className="card card-bordered p-6 group hover:shadow-xl transition-all duration-300"
                >
                  {/* Icon */}
                  <div
                    className={`w-12 h-12 rounded-xl ${feature.bg} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}
                  >
                    <Icon className={`w-6 h-6 ${feature.iconColor}`} />
                  </div>

                  {/* Content */}
                  <h3 className="font-display text-lg font-bold text-neutral-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-body-sm text-neutral-600 leading-relaxed">
                    {feature.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative px-6 py-20">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.5 }}
            className="card card-elevated p-12 text-center relative overflow-hidden"
          >
            {/* Background Gradient */}
            <div className="absolute inset-0 gradient-brand opacity-10" />
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-white/20 to-transparent rounded-full blur-2xl" />

            {/* Content */}
            <div className="relative z-10">
              <motion.div
                initial={{ scale: 0 }}
                whileInView={{ scale: 1 }}
                viewport={{ once: true }}
                transition={{ type: "spring", delay: 0.2 }}
                className="w-16 h-16 rounded-2xl gradient-primary flex items-center justify-center text-white text-2xl mx-auto mb-6 shadow-lg shadow-violet-500/30"
              >
                🚀
              </motion.div>

              <h2 className="text-display-md text-neutral-900 mb-4">
                准备好提升你的内容创作效率了吗？
              </h2>
              <p className="text-body-md text-neutral-600 mb-8 max-w-lg mx-auto">
                告别繁琐的内容创作流程，让 AI 为你代劳
                <br />
                专注于更重要的事情
              </p>

              <Link
                href="/content"
                className="btn btn-secondary btn-xl shadow-xl shadow-orange-500/25 inline-flex items-center gap-2"
              >
                <Sparkles className="w-5 h-5" />
                立即开始体验
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative px-6 py-12 border-t border-neutral-200/50">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center text-white text-sm">
                📢
              </div>
              <div>
                <p className="font-display font-bold text-neutral-900">
                  Vox
                </p>
                <p className="text-xs text-neutral-500">
                  AI 内容生成 Agent v0.1.0
                </p>
              </div>
            </div>

            <div className="flex items-center gap-6 text-body-sm text-neutral-500">
              <Link href="/content" className="hover:text-violet-600 transition-colors">
                内容生成
              </Link>
              <Link href="/generators" className="hover:text-violet-600 transition-colors">
                工具集
              </Link>
              <Link href="/templates" className="hover:text-violet-600 transition-colors">
                模板库
              </Link>
              <Link href="/settings" className="hover:text-violet-600 transition-colors">
                设置
              </Link>
            </div>
          </div>
        </div>
      </footer>

      {/* Deerflow Branding */}
      <a
        href="https://deerflow.tech"
        target="_blank"
        rel="noopener noreferrer"
        className="deerflow-badge"
      >
        Created By Deerflow
      </a>
    </div>
  );
}
