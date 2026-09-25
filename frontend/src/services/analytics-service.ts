import { api } from "@/services/api-client";

export interface AnalyticsSummary { total_amount: string; expense_count: number; average_amount: string; highest_amount: string | null; lowest_amount: string | null }
export const getAnalyticsSummary = () => api<AnalyticsSummary>("/analytics/summary");
