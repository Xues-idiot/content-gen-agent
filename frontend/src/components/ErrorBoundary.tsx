"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center p-8 bg-white rounded-xl shadow-lg max-w-md">
            <div className="text-6xl mb-4">😅</div>
            <h1 className="text-xl font-bold text-gray-800 mb-2">出了点小问题</h1>
            <p className="text-gray-500 mb-4">
              {this.state.error?.message || "发生了未知错误"}
            </p>
            <div className="flex flex-col gap-3">
              <button
                onClick={() => {
                  // Clear session storage to avoid corrupted state, then reload
                  try { sessionStorage.clear(); } catch {}
                  window.location.reload();
                }}
                className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
              >
                刷新页面
              </button>
              <button
                onClick={() => {
                  // Navigate to home instead of reload to break potential infinite loops
                  window.location.href = "/";
                }}
                className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                返回首页
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
