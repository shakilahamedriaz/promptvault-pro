import { useState, useEffect, useCallback } from "react";
import { api } from "@/api/client";

export interface EarningsSummary {
  total_revenue: number;
  this_month: number;
  this_week: number;
  avg_price: number;
  total_sales_count?: number;
}

export interface TopPrompt {
  id: string;
  title: string;
  revenue: number;
  sales_count: number;
  avg_rating?: number;
}

export interface Payout {
  id: string;
  amount: number;
  status: "pending" | "completed" | "failed";
  created_at: string;
}

export function useEarnings() {
  const [summary, setSummary] = useState<EarningsSummary | null>(null);
  const [topPrompts, setTopPrompts] = useState<TopPrompt[]>([]);
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEarnings = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [summaryRes, topRes, payoutRes] = await Promise.all([
        api.get<EarningsSummary>("/creator/earnings/summary"),
        api.get<{ items: TopPrompt[] }>("/creator/earnings/top-prompts"),
        api.get<{ items: Payout[] }>("/creator/payouts"),
      ]);

      setSummary(summaryRes);
      setTopPrompts(topRes.items ?? []);
      setPayouts(payoutRes.items ?? []);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load earnings");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEarnings();
  }, [fetchEarnings]);

  return { summary, topPrompts, payouts, isLoading, error };
}
