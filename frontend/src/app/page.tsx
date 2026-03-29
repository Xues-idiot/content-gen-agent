"use client";

import React, { useRef } from "react";
import Link from "next/link";
import { motion, useScroll, useTransform, useInView } from "motion/react";

const PLATFORMS = [
  { id: "xiaohongshu", name: "小红书", emoji: "📕", description: "种草笔记 · 长文案", gradient: "from-pink-500 to-rose-500" },
  { id: "tiktok", name: "抖音", emoji: "📺", description: "短视频口播脚本", gradient: "from-purple-500 to-pink-500" },
  { id: "official", name: "公众号", emoji: "📰", description: "深度长文 · 排版", gradient: "from-blue-500 to-cyan-500" },
  { id: "friend_circle", name: "朋友圈", emoji: "👥", description: "简短分享 · 互动", gradient: "from-emerald-500 to-teal-500" },
];

const FEATURES = [
  { title: "智能生成", desc: "基于大语言模型，理解平台特性与用户心理，生成高转化率内容", icon: "💡" },
  { title: "合规检测", desc: "内置广告法违规词库，自动检测并提供修改建议", icon: "🛡️" },
  { title: "配图建议", desc: "AI 生成配套图片提示词，支持多种图片生成工具", icon: "🖼️" },
  { title: "质量评分", desc: "多维度评分体系，量化文案质量，指明优化方向", icon: "📊" },
  { title: "多平台适配", desc: "一次输入，多平台内容一键生成，保持风格一致性", icon: "🔄" },
  { title: "营销工具集", desc: "标签推荐、发布时间、AB测试等实用工具", icon: "🎨" },
];

function Section({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });
  return (
    <motion.section
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
      className={className}
    >
      {children}
    </motion.section>
  );
}

export default function HomePage() {
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: heroRef });
  const y = useTransform(scrollYProgress, [0, 1], [0, -50]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-orange-50 to-stone-100 overflow-x-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-amber-50/95 via-orange-50/95 to-amber-50/95 backdrop-blur-md border-b border-amber-200/50 shadow-sm shadow-amber-200/20">
        <div className="max-w-7xl mx-auto px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">📢</span>
            <span className="font-bold text-lg bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">Vox</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link
              href="/content"
              className="px-6 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-full text-sm font-medium hover:from-amber-600 hover:to-orange-600 transition-all shadow-md shadow-amber-300/40 hover:shadow-lg hover:shadow-amber-400/50"
            >
              开始创作
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section ref={heroRef} className="relative pt-44 pb-28 px-8">
        <div style={{ maxWidth: "900px", margin: "0 auto" }} className="text-center">
          <motion.div style={{ y }} className="text-center">
            <span className="inline-block text-xs font-semibold tracking-[0.25em] text-amber-600 uppercase mb-8 px-5 py-2 bg-amber-100 rounded-full">
              AI 内容平台
            </span>
            <h1 className="font-bold text-6xl lg:text-8xl leading-tight tracking-tight mb-10 text-center" style={{ fontFamily: "'Sora', sans-serif" }}>
              <span className="text-stone-800 block text-center">一键生成</span>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-500 via-orange-500 to-rose-500 block text-center my-2">多平台</span>
              <span className="text-stone-800 block text-center">营销内容</span>
            </h1>
            <p className="text-xl text-stone-600 max-w-2xl mx-auto mb-14 leading-relaxed text-center">
              输入产品信息，AI 自动为你生成适配
              <strong className="text-stone-700"> 小红书 · 抖音 · 公众号 · 朋友圈 </strong>
              的高转化率营销文案
            </p>
            <div className="flex flex-wrap justify-center gap-6">
              <Link
                href="/content"
                className="px-14 py-5 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-full font-semibold hover:from-amber-600 hover:to-orange-600 transition-all shadow-xl shadow-amber-300/50 hover:shadow-2xl hover:shadow-amber-400/60 inline-flex items-center gap-3 text-lg"
              >
                开始创作
                <span className="text-xl">→</span>
              </Link>
              <Link
                href="/generators"
                className="px-14 py-5 bg-white border-2 border-amber-300 text-stone-700 rounded-full font-semibold hover:border-amber-500 hover:text-amber-700 hover:bg-amber-50 transition-all shadow-lg hover:shadow-xl inline-flex items-center gap-3 text-lg"
              >
                浏览工具集
              </Link>
            </div>
          </motion.div>

          {/* Stats */}
          <div className="flex justify-center gap-20 mt-24 pt-12 border-t border-amber-200">
            {[
              { value: "50+", label: "设计系统" },
              { value: "4", label: "主流平台" },
              { value: "10+", label: "营销工具" },
            ].map((stat, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center"
              >
                <div className="text-5xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">{stat.value}</div>
                <div className="text-sm text-stone-500 mt-2">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Platforms - Warm Section */}
      <Section className="py-28 px-8 bg-gradient-to-br from-amber-100 via-orange-100 to-rose-100/50">
        <div style={{ maxWidth: "1100px", margin: "0 auto" }}>
          <h2 className="text-4xl lg:text-5xl font-bold text-center mb-5 text-stone-800">
            支持主流社交平台
          </h2>
          <p className="text-center text-stone-600 mb-16 max-w-xl mx-auto text-lg">
            覆盖国内主流社交媒体，一站式内容适配
          </p>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {PLATFORMS.map((platform, i) => (
              <motion.div
                key={platform.id}
                initial={{ opacity: 0, y: 30, scale: 0.95 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                viewport={{ once: true }}
                whileHover={{ scale: 1.05, y: -5 }}
                transition={{ delay: i * 0.1, duration: 0.4 }}
                className="bg-white/80 backdrop-blur rounded-3xl p-8 text-center border border-white shadow-xl shadow-amber-200/30 hover:shadow-2xl hover:shadow-amber-300/40"
              >
                <div className="text-5xl mb-5">{platform.emoji}</div>
                <h3 className="font-semibold text-stone-800 text-lg mb-2">{platform.name}</h3>
                <p className="text-sm text-stone-500">{platform.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* Features */}
      <Section className="py-28 px-8 bg-gradient-to-b from-stone-100 to-amber-50/50">
        <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
          <h2 className="text-4xl lg:text-5xl font-bold text-stone-800 mb-5 text-center">
            AI 驱动的内容创作体验
          </h2>
          <p className="text-center text-stone-600 mb-16 max-w-xl mx-auto text-lg">
            强大的 AI 能力，让内容创作更高效
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {FEATURES.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                whileHover={{ y: -5, boxShadow: "0 25px 50px -12px rgba(245, 158, 11, 0.25)" }}
                transition={{ delay: i * 0.08, duration: 0.4 }}
                className="bg-white rounded-3xl p-8 border border-amber-100 hover:border-amber-300 transition-all shadow-lg hover:shadow-xl"
              >
                <div className="text-4xl mb-5">{feature.icon}</div>
                <h3 className="font-semibold text-stone-800 mb-3 text-xl">{feature.title}</h3>
                <p className="text-sm text-stone-600 leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* CTA - Warm Gradient */}
      <Section className="py-32 px-8 bg-gradient-to-br from-amber-400 via-orange-400 to-rose-400/80 relative overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-16 left-16 w-40 h-40 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-16 right-16 w-56 h-56 bg-rose-300 rounded-full blur-3xl"></div>
        </div>
        <div style={{ maxWidth: "800px", margin: "0 auto" }} className="text-center relative z-10">
          <h2 className="text-4xl lg:text-6xl font-bold text-white mb-6 leading-tight">
            准备好提升你的<br />
            <span className="text-amber-100">内容创作效率</span><br />
            了吗？
          </h2>
          <p className="text-xl text-amber-100/90 mb-14 max-w-lg mx-auto">
            告别繁琐的内容创作流程，让 AI 为你代劳
          </p>
          <Link
            href="/content"
            className="inline-flex items-center gap-3 px-16 py-6 bg-white text-amber-600 rounded-full font-bold text-xl hover:bg-amber-50 transition-all shadow-2xl hover:shadow-3xl hover:scale-105"
          >
            立即开始体验
            <span className="text-2xl">→</span>
          </Link>
        </div>
      </Section>

      {/* Footer */}
      <footer className="py-12 px-8 bg-gradient-to-b from-stone-800 to-stone-900">
        <div style={{ maxWidth: "1100px", margin: "0 auto" }} className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <span className="text-xl">📢</span>
            <span className="font-bold text-white">Vox</span>
            <span className="text-stone-400 text-sm ml-2">v0.1.0</span>
          </div>
          <div className="flex gap-10 text-sm text-stone-400">
            <Link href="/content" className="hover:text-amber-400 transition-colors">内容生成</Link>
            <Link href="/generators" className="hover:text-amber-400 transition-colors">工具集</Link>
            <Link href="/settings" className="hover:text-amber-400 transition-colors">设置</Link>
          </div>
        </div>
      </footer>

      {/* Branding */}
      <a
        href="https://deerflow.tech"
        target="_blank"
        rel="noopener noreferrer"
        className="fixed bottom-6 right-6 bg-gradient-to-r from-amber-500 to-orange-500 text-white px-5 py-2.5 rounded-full text-sm font-medium hover:from-amber-600 hover:to-orange-600 transition-all shadow-lg hover:shadow-xl"
      >
        Created by Deerflow
      </a>
    </div>
  );
}
