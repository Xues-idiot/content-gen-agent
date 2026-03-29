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

function Section({ children, className = "", style }: { children: React.ReactNode; className?: string; style?: React.CSSProperties }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });
  return <motion.section ref={ref} initial={{ opacity: 0 }} animate={isInView ? { opacity: 1 } : {}} transition={{ duration: 0.7 }} className={className} style={style}>{children}</motion.section>;
}

export default function HomePage() {
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: heroRef });
  const y = useTransform(scrollYProgress, [0, 1], [0, -60]);

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(180deg, var(--color-secondary-50) 0%, var(--color-secondary-100) 50%, var(--color-neutral-100) 100%)' }}>

      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50" style={{ background: 'transparent' }}>
        <div className="w-full px-16 h-20 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 pl-12">
            {Icons.logo}
            <span className="font-display font-bold text-2xl" style={{ background: 'linear-gradient(135deg, var(--color-secondary-600), var(--color-secondary-500))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>Vox</span>
          </Link>
          <div className="pr-12">
            <Link href="/content" className="btn btn-secondary btn-lg">
              开始创作
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section ref={heroRef} className="min-h-screen flex items-center justify-center px-16">
        <motion.div style={{ y }} className="w-full max-w-7xl text-center">

          <motion.span initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="badge badge-secondary text-label inline-block mb-20 px-10 py-4">
            AI 内容平台
          </motion.span>

          <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }} className="font-display font-bold text-display-xl leading-relaxed tracking-wide mb-24">
            <span className="block" style={{ color: 'var(--color-neutral-900)' }}>一键生成</span>
            <span className="block" style={{ background: 'linear-gradient(135deg, var(--color-secondary-500), var(--color-secondary-600), var(--color-accent-rose-500))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>多平台</span>
            <span className="block" style={{ color: 'var(--color-neutral-900)' }}>营销内容</span>
          </motion.h1>

          <motion.p initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="text-body-lg mb-24 tracking-wide max-w-3xl mx-auto px-8" style={{ color: 'var(--color-text-secondary)', lineHeight: '1.8' }}>
            输入产品信息，AI 自动为你生成适配
            <strong style={{ color: 'var(--color-neutral-900)' }}> 小红书 · 抖音 · 公众号 · 朋友圈 </strong>
            的高转化率营销文案
          </motion.p>

          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.65 }} className="flex flex-wrap justify-center gap-12 mb-40">
            <Link href="/content" className="btn btn-secondary btn-xl btn-pill inline-flex items-center gap-3">
              开始创作 {Icons.arrow}
            </Link>
            <Link href="/generators" className="btn btn-outline-secondary btn-xl btn-pill inline-flex items-center gap-3">
              浏览工具集
            </Link>
          </motion.div>

          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }} className="flex justify-around items-center w-full pt-16" style={{ borderTop: '1px solid var(--color-secondary-200)' }}>
            {[{ v: "50+", l: "设计系统" }, { v: "4", l: "主流平台" }, { v: "10+", l: "营销工具" }].map((s, i) => (
              <div key={i} className="flex flex-col items-center px-12">
                <div className="text-display-md font-bold tracking-wide" style={{ background: 'linear-gradient(135deg, var(--color-secondary-600), var(--color-secondary-500))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>{s.v}</div>
                <div className="text-body-md mt-6 tracking-wide" style={{ color: 'var(--color-neutral-500)' }}>{s.l}</div>
              </div>
            ))}
          </motion.div>
        </motion.div>
      </section>

      {/* Platforms */}
      <Section className="min-h-screen flex items-center justify-center px-16 py-40" style={{ background: 'linear-gradient(135deg, var(--color-secondary-100), var(--color-secondary-50), var(--color-accent-rose-50))' }}>
        <div className="w-full max-w-6xl text-center">
          <h2 className="font-display text-display-lg font-bold mb-32 tracking-wide" style={{ color: 'var(--color-neutral-900)' }}>支持主流社交平台</h2>
          <p className="text-body-lg mb-40 tracking-wide" style={{ color: 'var(--color-text-secondary)' }}>覆盖国内主流社交媒体，一站式内容适配</p>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-20">
            {PLATFORMS.map((p, i) => (
              <motion.div key={p.id} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} whileHover={{ y: -8 }} transition={{ delay: i * 0.12 }} className="card card-elevated p-14 flex flex-col items-center">
                <div className="mb-10 flex justify-center">{p.icon}</div>
                <h3 className="font-semibold text-lg mb-6 h-10 flex items-center justify-center tracking-wide" style={{ color: 'var(--color-neutral-900)' }}>{p.name}</h3>
                <p className="text-body-md leading-relaxed tracking-wide" style={{ color: 'var(--color-neutral-500)' }}>{p.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* Features */}
      <Section className="min-h-screen flex items-center justify-center px-16 py-40" style={{ background: 'linear-gradient(180deg, var(--color-neutral-100), var(--color-secondary-50))' }}>
        <div className="w-full max-w-6xl text-center">
          <h2 className="font-display text-display-lg font-bold mb-32 tracking-wide" style={{ color: 'var(--color-neutral-900)' }}>AI 驱动的内容创作体验</h2>
          <p className="text-body-lg mb-40 tracking-wide" style={{ color: 'var(--color-text-secondary)' }}>强大的 AI 能力，让内容创作更高效</p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-20">
            {FEATURES.map((f, i) => (
              <motion.div key={f.title} initial={{ opacity: 0, y: 25 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} whileHover={{ y: -8 }} transition={{ delay: i * 0.1 }} className="card card-elevated p-14 flex flex-col items-center">
                <div className="mb-10 flex justify-center">{f.icon}</div>
                <h3 className="font-semibold text-lg mb-6 h-10 flex items-center justify-center tracking-wide" style={{ color: 'var(--color-neutral-900)' }}>{f.title}</h3>
                <p className="text-body-md leading-relaxed tracking-wide" style={{ color: 'var(--color-text-secondary)' }}>{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* CTA */}
      <Section className="min-h-hscreen flex items-center justify-center px-16 relative overflow-hidden" style={{ background: 'linear-gradient(135deg, var(--color-secondary-400), var(--color-secondary-500), var(--color-accent-rose-500))', minHeight: '100vh' }}>
        <div className="absolute inset-0 opacity-15">
          <div className="absolute top-20 left-[10%] w-64 h-64 rounded-full" style={{ background: 'white', filter: 'blur(64px)' }}></div>
          <div className="absolute bottom-20 right-[10%] w-80 h-80 rounded-full" style={{ background: 'var(--color-accent-rose-300)', filter: 'blur(64px)' }}></div>
        </div>
        <div className="w-full max-w-6xl text-center relative z-10">
          <h2 className="font-display text-display-lg font-bold mb-24 leading-relaxed tracking-wide" style={{ color: 'white' }}>准备好提升你的<br /><span style={{ color: 'var(--color-secondary-100)' }}>内容创作效率</span><br />了吗？</h2>
          <p className="text-body-lg mb-40 tracking-wide" style={{ color: 'rgba(255,255,255,0.9)' }}>告别繁琐的内容创作流程，让 AI 为你代劳</p>
          <Link href="/content" className="btn btn-lg btn-pill inline-flex items-center gap-4 px-[4rem] py-[1.3rem] bg-white" style={{ color: 'var(--color-secondary-600)', boxShadow: 'var(--shadow-2xl)' }}>
            立即开始体验 {Icons.arrow}
          </Link>
        </div>
      </Section>

      {/* Footer */}
      <footer className="py-16 px-24" style={{ background: 'var(--color-neutral-900)' }}>
        <div className="flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="flex items-center gap-3 pl-8">
            {Icons.logo}
            <span className="font-display font-bold text-xl text-white">Vox</span>
            <span className="text-sm ml-4" style={{ color: 'var(--color-neutral-400)' }}>v0.1.0</span>
          </div>
          <div className="flex gap-14 text-body-md pr-8" style={{ color: 'var(--color-neutral-400)' }}>
            <Link href="/content" className="transition-colors" style={{ color: 'inherit' }}>内容生成</Link>
            <Link href="/generators" className="transition-colors" style={{ color: 'inherit' }}>工具集</Link>
            <Link href="/settings" className="transition-colors" style={{ color: 'inherit' }}>设置</Link>
          </div>
        </div>
      </footer>

      {/* Branding */}
      <a href="https://deerflow.tech" target="_blank" rel="noopener noreferrer" className="deerflow-badge fixed bottom-8 left-12">
        Created by Deerflow
      </a>
    </div>
  );
}
