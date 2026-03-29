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
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-amber-200/50 shadow-sm">
        <div className="w-full px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">📢</span>
            <span className="font-bold text-lg bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">Vox</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link
              href="/content"
              className="px-8 py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-full text-base font-semibold hover:from-amber-600 hover:to-orange-600 transition-all shadow-lg shadow-amber-300/40"
            >
              开始创作
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero - Full Width */}
      <section ref={heroRef} className="relative pt-36 pb-24 px-8">
        <div className="w-full text-center">
          <motion.div style={{ y }} className="w-full">
            <span className="inline-block text-sm font-semibold tracking-[0.3em] text-amber-600 uppercase mb-10 px-6 py-2.5 bg-amber-100 rounded-full">
              AI 内容平台
            </span>
            <h1 className="w-full font-bold text-7xl lg:text-[10rem] leading-none tracking-tight mb-12 text-center" style={{ fontFamily: "'Sora', sans-serif" }}>
              <span className="text-stone-800 block">一键生成</span>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-500 via-orange-500 to-rose-500 block">多平台</span>
              <span className="text-stone-800 block">营销内容</span>
            </h1>
            <p className="w-full text-2xl text-stone-600 mb-16 leading-relaxed text-center">
              输入产品信息，AI 自动为你生成适配
              <strong className="text-stone-700"> 小红书 · 抖音 · 公众号 · 朋友圈 </strong>
              的高转化率营销文案
            </p>
            <div className="w-full flex flex-wrap justify-center gap-8">
              <Link
                href="/content"
                className="px-16 py-6 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-full font-bold text-xl hover:from-amber-600 hover:to-orange-600 transition-all shadow-2xl shadow-amber-300/50 inline-flex items-center gap-4"
              >
                开始创作
                <span className="text-2xl">→</span>
              </Link>
              <Link
                href="/generators"
                className="px-16 py-6 bg-white border-3 border-amber-300 text-stone-700 rounded-full font-bold text-xl hover:border-amber-500 hover:text-amber-700 hover:bg-amber-50 transition-all shadow-xl inline-flex items-center gap-4"
              >
                浏览工具集
              </Link>
            </div>
          </motion.div>

          {/* Stats */}
          <div className="w-full flex justify-center gap-32 mt-28 pt-12 border-t-2 border-amber-200">
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
                transition={{ delay: i * 0.15 }}
                className="text-center"
              >
                <div className="text-6xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">{stat.value}</div>
                <div className="text-lg text-stone-500 mt-3">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Platforms - Full Width */}
      <Section className="py-32 px-8 bg-gradient-to-br from-amber-100 via-orange-100 to-rose-100/50">
        <div className="w-full">
          <h2 className="w-full text-5xl lg:text-7xl font-bold text-center mb-6 text-stone-800">
            支持主流社交平台
          </h2>
          <p className="w-full text-center text-stone-600 mb-20 text-xl">
            覆盖国内主流社交媒体，一站式内容适配
          </p>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 px-8">
            {PLATFORMS.map((platform, i) => (
              <motion.div
                key={platform.id}
                initial={{ opacity: 0, y: 30, scale: 0.95 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                viewport={{ once: true }}
                whileHover={{ scale: 1.05, y: -8 }}
                transition={{ delay: i * 0.1, duration: 0.4 }}
                className="bg-white/90 backdrop-blur rounded-3xl p-10 text-center border border-white shadow-2xl shadow-amber-200/30 hover:shadow-amber-300/50"
              >
                <div className="text-6xl mb-6">{platform.emoji}</div>
                <h3 className="font-semibold text-stone-800 text-2xl mb-3">{platform.name}</h3>
                <p className="text-base text-stone-500">{platform.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* Features - Full Width */}
      <Section className="py-32 px-8 bg-gradient-to-b from-stone-100 to-amber-50/50">
        <div className="w-full">
          <h2 className="w-full text-5xl lg:text-7xl font-bold text-stone-800 mb-6 text-center">
            AI 驱动的内容创作体验
          </h2>
          <p className="w-full text-center text-stone-600 mb-20 text-xl">
            强大的 AI 能力，让内容创作更高效
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-10 px-8">
            {FEATURES.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                whileHover={{ y: -8, boxShadow: "0 30px 60px -15px rgba(245, 158, 11, 0.3)" }}
                transition={{ delay: i * 0.08, duration: 0.4 }}
                className="bg-white rounded-3xl p-10 border border-amber-100 hover:border-amber-300 transition-all shadow-xl hover:shadow-2xl"
              >
                <div className="text-5xl mb-6">{feature.icon}</div>
                <h3 className="font-semibold text-stone-800 mb-4 text-2xl">{feature.title}</h3>
                <p className="text-base text-stone-600 leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* CTA - Full Width */}
      <Section className="py-36 px-8 bg-gradient-to-br from-amber-400 via-orange-400 to-rose-400/80 relative overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-20 left-[10%] w-60 h-60 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-[10%] w-80 h-80 bg-rose-300 rounded-full blur-3xl"></div>
        </div>
        <div className="w-full text-center relative z-10">
          <h2 className="w-full text-5xl lg:text-8xl font-bold text-white mb-8 leading-tight text-center">
            准备好提升你的<br />
            <span className="text-amber-100">内容创作效率</span><br />
            了吗？
          </h2>
          <p className="w-full text-2xl text-amber-100/90 mb-16 text-center">
            告别繁琐的内容创作流程，让 AI 为你代劳
          </p>
          <Link
            href="/content"
            className="inline-flex items-center gap-4 px-20 py-8 bg-white text-amber-600 rounded-full font-bold text-2xl hover:bg-amber-50 transition-all shadow-3xl hover:shadow-4xl hover:scale-105"
          >
            立即开始体验
            <span className="text-3xl">→</span>
          </Link>
        </div>
      </Section>

      {/* Footer */}
      <footer className="py-14 px-8 bg-stone-900">
        <div className="w-full flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <span className="text-2xl">📢</span>
            <span className="font-bold text-white text-lg">Vox</span>
            <span className="text-stone-400 text-sm ml-3">v0.1.0</span>
          </div>
          <div className="flex gap-12 text-base text-stone-400">
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
