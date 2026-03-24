import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// Vox 配色方案
export const colors = {
  // 主色：活力橙
  primary: "#FF6B35",
  primaryHover: "#E55A2B",
  // 辅色：珊瑚红
  secondary: "#FF8C61",
  // 点缀色：明黄
  accent: "#FFD93D",
  // 背景：浅暖灰
  background: "#FFF8F0",
  backgroundDark: "#FFF0E5",
  // 文字
  text: {
    primary: "#1F2937",
    secondary: "#6B7280",
    muted: "#9CA3AF",
  },
  // 状态色
  success: "#10B981",
  warning: "#F59E0B",
  error: "#EF4444",
  info: "#3B82F6",
};

// 平台信息
export const PLATFORM_INFO: Record<string, { name: string; icon: string; color: string; bgColor: string }> = {
  xiaohongshu: { name: "小红书", icon: "📕", color: "#EF4444", bgColor: "bg-red-50" },
  tiktok: { name: "抖音", icon: "📺", color: "#EC4899", bgColor: "bg-pink-50" },
  official: { name: "公众号", icon: "📰", color: "#3B82F6", bgColor: "bg-blue-50" },
  friend_circle: { name: "朋友圈", icon: "👥", color: "#10B981", bgColor: "bg-green-50" },
};

// 类别选项
export const CATEGORY_OPTIONS = [
  { value: "", label: "选择类别" },
  { value: "美妆", label: "美妆" },
  { value: "数码", label: "数码" },
  { value: "食品", label: "食品" },
  { value: "家居", label: "家居" },
  { value: "服装", label: "服装" },
  { value: "健康", label: "健康" },
  { value: "教育", label: "教育" },
  { value: "旅游", label: "旅游" },
  { value: "其他", label: "其他" },
];

// 导出格式
export const EXPORT_FORMATS = {
  json: { name: "JSON", icon: "📋", ext: ".json" },
  markdown: { name: "Markdown", icon: "📝", ext: ".md" },
  html: { name: "HTML", icon: "🌐", ext: ".html" },
  text: { name: "纯文本", icon: "📄", ext: ".txt" },
} as const;

// 质量评分颜色
export function getScoreColor(score: number): string {
  if (score >= 8) return colors.success;
  if (score >= 6) return colors.warning;
  return colors.error;
}

// 违规严重程度颜色
export function getSeverityColor(severity: string): string {
  switch (severity) {
    case "error":
      return colors.error;
    case "warning":
      return colors.warning;
    default:
      return colors.info;
  }
}

// 格式化日期
export function formatDate(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// 截断文本
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + "...";
}

// 复制到剪贴板
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

// 下载文件
export function downloadFile(content: string, filename: string, mimeType: string = "text/plain"): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// 生成唯一ID
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// 验证产品名称
export function validateProductName(name: string): string | null {
  if (!name.trim()) return "产品名称不能为空";
  if (name.length > 100) return "产品名称不能超过100个字符";
  return null;
}

// 验证产品描述
export function validateProductDescription(desc: string): string | null {
  if (!desc.trim()) return "产品描述不能为空";
  if (desc.length > 2000) return "产品描述不能超过2000个字符";
  return null;
}

// 验证 URL
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

// CTA 类型映射
export const CTA_PLATFORM_HINTS: Record<string, string[]> = {
  xiaohongshu: ["评论区见", "点赞关注", "收藏笔记", "私信咨询", "点击链接"],
  tiktok: ["评论区扣1", "点击链接", "分享给朋友", "关注账号", "进直播间"],
  official: ["关注公众号", "点击在看", "分享朋友圈", "私信回复"],
  friend_circle: ["评论区见", "私信咨询", "点赞支持"],
};

// 获取 CTA 提示
export function getCtaHint(platform: string): string {
  const hints = CTA_PLATFORM_HINTS[platform] || [];
  return hints.length > 0 ? `如：${hints[0]}` : "";
}
