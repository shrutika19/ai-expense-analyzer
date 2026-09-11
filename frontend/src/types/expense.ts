export interface ExpenseImportResponse {
  imported_count: number;
  failed_count: number;
  duplicate_count?: number;
  message: string;
  errors?: Array<{
    row: number;
    message: string;
    field?: string;
  }>;
  skipped_rows?: number[];
}