// API 工具函数

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8003";

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
  cta?: string;  // Call-to-Action 行动号召
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
}

export interface ApiError {
  error: string;
  detail?: string;
}

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
    return response.json();
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
      return response.ok;
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
      tags: tags.join(","),
    });
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
