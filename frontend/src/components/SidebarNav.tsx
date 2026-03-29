"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "motion/react";
import {
  Home,
  FileText,
  Sparkles,
  Calendar,
  Archive,
  BarChart3,
  Megaphone,
  ListTodo,
  Settings,
  X,
  Menu,
  ChevronRight,
  Layers,
} from "lucide-react";

interface SidebarNavProps {
  children: React.ReactNode;
}

const NAV_ITEMS = [
  { href: "/", icon: Home, label: "首页", color: "#F97316", gradient: "from-secondary-500 to-secondary-600" },
  { href: "/content", icon: FileText, label: "内容生成", color: "#7C3AED", gradient: "from-purple-500 to-violet-600" },
  { href: "/generators", icon: Sparkles, label: "工具集", color: "#F97316", gradient: "from-orange-500 to-amber-600" },
  { href: "/templates", icon: Layers, label: "模板库", color: "#0D9488", gradient: "from-teal-500 to-cyan-600" },
  { href: "/calendar", icon: Calendar, label: "内容日历", color: "#3B82F6", gradient: "from-blue-500 to-indigo-600" },
  { href: "/archive", icon: Archive, label: "内容归档", color: "#10B981", gradient: "from-emerald-500 to-teal-600" },
  { href: "/analytics", icon: BarChart3, label: "数据分析", color: "#8B5CF6", gradient: "from-violet-500 to-purple-600" },
  { href: "/campaigns", icon: Megaphone, label: "营销活动", color: "#EC4899", gradient: "from-pink-500 to-rose-600" },
  { href: "/tasks", icon: ListTodo, label: "任务管理", color: "#6366F1", gradient: "from-indigo-500 to-blue-600" },
  { href: "/settings", icon: Settings, label: "设置", color: "#78716C", gradient: "from-stone-500 to-neutral-600" },
];

export default function SidebarNav({ children }: SidebarNavProps) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const NavContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="p-5 border-b border-neutral-200/50">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="relative">
            <div className="w-11 h-11 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-105 transition-all" style={{ background: 'linear-gradient(135deg, var(--color-secondary-500), var(--color-secondary-600))', boxShadow: '0 4px 14px rgba(249, 115, 22, 0.25)' }}>
              <Sparkles className="w-5 h-5 text-white" />
            </div>
          </div>
          <div>
            <h1 className="font-display font-bold text-lg text-neutral-900 tracking-tight">
              Vox
            </h1>
            <p className="text-[10px] text-neutral-500 font-medium tracking-wide">
              AI 内容生成
            </p>
          </div>
        </Link>
      </div>

      {/* Navigation Label */}
      <div className="px-5 pt-5 pb-2">
        <p className="text-label text-neutral-400">导航</p>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 px-3 pb-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileOpen(false)}
              className="group relative"
            >
              <motion.div
                className={`
                  flex items-center gap-3 px-3 py-2.5 rounded-xl
                  transition-all duration-150
                  ${isActive
                    ? "bg-white/90 shadow-md"
                    : "hover:bg-white/50"
                  }
                `}
              >
                {/* Active Indicator */}
                {isActive && (
                  <motion.div
                    layoutId="activeIndicator"
                    className={`absolute inset-0 rounded-xl bg-gradient-to-r ${item.gradient} opacity-10`}
                    transition={{ duration: 0.15 }}
                  />
                )}

                {/* Icon */}
                <div
                  className={`
                    relative z-10 w-9 h-9 rounded-lg flex items-center justify-center
                    transition-all duration-150
                    ${isActive
                      ? "bg-gradient-to-br from-neutral-900 to-neutral-800 text-white shadow-lg"
                      : "bg-neutral-100 text-neutral-600 group-hover:bg-neutral-200"
                    }
                  `}
                >
                  <Icon className="w-4.5 h-4.5" strokeWidth={isActive ? 2.5 : 2} />
                </div>

                {/* Label */}
                <span
                  className={`
                    relative z-10 font-medium text-sm
                    ${isActive
                      ? "text-neutral-900"
                      : "text-neutral-600 group-hover:text-neutral-900"
                    }
                  `}
                >
                  {item.label}
                </span>

                {/* Active Chevron */}
                {isActive && (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="relative z-10 ml-auto"
                  >
                    <ChevronRight className="w-4 h-4 text-neutral-400" />
                  </motion.div>
                )}

                {/* Hover Gradient */}
                {!isActive && (
                  <div
                    className={`absolute inset-0 rounded-xl bg-gradient-to-r ${item.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-200`}
                  />
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-5 border-t border-neutral-200/50">
        <div className="card-bordered rounded-xl p-4 bg-gradient-to-br from-neutral-50 to-neutral-100/50">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="text-xs font-medium text-neutral-600">系统状态</span>
          </div>
          <p className="text-xs text-neutral-500">所有服务运行正常</p>
        </div>
        <p className="text-center text-xs text-neutral-400 mt-4 font-medium">
          Vox v0.1.0
        </p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex lg:flex-col lg:w-72 lg:fixed lg:inset-y-0">
        {/* Background */}
        <div className="absolute inset-0 bg-gradient-to-b from-neutral-50 via-neutral-100/50 to-neutral-50" />
        <div className="absolute inset-0 backdrop-blur-xl" />

        {/* Content */}
        <div className="relative z-10 flex flex-col h-full">
          <NavContent />
        </div>
      </aside>

      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50">
        <div className="bg-white/90 backdrop-blur-xl border-b border-neutral-200/50">
          <div className="flex items-center justify-between px-4 py-3">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-lg flex items-center justify-center shadow-md" style={{ background: 'linear-gradient(135deg, var(--color-secondary-500), var(--color-secondary-600))', boxShadow: '0 4px 14px rgba(249, 115, 22, 0.25)' }}>
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <span className="font-display font-bold text-neutral-900">
                Vox
              </span>
            </Link>
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="w-10 h-10 rounded-xl bg-neutral-100 flex items-center justify-center text-neutral-600 hover:bg-neutral-200 transition-colors"
            >
              {mobileOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="lg:hidden fixed inset-0 z-40 bg-neutral-900/50 backdrop-blur-sm"
              onClick={() => setMobileOpen(false)}
            />
            <motion.aside
              initial={{ x: -300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -300, opacity: 0 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="lg:hidden fixed left-0 top-0 bottom-0 w-72 z-50"
            >
              <div className="absolute inset-0 bg-gradient-to-b from-neutral-50 via-neutral-100/50 to-neutral-50" />
              <div className="absolute inset-0 backdrop-blur-xl" />
              <div className="relative z-10 h-full">
                <NavContent />
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Mobile Bottom Nav */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 z-30">
        <div className="bg-white/95 backdrop-blur-xl border-t border-neutral-200/50">
          <div className="flex items-center justify-around px-1 py-2">
            {NAV_ITEMS.slice(0, 5).map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileOpen(false)}
                  className={`
                    flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-xl min-w-[56px]
                    transition-all duration-200
                    ${isActive
                      ? "text-neutral-900"
                      : "text-neutral-500"
                    }
                  `}
                >
                  <div
                    className={`
                      w-7 h-7 rounded-lg flex items-center justify-center
                      transition-all duration-200
                      ${isActive
                        ? `bg-gradient-to-br ${item.gradient} text-white shadow-md`
                        : "bg-neutral-100"
                      }
                    `}
                  >
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-[9px] font-medium leading-tight">{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 lg:ml-72 min-h-screen">
        <div className="pt-16 lg:pt-0 pb-20 lg:pb-0">
          {children}
        </div>
      </main>
    </div>
  );
}
