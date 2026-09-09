import { createContext, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { useExpenses } from "@/hooks/use-expenses";
import type { Expense } from "@/types";

export type RangeKey = "1m" | "3m" | "6m";

export const RANGE_LABELS: Record<RangeKey, string> = {
  "1m": "This month",
  "3m": "Last 3 months",
  "6m": "Last 6 months",
};

interface RangeContextValue {
  range: RangeKey;
  setRange: (r: RangeKey) => void;
}

const RangeContext = createContext<RangeContextValue | null>(null);

export function RangeProvider({ children }: { children: ReactNode }) {
  const [range, setRange] = useState<RangeKey>("6m");
  const value = useMemo(() => ({ range, setRange }), [range]);
  return <RangeContext.Provider value={value}>{children}</RangeContext.Provider>;
}

export function useRange(): RangeContextValue {
  const ctx = useContext(RangeContext);
  if (!ctx) throw new Error("useRange must be used inside <RangeProvider>");
  return ctx;
}

function cutoffFor(range: RangeKey): string {
  const now = new Date();
  const months = range === "1m" ? 0 : range === "3m" ? 2 : 5;
  const start = new Date(now.getFullYear(), now.getMonth() - months, 1);
  return `${start.getFullYear()}-${String(start.getMonth() + 1).padStart(2, "0")}-01`;
}

/** Expenses narrowed by the shell's date-range selector. */
export function useRangedExpenses(): {
  expenses: Expense[];
  status: ReturnType<typeof useExpenses>["status"];
  reload: () => void;
} {
  const { expenses, status, reload } = useExpenses();
  const { range } = useRange();
  const filtered = useMemo(() => {
    const cutoff = cutoffFor(range);
    return expenses.filter((e) => e.date >= cutoff);
  }, [expenses, range]);
  return { expenses: filtered, status, reload };
}
