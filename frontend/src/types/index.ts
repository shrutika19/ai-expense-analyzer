export type ExpenseCategory =
  | "Food"
  | "Groceries" | "Dining"
  | "Transport"
  | "Rent"
  | "Housing"
  | "Utilities"
  | "Shopping"
  | "Healthcare" | "Health" | "Entertainment" | "Travel" | "Education" | "Other" | "Subscriptions";

export const EXPENSE_CATEGORIES: ExpenseCategory[] = [
  "Food",
  "Transport",
  "Rent",
  "Utilities",
  "Shopping",
  "Healthcare",
  "Entertainment",
  "Travel",
  "Education", "Other",
];

export interface Expense {
  id: string;
  /** ISO date, e.g. 2026-04-17 */
  date: string;
  merchant: string;
  category: ExpenseCategory;
  amount: number;
  note?: string;
  category_source?: "manual" | "ml";
  category_confidence?: number | null;
  model_version?: string | null;
}

export type NewExpense = Omit<Expense, "id" | "category"> & { category?: ExpenseCategory };

export interface Kpi {
  label: string;
  value: string;
  hint: string;
  deltaPct?: number;
}

export interface CategoryTotal {
  category: ExpenseCategory;
  total: number;
  count: number;
  share: number;
}

export interface MonthlyTotal {
  /** YYYY-MM */
  month: string;
  label: string;
  total: number;
  count: number;
}

export interface MerchantTotal {
  merchant: string;
  total: number;
  count: number;
}

export type LoadStatus = "loading" | "error" | "ready";

export interface InsightMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  pending?: boolean;
}

export type UploadStatus = "idle" | "validating" | "uploading" | "success" | "error";

export interface ParsedRow {
  date: string;
  merchant: string;
  category: string;
  amount: number;
}
