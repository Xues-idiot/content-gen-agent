"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface ProductData {
  name: string;
  description: string;
  sellingPoints: string[];
  targetUsers: string[];
  category: string;
  priceRange: string;
}

export interface CopyResult {
  platform: string;
  title: string;
  content: string;
  script?: string;
  tags: string[];
  imageSuggestions: string[];
  cta?: string;  // Call-to-Action 行动号召
  review?: {
    passed: boolean;
    qualityScore: number;
    violations: Array<{ word: string; suggestion: string; severity?: string }>;
    suggestions?: string[];
  };
  success: boolean;
  error?: string;
  version?: number;
  updatedAt?: number;
}

export interface ImageSuggestion {
  type: string;
  description: string;
  prompt: string;
}

export interface MarketResearch {
  insights: string[];
  trends: string[];
  competitors: { name: string; title: string; url: string }[];
}

interface HistoryEntry {
  id: string;
  timestamp: number;
  product: ProductData;
  platforms: string[];
  results: CopyResult[];
  suggestions: Record<string, ImageSuggestion[]>;
  marketResearch?: MarketResearch;
}

interface ContentState {
  // 状态
  product: ProductData | null;
  selectedPlatforms: string[];
  copyResults: CopyResult[];
  imageSuggestions: Record<string, ImageSuggestion[]>;
  marketResearch: MarketResearch;
  isLoading: boolean;
  error: string | null;
  progress: number;

  // 历史记录
  history: HistoryEntry[];
  currentHistoryIndex: number;

  // 版本历史
  versions: Record<string, CopyResult[]>;

  // UI 状态
  sidebarOpen: boolean;

  // 操作
  setProduct: (product: ProductData) => void;
  setSelectedPlatforms: (platforms: string[]) => void;
  setCopyResults: (results: CopyResult[]) => void;
  updateCopyResult: (platform: string, result: Partial<CopyResult>) => void;
  setImageSuggestions: (suggestions: Record<string, ImageSuggestion[]>) => void;
  setMarketResearch: (research: MarketResearch) => void;
  setIsLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setProgress: (progress: number | ((prev: number) => number)) => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  // 历史操作
  addToHistory: () => void;
  clearHistory: () => void;
  reset: () => void;
}

const generateId = () => `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

const initialState = {
  product: null,
  selectedPlatforms: ["xiaohongshu"] as string[],
  copyResults: [] as CopyResult[],
  imageSuggestions: {} as Record<string, ImageSuggestion[]>,
  marketResearch: { insights: [], trends: [], competitors: [] } as MarketResearch,
  isLoading: false,
  error: null as string | null,
  progress: 0,
  history: [] as HistoryEntry[],
  currentHistoryIndex: -1,
  versions: {} as Record<string, CopyResult[]>,
  sidebarOpen: true,
};

export const useContentStore = create<ContentState>()(
  persist(
    (set, get) => ({
      ...initialState,

      setProduct: (product) => set({ product }),

      setSelectedPlatforms: (platforms) => set({ selectedPlatforms: platforms }),

      setCopyResults: (results) => set({ copyResults: results }),

      updateCopyResult: (platform, update) =>
        set((state) => ({
          copyResults: state.copyResults.map((r) =>
            r.platform === platform ? { ...r, ...update } : r
          ),
        })),

      setImageSuggestions: (suggestions) => set({ imageSuggestions: suggestions }),

      setMarketResearch: (research) => set({ marketResearch: research }),

      setIsLoading: (loading) => set({ isLoading: loading }),

      setError: (error) => set({ error }),

      setProgress: (progress) => set((state) => ({
        progress: typeof progress === 'function' ? progress(state.progress) : progress,
      })),

      setSidebarOpen: (open) => set({ sidebarOpen: open }),

      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

      addToHistory: () => {
        const state = get();
        if (!state.product) return;

        const entry: HistoryEntry = {
          id: generateId(),
          timestamp: Date.now(),
          product: state.product,
          platforms: state.selectedPlatforms,
          results: state.copyResults,
          suggestions: state.imageSuggestions,
          marketResearch: state.marketResearch,
        };

        set((s) => ({
          history: [...s.history.slice(0, s.currentHistoryIndex + 1), entry].slice(-20),
          currentHistoryIndex: Math.min(s.currentHistoryIndex + 1, s.history.length),
        }));
      },

      clearHistory: () => set({ history: [], currentHistoryIndex: -1, versions: {} }),

      reset: () => set(initialState),

      // 版本管理
      saveVersion: (platform: string) => {
        const state = get();
        const currentResults = state.copyResults.filter((r) => r.platform === platform);
        if (currentResults.length === 0) return;

        set((s) => ({
          versions: {
            ...s.versions,
            [platform]: [...(s.versions[platform] || []), ...currentResults].slice(-5),
          },
        }));
      },

      getVersions: (platform: string) => {
        return get().versions[platform] || [];
      },

    }),
    {
      name: "vox-content-storage",
      partialize: (state) => ({
        history: state.history.slice(-10),
      }),
    }
  )
);
