// API 工具函数

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8003";

export interface ProductInput {
  name: string;
  description: string;
  selling_points: string[];
  target_users: string[];
  category: string;
  price_range: string;
}

export interface ContentRequest {
  product: ProductInput;
  platforms: string[];
  enable_research?: boolean;
}

export interface Violation {
  word: string;
  position: number;
  suggestion: string;
  severity: string;
}

export interface ReviewResult {
  passed: boolean;
  quality_score: number;
  violations: Violation[];
  suggestions: string[];
  analysis?: {
    has_emoji: boolean;
    has_numbers: boolean;
    has_hashtags: boolean;
    paragraph_count: number;
  };
}

export interface CopyResult {
  platform: string;
  title: string;
  content: string;
  script?: string;
  tags: string[];
  imageSuggestions: string[];
  cta?: string;
  review?: ReviewResult;
  success: boolean;
  error?: string;
}

export interface ContentResponse {
  success: boolean;
  platform_results: CopyResult[];
  errors: string[];
  market_insights?: string[];
  trend_topics?: string[];
  competitor_content?: { name: string; title: string; url: string }[];
}

export interface Platform {
  id: string;
  name: string;
  description: string;
  icon?: string;
}

export interface Category {
  id: string;
  name: string;
  icon: string;
}

export interface HealthStatus {
  status: string;
  version: string;
  api_key_configured: boolean;
  tavily_api_configured?: boolean;
  llm_provider?: string;
}

export interface ApiError {
  error: string;
  detail?: string;
}

// ============= Video Generation Types =============

export interface VideoSearchRequest {
  search_terms: string[];
  video_aspect: string;
  source: string;
}

export interface VideoSearchResponse {
  success: boolean;
  videos: {
    provider: string;
    url: string;
    duration: number;
    width: number;
    height: number;
    id: string;
  }[];
  total: number;
}

export interface VideoDownloadRequest {
  video_urls: string[];
  save_dir?: string;
}

export interface VideoDownloadResponse {
  success: boolean;
  video_paths: string[];
  total: number;
}

export interface AudioGenerateRequest {
  text: string;
  voice_name: string;
  voice_rate: number;
}

export interface AudioGenerateResponse {
  success: boolean;
  audio_path: string;
  subtitle_path: string;
  duration: number;
}

export interface SubtitleGenerateRequest {
  audio_path: string;
  language: string;
}

export interface SubtitleGenerateResponse {
  success: boolean;
  subtitle_path: string;
}

export interface VideoCombineRequest {
  video_paths: string[];
  audio_path: string;
  output_path?: string;
  video_aspect: string;
  video_length?: string;
  video_clip_duration?: number;
  concat_mode: string;
  transition_mode: string;
}

export interface VideoCombineResponse {
  success: boolean;
  video_path: string;
}

export interface VideoGenerateRequest {
  video_path: string;
  audio_path: string;
  subtitle_path?: string;
  output_path?: string;
  video_aspect: string;
  video_length?: string;
  video_clip_duration?: number;
  subtitle_enabled: boolean;
  bgm_type: string;
  bgm_volume: number;
}

export interface VideoGenerateResponse {
  success: boolean;
  video_path: string;
  duration: number;
  error?: string;
}

export interface Voice {
  name: string;
  language: string;
  gender: string;
}

// ============= API Client =============

class ApiClient {
  private baseUrl: string;
  private defaultHeaders: HeadersInit;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.defaultHeaders = {
      "Content-Type": "application/json",
    };
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({ error: "Unknown error" }));
      throw new Error(error.error || `API Error: ${response.status}`);
    }
    const text = await response.text();
    if (!text) {
      return {} as T;
    }
    return JSON.parse(text) as T;
  }

  async generateContent(request: ContentRequest): Promise<ContentResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/content/generate`, {
      method: "POST",
      headers: this.defaultHeaders,
      body: JSON.stringify(request),
    });
    return this.handleResponse<ContentResponse>(response);
  }

  async reviewContent(content: string): Promise<ReviewResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/content/review`, {
      method: "POST",
      headers: this.defaultHeaders,
      body: JSON.stringify({ content }),
    });
    return this.handleResponse<ReviewResult>(response);
  }

  async getPlatforms(): Promise<{ platforms: Platform[] }> {
    const response = await fetch(`${this.baseUrl}/api/v1/platforms`);
    return this.handleResponse<{ platforms: Platform[] }>(response);
  }

  async getCategories(): Promise<{ categories: Category[] }> {
    const response = await fetch(`${this.baseUrl}/api/v1/categories`);
    return this.handleResponse<{ categories: Category[] }>(response);
  }

  async getHealth(): Promise<HealthStatus> {
    const response = await fetch(`${this.baseUrl}/health`);
    return this.handleResponse<HealthStatus>(response);
  }

  async checkAvailable(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: "GET",
        signal: AbortSignal.timeout(3000),
      });
      if (!response.ok) return false;
      const data = await response.json();
      return data.status === "healthy";
    } catch {
      return false;
    }
  }

  async getStats(): Promise<{
    total_requests: number;
    total_platforms: number;
    supported_platforms: string[];
  }> {
    const response = await fetch(`${this.baseUrl}/api/v1/stats`);
    return this.handleResponse(response);
  }

  async getPlatformSuggestions(platform: string, content: string): Promise<{
    platform: string;
    suggestions: string[];
  }> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/suggestions/${platform}?content=${encodeURIComponent(content)}`
    );
    return this.handleResponse(response);
  }

  async getTrendingTopics(platform: string, category: string = "general"): Promise<{
    platform: string;
    category: string;
    success: boolean;
    results: { title: string; url: string; content: string; score: number }[];
    error?: string;
  }> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/trending/${platform}?category=${encodeURIComponent(category)}`
    );
    return this.handleResponse(response);
  }

  async getHotKeywords(category: string = "general"): Promise<{
    category: string;
    hot_keywords: string[];
    timestamp: string;
  }> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/hot-keywords?category=${encodeURIComponent(category)}`
    );
    return this.handleResponse(response);
  }

  async getBestPractices(platform: string): Promise<{
    success: boolean;
    platform: string;
    practices: {
      name: string;
      optimal_length: string;
      hashtag_format: string;
      emoji_usage: string;
      best_posting_times: string[];
      tips: string[];
    };
  }> {
    const response = await fetch(`${this.baseUrl}/api/v1/best-practices/${platform}`);
    return this.handleResponse(response);
  }

  async getContentCalendar(platform?: string): Promise<{
    success: boolean;
    scheduled_content: {
      id: string;
      product_name: string;
      platform: string;
      title: string;
      content: string;
      tags: string[];
      scheduled_time: string;
      status: string;
      created_at: string;
    }[];
    total: number;
  }> {
    const params = platform ? `?platform=${encodeURIComponent(platform)}` : "";
    const response = await fetch(`${this.baseUrl}/api/v1/calendar${params}`);
    return this.handleResponse(response);
  }

  async scheduleContent(
    productName: string,
    platform: string,
    title: string,
    content: string,
    tags: string[] = [],
    scheduledTime?: string
  ): Promise<{
    success: boolean;
    scheduled_content: {
      id: string;
      product_name: string;
      platform: string;
      title: string;
      content: string;
      tags: string[];
      scheduled_time: string;
      status: string;
      created_at: string;
    }[];
    total: number;
  }> {
    const params = new URLSearchParams({
      product_name: productName,
      platform,
      title,
      content,
    });
    // Append tags individually for proper array handling
    tags.forEach(tag => params.append("tags", tag));
    if (scheduledTime) params.append("scheduled_time", scheduledTime);

    const response = await fetch(`${this.baseUrl}/api/v1/schedule?${params}`, {
      method: "POST",
    });
    return this.handleResponse(response);
  }

  async deleteScheduledContent(scheduleId: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/v1/schedule/${scheduleId}`, {
      method: "DELETE",
    });
    return this.handleResponse(response);
  }

  async markContentPublished(scheduleId: string): Promise<{
    success: boolean;
    content: {
      id: string;
      status: string;
    };
  }> {
    const response = await fetch(`${this.baseUrl}/api/v1/schedule/${scheduleId}/publish`, {
      method: "PUT",
    });
    return this.handleResponse(response);
  }

  // ============= Video Generation Methods =============

  async searchVideoMaterials(request: VideoSearchRequest): Promise<VideoSearchResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/video/search-materials`, {
      method: "POST",
      headers: this.defaultHeaders,
      body: JSON.stringify(request),
    });
    return this.handleResponse<VideoSearchResponse>(response);
  }

  async downloadVideos(request: VideoDownloadRequest): Promise<VideoDownloadResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/video/download`, {
      method: "POST",
      headers: this.defaultHeaders,
      body: JSON.stringify(request),
    });
    return this.handleResponse<VideoDownloadResponse>(response);
  }

  async generateAudio(request: AudioGenerateRequest): Promise<AudioGenerateResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/video/generate-audio`, {
      method: "POST",
      headers: this.defaultHeaders,
      body: JSON.stringify(request),
    });
    return this.handleResponse<AudioGenerateResponse>(response);
  }

  async generateSubtitle(request: SubtitleGenerateRequest): Promise<SubtitleGenerateResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/video/generate-subtitle`, {
      method: "POST",
      headers: this.defaultHeaders,
      body: JSON.stringify(request),
    });
    return this.handleResponse<SubtitleGenerateResponse>(response);
  }

  async combineVideos(request: VideoCombineRequest): Promise<VideoCombineResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/video/combine`, {
      method: "POST",
      headers: this.defaultHeaders,
      body: JSON.stringify(request),
    });
    return this.handleResponse<VideoCombineResponse>(response);
  }

  async generateVideo(request: VideoGenerateRequest): Promise<VideoGenerateResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/video/generate`, {
      method: "POST",
      headers: this.defaultHeaders,
      body: JSON.stringify(request),
    });
    return this.handleResponse<VideoGenerateResponse>(response);
  }

  async getAvailableVoices(): Promise<{ success: boolean; voices: Voice[]; total: number }> {
    const response = await fetch(`${this.baseUrl}/api/v1/video/voices`);
    return this.handleResponse(response);
  }
}

// 导出单例
export const api = new ApiClient(API_BASE_URL);

// 保持向后兼容的导出
export const generateContent = (request: ContentRequest) => api.generateContent(request);
export const reviewContent = (content: string) => api.reviewContent(content);
export const getPlatforms = () => api.getPlatforms();
export const getCategories = () => api.getCategories();
export const getHealth = () => api.getHealth();
export const getStats = () => api.getStats();
export const getPlatformSuggestions = (platform: string, content: string) =>
  api.getPlatformSuggestions(platform, content);

// Video API exports
export const searchVideoMaterials = (request: VideoSearchRequest) => api.searchVideoMaterials(request);
export const downloadVideos = (request: VideoDownloadRequest) => api.downloadVideos(request);
export const generateAudio = (request: AudioGenerateRequest) => api.generateAudio(request);
export const generateSubtitle = (request: SubtitleGenerateRequest) => api.generateSubtitle(request);
export const combineVideos = (request: VideoCombineRequest) => api.combineVideos(request);
export const generateVideo = (request: VideoGenerateRequest) => api.generateVideo(request);
export const getAvailableVoices = () => api.getAvailableVoices();

// ============= Hashtag Types =============

export interface HashtagInfo {
  tag: string;
  category: 'brand' | 'industry' | 'trending' | 'emotional';
  heat_score: number;
  exposure: '低' | '中' | '高';
  reason: string;
}

export interface HashtagCombination {
  name: string;
  description: string;
  hashtags: string[];
  expected_exposure: '低' | '中' | '高';
  best_for: string;
}

export interface HashtagRecommendRequest {
  content: string;
  platform: string;
  amount?: number;
  product_info?: ProductInput;
}

export interface HashtagRecommendResponse {
  success: boolean;
  hashtags: HashtagInfo[];
  combinations: HashtagCombination[];
  detected_industry: string;
}

export interface TrendingHashtagRequest {
  platform: string;
  industry?: string;
  amount?: number;
}

// ============= Hashtag API Methods =============

export const recommendHashtags = async (request: HashtagRecommendRequest): Promise<HashtagRecommendResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/hashtags/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};

export const getTrendingHashtags = async (request: TrendingHashtagRequest): Promise<HashtagRecommendResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/hashtags/trending`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};

// ============= Image Generation Types =============

export interface ImageGenerateRequest {
  prompt: string;
  style?: string;
  size?: string;
  save_local?: boolean;
}

export interface ImageGenerateResponse {
  success: boolean;
  url: string;
  local_path: string;
  prompt: string;
  style: string;
  width: number;
  height: number;
}

// ============= Image Generation API =============

export const generateImage = async (request: ImageGenerateRequest): Promise<ImageGenerateResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/image/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};

// ============= Translation Types =============

export interface TranslationRequest {
  content: string;
  target_lang: string;
  source_lang?: string;
}

export interface TranslationResponse {
  success: boolean;
  original: string;
  translated: string;
  source_lang: string;
  target_lang: string;
}

// ============= Translation API =============

export const translateContent = async (request: TranslationRequest): Promise<TranslationResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/translate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};

// ============= Content Template Types =============

export interface ContentTemplateRequest {
  platform: string;
  content_type: string;
  tone?: string;
  product_info?: ProductInput;
}

export interface ContentTemplateResponse {
  success: boolean;
  platform: string;
  content_type: string;
  template: string;
  placeholders: string[];
  examples: string[];
}

// ============= Content Template API =============

export const getContentTemplate = async (request: ContentTemplateRequest): Promise<ContentTemplateResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/content/template`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};

// ============= Content Score Types =============

export interface ContentScoreRequest {
  content: string;
  platform?: string;
  title?: string;
  tags?: string[];
}

export interface ContentScoreResponse {
  success: boolean;
  overall_score: number;
  engagement_score: number;
  compliance_score: number;
  readability_score: number;
  seo_score: number;
  platform_fit_score: number;
  score_level: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
}

// ============= Content Score API =============

export const scoreContent = async (request: ContentScoreRequest): Promise<ContentScoreResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/content/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};

// ============= Content History Types =============

export interface ContentHistoryRecord {
  id: string;
  platform: string;
  title: string;
  content: string;
  tags: string[];
  created_at: string;
  updated_at: string;
  is_draft: boolean;
  product_name: string;
  metadata: Record<string, any>;
}

export interface ContentHistoryStats {
  total: number;
  drafts: number;
  published: number;
  platforms: string[];
}

export interface ContentHistoryAddRequest {
  platform: string;
  title: string;
  content: string;
  tags?: string[];
  product_name?: string;
  metadata?: Record<string, any>;
  is_draft?: boolean;
}

export interface ContentHistoryUpdateRequest {
  title?: string;
  content?: string;
  tags?: string[];
  is_draft?: boolean;
}

export interface ContentHistoryResponse {
  success: boolean;
  records: ContentHistoryRecord[];
  total: number;
  stats?: ContentHistoryStats;
}

// ============= Content History API =============

export const addContentHistory = async (request: ContentHistoryAddRequest): Promise<ContentHistoryResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/content/history`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};

export const getContentHistory = async (params?: {
  keyword?: string;
  platform?: string;
  is_draft?: boolean;
  limit?: number;
}): Promise<ContentHistoryResponse> => {
  const searchParams = new URLSearchParams();
  if (params?.keyword) searchParams.append("keyword", params.keyword);
  if (params?.platform) searchParams.append("platform", params.platform);
  if (params?.is_draft !== undefined && params?.is_draft !== null) {
    searchParams.append("is_draft", String(params.is_draft));
  }
  if (params?.limit) searchParams.append("limit", String(params.limit));

  const response = await fetch(`${API_BASE_URL}/api/v1/content/history?${searchParams}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};

export const getContentHistoryRecord = async (recordId: string): Promise<ContentHistoryResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/content/history/${recordId}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};

export const updateContentHistoryRecord = async (
  recordId: string,
  request: ContentHistoryUpdateRequest
): Promise<ContentHistoryResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/content/history/${recordId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};

export const deleteContentHistoryRecord = async (recordId: string): Promise<{ success: boolean; message: string }> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/content/history/${recordId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};

export const getContentHistoryStats = async (): Promise<{ success: boolean; stats: ContentHistoryStats }> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/content/history/stats/summary`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};