"use client";

import React, { useState } from "react";
import { motion } from "motion/react";
import { Sparkles, Package, Target, Tag, DollarSign, ArrowRight } from "lucide-react";

interface ProductInputProps {
  onGenerate: (product: ProductData) => void;
  isLoading: boolean;
}

export interface ProductData {
  name: string;
  description: string;
  sellingPoints: string[];
  targetUsers: string[];
  category: string;
  priceRange: string;
}

const CATEGORIES = [
  { value: "美妆", label: "美妆", color: "#EC4899" },
  { value: "数码", label: "数码", color: "#3B82F6" },
  { value: "食品", label: "食品", color: "#F97316" },
  { value: "家居", label: "家居", color: "#10B981" },
  { value: "服装", label: "服装", color: "#8B5CF6" },
  { value: "健康", label: "健康", color: "#EF4444" },
  { value: "教育", label: "教育", color: "#6366F1" },
  { value: "旅游", label: "旅游", color: "#0EA5E9" },
  { value: "母婴", label: "母婴", color: "#F43F5E" },
  { value: "其他", label: "其他", color: "#78716C" },
];

export default function ProductInput({ onGenerate, isLoading }: ProductInputProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [sellingPoints, setSellingPoints] = useState("");
  const [targetUsers, setTargetUsers] = useState("");
  const [category, setCategory] = useState("");
  const [priceRange, setPriceRange] = useState("");

  // Validation errors
  const [nameError, setNameError] = useState<string | null>(null);
  const [descError, setDescError] = useState<string | null>(null);

  const validateProductName = (value: string): string | null => {
    if (!value.trim()) return "请输入产品名称";
    if (value.length < 2) return "产品名称至少2个字符";
    if (value.length > 50) return "产品名称不超过50个字符";
    return null;
  };

  const validateProductDescription = (value: string): string | null => {
    if (!value.trim()) return "请输入产品描述";
    if (value.length < 10) return "产品描述至少10个字符";
    if (value.length > 2000) return "产品描述不超过2000个字符";
    return null;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const nameErr = validateProductName(name);
    const descErr = validateProductDescription(description);

    if (nameErr) {
      setNameError(nameErr);
      return;
    }
    if (descErr) {
      setDescError(descErr);
      return;
    }

    setNameError(null);
    setDescError(null);

    const product: ProductData = {
      name,
      description,
      sellingPoints: sellingPoints.split(",").map((s) => s.trim()).filter(Boolean),
      targetUsers: targetUsers.split(",").map((s) => s.trim()).filter(Boolean),
      category,
      priceRange,
    };

    onGenerate(product);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="card card-elevated overflow-hidden"
    >
      {/* Header */}
      <div className="px-6 py-5 border-b border-neutral-200/50" style={{ background: 'linear-gradient(135deg, var(--color-secondary-50), white)' }}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-md" style={{ background: 'linear-gradient(135deg, var(--color-secondary-500), var(--color-secondary-600))', boxShadow: '0 4px 14px rgba(249, 115, 22, 0.25)' }}>
            <Package className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-display text-lg font-bold text-neutral-900">
              产品信息
            </h2>
            <p className="text-xs text-neutral-500">输入产品核心信息</p>
          </div>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="p-6 space-y-5">
        {/* Product Name */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <label className="flex items-center gap-3 text-sm font-semibold text-neutral-700 mb-2.5">
            <span className="w-6 h-6 rounded-lg bg-secondary-100 flex items-center justify-center flex-shrink-0">
              <span className="text-secondary-600 text-xs font-bold">1</span>
            </span>
            产品名称 <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              type="text"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                setNameError(null);
              }}
              className={`
                input input-lg w-full
                ${nameError ? "input-error" : name.length > 0 ? "input-success" : ""}
              `}
              placeholder="例如：智能睡眠枕 Pro"
              required
            />
            {name.length > 0 && !nameError && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center"
              >
                <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </motion.div>
            )}
          </div>
          {nameError && (
            <motion.p
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-red-500 text-xs mt-1.5 flex items-center gap-1"
            >
              <span className="w-1 h-1 rounded-full bg-red-500" />
              {nameError}
            </motion.p>
          )}
        </motion.div>

        {/* Product Description */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.15 }}
        >
          <label className="flex items-center gap-3 text-sm font-semibold text-neutral-700 mb-2.5">
            <span className="w-6 h-6 rounded-lg bg-secondary-100 flex items-center justify-center flex-shrink-0">
              <span className="text-secondary-600 text-xs font-bold">2</span>
            </span>
            产品描述 <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <textarea
              value={description}
              onChange={(e) => {
                setDescription(e.target.value);
                setDescError(null);
              }}
              className={`
                input textarea w-full min-h-[100px]
                ${descError ? "input-error" : description.length > 0 ? "input-success" : ""}
              `}
              placeholder="详细描述产品的核心功能、特点和优势..."
              rows={4}
              required
            />
            {description.length > 0 && !descError && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute right-3 top-3 w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center"
              >
                <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </motion.div>
            )}
          </div>
          <div className="flex justify-between items-center mt-1.5">
            {descError ? (
              <motion.p
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-red-500 text-xs flex items-center gap-1"
              >
                <span className="w-1 h-1 rounded-full bg-red-500" />
                {descError}
              </motion.p>
            ) : <span />}
            <span className={`text-xs ${description.length > 1800 ? "text-red-500" : "text-neutral-400"}`}>
              {description.length}/2000
            </span>
          </div>
        </motion.div>

        {/* Selling Points & Target Users */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-4"
        >
          <div>
            <label className="flex items-center gap-3 text-sm font-semibold text-neutral-700 mb-2.5">
              <span className="w-6 h-6 rounded-lg bg-secondary-100 flex items-center justify-center flex-shrink-0">
                <Tag className="w-3.5 h-3.5 text-secondary-500" />
              </span>
              核心卖点
            </label>
            <input
              type="text"
              value={sellingPoints}
              onChange={(e) => setSellingPoints(e.target.value)}
              className="input input-md w-full"
              placeholder="改善睡眠,AI监测..."
            />
            <p className="text-xs text-neutral-400 mt-1.5">多个卖点用逗号分隔</p>
          </div>

          <div>
            <label className="flex items-center gap-3 text-sm font-semibold text-neutral-700 mb-2.5">
              <span className="w-6 h-6 rounded-lg bg-secondary-100 flex items-center justify-center flex-shrink-0">
                <Target className="w-3.5 h-3.5 text-secondary-500" />
              </span>
              目标用户
            </label>
            <input
              type="text"
              value={targetUsers}
              onChange={(e) => setTargetUsers(e.target.value)}
              className="input input-md w-full"
              placeholder="加班族,失眠人群..."
            />
            <p className="text-xs text-neutral-400 mt-1.5">多个用户群体用逗号分隔</p>
          </div>
        </motion.div>

        {/* Category & Price */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.25 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-4"
        >
          <div>
            <label className="flex items-center gap-3 text-sm font-semibold text-neutral-700 mb-2.5">
              <span className="w-6 h-6 rounded-lg bg-secondary-100 flex items-center justify-center flex-shrink-0">
                <span className="text-secondary-600 text-xs font-bold">3</span>
              </span>
              产品类别
            </label>
            <div className="relative">
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="input input-md w-full select"
              >
                <option value="">选择类别</option>
                {CATEGORIES.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="flex items-center gap-3 text-sm font-semibold text-neutral-700 mb-2.5">
              <span className="w-6 h-6 rounded-lg bg-secondary-100 flex items-center justify-center flex-shrink-0">
                <DollarSign className="w-3.5 h-3.5 text-secondary-500" />
              </span>
              价格区间
            </label>
            <input
              type="text"
              value={priceRange}
              onChange={(e) => setPriceRange(e.target.value)}
              className="input input-md w-full"
              placeholder="100-500元"
            />
          </div>
        </motion.div>

        {/* Submit Button */}
        <motion.button
          type="submit"
          disabled={isLoading || !name.trim()}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          whileHover={!isLoading && name.trim() ? { scale: 1.01, y: -2 } : {}}
          whileTap={!isLoading && name.trim() ? { scale: 0.99 } : {}}
          className={`
            w-full py-4 rounded-xl font-semibold text-base
            transition-all duration-300 shadow-lg
            flex items-center justify-center gap-2
            ${isLoading || !name.trim()
              ? "bg-neutral-200 text-neutral-500 cursor-not-allowed shadow-none"
              : "btn-secondary text-white hover:shadow-xl"
            }
          `}
        >
          {isLoading ? (
            <motion.span
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="flex items-center gap-2"
            >
              <svg className="w-5 h-5 spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              AI 正在生成中...
            </motion.span>
          ) : (
            <span className="flex items-center gap-2">
              <Sparkles className="w-5 h-5" />
              开始生成内容
              <ArrowRight className="w-4 h-4" />
            </span>
          )}
        </motion.button>
      </form>
    </motion.div>
  );
}
