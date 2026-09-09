import type {
  CategoryTotal,
  Expense,
  ExpenseCategory,
  MerchantTotal,
  MonthlyTotal,
} from "@/types";
import { monthLabel } from "@/utils/format";

/**
 * Presentation-side derivations over the mock dataset.
 * These are placeholders for values the FastAPI backend will return later.
 */

export function totalSpend(expenses: Expense[]): number {
  return expenses.reduce((sum, e) => sum + e.amount, 0);
}

export function averageExpense(expenses: Expense[]): number {
  return expenses.length ? totalSpend(expenses) / expenses.length : 0;
}

export function byCategory(expenses: Expense[]): CategoryTotal[] {
  const map = new Map<ExpenseCategory, { total: number; count: number }>();
  for (const e of expenses) {
    const entry = map.get(e.category) ?? { total: 0, count: 0 };
    entry.total += e.amount;
    entry.count += 1;
    map.set(e.category, entry);
  }
  const grand = totalSpend(expenses) || 1;
  return [...map.entries()]
    .map(([category, v]) => ({
      category,
      total: v.total,
      count: v.count,
      share: (v.total / grand) * 100,
    }))
    .sort((a, b) => b.total - a.total);
}

export function byMonth(expenses: Expense[]): MonthlyTotal[] {
  const map = new Map<string, { total: number; count: number }>();
  for (const e of expenses) {
    const month = e.date.slice(0, 7);
    const entry = map.get(month) ?? { total: 0, count: 0 };
    entry.total += e.amount;
    entry.count += 1;
    map.set(month, entry);
  }
  return [...map.entries()]
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([month, v]) => ({ month, label: monthLabel(month), total: v.total, count: v.count }));
}

export function byMerchant(expenses: Expense[], limit = 6): MerchantTotal[] {
  const map = new Map<string, { total: number; count: number }>();
  for (const e of expenses) {
    const entry = map.get(e.merchant) ?? { total: 0, count: 0 };
    entry.total += e.amount;
    entry.count += 1;
    map.set(e.merchant, entry);
  }
  return [...map.entries()]
    .map(([merchant, v]) => ({ merchant, total: v.total, count: v.count }))
    .sort((a, b) => b.total - a.total)
    .slice(0, limit);
}

export function monthOverMonth(expenses: Expense[]): number {
  const months = byMonth(expenses);
  if (months.length < 2) return 0;
  const last = months[months.length - 1]?.total ?? 0;
  const prev = months[months.length - 2]?.total ?? 0;
  if (!prev) return 0;
  return ((last - prev) / prev) * 100;
}

export function recent(expenses: Expense[], limit = 6): Expense[] {
  return [...expenses].sort((a, b) => b.date.localeCompare(a.date)).slice(0, limit);
}
