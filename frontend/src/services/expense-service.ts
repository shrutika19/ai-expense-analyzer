import type { ExpenseImportResponse } from "@/types/expense";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function importExpenses(
  file: File,
): Promise<ExpenseImportResponse> {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/api/v1/expenses/import`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    let message = "Failed to import expenses.";

    try {
      const error = await response.json();

      message =
        error?.error?.message ??
        error?.detail ??
        message;
    } catch {
      // Keep default message.
    }

    throw new Error(message);
  }

  return response.json();
}