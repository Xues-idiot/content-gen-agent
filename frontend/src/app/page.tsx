"use client";

import React, { useRef } from "react";
import Link from "next/link";
import { motion, useScroll, useTransform, useInView } from "motion/react";

const PLATFORMS = [
  { id: "xiaohongshu", name: "小红书", emoji: "📕", description: "种草笔记 · 长文案", color: "#E11D48" },
  { id: "tiktok", name: "抖音", emoji: "📺", description: "短视频口播脚本", color: "#DB2777" },
  { id: "official", name: "公众号", emoji: "📰", description: "深度长文 · 排版", color: "#2563EB" },
  { id: "friend_circle", name: "朋友圈", emoji: "👥", description: "简短分享 · 互动", color: "#059669" },
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
      transition={{ duration: 0.6, ease: "easeOut" }}
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
    <div className="min-h-screen bg-stone-50 overflow-x-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-stone-200/50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">📢</span>
            <span className="font-bold text-lg text-stone-900">Vox</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link
              href="/content"
              className="px-5 py-2 bg-stone-900 text-white rounded-full text-sm font-medium hover:bg-stone-800 transition-colors"
            >
              开始创作
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section ref={heroRef} className="relative pt-32 pb-20 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <motion.div style={{ y }}>
            <span className="inline-block text-xs font-semibold tracking-[0.2em] text-amber-600 uppercase mb-4">
              AI 内容平台
            </span>
            <h1 className="font-serif text-5xl lg:text-7xl font-bold text-stone-900 leading-tight tracking-tight mb-6">
              一键生成
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-500 to-orange-600">
                多平台
              </span>
              <br />
              营销内容
            </h1>
            <p className="text-lg text-stone-600 max-w-xl mx-auto mb-10 leading-relaxed">
              输入产品信息，AI 自动为你生成适配
              <strong className="text-stone-900"> 小红书 · 抖音 · 公众号 · 朋友圈 </strong>
              的高转化率营销文案
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link
                href="/content"
                className="px-8 py-3 bg-stone-900 text-white rounded-full font-semibold hover:bg-stone-800 transition-colors inline-flex items-center gap-2"
              >
                开始创作
                <span>→</span>
              </Link>
              <Link
                href="/generators"
                className="px-8 py-3 border-2 border-stone-300 text-stone-700 rounded-full font-semibold hover:border-stone-900 hover:text-stone-900 transition-colors"
              >
                浏览工具集
              </Link>
            </div>
          </motion.div>

          {/* Stats */}
          <div className="flex justify-center gap-12 mt-16 pt-8 border-t border-stone-200">
            {[
              { value: "50+", label: "设计系统" },
              { value: "4", label: "主流平台" },
              { value: "10+", label: "营销工具" },
            ].map((stat, i) => (
              <div key={i}>
                <div className="font-serif text-3xl font-bold text-stone-900">{stat.value}</div>
                <div className="text-sm text-stone-500 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Platforms */}
      <Section className="py-20 px-6 bg-stone-900">
        <div className="max-w-5xl mx-auto">
          <h2 className="font-serif text-3xl lg:text-4xl font-bold text-white text-center mb-12">
            支持主流社交平台
          </h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {PLATFORMS.map((platform, i) => (
              <motion.div
                key={platform.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.4 }}
                className="bg-stone-800/50 backdrop-blur rounded-2xl p-6 text-center border border-stone-700/50 hover:border-stone-600 transition-colors"
              >
                <div className="text-4xl mb-3">{platform.emoji}</div>
                <h3 className="font-semibold text-white mb-1">{platform.name}</h3>
                <p className="text-sm text-stone-400">{platform.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* Features */}
      <Section className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="font-serif text-3xl lg:text-4xl font-bold text-stone-900 mb-12 text-center">
            AI 驱动的内容创作体验
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08, duration: 0.4 }}
                className="bg-white rounded-2xl p-6 border border-stone-200 hover:border-amber-300 hover:shadow-lg transition-all"
              >
                <div className="text-3xl mb-4">{feature.icon}</div>
                <h3 className="font-semibold text-stone-900 mb-2">{feature.title}</h3>
                <p className="text-sm text-stone-600 leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* CTA */}
      <Section className="py-20 px-6 bg-gradient-to-br from-stone-900 to-stone-800">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="font-serif text-3xl lg:text-4xl font-bold text-white mb-6">
            准备好提升你的
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-400">
              内容创作效率
            </span>
            了吗？
          </h2>
          <p className="text-lg text-stone-300 mb-10">
            告别繁琐的内容创作流程，让 AI 为你代劳
          </p>
          <Link
            href="/content"
            className="inline-flex items-center gap-2 px-10 py-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-full font-semibold text-lg hover:shadow-xl hover:shadow-amber-500/30 transition-all"
          >
            立即开始体验
            <span>→</span>
          </Link>
        </div>
      </Section>

      {/* Footer */}
      <footer className="py-8 px-6 bg-stone-950">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xl">📢</span>
            <span className="font-bold text-white">Vox</span>
            <span className="text-stone-500 text-sm ml-2">v0.1.0</span>
          </div>
          <div className="flex gap-6 text-sm text-stone-400">
            <Link href="/content" className="hover:text-white transition-colors">内容生成</Link>
            <Link href="/generators" className="hover:text-white transition-colors">工具集</Link>
            <Link href="/settings" className="hover:text-white transition-colors">设置</Link>
          </div>
        </div>
      </footer>

      {/* Branding */}
      <a
        href="https://deerflow.tech"
        target="_blank"
        rel="noopener noreferrer"
        className="fixed bottom-4 right-4 bg-stone-900 text-white px-3 py-1.5 rounded-full text-xs font-medium hover:bg-stone-800 transition-colors"
      >
        Created by Deerflow
      </a>
    </div>
  );
}
