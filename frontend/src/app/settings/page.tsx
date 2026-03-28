"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion } from "motion/react";
import SidebarNav from "@/components/SidebarNav";
import { ToastProvider, useToast } from "@/components/Toast";
import {
  Settings,
  Key,
  Globe,
  Palette,
  Bell,
  Shield,
  Info,
  CheckCircle,
  XCircle,
  Bot,
  ChevronRight,
  Loader2,
  RefreshCw,
  Sparkles,
} from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

interface LLMProvider {
  name: string;
  configured: boolean;
  models: string[];
}

interface LLMConfig {
  current_provider: string;
  available_providers: string[];
  provider_info: {
    provider: string;
    model: string;
    base_url: string;
    configured: boolean;
  };
}

function SettingsPageContent() {
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState("general");
  const [backendStatus, setBackendStatus] = useState({
    api: false,
    tavily: false,
    version: "",
  });
  const [llmProviders, setLlmProviders] = useState<LLMProvider[]>([]);
  const [llmConfig, setLlmConfig] = useState<LLMConfig | null>(null);
  const [selectedProvider, setSelectedProvider] = useState("");
  const [providerApiKey, setProviderApiKey] = useState("");
  const [providerBaseUrl, setProviderBaseUrl] = useState("");
  const [providerModel, setProviderModel] = useState("");
  const [testingProvider, setTestingProvider] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; response: string } | null>(null);
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    checkBackendHealth();
    if (activeTab === "llm") {
      loadLLMConfig();
    }
    return () => { isMountedRef.current = false; };
  }, [activeTab]);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (response.ok) {
        const data = await response.json();
        if (isMountedRef.current) {
          setBackendStatus({
            api: data.api_key_configured || false,
            tavily: data.tavily_api_configured || false,
            version: data.version || "",
          });
        }
      }
    } catch {
      // Backend not available
    }
  };

  const loadLLMConfig = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/llm/config`);
      if (response.ok) {
        const data = await response.json();
        if (isMountedRef.current) {
          setLlmConfig(data);
          setSelectedProvider(data.current_provider);
        }

        // Load providers list
        const providersResponse = await fetch(`${API_BASE_URL}/llm/providers`);
        if (providersResponse.ok && isMountedRef.current) {
          setLlmProviders(await providersResponse.json());
        }
      }
    } catch {
      if (isMountedRef.current) {
        showToast("加载 LLM 配置失败", "error");
      }
    }
  };

  const switchProvider = async () => {
    if (!selectedProvider) return;

    try {
      const response = await fetch(`${API_BASE_URL}/llm/provider`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider: selectedProvider,
          api_key: providerApiKey || undefined,
          base_url: providerBaseUrl || undefined,
          model: providerModel || undefined,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        if (isMountedRef.current) {
          showToast(data.message, "success");
          loadLLMConfig();
          setProviderApiKey("");
          setProviderBaseUrl("");
          setProviderModel("");
        }
      } else {
        if (isMountedRef.current) {
          showToast(data.detail || "切换失败", "error");
        }
      }
    } catch {
      if (isMountedRef.current) {
        showToast("切换 LLM Provider 失败", "error");
      }
    }
  };

  const testConnection = async () => {
    if (!isMountedRef.current) return;
    setTestingProvider(true);
    setTestResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/llm/test?prompt=${encodeURIComponent("请回复'连接成功'")}`);
      const data = await response.json();

      if (isMountedRef.current) {
        setTestResult({
          success: data.success,
          response: data.success ? data.response : data.error || data.response,
        });

        if (data.success) {
          showToast("连接测试成功", "success");
        } else {
          showToast("连接测试失败", "error");
        }
      }
    } catch {
      if (isMountedRef.current) {
        setTestResult({ success: false, response: "请求失败" });
        showToast("连接测试失败", "error");
      }
    } finally {
      if (isMountedRef.current) setTestingProvider(false);
    }
  };

  const tabs = [
    { id: "general", label: "通用", icon: Settings },
    { id: "api", label: "API 配置", icon: Key },
    { id: "llm", label: "LLM 设置", icon: Bot },
    { id: "appearance", label: "外观", icon: Palette },
    { id: "about", label: "关于", icon: Info },
  ];

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

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-gray-400 to-gray-500 flex items-center justify-center">
            <Settings className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">设置</h1>
            <p className="text-gray-500 text-sm">配置应用参数和 API</p>
          </div>
        </div>
      </motion.div>

      <div className="flex gap-6">
        {/* Tabs */}
        <div className="w-48 shrink-0">
          <nav className="space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? "bg-orange-50 text-orange-600"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm"
          >
            {activeTab === "general" && (
              <motion.div variants={item} className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">通用设置</h2>
                </div>

                {/* Backend Status */}
                <div className="p-4 bg-gray-50 rounded-xl">
                  <h3 className="font-medium text-gray-900 mb-3">后端服务状态</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">后端版本</span>
                      <span className="text-sm font-medium text-gray-900">
                        {backendStatus.version || "未知"}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">MiniMax API</span>
                      <span className="flex items-center gap-1.5">
                        {backendStatus.api ? (
                          <>
                            <CheckCircle className="w-4 h-4 text-green-500" />
                            <span className="text-sm text-green-600">已配置</span>
                          </>
                        ) : (
                          <>
                            <XCircle className="w-4 h-4 text-red-500" />
                            <span className="text-sm text-red-600">未配置</span>
                          </>
                        )}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Tavily API</span>
                      <span className="flex items-center gap-1.5">
                        {backendStatus.tavily ? (
                          <>
                            <CheckCircle className="w-4 h-4 text-green-500" />
                            <span className="text-sm text-green-600">已配置</span>
                          </>
                        ) : (
                          <>
                            <XCircle className="w-4 h-4 text-yellow-500" />
                            <span className="text-sm text-yellow-600">可选</span>
                          </>
                        )}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={checkBackendHealth}
                    className="mt-3 text-sm text-orange-500 hover:text-orange-600 font-medium"
                  >
                    刷新状态
                  </button>
                </div>

                {/* Default Platform */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    默认平台
                  </label>
                  <select className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-orange-300 focus:ring-2 focus:ring-orange-100 outline-none transition-all">
                    <option value="xiaohongshu">小红书</option>
                    <option value="tiktok">抖音</option>
                    <option value="official">公众号</option>
                    <option value="friend_circle">朋友圈</option>
                  </select>
                  <p className="mt-1 text-xs text-gray-500">
                    新建内容时默认选择的平台
                  </p>
                </div>

                {/* Auto Save */}
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">自动保存</p>
                    <p className="text-sm text-gray-500">自动保存草稿到本地</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" defaultChecked className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-orange-100 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-500"></div>
                  </label>
                </div>
              </motion.div>
            )}

            {activeTab === "api" && (
              <motion.div variants={item} className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">API 配置</h2>
                  <p className="text-sm text-gray-500 mb-4">
                    API 密钥配置在后端环境变量中，请参考 .env.example 文件
                  </p>
                </div>

                <div className="p-4 bg-gray-50 rounded-xl space-y-4">
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">MiniMax API</h3>
                    <p className="text-sm text-gray-500 mb-2">
                      用于 AI 文案生成的核心 API
                    </p>
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-gray-600">状态:</span>
                      {backendStatus.api ? (
                        <span className="text-green-600 flex items-center gap-1">
                          <CheckCircle className="w-4 h-4" /> 已配置
                        </span>
                      ) : (
                        <span className="text-red-600 flex items-center gap-1">
                          <XCircle className="w-4 h-4" /> 未配置
                        </span>
                      )}
                    </div>
                  </div>

                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Tavily API</h3>
                    <p className="text-sm text-gray-500 mb-2">
                      用于市场调研和趋势分析（可选）
                    </p>
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-gray-600">状态:</span>
                      {backendStatus.tavily ? (
                        <span className="text-green-600 flex items-center gap-1">
                          <CheckCircle className="w-4 h-4" /> 已配置
                        </span>
                      ) : (
                        <span className="text-yellow-600 flex items-center gap-1">
                          <XCircle className="w-4 h-4" /> 未配置（可选功能）
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-orange-50 border border-orange-200 rounded-xl">
                  <h3 className="font-medium text-orange-900 mb-2">配置说明</h3>
                  <ol className="text-sm text-orange-700 space-y-1 list-decimal list-inside">
                    <li>复制项目根目录下的 .env.example 为 .env</li>
                    <li>填入你的 MiniMax API Key</li>
                    <li>（可选）填入 Tavily API Key</li>
                    <li>重启后端服务</li>
                  </ol>
                </div>
              </motion.div>
            )}

            {activeTab === "llm" && llmConfig && (
              <motion.div variants={item} className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">LLM 设置</h2>
                  <p className="text-sm text-gray-500 mb-4">
                    选择和配置不同的 LLM Provider，支持 DeepSeek、Moonshot、OpenAI、Ollama 等
                  </p>
                </div>

                {/* Current Provider Status */}
                <div className="p-4 bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl border border-orange-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-orange-500 flex items-center justify-center">
                        <Sparkles className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">
                          当前使用: {llmConfig.current_provider.toUpperCase()}
                        </p>
                        <p className="text-sm text-gray-500">
                          模型: {llmConfig.provider_info?.model || "默认"}
                        </p>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      llmConfig.provider_info?.configured
                        ? "bg-green-100 text-green-700"
                        : "bg-red-100 text-red-700"
                    }`}>
                      {llmConfig.provider_info?.configured ? "已配置" : "未配置"}
                    </span>
                  </div>
                </div>

                {/* Provider Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    选择 LLM Provider
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    {llmProviders.map((provider) => (
                      <button
                        key={provider.name}
                        onClick={() => setSelectedProvider(provider.name)}
                        className={`p-3 rounded-xl border-2 transition-all text-left ${
                          selectedProvider === provider.name
                            ? "border-orange-500 bg-orange-50"
                            : "border-gray-200 hover:border-gray-300 bg-white"
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium text-gray-900 capitalize">
                            {provider.name}
                          </span>
                          {provider.configured ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : (
                            <XCircle className="w-4 h-4 text-gray-300" />
                          )}
                        </div>
                        <p className="text-xs text-gray-500">
                          {provider.models.slice(0, 2).join(", ")}
                          {provider.models.length > 2 ? "..." : ""}
                        </p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Custom Configuration */}
                {selectedProvider && selectedProvider !== "pollinations" && selectedProvider !== "ollama" && (
                  <div className="p-4 bg-gray-50 rounded-xl space-y-4">
                    <h3 className="font-medium text-gray-900">自定义配置</h3>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        API Key {selectedProvider === "minimax" ? "(可选)" : "(必填)"}
                      </label>
                      <input
                        type="password"
                        value={providerApiKey}
                        onChange={(e) => setProviderApiKey(e.target.value)}
                        placeholder="输入 API Key"
                        className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-orange-300 focus:ring-2 focus:ring-orange-100 outline-none transition-all"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Base URL {selectedProvider === "minimax" ? "(可选)" : "(必填)"}
                      </label>
                      <input
                        type="text"
                        value={providerBaseUrl}
                        onChange={(e) => setProviderBaseUrl(e.target.value)}
                        placeholder={`https://api.${selectedProvider}.com`}
                        className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-orange-300 focus:ring-2 focus:ring-orange-100 outline-none transition-all"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        模型名称
                      </label>
                      <input
                        type="text"
                        value={providerModel}
                        onChange={(e) => setProviderModel(e.target.value)}
                        placeholder={llmProviders.find(p => p.name === selectedProvider)?.models[0] || "输入模型名称"}
                        className="w-full px-3 py-2.5 rounded-xl border border-gray-200 focus:border-orange-300 focus:ring-2 focus:ring-orange-100 outline-none transition-all"
                      />
                    </div>
                  </div>
                )}

                {/* Provider Info */}
                {selectedProvider && (
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
                    <h3 className="font-medium text-blue-900 mb-2 capitalize">{selectedProvider} 使用说明</h3>
                    <ul className="text-sm text-blue-700 space-y-1">
                      {selectedProvider === "minimax" && (
                        <>
                          <li>• MiniMax API 默认配置，无需额外设置</li>
                          <li>• 支持环境变量: MINIMAX_API_KEY</li>
                        </>
                      )}
                      {selectedProvider === "deepseek" && (
                        <>
                          <li>• DeepSeek API 兼容 OpenAI 格式</li>
                          <li>• 支持模型: deepseek-chat, deepseek-coder</li>
                        </>
                      )}
                      {selectedProvider === "moonshot" && (
                        <>
                          <li>• Moonshot API 兼容 OpenAI 格式</li>
                          <li>• 支持模型: moonshot-v1-8k/32k/128k</li>
                        </>
                      )}
                      {selectedProvider === "openai" && (
                        <>
                          <li>• OpenAI API，支持 GPT-4o、GPT-4 等</li>
                          <li>• 支持自定义 API 代理地址</li>
                        </>
                      )}
                      {selectedProvider === "azure" && (
                        <>
                          <li>• Azure OpenAI Service</li>
                          <li>• 需要配置 Azure 端点和 API 版本</li>
                        </>
                      )}
                      {selectedProvider === "ollama" && (
                        <>
                          <li>• Ollama 本地模型，无需 API Key</li>
                          <li>• 默认地址: http://localhost:11434</li>
                        </>
                      )}
                      {selectedProvider === "gemini" && (
                        <>
                          <li>• Google Gemini API</li>
                          <li>• 支持模型: gemini-1.5-flash, gemini-1.5-pro</li>
                        </>
                      )}
                      {selectedProvider === "pollinations" && (
                        <>
                          <li>• Pollinations 免费 LLM 服务</li>
                          <li>• 无需 API Key，直接可用</li>
                          <li>• 支持 openai-fast 模型</li>
                        </>
                      )}
                    </ul>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3">
                  <button
                    onClick={switchProvider}
                    disabled={!selectedProvider}
                    className="flex-1 px-4 py-2.5 bg-orange-500 text-white rounded-xl font-medium hover:bg-orange-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    <ChevronRight className="w-4 h-4" />
                    切换 Provider
                  </button>
                  <button
                    onClick={testConnection}
                    disabled={testingProvider}
                    className="px-4 py-2.5 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {testingProvider ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <RefreshCw className="w-4 h-4" />
                    )}
                    测试连接
                  </button>
                </div>

                {/* Test Result */}
                {testResult && (
                  <div className={`p-4 rounded-xl border ${
                    testResult.success
                      ? "bg-green-50 border-green-200"
                      : "bg-red-50 border-red-200"
                  }`}>
                    <div className="flex items-start gap-3">
                      {testResult.success ? (
                        <CheckCircle className="w-5 h-5 text-green-500 shrink-0 mt-0.5" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                      )}
                      <div>
                        <p className={`font-medium ${
                          testResult.success ? "text-green-900" : "text-red-900"
                        }`}>
                          {testResult.success ? "连接成功" : "连接失败"}
                        </p>
                        <p className={`text-sm mt-1 ${
                          testResult.success ? "text-green-700" : "text-red-700"
                        }`}>
                          {testResult.response}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {activeTab === "appearance" && (
              <motion.div variants={item} className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">外观设置</h2>
                </div>

                {/* Theme */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    主题颜色
                  </label>
                  <div className="flex gap-3">
                    {[
                      { id: "orange", color: "#FF6B35", name: "活力橙" },
                      { id: "blue", color: "#3B82F6", name: "天空蓝" },
                      { id: "green", color: "#10B981", name: "自然绿" },
                      { id: "purple", color: "#8B5CF6", name: "梦幻紫" },
                    ].map((theme) => (
                      <button
                        key={theme.id}
                        onClick={() => showToast(`主题已切换为${theme.name}`, "success")}
                        className={`w-12 h-12 rounded-xl border-2 transition-all ${
                          theme.id === "orange"
                            ? "border-orange-500 ring-2 ring-orange-200"
                            : "border-gray-200 hover:border-gray-300"
                        }`}
                        style={{ backgroundColor: theme.color }}
                        title={theme.name}
                      />
                    ))}
                  </div>
                </div>

                {/* Compact Mode */}
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">紧凑模式</p>
                    <p className="text-sm text-gray-500">减少界面元素间距</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-orange-100 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-500"></div>
                  </label>
                </div>
              </motion.div>
            )}

            {activeTab === "about" && (
              <motion.div variants={item} className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">关于 Vox</h2>
                </div>

                <div className="text-center py-8">
                  <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-orange-400 to-orange-500 flex items-center justify-center text-4xl mx-auto mb-4">
                    📢
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-1">Vox</h3>
                  <p className="text-gray-500 mb-4">内容生成 Agent</p>
                  <p className="text-sm text-gray-400">版本 {backendStatus.version || "0.1.0"}</p>
                </div>

                <div className="p-4 bg-gray-50 rounded-xl space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">前端框架</span>
                    <span className="text-gray-900">Next.js 15 + React 19</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">后端框架</span>
                    <span className="text-gray-900">FastAPI + LangGraph</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">样式框架</span>
                    <span className="text-gray-900">Tailwind CSS v4</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">AI 模型</span>
                    <span className="text-gray-900">MiniMax-M2.7</span>
                  </div>
                </div>

                <div className="text-center text-sm text-gray-400">
                  <p>基于 AI 的多平台营销内容生成工具</p>
                  <p className="mt-1">支持小红书、抖音、公众号、朋友圈</p>
                </div>
              </motion.div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}

export default function SettingsPage() {
  return (
    <SidebarNav>
      <ToastProvider>
        <SettingsPageContent />
      </ToastProvider>
    </SidebarNav>
  );
}
