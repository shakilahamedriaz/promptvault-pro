import { useState, useEffect, useCallback } from 'react';
import { api } from '@/api/client';
import toast from 'react-hot-toast';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Prompt {
  id: string;
  title: string;
  body: string;
  category: string;
  tags: string[];
  is_favorite: boolean;
  use_count: number;
  quality_score: number | null;
  variables: Record<string, string>;
  created_at: string;
  updated_at: string;
}

export interface PromptVersion {
  id: string;
  prompt_id: string;
  body: string;
  version_number: number;
  created_at: string;
}

export interface CreatePromptPayload {
  title: string;
  body: string;
  category: string;
  tags: string[];
}

export interface UpdatePromptPayload extends Partial<CreatePromptPayload> {
  is_favorite?: boolean;
}

interface PromptsListResponse {
  items: Prompt[];
  total: number;
  page: number;
  per_page: number;
}

export type SortOption = 'recent' | 'alpha' | 'most_used';

interface UsePromptsOptions {
  search?: string;
  category?: string;
  tag?: string;
  sort?: SortOption;
  page?: number;
  perPage?: number;
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function usePrompts(options: UsePromptsOptions = {}) {
  const { search = '', category = '', tag = '', sort = 'recent', page = 1, perPage = 20 } = options;

  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPrompts = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (search) params.set('search', search);
      if (category) params.set('category', category);
      if (tag) params.set('tag', tag);
      params.set('sort', sort);
      params.set('page', String(page));
      params.set('per_page', String(perPage));

      const data = await api.get<PromptsListResponse>(`/prompts?${params}`);
      setPrompts(data.items);
      setTotal(data.total);
    } catch {
      setError('Failed to load prompts.');
    } finally {
      setIsLoading(false);
    }
  }, [search, category, tag, sort, page, perPage]);

  useEffect(() => {
    fetchPrompts();
  }, [fetchPrompts]);

  const createPrompt = useCallback(async (payload: CreatePromptPayload): Promise<Prompt> => {
    const created = await api.post<Prompt>('/prompts', payload);
    setPrompts((prev) => [created, ...prev]);
    setTotal((t) => t + 1);
    toast.success('Prompt created!');
    return created;
  }, []);

  const updatePrompt = useCallback(
    async (id: string, payload: UpdatePromptPayload): Promise<Prompt> => {
      const updated = await api.put<Prompt>(`/prompts/${id}`, payload);
      setPrompts((prev) => prev.map((p) => (p.id === id ? updated : p)));
      toast.success('Prompt updated!');
      return updated;
    },
    [],
  );

  const deletePrompt = useCallback(async (id: string): Promise<void> => {
    await api.delete(`/prompts/${id}`);
    setPrompts((prev) => prev.filter((p) => p.id !== id));
    setTotal((t) => t - 1);
    toast.success('Prompt deleted.');
  }, []);

  const toggleFavorite = useCallback(
    async (id: string): Promise<void> => {
      const prompt = prompts.find((p) => p.id === id);
      if (!prompt) return;
      await updatePrompt(id, { is_favorite: !prompt.is_favorite });
    },
    [prompts, updatePrompt],
  );

  const getVersions = useCallback(async (id: string): Promise<PromptVersion[]> => {
    return api.get<PromptVersion[]>(`/prompts/${id}/versions`);
  }, []);

  return {
    prompts,
    total,
    isLoading,
    error,
    refetch: fetchPrompts,
    createPrompt,
    updatePrompt,
    deletePrompt,
    toggleFavorite,
    getVersions,
  };
}
