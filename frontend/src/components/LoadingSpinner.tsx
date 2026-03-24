"use client";

import React from "react";
import { motion } from "motion/react";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  text?: string;
  fullScreen?: boolean;
  steps?: string[];
  currentStep?: number;
}

export default function LoadingSpinner({
  size = "md",
  text = "加载中...",
  fullScreen = false,
  steps,
  currentStep = 0,
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
          className="mt-4 text-gray-600 font-medium"
        >
          {text}
        </motion.p>
      )}
      {steps && steps.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-4 flex flex-col items-center gap-2"
        >
          {steps.map((step, index) => (
            <motion.div
              key={step}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center gap-2"
            >
              <div
                className={`w-2 h-2 rounded-full transition-colors ${
                  index < currentStep
                    ? "bg-green-500"
                    : index === currentStep
                    ? "bg-orange-400 animate-pulse"
                    : "bg-gray-300"
                }`}
              />
              <span
                className={`text-xs ${
                  index === currentStep ? "text-orange-600 font-medium" : "text-gray-400"
                }`}
              >
                {step}
              </span>
            </motion.div>
          ))}
        </motion.div>
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
