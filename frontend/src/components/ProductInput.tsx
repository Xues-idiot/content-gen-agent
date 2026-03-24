"use client";

import React, { useState } from "react";
import { motion } from "motion/react";
import { validateProductName, validateProductDescription, colors } from "@/lib/utils";

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate
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

  const categories = [
    { value: "", label: "选择类别" },
    { value: "美妆", label: "💄 美妆" },
    { value: "数码", label: "📱 数码" },
    { value: "食品", label: "🍜 食品" },
    { value: "家居", label: "🏠 家居" },
    { value: "服装", label: "👗 服装" },
    { value: "健康", label: "💊 健康" },
    { value: "教育", label: "📚 教育" },
    { value: "旅游", label: "✈️ 旅游" },
    { value: "其他", label: "📦 其他" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-xl shadow-md p-6"
    >
      <motion.h2
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.1 }}
        className="text-xl font-bold mb-4"
        style={{ color: colors.primary }}
      >
        产品信息
      </motion.h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <label className="block text-sm font-medium text-gray-700 mb-1">
            产品名称 *
          </label>
          <motion.input
            type="text"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
              setNameError(null);
            }}
            className={`w-full px-3 py-2 border-2 rounded-lg focus:outline-none transition-colors ${
              nameError ? "border-red-300 focus:border-red-500" : "border-gray-200 focus:border-orange-400"
            }`}
            placeholder="例如：智能睡眠枕"
            required
            whileFocus={{ scale: 1.01 }}
          />
          {nameError && (
            <motion.p
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-red-500 text-xs mt-1"
            >
              {nameError}
            </motion.p>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.25 }}
        >
          <label className="block text-sm font-medium text-gray-700 mb-1">
            产品描述 *
          </label>
          <motion.textarea
            value={description}
            onChange={(e) => {
              setDescription(e.target.value);
              setDescError(null);
            }}
            className={`w-full px-3 py-2 border-2 rounded-lg focus:outline-none transition-colors ${
              descError ? "border-red-300 focus:border-red-500" : "border-gray-200 focus:border-orange-400"
            }`}
            placeholder="描述产品的核心功能和特点"
            rows={3}
            required
            whileFocus={{ scale: 1.01 }}
          />
          <div className="flex justify-between items-center mt-1">
            {descError ? (
              <motion.p
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-red-500 text-xs"
              >
                {descError}
              </motion.p>
            ) : (
              <span />
            )}
            <span className="text-xs text-gray-400">{description.length}/2000</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <label className="block text-sm font-medium text-gray-700 mb-1">
            核心卖点
          </label>
          <motion.input
            type="text"
            value={sellingPoints}
            onChange={(e) => setSellingPoints(e.target.value)}
            className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-orange-400 transition-colors"
            placeholder="用逗号分隔，例如：改善睡眠,AI监测,个性化调节"
            whileFocus={{ scale: 1.01, borderColor: colors.primary }}
          />
          <p className="text-xs text-gray-500 mt-1">多个卖点用逗号分隔</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.35 }}
        >
          <label className="block text-sm font-medium text-gray-700 mb-1">
            目标用户
          </label>
          <motion.input
            type="text"
            value={targetUsers}
            onChange={(e) => setTargetUsers(e.target.value)}
            className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-orange-400 transition-colors"
            placeholder="用逗号分隔，例如：加班族,失眠人群"
            whileFocus={{ scale: 1.01, borderColor: colors.primary }}
          />
          <p className="text-xs text-gray-500 mt-1">多个用户群体用逗号分隔</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="grid grid-cols-2 gap-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              产品类别
            </label>
            <motion.select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-orange-400 transition-colors"
              whileFocus={{ scale: 1.01, borderColor: colors.primary }}
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </motion.select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              价格区间
            </label>
            <motion.input
              type="text"
              value={priceRange}
              onChange={(e) => setPriceRange(e.target.value)}
              className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-orange-400 transition-colors"
              placeholder="例如：100-500元"
              whileFocus={{ scale: 1.01, borderColor: colors.primary }}
            />
          </div>
        </motion.div>

        <motion.button
          type="submit"
          disabled={isLoading || !name.trim()}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.45 }}
          whileHover={!isLoading && name.trim() ? { scale: 1.02 } : {}}
          whileTap={!isLoading && name.trim() ? { scale: 0.98 } : {}}
          className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-all shadow-md ${
            isLoading || !name.trim()
              ? "bg-gray-400 cursor-not-allowed"
              : ""
          }`}
          style={{
            backgroundColor: isLoading || !name.trim() ? undefined : colors.primary,
          }}
        >
          {isLoading ? (
            <motion.span
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              生成中...
            </motion.span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              <span>✨</span> 生成内容
            </span>
          )}
        </motion.button>
      </form>
    </motion.div>
  );
}
