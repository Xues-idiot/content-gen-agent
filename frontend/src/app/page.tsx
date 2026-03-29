"use client";

import React, { useRef } from "react";
import Link from "next/link";
import { motion, useScroll, useTransform, useInView } from "motion/react";

const Icons = {
  spark: <svg width="52" height="52" viewBox="0 0 48 48" fill="none"><path d="M24 4L28.5 17.5L42 24L28.5 30.5L24 44L19.5 30.5L6 24L19.5 17.5L24 4Z" fill="url(#s1)"/><defs><linearGradient id="s1" x1="6" y1="4" x2="42" y2="44"><stop stopColor="#F59E0B"/><stop offset="1" stopColor="#EA580C"/></linearGradient></defs></svg>,
  shield: <svg width="52" height="52" viewBox="0 0 48 48" fill="none"><path d="M24 4L40 10V22C40 32.5 33 40.5 24 44C15 40.5 8 32.5 8 22V10L24 4Z" stroke="url(#s2)" strokeWidth="3" fill="none"/><path d="M17 24L22 29L31 20" stroke="url(#s2)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/><defs><linearGradient id="s2" x1="8" y1="4" x2="40" y2="44"><stop stopColor="#F59E0B"/><stop offset="1" stopColor="#EA580C"/></linearGradient></defs></svg>,
  image: <svg width="52" height="52" viewBox="0 0 48 48" fill="none"><rect x="6" y="10" width="36" height="28" rx="3" stroke="url(#s3)" strokeWidth="3"/><circle cx="16" cy="20" r="4" stroke="url(#s3)" strokeWidth="2.5"/><path d="M6 32L16 24L26 32L36 22" stroke="url(#s3)" strokeWidth="2.5" strokeLinecap="round"/><defs><linearGradient id="s3" x1="6" y1="10" x2="42" y2="38"><stop stopColor="#F59E0B"/><stop offset="1" stopColor="#EA580C"/></linearGradient></defs></svg>,
  chart: <svg width="52" height="52" viewBox="0 0 48 48" fill="none"><path d="M8 38V18M18 38V12M28 38V20M38 38V8" stroke="url(#s4)" strokeWidth="3" strokeLinecap="round"/><defs><linearGradient id="s4" x1="8" y1="8" x2="38" y2="38"><stop stopColor="#F59E0B"/><stop offset="1" stopColor="#EA580C"/></linearGradient></defs></svg>,
  sync: <svg width="52" height="52" viewBox="0 0 48 48" fill="none"><path d="M40 24C40 32.8 32.8 40 24 40C18 40 12.5 36.5 9 31M8 24C8 15.2 15.2 8 24 8C30 8 35.5 11.5 39 17M36 17L40 24L33 28M12 31L8 24L15 20" stroke="url(#s5)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/><defs><linearGradient id="s5" x1="8" y1="8" x2="40" y2="40"><stop stopColor="#F59E0B"/><stop offset="1" stopColor="#EA580C"/></linearGradient></defs></svg>,
  tools: <svg width="52" height="52" viewBox="0 0 48 48" fill="none"><circle cx="24" cy="24" r="10" stroke="url(#s6)" strokeWidth="3"/><path d="M24 4V14M24 34V44M4 24H14M34 24H44M9 9L15 15M33 33L39 39M9 39L15 33M33 15L39 9" stroke="url(#s6)" strokeWidth="3" strokeLinecap="round"/><defs><linearGradient id="s6" x1="4" y1="4" x2="44" y2="44"><stop stopColor="#F59E0B"/><stop offset="1" stopColor="#EA580C"/></linearGradient></defs></svg>,
  xiaohongshu: <svg width="64" height="64" viewBox="0 0 64 64" fill="none"><rect x="8" y="8" width="48" height="48" rx="12" fill="#FE2C55"/><path d="M32 18C26 18 22 24 22 30C22 38 32 46 32 46C32 46 42 38 42 30C42 24 38 18 32 18Z" fill="white"/><circle cx="32" cy="28" r="4" fill="#FE2C55"/></svg>,
  tiktok: <svg width="64" height="64" viewBox="0 0 64 64" fill="none"><rect x="8" y="8" width="48" height="48" rx="12" fill="black"/><path d="M40 20C36 20 32 24 32 28C32 28 32 36 24 36V42C28 42 40 38 40 28V20Z" stroke="#69FF96" strokeWidth="3" fill="none"/><path d="M24 36V28" stroke="#69FF96" strokeWidth="3"/></svg>,
  official: <svg width="64" height="64" viewBox="0 0 64 64" fill="none"><rect x="8" y="8" width="48" height="48" rx="12" fill="#07AFEE"/><rect x="16" y="18" width="32" height="28" rx="2" fill="white"/><path d="M24 26H40M24 32H36M24 38H32" stroke="#07AFEE" strokeWidth="2" strokeLinecap="round"/></svg>,
  friends: <svg width="64" height="64" viewBox="0 0 64 64" fill="none"><rect x="8" y="8" width="48" height="48" rx="12" fill="#07C160"/><circle cx="24" cy="26" r="6" fill="white"/><circle cx="40" cy="26" r="6" fill="white"/><path d="M16 40C16 34 20 30 24 30C28 30 32 34 32 40V44H16V40Z" fill="white"/><path d="M32 40C32 34 36 30 40 30C44 30 48 34 48 40V44H32V40Z" fill="white"/></svg>,
  arrow: <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M5 12H19M19 12L13 6M19 12L13 18" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  logo: <svg width="32" height="32" viewBox="0 0 32 32" fill="none"><circle cx="16" cy="16" r="14" fill="url(#lg)"/><path d="M16 6L20 13H26L21 18L23 26L16 21L9 26L11 18L6 13H12L16 6Z" fill="white"/><defs><linearGradient id="lg" x1="2" y1="2" x2="30" y2="30"><stop stopColor="#F59E0B"/><stop offset="1" stopColor="#EA580C"/></linearGradient></defs></svg>,
};

const PLATFORMS = [
  { id: "xiaohongshu", name: "小红书", desc: "种草笔记 · 长文案", icon: Icons.xiaohongshu },
  { id: "tiktok", name: "抖音", desc: "短视频口播脚本", icon: Icons.tiktok },
  { id: "official", name: "公众号", desc: "深度长文 · 排版", icon: Icons.official },
  { id: "friend_circle", name: "朋友圈", desc: "简短分享 · 互动", icon: Icons.friends },
];

const FEATURES = [
  { title: "智能生成", desc: "基于大语言模型，理解平台特性与用户心理，生成高转化率内容", icon: Icons.spark },
  { title: "合规检测", desc: "内置广告法违规词库，自动检测并提供修改建议", icon: Icons.shield },
  { title: "配图建议", desc: "AI 生成配套图片提示词，支持多种图片生成工具", icon: Icons.image },
  { title: "质量评分", desc: "多维度评分体系，量化文案质量，指明优化方向", icon: Icons.chart },
  { title: "多平台适配", desc: "一次输入，多平台内容一键生成，保持风格一致性", icon: Icons.sync },
  { title: "营销工具集", desc: "标签推荐、发布时间、AB测试等实用工具", icon: Icons.tools },
];

function Section({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });
  return <motion.section ref={ref} initial={{ opacity: 0 }} animate={isInView ? { opacity: 1 } : {}} transition={{ duration: 0.7 }} className={className}>{children}</motion.section>;
}

export default function HomePage() {
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: heroRef });
  const y = useTransform(scrollYProgress, [0, 1], [0, -60]);

  return (
    <>
      <style>{`
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: #FEF3C7; }
        ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #F59E0B, #EA580C); border-radius: 5px; border: 2px solid #FEF3C7; }
        ::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #D97706, #C2410C); }
      `}</style>

      <div className="min-h-screen bg-gradient-to-b from-amber-50 via-orange-50 to-stone-100">

        {/* Nav */}
        <nav className="fixed top-0 left-0 right-0 z-50 bg-transparent">
          <div className="w-full px-16 h-20 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3 pl-12">
              {Icons.logo}
              <span className="font-bold text-2xl bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">Vox</span>
            </Link>
            <div className="pr-12">
              <Link href="/content" className="px-12 py-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-full font-semibold text-base hover:from-amber-600 hover:to-orange-600 transition-all shadow-lg shadow-amber-300/50">
                开始创作
              </Link>
            </div>
          </div>
        </nav>

        {/* Hero */}
        <section ref={heroRef} className="min-h-screen flex items-center justify-center px-16">
          <motion.div style={{ y }} className="w-full max-w-7xl text-center">

            <motion.span initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="inline-block text-sm font-semibold tracking-[0.2em] text-amber-600 uppercase mb-16 px-8 py-3 bg-amber-100 rounded-full">
              AI 内容平台
            </motion.span>

            <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }} className="font-bold text-6xl lg:text-8xl leading-[1.3] tracking-tight" style={{ fontFamily: "'Sora', sans-serif" }}>
              <span className="text-stone-800 block mb-20">一键生成</span>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-500 via-orange-500 to-rose-500 block mb-20">多平台</span>
              <span className="text-stone-800 block">营销内容</span>
            </motion.h1>

            <motion.p initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="text-xl text-stone-600 mb-20 leading-relaxed">
              输入产品信息，AI 自动为你生成适配
              <strong className="text-stone-800"> 小红书 · 抖音 · 公众号 · 朋友圈 </strong>
              的高转化率营销文案
            </motion.p>

            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.65 }} className="flex flex-wrap justify-center gap-10 mb-32">
              <Link href="/content" className="px-[3.5rem] py-[1.2rem] bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-full font-semibold text-lg hover:from-amber-600 hover:to-orange-600 transition-all shadow-xl shadow-amber-300/50 inline-flex items-center gap-3">
                开始创作 {Icons.arrow}
              </Link>
              <Link href="/generators" className="px-[3.5rem] py-[1.2rem] bg-white border-2 border-amber-300 text-stone-700 rounded-full font-semibold text-lg hover:border-amber-500 hover:text-amber-700 hover:bg-amber-50 transition-all shadow-lg inline-flex items-center gap-3">
                浏览工具集
              </Link>
            </motion.div>

            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }} className="flex justify-center gap-64 pt-12 border-t border-amber-200">
              {[{ v: "50+", l: "设计系统" }, { v: "4", l: "主流平台" }, { v: "10+", l: "营销工具" }].map((s, i) => (
                <div key={i} className="text-center">
                  <div className="text-5xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">{s.v}</div>
                  <div className="text-base text-stone-500 mt-4">{s.l}</div>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </section>

        {/* Platforms */}
        <Section className="min-h-screen flex items-center justify-center px-16 bg-gradient-to-br from-amber-100 via-orange-100 to-rose-100/50">
          <div className="w-full max-w-7xl text-center">
            <h2 className="text-5xl lg:text-6xl font-bold text-stone-800 mb-20">支持主流社交平台</h2>
            <p className="text-xl text-stone-600 mb-24">覆盖国内主流社交媒体，一站式内容适配</p>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-14">
              {PLATFORMS.map((p, i) => (
                <motion.div key={p.id} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} whileHover={{ y: -8 }} transition={{ delay: i * 0.12 }} className="bg-white/90 backdrop-blur rounded-3xl p-10 border border-white shadow-xl">
                  <div className="mb-6 flex justify-center">{p.icon}</div>
                  <h3 className="font-semibold text-stone-800 text-lg mb-3">{p.name}</h3>
                  <p className="text-sm text-stone-500 leading-relaxed">{p.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </Section>

        {/* Features */}
        <Section className="min-h-screen flex items-center justify-center px-16 bg-gradient-to-b from-stone-100 to-amber-50/50">
          <div className="w-full max-w-7xl text-center">
            <h2 className="text-5xl lg:text-6xl font-bold text-stone-800 mb-20">AI 驱动的内容创作体验</h2>
            <p className="text-xl text-stone-600 mb-24">强大的 AI 能力，让内容创作更高效</p>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-14">
              {FEATURES.map((f, i) => (
                <motion.div key={f.title} initial={{ opacity: 0, y: 25 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} whileHover={{ y: -8 }} transition={{ delay: i * 0.1 }} className="bg-white rounded-3xl p-10 border border-amber-100 hover:border-amber-300 transition-all shadow-lg">
                  <div className="mb-6 flex justify-center">{f.icon}</div>
                  <h3 className="font-semibold text-stone-800 text-lg mb-3">{f.title}</h3>
                  <p className="text-sm text-stone-600 leading-relaxed">{f.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </Section>

        {/* CTA */}
        <Section className="min-h-screen flex items-center justify-center px-16 bg-gradient-to-br from-amber-400 via-orange-400 to-rose-400/80 relative overflow-hidden">
          <div className="absolute inset-0 opacity-15">
            <div className="absolute top-20 left-[10%] w-64 h-64 bg-white rounded-full blur-3xl"></div>
            <div className="absolute bottom-20 right-[10%] w-80 h-80 bg-rose-300 rounded-full blur-3xl"></div>
          </div>
          <div className="w-full max-w-6xl text-center relative z-10">
            <h2 className="text-5xl lg:text-6xl font-bold text-white mb-20 leading-tight">准备好提升你的<br /><span className="text-amber-100">内容创作效率</span><br />了吗？</h2>
            <p className="text-xl text-amber-100/90 mb-36">告别繁琐的内容创作流程，让 AI 为你代劳</p>
            <Link href="/content" className="inline-flex items-center gap-4 px-[4rem] py-[1.3rem] bg-white text-amber-600 rounded-full font-bold text-xl hover:bg-amber-50 transition-all shadow-2xl hover:shadow-3xl hover:scale-105">
              立即开始体验 {Icons.arrow}
            </Link>
          </div>
        </Section>

        {/* Footer */}
        <footer className="py-16 px-24 bg-stone-900">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="flex items-center gap-3 pl-8">
              {Icons.logo}
              <span className="font-bold text-xl text-white">Vox</span>
              <span className="text-stone-400 text-sm ml-4">v0.1.0</span>
            </div>
            <div className="flex gap-14 text-base text-stone-400 pr-8">
              <Link href="/content" className="hover:text-amber-400 transition-colors">内容生成</Link>
              <Link href="/generators" className="hover:text-amber-400 transition-colors">工具集</Link>
              <Link href="/settings" className="hover:text-amber-400 transition-colors">设置</Link>
            </div>
          </div>
        </footer>

        {/* Branding */}
        <a href="https://deerflow.tech" target="_blank" rel="noopener noreferrer" className="fixed bottom-8 left-12 bg-gradient-to-r from-amber-500 to-orange-500 text-white px-5 py-2.5 rounded-full text-sm font-medium hover:from-amber-600 hover:to-orange-600 transition-all shadow-lg hover:shadow-xl">
          Created by Deerflow
        </a>
      </div>
    </>
  );
}
