import { createFileRoute } from "@tanstack/react-router";

import { AppShell } from "@/common/app-shell";
import { ErrorBlock } from "@/common/states";
import { ExpensesTable } from "@/dashboard/expenses-table";
import { useRangedExpenses } from "@/hooks/use-range";

export const Route = createFileRoute("/expenses")({
  head: () => ({
    meta: [
      { title: "Expenses — AI Expense Analyzer" },
      {
        name: "description",
        content:
          "Search, filter and sort every transaction, add new expenses, and remove entries you don't need.",
      },
      { property: "og:title", content: "Expenses — AI Expense Analyzer" },
      {
        property: "og:description",
        content: "A searchable, sortable table of all your recorded transactions.",
      },
    ],
  }),
  component: ExpensesPage,
});

function ExpensesPage() {
  const { expenses, status, reload } = useRangedExpenses();

  return (
    <AppShell title="Expenses" description="Every transaction in the selected range">
      {status === "error" ? (
        <ErrorBlock onRetry={reload} />
      ) : (
        <ExpensesTable expenses={expenses} loading={status === "loading"} />
      )}
    </AppShell>
  );
}
