import { useEffect, useState } from "react";
import { getAnalyticsSummary, type AnalyticsSummary } from "@/services/analytics-service";
export function useAnalyticsSummary() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null); const [error, setError] = useState(false);
  useEffect(() => { getAnalyticsSummary().then(setSummary).catch(() => setError(true)); }, []);
  return { summary, loading: !summary && !error, error };
}
