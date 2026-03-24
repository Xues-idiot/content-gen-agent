"use client";

import React from "react";
import { motion } from "motion/react";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  text?: string;
  fullScreen?: boolean;
}

export default function LoadingSpinner({
  size = "md",
  text = "加载中...",
  fullScreen = false,
}: LoadingSpinnerProps) {
  const sizeMap = {
    sm: 24,
    md: 40,
    lg: 64,
  };

  const spinnerSize = sizeMap[size];

  const spinner = (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      className="flex flex-col items-center justify-center"
    >
      <motion.div
        style={{
          width: spinnerSize,
          height: spinnerSize,
          border: "4px solid #FFE4D6",
          borderTopColor: "#FF6B35",
          borderRadius: "50%",
        }}
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      />
      {text && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mt-4 text-gray-600"
        >
          {text}
        </motion.p>
      )}
    </motion.div>
  );

  if (fullScreen) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="fixed inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm z-50"
      >
        {spinner}
      </motion.div>
    );
  }

  return spinner;
}
