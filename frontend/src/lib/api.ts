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
