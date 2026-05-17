import { useState, useEffect, useCallback } from "react";
import { api } from "@/api/client";

export interface Review {
  id: string;
  prompt_id: string;
  user_id: string;
  title: string;
  content: string;
  rating: number;
  helpful_count: number;
  unhelpful_count: number;
  user_helpful?: boolean;
  created_at: string;
  author_name: string;
}

interface ReviewsResponse {
  items: Review[];
  total: number;
}

export function useReviews(promptId: string) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReviews = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.get<ReviewsResponse>(`/marketplace/prompts/${promptId}/reviews`);
      setReviews(response.items ?? []);
      setTotal(response.total ?? 0);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load reviews");
    } finally {
      setIsLoading(false);
    }
  }, [promptId]);

  useEffect(() => {
    fetchReviews();
  }, [fetchReviews]);

  const createReview = useCallback(async (title: string, content: string, rating: number) => {
    try {
      const result = await api.post<Review>(`/marketplace/prompts/${promptId}/reviews`, {
        title,
        content,
        rating,
      });
      setReviews((prev) => [result, ...prev]);
      setTotal((n) => n + 1);
      return result;
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to post review");
      throw err;
    }
  }, [promptId]);

  const voteHelpful = useCallback(async (reviewId: string, helpful: boolean) => {
    try {
      await api.post(`/reviews/${reviewId}/helpful`, { helpful });
      setReviews((prev) =>
        prev.map((r) =>
          r.id === reviewId
            ? {
                ...r,
                helpful_count: helpful ? r.helpful_count + 1 : r.helpful_count,
                user_helpful: helpful,
              }
            : r
        )
      );
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to vote");
      throw err;
    }
  }, []);

  return { reviews, total, isLoading, error, createReview, voteHelpful, fetchReviews };
}
