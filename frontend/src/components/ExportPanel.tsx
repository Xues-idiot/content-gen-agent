"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";

interface ExportPanelProps {
  content: Record<string, any>;
  disabled?: boolean;
}

type ExportFormat = "json" | "markdown" | "html" | "text";

const FORMAT_INFO: Record<ExportFormat, { name: string; icon: string; ext: string }> = {
  json: { name: "JSON", icon: "📋", ext: ".json" },
  markdown: { name: "Markdown", icon: "📝", ext: ".md" },
  html: { name: "HTML", icon: "🌐", ext: ".html" },
  text: { name: "纯文本", icon: "📄", ext: ".txt" },
};

export default function ExportPanel({ content, disabled = false }: ExportPanelProps) {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>("markdown");
  const [exportedContent, setExportedContent] = useState<string | null>(null);
  const [isExported, setIsExported] = useState(false);

  const handleExport = () => {
    if (!content || Object.keys(content).length === 0) return;

    let contentStr = "";
    const ext = FORMAT_INFO[selectedFormat].ext;

    if (selectedFormat === "json") {
      contentStr = JSON.stringify(content, null, 2);
    } else if (selectedFormat === "markdown") {
      contentStr = "# 内容生成报告\n\n";
      if (content.product) {
        contentStr += `## 产品: ${content.product.name}\n\n`;
      }
      if (content.copies) {
        Object.entries(content.copies).forEach(([platform, data]: [string, any]) => {
          contentStr += `### ${platform}\n\n`;
          if (data.copy?.title) contentStr += `**标题**: ${data.copy.title}\n\n`;
          if (data.copy?.content) contentStr += `${data.copy.content}\n\n`;
        });
      }
    } else if (selectedFormat === "html") {
      contentStr = `<html><body><h1>内容生成报告</h1><pre>${JSON.stringify(content, null, 2)}</pre></body></html>`;
    } else {
      contentStr = JSON.stringify(content, null, 2);
    }

    setExportedContent(contentStr);
    setIsExported(true);
  };

  const handleDownload = () => {
    if (!exportedContent) return;

    const blob = new Blob([exportedContent], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `vox-content${FORMAT_INFO[selectedFormat].ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleCopy = async () => {
    if (!exportedContent) return;
    try {
      await navigator.clipboard.writeText(exportedContent);
      alert("已复制到剪贴板");
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="bg-white rounded-xl shadow-md p-6"
    >
      <motion.h2
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.25 }}
        className="text-xl font-bold mb-4"
        style={{ color: "#FF6B35" }}
      >
        导出内容
      </motion.h2>

      <div className="space-y-4">
        {/* Format Selection */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <label className="block text-sm font-medium text-gray-700 mb-2">
            选择导出格式
          </label>
          <div className="grid grid-cols-4 gap-2">
            {(Object.keys(FORMAT_INFO) as ExportFormat[]).map((format, index) => (
              <motion.button
                key={format}
                onClick={() => {
                  setSelectedFormat(format);
                  setIsExported(false);
                }}
                disabled={disabled}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.35 + index * 0.05 }}
                whileHover={disabled ? {} : { scale: 1.05, y: -2 }}
                whileTap={disabled ? {} : { scale: 0.95 }}
                className={`p-3 rounded-lg border-2 text-center transition-all ${
                  selectedFormat === format
                    ? "border-orange-400 bg-orange-50"
                    : "border-gray-200 hover:border-gray-300"
                } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
                style={{
                  borderColor: selectedFormat === format ? "#FF6B35" : "#E5E7EB",
                }}
              >
                <motion.div
                  whileHover={disabled ? {} : { scale: 1.1 }}
                  className="text-xl mb-1"
                >
                  {FORMAT_INFO[format].icon}
                </motion.div>
                <div className="text-xs font-medium">{FORMAT_INFO[format].name}</div>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Export Button */}
        <motion.button
          onClick={handleExport}
          disabled={disabled || !content || Object.keys(content).length === 0}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          whileHover={
            disabled || !content || Object.keys(content).length === 0
              ? {}
              : { scale: 1.02, boxShadow: "0 4px 12px rgba(255, 107, 53, 0.3)" }
          }
          whileTap={
            disabled || !content || Object.keys(content).length === 0
              ? {}
              : { scale: 0.98 }
          }
          className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
            disabled || !content || Object.keys(content).length === 0
              ? "bg-gray-400 cursor-not-allowed"
              : "shadow-md"
          }`}
          style={{
            backgroundColor:
              disabled || !content || Object.keys(content).length === 0
                ? "#9CA3AF"
                : "#10B981",
            color: "white",
          }}
        >
          生成导出文件
        </motion.button>

        {/* Preview / Download */}
        <AnimatePresence>
          {isExported && exportedContent && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="space-y-2"
            >
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="rounded-lg p-4"
                style={{ backgroundColor: "#F9FAFB" }}
              >
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700">预览</span>
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.2, type: "spring" }}
                    className="text-xs text-gray-500"
                  >
                    {exportedContent.length} 字符
                  </motion.span>
                </div>
                <pre className="text-xs overflow-auto max-h-40 whitespace-pre-wrap bg-white p-2 rounded border border-gray-200">
                  {exportedContent.slice(0, 500)}
                  {exportedContent.length > 500 && "..."}
                </pre>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 }}
                className="flex gap-2"
              >
                <motion.button
                  onClick={handleDownload}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex-1 py-2 px-4 text-white rounded-lg transition-colors shadow-md"
                  style={{ backgroundColor: "#FF6B35" }}
                >
                  下载{FORMAT_INFO[selectedFormat].name}
                </motion.button>
                <motion.button
                  onClick={handleCopy}
                  whileHover={{ scale: 1.02, backgroundColor: "#E5E7EB" }}
                  whileTap={{ scale: 0.98 }}
                  className="flex-1 py-2 px-4 bg-gray-200 text-gray-700 rounded-lg transition-colors"
                >
                  复制
                </motion.button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty State */}
        {(!content || Object.keys(content).length === 0) && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-center text-gray-500 text-sm"
          >
            生成内容后即可导出
          </motion.p>
        )}
      </div>
    </motion.div>
  );
}
