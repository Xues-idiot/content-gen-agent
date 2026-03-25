"use client";

import { motion } from "framer-motion";
import { Lightbulb, BookOpen, Copy, CheckCircle } from "lucide-react";
import { useState } from "react";
import { API_BASE_URL } from "@/lib/api";

interface ContentAngle {
  type: string;
  title: string;
  description: string;
  template: string;
  tone: string;
}

interface Template {
  name: string;
  structure: string[];
  example_title: string;
}

const platformColors = {
  xiaohongshu: { bg: "bg-gradient-to-br from-pink-500 to-rose-600", text: "text-pink-600", light: "bg-pink-50", border: "border-pink-200" },
  tiktok: { bg: "bg-gradient-to-br from-gray-800 to-black", text: "text-gray-800", light: "bg-gray-100", border: "border-gray-200" },
  official: { bg: "bg-gradient-to-br from-blue-500 to-blue-700", text: "text-blue-600", light: "bg-blue-50", border: "border-blue-200" },
  friend_circle: { bg: "bg-gradient-to-br from-green-500 to-emerald-600", text: "text-green-600", light: "bg-green-50", border: "border-green-200" },
};

const platformLabels = {
  xiaohongshu: "小红书",
  tiktok: "抖音",
  official: "公众号",
  friend_circle: "朋友圈",
};

export default function ContentInspiration() {
  const [productName, setProductName] = useState("");
  const [description, setDescription] = useState("");
  const [sellingPoints, setSellingPoints] = useState("");
  const [selectedPlatform, setSelectedPlatform] = useState("xiaohongshu");
  const [angles, setAngles] = useState<ContentAngle[]>([]);
  const [templates, setTemplates] = useState<Record<string, Template>>({});
  const [loading, setLoading] = useState(false);
  const [copiedAngle, setCopiedAngle] = useState<string | null>(null);

  const fetchAngles = async () => {
    if (!productName.trim()) return;

    setLoading(true);
    try {
      const params = new URLSearchParams({
        product_name: productName,
        description,
        selling_points: sellingPoints,
        platform: selectedPlatform,
      });

      const response = await fetch(`${API_BASE_URL}/api/v1/content/angles`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: params,
      });

      const data = await response.json();
      if (data.success) {
        setAngles(data.angles || []);
      }
    } catch (error) {
      console.error("Failed to fetch angles:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/templates/library/${selectedPlatform}`);
      const data = await response.json();
      if (data.success) {
        setTemplates(data.templates || {});
      }
    } catch (error) {
      console.error("Failed to fetch templates:", error);
    } finally {
      setLoading(false);
    }
  };

  const copyTemplate = (template: string) => {
    navigator.clipboard.writeText(template);
    setCopiedAngle(template);
    setTimeout(() => setCopiedAngle(null), 2000);
  };

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.05 },
    },
  };

  const item = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0 },
  };

  const colors = platformColors[selectedPlatform as keyof typeof platformColors];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
          <Lightbulb className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-gray-900">内容灵感</h2>
          <p className="text-sm text-gray-500">获取创作角度和模板建议</p>
        </div>
      </div>

      {/* Product Input */}
      <div className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">产品名称</label>
            <input
              type="text"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="例如：智能手表"
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">目标平台</label>
            <select
              value={selectedPlatform}
              onChange={(e) => setSelectedPlatform(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
            >
              {Object.entries(platformLabels).map(([key, label]) => (
                <option key={key} value={key}>{label}</option>
              ))}
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">产品描述</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="描述产品的功能、特点..."
            rows={2}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all resize-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">卖点（逗号分隔）</label>
          <input
            type="text"
            value={sellingPoints}
            onChange={(e) => setSellingPoints(e.target.value)}
            placeholder="例如：续航长、功能多、性价比高"
            className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
          />
        </div>
        <div className="flex gap-3">
          <button
            onClick={fetchAngles}
            disabled={loading || !productName.trim()}
            className="flex-1 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors text-sm font-medium disabled:opacity-50"
          >
            {loading ? "生成中..." : "获取创作角度"}
          </button>
          <button
            onClick={fetchTemplates}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-white border border-purple-500 text-purple-600 rounded-lg hover:bg-purple-50 transition-colors text-sm font-medium disabled:opacity-50"
          >
            查看模板
          </button>
        </div>
      </div>

      {/* Content Angles */}
      {angles.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-purple-500" />
            创作角度建议
          </h3>
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="grid grid-cols-1 md:grid-cols-2 gap-3"
          >
            {angles.map((angle, idx) => (
              <motion.div
                key={angle.type}
                variants={item}
                className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${colors.bg}`} />
                    <h4 className="font-medium text-gray-900">{angle.title}</h4>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-xs ${colors.light} ${colors.text}`}>
                    {angle.tone}
                  </span>
                </div>
                <p className="text-sm text-gray-500 mb-3">{angle.description}</p>
                <div className={`p-3 rounded-lg ${colors.light}`}>
                  <div className="text-xs text-gray-500 mb-1">模板</div>
                  <div className="text-sm text-gray-700">{angle.template}</div>
                </div>
                <button
                  onClick={() => copyTemplate(angle.template)}
                  className="mt-3 flex items-center gap-1 text-xs text-purple-600 hover:text-purple-700"
                >
                  {copiedAngle === angle.template ? (
                    <>
                      <CheckCircle className="w-3 h-3" />
                      已复制
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3" />
                      复制模板
                    </>
                  )}
                </button>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      )}

      {/* Templates */}
      {Object.keys(templates).length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-purple-500" />
            内容模板
          </h3>
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-3"
          >
            {Object.entries(templates).map(([key, template]) => (
              <motion.div
                key={key}
                variants={item}
                className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm"
              >
                <div className="flex items-start justify-between gap-2 mb-3">
                  <h4 className="font-medium text-gray-900">{template.name}</h4>
                  <button
                    onClick={() => copyTemplate(template.example_title)}
                    className="flex items-center gap-1 text-xs text-purple-600 hover:text-purple-700"
                  >
                    <Copy className="w-3 h-3" />
                    复制标题
                  </button>
                </div>
                <div className="mb-3">
                  <div className="text-xs text-gray-500 mb-2">结构</div>
                  <div className="flex flex-wrap gap-2">
                    {template.structure.map((step, idx) => (
                      <span
                        key={idx}
                        className={`px-2 py-1 rounded text-xs ${colors.light} ${colors.text}`}
                      >
                        {idx + 1}. {step}
                      </span>
                    ))}
                  </div>
                </div>
                <div className={`p-3 rounded-lg ${colors.light}`}>
                  <div className="text-xs text-gray-500 mb-1">示例标题</div>
                  <div className="text-sm text-gray-700">{template.example_title}</div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      )}

      {/* Empty State */}
      {!loading && angles.length === 0 && Object.keys(templates).length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-xl">
          <Lightbulb className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">输入产品信息获取灵感</p>
          <p className="text-sm text-gray-400 mt-1">点击"获取创作角度"开始</p>
        </div>
      )}
    </motion.div>
  );
}