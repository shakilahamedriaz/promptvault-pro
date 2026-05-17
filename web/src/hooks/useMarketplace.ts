import { useState, useEffect, useCallback } from "react";
import { api } from "@/api/client";

export interface MarketplacePrompt {
  id: string;
  title: string;
  body: string;
  description?: string;
  category: string;
  tags: string[];
  quality_score?: number;
  is_public: boolean;
  fork_of_id?: string;
  use_count: number;
  fork_count: number;
  avg_rating: number;
  rating_count: number;
  price_credits?: number;
  author_name: string;
  author_id: string;
  created_at: string;
}

export type SortOption = "newest" | "popular" | "rating";

export interface MarketplaceFilters {
  category?: string;
  tags?: string[];
  q?: string;
  sort?: SortOption;
  page?: number;
  per_page?: number;
  min_quality?: number;
  min_rating?: number;
  min_use_count?: number;
}

interface MarketplaceResponse {
  items: MarketplacePrompt[];
  total: number;
}

export function useMarketplace(filters: MarketplaceFilters = {}) {
  const [prompts, setPrompts] = useState<MarketplacePrompt[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { category, q, sort, page, per_page } = filters;

  const fetchPrompts = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (category && category !== "All") params.append("category", category);
      if (q) params.append("q", q);
      if (sort) params.append("sort", sort);
      if (page) params.append("page", String(page));
      if (per_page) params.append("per_page", String(per_page));

      const response = await api.get<MarketplaceResponse>(`/marketplace/prompts?${params.toString()}`);
      setPrompts(response.items ?? []);
      setTotal(response.total ?? 0);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load marketplace");
    } finally {
      setIsLoading(false);
    }
  }, [category, q, sort, page, per_page]); // primitives — stable refs, no blink loop

  useEffect(() => {
    fetchPrompts();
  }, [fetchPrompts]);

  const forkPrompt = useCallback(async (id: string) => {
    try {
      return await api.post<MarketplacePrompt>(`/marketplace/prompts/${id}/fork`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to fork prompt");
      throw err;
    }
  }, []);

  const ratePrompt = useCallback(async (id: string, score: number) => {
    try {
      await api.post(`/marketplace/prompts/${id}/rate`, { score });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to rate prompt");
      throw err;
    }
  }, []);

  const favoritePrompt = useCallback(async (id: string) => {
    try {
      await api.post(`/marketplace/prompts/${id}/favorite`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to favorite prompt");
      throw err;
    }
  }, []);

  const unfavoritePrompt = useCallback(async (id: string) => {
    try {
      await api.delete(`/marketplace/prompts/${id}/favorite`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to unfavorite prompt");
      throw err;
    }
  }, []);

  const checkFavorited = useCallback(async (id: string): Promise<boolean> => {
    try {
      const response = await api.get<{ is_favorited: boolean }>(`/marketplace/prompts/${id}/is-favorited`);
      return response.is_favorited;
    } catch {
      return false;
    }
  }, []);

  return {
    prompts,
    total,
    isLoading,
    error,
    fetchPrompts,
    forkPrompt,
    ratePrompt,
    favoritePrompt,
    unfavoritePrompt,
    checkFavorited,
  };
}
