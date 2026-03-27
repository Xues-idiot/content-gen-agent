"use client";

import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  searchVideoMaterials,
  downloadVideos,
  generateAudio,
  generateSubtitle,
  combineVideos,
  generateVideo,
  getAvailableVoices,
  VideoSearchRequest,
  VideoSearchResponse,
  AudioGenerateResponse,
  VideoGenerateResponse,
  Voice,
} from "@/lib/api";

const VIDEO_ASPECTS = [
  { value: "9:16", label: "竖屏 (9:16)", icon: "📱" },
  { value: "16:9", label: "横屏 (16:9)", icon: "🖥️" },
  { value: "1:1", label: "方屏 (1:1)", icon: "📐" },
];

const VIDEO_SOURCES = [
  { value: "pexels", label: "Pexels" },
  { value: "pixabay", label: "Pixabay" },
];

const VIDEO_LENGTH_PRESETS = [
  { value: "short", label: "短 (15-30秒)", duration: "3秒片段" },
  { value: "medium", label: "中 (30-60秒)", duration: "5秒片段" },
  { value: "long", label: "长 (60-120秒)", duration: "8秒片段" },
  { value: "custom", label: "自定义", duration: "可调片段" },
];

const TRANSITION_MODES = [
  { value: "none", label: "无" },
  { value: "fade_in", label: "淡入" },
  { value: "fade_out", label: "淡出" },
  { value: "slide_in", label: "滑入" },
  { value: "slide_out", label: "滑出" },
  { value: "shuffle", label: "随机" },
];

const CONCAT_MODES = [
  { value: "random", label: "随机" },
  { value: "sequential", label: "顺序" },
];

interface VideoGeneratorProps {
  script?: string;
  title?: string;
}

export default function VideoGenerator({ script = "", title = "" }: VideoGeneratorProps) {
  const [step, setStep] = useState<"search" | "audio" | "combine" | "generate" | "done">("search");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Search state
  const [searchTerms, setSearchTerms] = useState<string[]>([]);
  const [videoAspect, setVideoAspect] = useState("9:16");
  const [videoSource, setVideoSource] = useState("pexels");
  const [videoLength, setVideoLength] = useState("medium");
  const [videoClipDuration, setVideoClipDuration] = useState(5);
  const [searchResults, setSearchResults] = useState<VideoSearchResponse["videos"]>([]);
  const [selectedVideos, setSelectedVideos] = useState<string[]>([]);
  const [downloadedVideoPaths, setDownloadedVideoPaths] = useState<string[]>([]);

  // Audio state
  const [voices, setVoices] = useState<Voice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState("zh-CN-XiaoyiNeural");
  const [voiceRate, setVoiceRate] = useState(1.0);
  const [audioResult, setAudioResult] = useState<AudioGenerateResponse | null>(null);

  // Combine state
  const [concatMode, setConcatMode] = useState("random");
  const [transitionMode, setTransitionMode] = useState("fade_in");
  const [combinedVideoPath, setCombinedVideoPath] = useState<string>("");

  // Generate state
  const [subtitleEnabled, setSubtitleEnabled] = useState(true);
  const [bgmType, setBgmType] = useState("none");
  const [bgmVolume, setBgmVolume] = useState(0.3);
  const [finalVideoPath, setFinalVideoPath] = useState<string>("");

  // Unmount protection
  const isMountedRef = useRef(true);

  // Load voices on mount
  React.useEffect(() => {
    isMountedRef.current = true;
    let ignore = false;
    getAvailableVoices().then((res) => {
      if (!ignore && res.success) setVoices(res.voices);
    }).catch(() => {});
    return () => {
      ignore = true;
      isMountedRef.current = false;
    };
  }, []);

  const handleSearch = async () => {
    if (!searchTerms.length) {
      setError("请输入至少一个搜索关键词");
      return;
    }
    if (!isMountedRef.current) return;
    setLoading(true);
    setError(null);
    try {
      const request: VideoSearchRequest = {
        search_terms: searchTerms,
        video_aspect: videoAspect,
        source: videoSource,
      };
      const response = await searchVideoMaterials(request);
      if (isMountedRef.current) {
        setSearchResults(response.videos);
        if (response.videos.length === 0) {
          setError("未找到相关视频素材");
        }
      } else {
        return; // Component unmounted, skip state updates
      }
    } catch (e) {
      if (isMountedRef.current) {
        setError(`搜索失败: ${e instanceof Error ? e.message : "未知错误"}`);
      }
    }
    if (isMountedRef.current) setLoading(false);
  };

  const handleDownload = async () => {
    if (selectedVideos.length === 0) {
      setError("请选择至少一个视频");
      return;
    }
    if (!isMountedRef.current) return;
    setLoading(true);
    setError(null);
    try {
      const response = await downloadVideos({ video_urls: selectedVideos });
      if (isMountedRef.current) {
        if (response.success && response.video_paths.length > 0) {
          setDownloadedVideoPaths(response.video_paths);
          setStep("audio");
        } else {
          setError("视频下载失败");
        }
      }
    } catch (e) {
      if (isMountedRef.current) {
        setError(`下载失败: ${e instanceof Error ? e.message : "未知错误"}`);
      }
    }
    if (isMountedRef.current) setLoading(false);
  };

  const handleGenerateAudio = async () => {
    if (!script) {
      setError("请提供要转换的文本脚本");
      return;
    }
    if (!isMountedRef.current) return;
    setLoading(true);
    setError(null);
    try {
      const response = await generateAudio({
        text: script,
        voice_name: selectedVoice,
        voice_rate: voiceRate,
      });
      if (isMountedRef.current) {
        setAudioResult(response);
        if (response.success) {
          setStep("combine");
        } else {
          setError("音频生成失败");
        }
      }
    } catch (e) {
      if (isMountedRef.current) {
        setError(`音频生成失败: ${e instanceof Error ? e.message : "未知错误"}`);
      }
    }
    if (isMountedRef.current) setLoading(false);
  };

  const handleCombine = async () => {
    if (downloadedVideoPaths.length === 0 || !audioResult?.audio_path) {
      setError("缺少视频或音频");
      return;
    }
    if (!isMountedRef.current) return;
    setLoading(true);
    setError(null);
    try {
      const response = await combineVideos({
        video_paths: downloadedVideoPaths,
        audio_path: audioResult.audio_path,
        video_aspect: videoAspect,
        video_length: videoLength,
        video_clip_duration: videoClipDuration,
        concat_mode: concatMode,
        transition_mode: transitionMode,
      });
      if (isMountedRef.current) {
        if (response.success && response.video_path) {
          setCombinedVideoPath(response.video_path);
          setStep("generate");
        } else {
          setError("视频合并失败");
        }
      }
    } catch (e) {
      if (isMountedRef.current) {
        setError(`合并失败: ${e instanceof Error ? e.message : "未知错误"}`);
      }
    }
    if (isMountedRef.current) setLoading(false);
  };

  const handleGenerateFinal = async () => {
    if (!combinedVideoPath || !audioResult?.audio_path) {
      setError("缺少视频或音频");
      return;
    }
    if (!isMountedRef.current) return;
    setLoading(true);
    setError(null);
    try {
      let subtitlePath = "";
      if (subtitleEnabled && audioResult.subtitle_path) {
        try {
          const subRes = await generateSubtitle({
            audio_path: audioResult.audio_path,
            language: "zh",
          });
          if (subRes.success) subtitlePath = subRes.subtitle_path;
        } catch {
          // subtitle generation optional, continue without it
        }
      }

      const response = await generateVideo({
        video_path: combinedVideoPath,
        audio_path: audioResult.audio_path,
        subtitle_path: subtitlePath,
        video_aspect: videoAspect,
        video_length: videoLength,
        video_clip_duration: videoClipDuration,
        subtitle_enabled: subtitleEnabled,
        bgm_type: bgmType,
        bgm_volume: bgmVolume,
      });
      if (isMountedRef.current) {
        if (response.success) {
          setFinalVideoPath(response.video_path);
          setStep("done");
        } else {
          setError(response.error || "视频生成失败");
        }
      }
    } catch (e) {
      if (isMountedRef.current) {
        setError(`生成失败: ${e instanceof Error ? e.message : "未知错误"}`);
      }
    }
    if (isMountedRef.current) setLoading(false);
  };

  const toggleVideoSelection = (url: string) => {
    setSelectedVideos((prev) =>
      prev.includes(url) ? prev.filter((u) => u !== url) : [...prev, url]
    );
  };

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
        className="text-xl font-bold mb-4 flex items-center gap-2"
        style={{ color: "#FF6B35" }}
      >
        <span>🎬</span> 视频生成
      </motion.h2>

      {/* Error Display */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4"
          >
            <p className="text-red-600 text-sm">{error}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Step Indicator */}
      <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-2">
        {["search", "audio", "combine", "generate", "done"].map((s, i) => (
          <div key={s} className="flex items-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: i * 0.1 }}
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                step === s
                  ? "bg-orange-500 text-white"
                  : ["search", "audio", "combine", "generate", "done"].indexOf(step) > i
                  ? "bg-green-500 text-white"
                  : "bg-gray-200 text-gray-500"
              }`}
            >
              {i + 1}
            </motion.div>
            {i < 4 && <div className="w-4 h-0.5 bg-gray-200" />}
          </div>
        ))}
      </div>

      {/* Step 1: Search Materials */}
      {step === "search" && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">搜索关键词</label>
            <input
              type="text"
              placeholder="输入关键词，多个用逗号分隔"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
              onChange={(e) => setSearchTerms(e.target.value.split(",").map((s) => s.trim()).filter(Boolean))}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">视频比例</label>
              <select
                value={videoAspect}
                onChange={(e) => setVideoAspect(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
              >
                {VIDEO_ASPECTS.map((a) => (
                  <option key={a.value} value={a.value}>
                    {a.icon} {a.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">素材来源</label>
              <select
                value={videoSource}
                onChange={(e) => setVideoSource(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
              >
                {VIDEO_SOURCES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleSearch}
            disabled={loading}
            className="w-full py-2 bg-orange-500 text-white rounded-lg font-medium hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "搜索中..." : "搜索视频素材"}
          </motion.button>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="mt-4">
              <p className="text-sm text-gray-600 mb-2">找到 {searchResults.length} 个素材，选择要使用的：</p>
              <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto">
                {searchResults.map((video) => (
                  <motion.div
                    key={video.id}
                    whileHover={{ scale: 1.02 }}
                    onClick={() => toggleVideoSelection(video.url)}
                    className={`p-2 rounded-lg border cursor-pointer transition-colors ${
                      selectedVideos.includes(video.url)
                        ? "border-orange-500 bg-orange-50"
                        : "border-gray-200 hover:border-orange-300"
                    }`}
                  >
                    <p className="text-xs text-gray-500 truncate">{video.provider}</p>
                    <p className="text-sm truncate">{video.duration}s</p>
                    <p className="text-xs text-gray-400">
                      {video.width}x{video.height}
                    </p>
                  </motion.div>
                ))}
              </div>
              {selectedVideos.length > 0 && (
                <motion.button
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleDownload}
                  disabled={loading}
                  className="w-full mt-4 py-2 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 disabled:opacity-50"
                >
                  {loading ? "下载中..." : `下载选择的视频 (${selectedVideos.length})`}
                </motion.button>
              )}
            </div>
          )}
        </motion.div>
      )}

      {/* Step 2: Generate Audio */}
      {step === "audio" && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">语音</label>
            <select
              value={selectedVoice}
              onChange={(e) => setSelectedVoice(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
            >
              {voices.map((v) => (
                <option key={v.name} value={v.name}>
                  {v.name} ({v.gender})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">语速: {voiceRate}x</label>
            <input
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              value={voiceRate}
              onChange={(e) => setVoiceRate(parseFloat(e.target.value))}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">脚本预览</label>
            <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-2 max-h-32 overflow-y-auto">
              {script || "暂无脚本内容"}
            </p>
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleGenerateAudio}
            disabled={loading || !script}
            className="w-full py-2 bg-orange-500 text-white rounded-lg font-medium hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "生成中..." : "生成语音"}
          </motion.button>
        </motion.div>
      )}

      {/* Step 3: Combine Videos */}
      {step === "combine" && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-4"
        >
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">拼接模式</label>
              <select
                value={concatMode}
                onChange={(e) => setConcatMode(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
              >
                {CONCAT_MODES.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">转场效果</label>
              <select
                value={transitionMode}
                onChange={(e) => setTransitionMode(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
              >
                {TRANSITION_MODES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">视频时长</label>
            <select
              value={videoLength}
              onChange={(e) => {
                setVideoLength(e.target.value);
                if (e.target.value !== "custom") {
                  const presetMap: Record<string, number> = { short: 3, medium: 5, long: 8 };
                  setVideoClipDuration(presetMap[e.target.value] || 5);
                }
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
            >
              {VIDEO_LENGTH_PRESETS.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>

          {videoLength === "custom" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                片段时长: {videoClipDuration}秒
              </label>
              <input
                type="range"
                min="1"
                max="30"
                value={videoClipDuration}
                onChange={(e) => setVideoClipDuration(parseInt(e.target.value))}
                className="w-full"
              />
            </div>
          )}

          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-sm text-gray-600">
              <span className="font-medium">音频时长:</span> {audioResult?.duration?.toFixed(1)}s
            </p>
            <p className="text-sm text-gray-600">
              <span className="font-medium">已选视频:</span> {selectedVideos.length} 个
            </p>
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleCombine}
            disabled={loading}
            className="w-full py-2 bg-orange-500 text-white rounded-lg font-medium hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "合并中..." : "合并视频"}
          </motion.button>
        </motion.div>
      )}

      {/* Step 4: Generate Final */}
      {step === "generate" && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-4"
        >
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={subtitleEnabled}
                onChange={(e) => setSubtitleEnabled(e.target.checked)}
                className="w-4 h-4 text-orange-500 rounded focus:ring-orange-500"
              />
              <span className="text-sm">启用字幕</span>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">背景音乐</label>
            <select
              value={bgmType}
              onChange={(e) => setBgmType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
            >
              <option value="none">无</option>
              <option value="random">随机</option>
            </select>
          </div>

          {bgmType !== "none" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">音量: {Math.round(bgmVolume * 100)}%</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={bgmVolume}
                onChange={(e) => setBgmVolume(parseFloat(e.target.value))}
                className="w-full"
              />
            </div>
          )}

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleGenerateFinal}
            disabled={loading}
            className="w-full py-2 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "生成中..." : "生成最终视频"}
          </motion.button>
        </motion.div>
      )}

      {/* Step 5: Done */}
      {step === "done" && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center py-8"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200, damping: 15 }}
            className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4"
          >
            <span className="text-3xl">✅</span>
          </motion.div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">视频生成完成!</h3>
          <p className="text-gray-600 mb-4">视频已保存至:</p>
          <p className="text-sm bg-gray-100 rounded-lg p-2 break-all">{finalVideoPath}</p>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => {
              setStep("search");
              setFinalVideoPath("");
              setSelectedVideos([]);
              setDownloadedVideoPaths([]);
              setSearchResults([]);
              setError(null);
            }}
            className="mt-6 px-6 py-2 bg-orange-500 text-white rounded-lg font-medium hover:bg-orange-600"
          >
            生成下一个视频
          </motion.button>
        </motion.div>
      )}
    </motion.div>
  );
}