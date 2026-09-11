import { useState } from "react";

import {
  importExpenses,
} from "@/services/expense-service";

import type {
  ExpenseImportResponse,
} from "@/types/expense";

interface UseExpenseUploadResult {
  upload_file: (
    file: File,
  ) => Promise<ExpenseImportResponse | null>;
  loading: boolean;
  result: ExpenseImportResponse | null;
  error_msg: string | null;
  reset_file: () => void;
}

export function useExpenseUpload(): UseExpenseUploadResult {
  const [loading, setLoading] = useState(false);
  const [result, setResult] =
    useState<ExpenseImportResponse | null>(null);
  const [error, setError] =
    useState<string | null>(null);

  const upload_file = async (
    file: File,
  ): Promise<ExpenseImportResponse | null> => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await importExpenses(file);

      setResult(response);

      return response;
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Failed to upload expenses.";

      setError(message);

      return null;
    } finally {
      setLoading(false);
    }
  };

  const reset_file = () => {
    setLoading(false);
    setResult(null);
    setError(null);
  };

  return {
    upload_file,
    loading,
    result,
    error_msg: error,
    reset_file,
  };
}