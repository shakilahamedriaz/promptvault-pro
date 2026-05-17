import { useState, useEffect, useCallback } from "react";
import { api } from "@/api/client";

export interface CreatorProfile {
  id: string;
  display_name: string;
  bio?: string;
  avatar_url?: string;
  follower_count: number;
  following_count: number;
  prompt_count: number;
  total_prompts?: number;
  avg_rating: number;
  avg_quality_score?: number;
  total_ratings?: number;
  is_following: boolean;
  created_at?: string;
}

interface CreatorPromptsResponse {
  items: unknown[];
  total?: number;
}

export function useCreator(userId: string | null) {
  const [profile, setProfile] = useState<CreatorProfile | null>(null);
  const [prompts, setPrompts] = useState<unknown[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCreator = useCallback(async () => {
    if (!userId) return;

    setIsLoading(true);
    setError(null);
    try {
      const profileData = await api.get<CreatorProfile>(`/creators/${userId}`);
      setProfile(profileData);

      const promptsData = await api.get<CreatorPromptsResponse>(`/creators/${userId}/prompts`);
      setPrompts(promptsData.items ?? []);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load creator");
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchCreator();
  }, [fetchCreator]);

  const toggleFollow = useCallback(async () => {
    if (!userId || !profile) return;

    try {
      if (profile.is_following) {
        await api.post(`/users/${userId}/unfollow`);
      } else {
        await api.post(`/users/${userId}/follow`);
      }
      setProfile((prev) => prev ? { ...prev, is_following: !prev.is_following } : null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to toggle follow");
    }
  }, [userId, profile]);

  return { profile, prompts, isLoading, error, toggleFollow };
}
