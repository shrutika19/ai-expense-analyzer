import { api } from "@/services/api-client";
import type { Expense, NewExpense } from "@/types";
import type { ExpenseImportResponse } from "@/types/expense";

type ApiExpense = Omit<Expense, "merchant" | "date"> & { description: string; expense_date: string };
const mapExpense = (expense: ApiExpense): Expense => ({ ...expense, amount: Number(expense.amount), merchant: expense.description, date: expense.expense_date });
export const getExpenses = async () => (await api<ApiExpense[]>("/expenses")).map(mapExpense);
export const createExpense = async (input: NewExpense) => mapExpense(await api<ApiExpense>("/expenses", {
  method: "POST", body: JSON.stringify({ description: input.merchant, amount: input.amount,
    expense_date: input.date, category: input.category || undefined }),
}));

export async function importExpenses(
  file: File,
): Promise<ExpenseImportResponse> {
  const formData = new FormData();

  formData.append("file", file);

  return api<ExpenseImportResponse>("/expenses/import", { method: "POST", body: formData });
}
