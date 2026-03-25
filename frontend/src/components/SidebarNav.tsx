"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  Home,
  FileText,
  Calendar,
  Archive,
  BarChart3,
  Megaphone,
  ListTodo,
  Settings,
  Sparkles,
  X,
  Menu,
} from "lucide-react";

interface SidebarNavProps {
  children: React.ReactNode;
}

const navItems = [
  { href: "/", icon: Home, label: "首页", color: "#FF6B35" },
  { href: "/content", icon: FileText, label: "内容生成", color: "#FF6B35" },
  { href: "/templates", icon: Sparkles, label: "模板库", color: "#FF8C61" },
  { href: "/calendar", icon: Calendar, label: "内容日历", color: "#FFD93D" },
  { href: "/archive", icon: Archive, label: "内容归档", color: "#10B981" },
  { href: "/analytics", icon: BarChart3, label: "数据分析", color: "#3B82F6" },
  { href: "/campaigns", icon: Megaphone, label: "营销活动", color: "#EC4899" },
  { href: "/tasks", icon: ListTodo, label: "任务管理", color: "#8B5CF6" },
  { href: "/settings", icon: Settings, label: "设置", color: "#6B7280" },
];

export default function SidebarNav({ children }: SidebarNavProps) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const NavContent = () => (
    <>
      {/* Logo */}
      <div className="p-4 border-b border-gray-100">
        <Link href="/" className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center text-2xl"
            style={{ backgroundColor: "#FF6B35" }}
          >
            📢
          </div>
          <div>
            <h1 className="font-bold text-lg" style={{ color: "#FF6B35" }}>
              Vox
            </h1>
            <p className="text-xs text-gray-500">内容生成 Agent</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all ${
                isActive
                  ? "text-white shadow-md"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
              style={isActive ? { backgroundColor: item.color } : undefined}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium text-sm">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-100">
        <p className="text-xs text-gray-400 text-center">
          Vox v0.1.0
        </p>
      </div>
    </>
  );

  return (
    <div className="min-h-screen flex" style={{ backgroundColor: "#FFF8F0" }}>
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 bg-white shadow-sm">
        <NavContent />
      </aside>

      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-white shadow-sm">
        <div className="flex items-center justify-between px-4 py-3">
          <Link href="/" className="flex items-center gap-2">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center text-lg"
              style={{ backgroundColor: "#FF6B35" }}
            >
              📢
            </div>
            <span className="font-bold" style={{ color: "#FF6B35" }}>
              Vox
            </span>
          </Link>
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      {mobileOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="lg:hidden fixed inset-0 z-40"
        >
          <div
            className="absolute inset-0 bg-black/30"
            onClick={() => setMobileOpen(false)}
          />
          <motion.aside
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="absolute left-0 top-0 bottom-0 w-64 bg-white shadow-xl"
          >
            <NavContent />
          </motion.aside>
        </motion.div>
      )}

      {/* Mobile Nav Pills */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-gray-200">
        <div className="flex items-center justify-around px-2 py-2">
          {navItems.slice(0, 5).map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex flex-col items-center gap-1 px-3 py-1.5 rounded-lg transition-colors ${
                  isActive ? "text-orange-500" : "text-gray-500"
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-[10px] font-medium">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 lg:ml-64 min-h-screen pt-14 lg:pt-0 pb-16 lg:pb-0">
        {children}
      </main>
    </div>
  );
}
