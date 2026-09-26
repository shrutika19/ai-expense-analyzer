import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { createExpense, getExpenses } from "@/services/expense-service";
import { useAuth } from "@/hooks/use-auth";
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
  addExpense: (input: NewExpense) => Promise<Expense>;
  deleteExpense: (id: string) => void;
}

const ExpensesContext = createContext<ExpensesContextValue | null>(null);

export function ExpensesProvider({ children }: { children: ReactNode }) {
  const { user, loading: authLoading } = useAuth();
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [status, setStatus] = useState<LoadStatus>("loading");
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    // Do not request protected data from login/register pages or while the
    // stored JWT is still being verified.
    if (authLoading) return;
    if (!user) {
      setExpenses([]);
      setStatus("ready");
      return;
    }
    let active = true;
    getExpenses().then((items) => { if (active) { setExpenses(items); setStatus("ready"); } })
      .catch(() => { if (active) setStatus("error"); });
    return () => {
      active = false;
    };
  }, [nonce, user, authLoading]);

  const reload = useCallback(() => setNonce((n) => n + 1), []);

  const addExpense = useCallback(async (input: NewExpense) => {
    const expense = await createExpense(input);
    setExpenses((prev) => [expense, ...prev].sort((a, b) => b.date.localeCompare(a.date)));
    return expense;
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
