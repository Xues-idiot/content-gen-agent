"use client";

import { useEffect, useCallback } from "react";

interface Shortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  meta?: boolean;
  action: () => void;
  description?: string;
}

export function useKeyboardShortcuts(shortcuts: Shortcut[]) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in inputs (unless it's Escape)
      const target = event.target as HTMLElement;
      const isInput =
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable;

      if (isInput && event.key !== "Escape") {
        return;
      }

      for (const shortcut of shortcuts) {
        const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase();
        const ctrlMatch = shortcut.ctrl ? event.ctrlKey || event.metaKey : !event.ctrlKey && !event.metaKey;
        const shiftMatch = shortcut.shift ? event.shiftKey : !event.shiftKey;
        const altMatch = shortcut.alt ? event.altKey : !event.altKey;

        if (keyMatch && ctrlMatch && shiftMatch && altMatch) {
          event.preventDefault();
          shortcut.action();
          return;
        }
      }
    },
    [shortcuts]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);
}

export function useCopyShortcut(onCopy: () => void) {
  useKeyboardShortcuts([
    {
      key: "c",
      ctrl: true,
      action: onCopy,
      description: "复制 (Ctrl+C)",
    },
  ]);
}

// Keyboard shortcuts helper for content page
export const CONTENT_PAGE_SHORTCUTS = {
  FOCUS_GENERATE: { key: "g", ctrl: true, description: "聚焦生成按钮 (Ctrl+G)" },
  COPY_ALL: { key: "c", ctrl: true, shift: true, description: "复制所有文案 (Ctrl+Shift+C)" },
  EXPORT: { key: "e", ctrl: true, description: "导出内容 (Ctrl+E)" },
  REFRESH: { key: "r", ctrl: true, description: "重新生成 (Ctrl+R)" },
  ESCAPE: { key: "Escape", description: "关闭弹窗/取消" },
} as const;
