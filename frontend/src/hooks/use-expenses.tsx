import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { MOCK_EXPENSES } from "@/common/mock-expenses";
import type { Expense, LoadStatus, NewExpense } from "@/types";

/**
 * Single seam between the UI and the future FastAPI backend.
 * Today it serves the mock dataset with a simulated latency; swapping in a
 * real fetch means changing only this file.
 */

interface ExpensesContextValue {
  expenses: Expense[];
  status: LoadStatus;
  reload: () => void;
  addExpense: (input: NewExpense) => void;
  deleteExpense: (id: string) => void;
}

const ExpensesContext = createContext<ExpensesContextValue | null>(null);

export function ExpensesProvider({ children }: { children: ReactNode }) {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [status, setStatus] = useState<LoadStatus>("loading");
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    let active = true;
    const timer = setTimeout(() => {
      if (!active) return;
      setExpenses(MOCK_EXPENSES);
      setStatus("ready");
    }, 650);
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [nonce]);

  const reload = useCallback(() => setNonce((n) => n + 1), []);

  const addExpense = useCallback((input: NewExpense) => {
    setExpenses((prev) =>
      [{ ...input, id: `exp-local-${Date.now()}` }, ...prev].sort((a, b) =>
        b.date.localeCompare(a.date),
      ),
    );
  }, []);

  const deleteExpense = useCallback((id: string) => {
    setExpenses((prev) => prev.filter((e) => e.id !== id));
  }, []);

  const value = useMemo(
    () => ({ expenses, status, reload, addExpense, deleteExpense }),
    [expenses, status, reload, addExpense, deleteExpense],
  );

  return <ExpensesContext.Provider value={value}>{children}</ExpensesContext.Provider>;
}

export function useExpenses(): ExpensesContextValue {
  const ctx = useContext(ExpensesContext);
  if (!ctx) throw new Error("useExpenses must be used inside <ExpensesProvider>");
  return ctx;
}
