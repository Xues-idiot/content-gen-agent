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

  // UI 状态
  sidebarOpen: boolean;

  // 操作
  setProduct: (product: ProductData) => void;
  setSelectedPlatforms: (platforms: string[]) => void;
  setCopyResults: (results: CopyResult[]) => void;
  setImageSuggestions: (suggestions: Record<string, ImageSuggestion[]>) => void;
  setMarketResearch: (research: MarketResearch) => void;
  setIsLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setProgress: (progress: number) => void;
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
  sidebarOpen: true,
};

export const useContentStore = create<ContentState>()(
  persist(
    (set, get) => ({
      ...initialState,

      setProduct: (product) => set({ product }),

      setSelectedPlatforms: (platforms) => set({ selectedPlatforms: platforms }),

      setCopyResults: (results) => set({ copyResults: results }),

      setImageSuggestions: (suggestions) => set({ imageSuggestions: suggestions }),

      setMarketResearch: (research) => set({ marketResearch: research }),

      setIsLoading: (loading) => set({ isLoading: loading }),

      setError: (error) => set({ error }),

      setProgress: (progress) => set({ progress }),

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

      clearHistory: () => set({ history: [], currentHistoryIndex: -1 }),

      reset: () => set(initialState),
    }),
    {
      name: "vox-content-storage",
      partialize: (state) => ({
        history: state.history.slice(-10),
      }),
    }
  )
);
